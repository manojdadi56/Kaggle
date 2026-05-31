"""Patch the live Kaggle notebook so a browser 'Save & Run All' actually succeeds.

Two known run-blocking/correctness gaps this fixes (audited 2026-05-31, notebook v42):
  1. Cell 0 was EMPTY -> the nvidia-utility-script offline stack (cutlass.cute / Mamba3
     deps) was never activated, so model load with trust_remote_code crashes with
     ModuleNotFoundError: cutlass.cute. We restore the verified site.addsitedir bootstrap
     (per memory: kaggle-nvidia-utility-script-offline-import) + Blackwell ptxas mirror.
  2. The last cell was a stale non-host-parity eval that OVERWROTE cv_score.json with a
     wrong score AND no submission.zip was ever produced. We replace it with adapter
     packaging into submission.zip (rank<=32 validated) so the run yields a submittable
     artifact.

Pushes via MCP save_notebook QuickSave (preserves all fork bindings/dataSources).
The user still must select RTX Pro 6000 + Internet ON and click 'Save & Run All (Commit)'.

Usage:
    python tools/patch_notebook_bootstrap.py            # pull live, patch, push
    python tools/patch_notebook_bootstrap.py --dry-run  # write patched nb locally, no push
"""
from __future__ import annotations
import argparse
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NB_SLUG = "sai1881/nvidia-nemotron-submission-demo"

CELL0_BOOTSTRAP = r'''# === v43 bootstrap: activate offline Nemotron stack BEFORE any `import torch` ===
# ryanholbrook/nvidia-utility-script vendors torch2.12 + transformers5.3 + nvidia-cutlass-dsl
# (cutlass / cutlass.cute) + mamba_ssm + flash_attn. Activate via site.addsitedir so the .pth
# hooks wire `cutlass`. DO NOT `import nvidia_utility_script` (runs live pip -> breaks offline).
import os, sys, site, glob, shutil
UTIL = '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script'
if not os.path.isdir(UTIL):
    hits = (glob.glob('/kaggle/usr/lib/notebooks/*/nvidia-utility-script')
            or glob.glob('/kaggle/usr/lib/*/nvidia-utility-script'))
    if hits:
        UTIL = hits[0]
if os.path.isdir(UTIL):
    site.addsitedir(UTIL)        # runs .pth hooks -> wires cutlass / cutlass.cute
    sys.path.insert(0, UTIL)     # shadow base torch/transformers with vendored 2.12 / 5.3
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    print('utility-script activated:', UTIL)
else:
    print('WARN: nvidia-utility-script mount NOT found - model load may fail on cutlass.cute')

# Blackwell (RTX Pro 6000, sm_120): RO mount strips +x from triton ptxas-blackwell ->
# PermissionError when a kernel compiles. Mirror ONLY triton's nvidia bin dir to /tmp,
# chmod +x, point TRITON_* env at the writable copies. (.so unaffected; never copy whole tree.)
try:
    import triton
    tdir = os.path.join(os.path.dirname(triton.__file__), 'backends', 'nvidia', 'bin')
    if os.path.isdir(tdir):
        dst = '/tmp/triton_bin'
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(tdir):
            s = os.path.join(tdir, f); d = os.path.join(dst, f)
            if not os.path.exists(d):
                shutil.copy2(s, d); os.chmod(d, 0o755)
        for env_k, fn in [('TRITON_PTXAS_PATH', 'ptxas'),
                          ('TRITON_CUOBJDUMP_PATH', 'cuobjdump'),
                          ('TRITON_NVDISASM_PATH', 'nvdisasm')]:
            p = os.path.join(dst, fn)
            if os.path.exists(p):
                os.environ[env_k] = p
        os.environ['PATH'] = dst + os.pathsep + os.environ.get('PATH', '')
        print('triton bin mirrored to', dst)
except Exception as e:
    print('triton bin mirror skipped:', e)
'''

CELL_PACKAGE = r'''# === v43: package LoRA adapter into submission.zip (host requires rank<=32) ===
import os, json, glob, zipfile
OUT = '/kaggle/working'
cfg_path = os.path.join(OUT, 'adapter_config.json')
assert os.path.exists(cfg_path), 'no adapter_config.json - training/save step did not run'
cfg = json.load(open(cfg_path))
assert cfg.get('r', 999) <= 32, f"adapter rank {cfg.get('r')} > 32 - host rejects"
files = ['adapter_config.json']
files += [os.path.basename(p) for p in glob.glob(os.path.join(OUT, 'adapter_model*'))]
for extra in ['README.md', 'adapter_model.safetensors']:
    fp = os.path.join(OUT, extra)
    if os.path.exists(fp) and extra not in files:
        files.append(extra)
zip_path = os.path.join(OUT, 'submission.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        fp = os.path.join(OUT, f)
        if os.path.exists(fp):
            z.write(fp, arcname=f)
print('submission.zip packaged with:', files)
cvp = os.path.join(OUT, 'cv_score.json')
print('cv_score.json:', json.load(open(cvp)) if os.path.exists(cvp) else 'MISSING')
'''


def _env() -> dict:
    out = {}
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _mcp(tok: str, name: str, args: dict, timeout: int = 120) -> str:
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": name, "arguments": args}}
    req = urllib.request.Request(
        "https://www.kaggle.com/mcp", data=json.dumps(rpc).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "Accept": "application/json,text/event-stream"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result", {}).get("content", [{}])[0].get("text", "")
    return body


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    env = _env()
    tok = env["KAGGLE_API_TOKEN"]
    user, slug = NB_SLUG.split("/")

    info = _mcp(tok, "get_notebook_info", {"request": {"userName": user, "kernelSlug": slug}})
    nb = json.loads(json.loads(info)["blob"]["source"])
    cells = nb["cells"]
    print(f"pulled notebook: {len(cells)} cells")

    # Cell 0 -> bootstrap
    cells[0]["source"] = CELL0_BOOTSTRAP
    # Last cell -> packaging (was stale eval overwriting cv_score.json)
    cells[-1]["source"] = CELL_PACKAGE
    print("patched cell 0 (bootstrap) + last cell (packaging)")

    (REPO / "state" / "live_notebook_v43_patched.json").write_text(
        json.dumps(nb, indent=1), encoding="utf-8")

    if args.dry_run:
        print("DRY RUN: wrote state/live_notebook_v43_patched.json, not pushing")
        return 0

    body = {"request": {"slug": NB_SLUG, "newTitle": "nvidia-nemotron-submission-demo",
                        "text": json.dumps(nb), "kernelType": "notebook", "language": "python",
                        "isPrivate": True, "kernelExecutionType": "QuickSave"}}
    push = _mcp(tok, "save_notebook", body)
    print("push result:", push[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

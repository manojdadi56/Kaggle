"""Apply one ablation config from experiments/ablation_configs.py to the live Kaggle notebook.

Usage:
    python tools/apply_ablation.py rank16
    python tools/apply_ablation.py 2epoch
    python tools/apply_ablation.py select2reason

Reads CONFIGS dict, updates the notebook's tunable constants via search-and-replace,
re-pushes via MCP save_notebook. Preserves all bindings.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ABLATION_PY = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "experiments" / "ablation_configs.py"
NB_SLUG = "sai1881/nvidia-nemotron-submission-demo"


def _load_configs() -> dict:
    spec = importlib.util.spec_from_file_location("ablation_configs", ABLATION_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "CONFIGS", {})


def _env() -> dict[str, str]:
    out: dict[str, str] = {}
    env = REPO / ".env"
    if not env.exists(): return out
    for line in env.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _mcp(tok: str, name: str, args: dict):
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}}
    req = urllib.request.Request("https://www.kaggle.com/mcp", data=json.dumps(rpc).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "Accept": "application/json,text/event-stream"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode("utf-8", "replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result", {}).get("content", [{}])[0].get("text", "")
    return body


# Notebook-source replacements for each tunable
REPLACEMENTS = {
    "lora_rank": (r"LORA_RANK\s*=\s*\d+", "LORA_RANK = {value}"),
    "alpha":     (r"lora_alpha=\d+",       "lora_alpha={value}"),
    "epochs":    (r"EPOCHS\s*=\s*\d+",     "EPOCHS = {value}"),
    "lr":        (r"lr_initial\s*=\s*[\d.e\-]+", "lr_initial = {value}"),
}


def apply(config_name: str) -> int:
    configs = _load_configs()
    if config_name not in configs:
        print(f"ERROR: '{config_name}' not in CONFIGS. Available: {list(configs.keys())}", file=sys.stderr)
        return 2
    cfg = configs[config_name]
    print(f"applying config '{config_name}':")
    for k, v in cfg.items():
        if k not in ("hypothesis", "source", "target_modules"): print(f"  {k} = {v}")

    env = _env()
    tok = env.get("KAGGLE_API_TOKEN")
    if not tok:
        print("ERROR: KAGGLE_API_TOKEN not in .env", file=sys.stderr); return 2

    # Fetch current source
    user, slug = NB_SLUG.split("/")
    info = _mcp(tok, "get_notebook_info", {"request": {"userName": user, "kernelSlug": slug}})
    obj = json.loads(info)
    nb = json.loads(obj["blob"]["source"])

    # Apply replacements per cell
    changes = 0
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code": continue
        src = cell.get("source", "")
        if isinstance(src, list): src = "".join(src)
        new = src
        for k, (pattern, template) in REPLACEMENTS.items():
            if k in cfg:
                new = re.sub(pattern, template.format(value=cfg[k]), new)
        if new != src:
            cell["source"] = new
            changes += 1
    print(f"changed cells: {changes}")

    # Push as QuickSave
    body_args = {"request": {
        "slug": NB_SLUG, "newTitle": "nvidia-nemotron-submission-demo",
        "text": json.dumps(nb), "kernelType": "notebook", "language": "python",
        "isPrivate": True, "kernelExecutionType": "QuickSave",
    }}
    push = _mcp(tok, "save_notebook", body_args)
    print(json.dumps(json.loads(push), indent=2)[:400] if push.startswith("{") else push[:400])
    return 0


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("config", help="config name (baseline, rank16, 2epoch, curriculum, select2reason, logprob_filter)")
    args = p.parse_args(argv)
    return apply(args.config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""v27: keep user's heartbeat cell 0 + append cutlass DSL + ptxas chmod + bnb install at its end."""
import json, urllib.request
from pathlib import Path

nb = json.loads(Path("_live.json").read_text(encoding="utf-8"))

# Read current cell 0
src0 = nb["cells"][0]["source"]
if isinstance(src0, list): src0 = "".join(src0)

# Check if my fixes are already in cell 0 (idempotent)
fixes_already_in = "nvidia_cutlass_dsl" in src0 and "ptxas" in src0

if not fixes_already_in:
    APPEND = "\n\n# --- v27 fixes (append to heartbeat): cutlass DSL + ptxas + bitsandbytes ---\n" + (
"# (1) The utility-script's mamba_ssm.Mamba3 imports cutlass.cute. Restore that path.\n"
"import site as _site\n"
"_CUT = '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/'\n"
"if os.path.isdir(_CUT):\n"
"    _site.addsitedir(_CUT); print(f'[v27] added cutlass DSL: {_CUT}', flush=True)\n"
"else:\n"
"    print(f'[v27] WARN: cutlass DSL not found at {_CUT}', flush=True)\n"
"\n"
"# (2) chmod ptxas binaries to /tmp (defense: RTX Pro 6000 sm_120 needs ptxas-blackwell executable)\n"
"import shutil as _shutil\n"
"_patched = []\n"
"for _nm in ('ptxas-blackwell','ptxas-hopper','ptxas-ada','ptxas'):\n"
"    for _src in glob.glob(f'/kaggle/usr/lib/notebooks/**/triton/backends/nvidia/bin/{_nm}', recursive=True):\n"
"        _dst = f'/tmp/triton_bin/{os.path.basename(_src)}'\n"
"        os.makedirs(os.path.dirname(_dst), exist_ok=True)\n"
"        if not os.path.exists(_dst):\n"
"            try: _shutil.copy(_src, _dst); os.chmod(_dst, 0o755); _patched.append(os.path.basename(_src))\n"
"            except Exception as _e: print(f'[v27] chmod skip {_src}: {_e}', flush=True)\n"
"if _patched:\n"
"    os.environ['PATH'] = '/tmp/triton_bin:' + os.environ.get('PATH','')\n"
"    print(f'[v27] patched triton: {_patched}', flush=True)\n"
"\n"
"# (3) Smoke-test mamba_ssm (triggers Mamba3 -> cutlass.cute import)\n"
"try:\n"
"    import mamba_ssm\n"
"    print(f'[v27] mamba_ssm OK: {mamba_ssm.__file__}', flush=True)\n"
"except Exception as _e:\n"
"    print(f'[v27] mamba_ssm FAIL (will likely fail downstream): {_e}', flush=True)\n"
"\n"
"# (4) bitsandbytes >= 0.46.1 if internet, else hope it's preinstalled\n"
"try:\n"
"    import bitsandbytes\n"
"    print(f'[v27] bitsandbytes OK: {bitsandbytes.__version__}', flush=True)\n"
"except ImportError:\n"
"    if _has_internet():\n"
"        print('[v27] installing bitsandbytes...', flush=True)\n"
"        _r = subprocess.run([sys.executable,'-m','pip','install','-q','-U','bitsandbytes>=0.46.1'], capture_output=True, text=True)\n"
"        print(f'[v27] bitsandbytes rc={_r.returncode}', flush=True)\n"
"        if _r.returncode != 0: print(_r.stderr[-500:], flush=True)\n"
"    else:\n"
"        print('[v27] bitsandbytes missing AND internet off — 4-bit path will fail. Toggle Internet ON.', flush=True)\n"
)
    src0 = src0 + APPEND
    nb["cells"][0]["source"] = src0
    print("appended v27 fixes to user's cell 0")
else:
    print("fixes already present in cell 0; no append")

Path("_v27.json").write_text(json.dumps(nb), encoding="utf-8")

env = {l.split("=",1)[0]: l.split("=",1)[1] for l in Path(".env").read_text(encoding="utf-8").splitlines() if l and "=" in l and not l.startswith("#")}
tok = env["KAGGLE_API_TOKEN"]
def call(name, args):
    rpc = {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":name,"arguments":args}}
    req = urllib.request.Request("https://www.kaggle.com/mcp", data=json.dumps(rpc).encode(),
        headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json","Accept":"application/json,text/event-stream"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode("utf-8","replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result",{}).get("content",[{}])[0].get("text","")
    return body

args = {"request": {
    "slug": "sai1881/nvidia-nemotron-submission-demo",
    "newTitle": "nvidia-nemotron-submission-demo",
    "text": Path("_v27.json").read_text(encoding="utf-8"),
    "kernelType": "notebook", "language": "python", "isPrivate": True,
    "kernelExecutionType": "QuickSave",
}}
print("push:", call("save_notebook", args))
info = call("get_notebook_info", {"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}})
m = json.loads(info)["metadata"]
print(f"version: {m.get('current_version_number')} | cells: {len(json.loads(json.loads(info)['blob']['source'])['cells'])}")

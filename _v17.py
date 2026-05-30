"""v17: prepend a chmod-fix cell for the ptxas-blackwell PermissionError on RTX Pro 6000 (Blackwell sm_120)."""
import json, urllib.request
from pathlib import Path

nb = json.loads(Path("_live.json").read_text(encoding="utf-8"))

# New first cell: chmod-fix any non-executable triton binaries from read-only mounts
chmod_fix_cell = {
    "cell_type": "code",
    "source": (
        "# ---- FIX: PermissionError on ptxas-blackwell (utility-script Triton wheel is read-only, missing +x) ----\n"
        "import os, glob, shutil, stat\n"
        "import importlib, sys\n"
        "patched = []\n"
        "for nm in ('ptxas-blackwell', 'ptxas-hopper', 'ptxas-ada', 'ptxas'):\n"
        "    for src in glob.glob(f'/kaggle/usr/lib/notebooks/**/triton/backends/nvidia/bin/{nm}', recursive=True):\n"
        "        dst = f'/tmp/triton_bin/{os.path.basename(src)}'\n"
        "        os.makedirs(os.path.dirname(dst), exist_ok=True)\n"
        "        if not os.path.exists(dst):\n"
        "            shutil.copy(src, dst)\n"
        "            os.chmod(dst, 0o755)\n"
        "            patched.append((src, dst))\n"
        "print('triton binaries patched:', len(patched))\n"
        "for s, d in patched: print(f'  {os.path.basename(s)} -> {d}')\n"
        "# Add the writable bin dir to PATH so subprocess calls find the executable ptxas first\n"
        "os.environ['PATH'] = '/tmp/triton_bin:' + os.environ.get('PATH', '')\n"
        "# Also try to override Triton's hardcoded path if it has been imported\n"
        "try:\n"
        "    import triton\n"
        "    print('triton already imported at:', triton.__file__)\n"
        "except ImportError:\n"
        "    print('triton not yet imported (good — will pick up the patched PATH)')"
    ),
    "metadata": {"trusted": True},
    "outputs": [],
    "execution_count": None,
}

# Insert at the very front
nb["cells"] = [chmod_fix_cell] + nb["cells"]
Path("_v17.json").write_text(json.dumps(nb), encoding="utf-8")

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
    "text": Path("_v17.json").read_text(encoding="utf-8"),
    "kernelType": "notebook", "language": "python", "isPrivate": True,
    "kernelExecutionType": "QuickSave",
}}
print("push:", call("save_notebook", args))
info = call("get_notebook_info", {"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}})
obj = json.loads(info)
m = obj["metadata"]
kg = json.loads(obj["blob"]["source"])["metadata"]["kaggle"]
print(f"version: {m.get('current_version_number')} | accelerator: {kg.get('accelerator')} | sources: {len(kg.get('dataSources', []))} | cells: {len(json.loads(obj['blob']['source'])['cells'])}")

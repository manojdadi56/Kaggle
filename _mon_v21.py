import json, urllib.request, time
from pathlib import Path
env={l.split("=",1)[0]:l.split("=",1)[1] for l in Path(".env").read_text(encoding="utf-8").splitlines() if l and "=" in l and not l.startswith("#")}
tok=env["KAGGLE_API_TOKEN"]
def call(n,a,to=120):
    rpc={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":n,"arguments":a}}
    req=urllib.request.Request("https://www.kaggle.com/mcp",data=json.dumps(rpc).encode(),headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json","Accept":"application/json,text/event-stream"},method="POST")
    with urllib.request.urlopen(req,timeout=to) as r:
        b=r.read().decode("utf-8","replace")
    for l in b.splitlines():
        if l.startswith("data: "): return json.loads(l[6:])["result"]["content"][0]["text"]
REQ={"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}}
prev=None
last_ver=None
for i in range(150):
    try:
        info=json.loads(call("get_notebook_info",REQ))
        ver=info.get("metadata",{}).get("current_version_number")
        st=json.loads(call("get_notebook_session_status",REQ)).get("status","?")
    except Exception as e:
        st=f"ERR:{e}"; ver="?"
    if st!=prev or ver!=last_ver:
        print(f"[{i*2}min] v{ver} status={st}",flush=True); prev=st; last_ver=ver
    if any(t in str(st).upper() for t in ("COMPLETE","ERROR","CANCEL")): break
    time.sleep(120)
out=call("list_notebook_session_output",REQ)
full="".join(e.get("data","") for e in json.loads(json.loads(out).get("log","[]")))
print(f"=== log {len(full)} chars ===",flush=True)
for l in full.splitlines():
    if any(k in l for k in ["GPU","RTX","T4","sm_","mamba_ssm OK","bitsandbytes","cutlass","trainable","loaded","step ","Training done","adapter r","CV ","Saving","submission.zip","Error","ModuleNotFoundError","INCOMPATIBLE","MODEL_PATH","Loading","Found no","CANNOT INSTALL","ptxas","Permission","patched triton","added cutlass"]):
        print(">",l.encode("ascii","replace").decode()[:180],flush=True)

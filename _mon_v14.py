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
for i in range(180):
    try: st=json.loads(call("get_notebook_session_status",REQ)).get("status","?")
    except Exception as e: st=f"ERR:{e}"
    if st!=prev: print(f"[{i*2}min] {st}",flush=True); prev=st
    if any(t in str(st).upper() for t in ("COMPLETE","ERROR","CANCEL")): break
    time.sleep(120)
out=call("list_notebook_session_output",REQ)
full="".join(e.get("data","") for e in json.loads(json.loads(out).get("log","[]")))
print(f"=== log {len(full)} chars ===",flush=True)
for l in full.splitlines():
    if any(k in l for k in ["GPU0","GPU1","Total VRAM","T4","P100","RTX","sm_","OFFLINE_DIR","train.csv","loaded","installing bnb","installing bitsandbytes","bnb installed","bnb already","rc=","Found no","Traceback","trainable","step ","Training done","adapter r","CV ","Saving","submission.zip"]):
        print(">",l.encode("ascii","replace").decode()[:185],flush=True)

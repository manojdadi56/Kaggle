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
last_machine=None
for i in range(150):
    try:
        st=json.loads(call("get_notebook_session_status",REQ)).get("status","?")
        if i%5==0:
            info=json.loads(call("get_notebook_info",REQ))
            m=info["metadata"].get("machine_shape")
            if m!=last_machine:
                print(f"[{i*2}min] status={st} machine={m}",flush=True); last_machine=m
                continue
    except Exception as e: st=f"ERR:{e}"
    if st!=prev: print(f"[{i*2}min] status={st}",flush=True); prev=st
    if any(t in str(st).upper() for t in ("COMPLETE","ERROR","CANCEL")): break
    time.sleep(120)
out=call("list_notebook_session_output",REQ)
try:
    obj=json.loads(out)
    log=obj.get("log","")
    ev=json.loads(log) if isinstance(log,str) and log.strip().startswith("[") else log
    full="".join(e.get("data","") for e in ev) if isinstance(ev,list) else str(ev)
    print(f"=== log {len(full)} chars ===",flush=True)
    for l in full.splitlines():
        if any(k in l for k in ["GPU","RTX","T4","P100","sm_","trainable","loaded","step ","Training done","adapter r","CV ","Error","INCOMPATIBLE","heartbeat","mamba","bitsandbytes","cutlass","MODEL_PATH","kaggle/input"]):
            print(">",l.encode("ascii","replace").decode()[:180],flush=True)
except Exception as e: print("parse err:",e)

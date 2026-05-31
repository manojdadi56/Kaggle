import os, json, shutil, tempfile, urllib.request
from pathlib import Path

env = {l.split("=",1)[0]: l.split("=",1)[1] for l in Path(".env").read_text(encoding="utf-8").splitlines() if l and "=" in l and not l.startswith("#")}
for k,v in env.items():
    if k.startswith("KAGGLE"): os.environ[k] = v

import kaggle
api = kaggle.KaggleApi(); api.authenticate()

CORPUS = Path("competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v6_local/corpus.jsonl")
USER = env["KAGGLE_USERNAME"]
SLUG = "nemotron-cot-corpus-v6"

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    shutil.copy(CORPUS, td / "corpus.jsonl")
    (td / "dataset-metadata.json").write_text(json.dumps({
        "title": "Nemotron CoT corpus v6 (gravity unit numeral)",
        "id": f"{USER}/{SLUG}",
        "licenses": [{"name": "CC0-1.0"}],
        "subtitle": "Verified CoT: gravity, unit_conv, numeral",
        "description": "1569 verified-CoT rows. Solvers add numeral (Roman) to v5.",
        "keywords": ["reasoning"],
    }, indent=2), encoding="utf-8")
    try:
        r = api.dataset_create_new(folder=str(td), public=False, quiet=True)
        print("create:", str(r)[:300])
    except Exception as e:
        print("trying version:", e)
        r = api.dataset_create_version(folder=str(td), version_notes="v6", quiet=True)
        print("version:", str(r)[:300])

# now push v33 attaching v6
tok = env["KAGGLE_API_TOKEN"]
def mcp(name, args):
    rpc = {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":name,"arguments":args}}
    req = urllib.request.Request("https://www.kaggle.com/mcp", data=json.dumps(rpc).encode(),
        headers={"Authorization":f"Bearer {tok}","Content-Type":"application/json","Accept":"application/json,text/event-stream"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode("utf-8","replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result",{}).get("content",[{}])[0].get("text","")
    return body

info = mcp("get_notebook_info", {"request":{"userName":USER,"kernelSlug":"nvidia-nemotron-submission-demo"}})
nb = json.loads(json.loads(info)["blob"]["source"])
ds = nb["metadata"]["kaggle"].get("dataSources",[])
if not any("nemotron-cot-corpus-v6" in str(d) for d in ds):
    ds.append({"sourceType":"datasetVersion","sourceId":f"{USER}/{SLUG}"})
    nb["metadata"]["kaggle"]["dataSources"] = ds
print("dataSources count:", len(ds))
push_args = {"request":{"slug":f"{USER}/nvidia-nemotron-submission-demo","newTitle":"nvidia-nemotron-submission-demo",
    "text":json.dumps(nb),"kernelType":"notebook","language":"python","isPrivate":True,"kernelExecutionType":"QuickSave"}}
print("push:", mcp("save_notebook", push_args)[:300])

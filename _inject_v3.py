"""Inject 4-bit-NF4 adaptive training code into the demo-fork (preserves bindings)."""
import json, urllib.request
from pathlib import Path

nb = json.loads(Path("_live.json").read_text(encoding="utf-8"))

def code(src):
    return {"cell_type": "code", "source": src, "metadata": {"trusted": True}, "outputs": [], "execution_count": None}

cells = []

# Cell 1: env + GPU detect + data load
cells.append(code(
"import os, sys, glob, json, subprocess\n"
"import site\n"
"site.addsitedir('/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/')\n"
"import torch\n"
"props = torch.cuda.get_device_properties(0)\n"
"vram_gb = props.total_memory / 1024**3\n"
"cc = props.major + props.minor / 10\n"
"print(f'GPU: {props.name} | {vram_gb:.1f} GB | sm_{props.major}{props.minor}')\n"
"assert cc >= 7.0, f'GPU sm_{props.major}{props.minor} INCOMPATIBLE; need >= sm_70.'\n"
"# Install bitsandbytes early if small GPU (T4/single)\n"
"if vram_gb < 60:\n"
"    try: import bitsandbytes  # noqa\n"
"    except ImportError:\n"
"        print('installing bitsandbytes...')\n"
"        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'bitsandbytes'], check=False)\n"
"        import bitsandbytes  # noqa\n"
"# Data\n"
"import csv\n"
"cands = glob.glob('/kaggle/input/*/train.csv')\n"
"print('train.csv:', cands)\n"
"train_data = []\n"
"if cands:\n"
"    with open(cands[0], encoding='utf-8') as f:\n"
"        for row in csv.DictReader(f):\n"
"            q = row.get('prompt') or row.get('question') or ''\n"
"            a = row.get('answer') or row.get('completion') or ''\n"
"            if q and a: train_data.append({'prompt': q, 'completion': str(a)})\n"
"            if len(train_data) >= 50: break\n"
"print('loaded', len(train_data), 'training rows')"
))

# Cell 2: model load (4-bit if small VRAM) + LoRA + train + save adapter
cells.append(code(
"import kagglehub\n"
"from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training\n"
"from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\n"
"\n"
"MODEL_PATH = kagglehub.model_download('metric/nemotron-3-nano-30b-a3b-bf16/transformers/default')\n"
"OUTPUT_DIR = '/kaggle/working'\n"
"LORA_RANK = 32\n"
"print('MODEL_PATH:', MODEL_PATH)\n"
"\n"
"if vram_gb >= 60:\n"
"    print(f'Loading full bf16 (large {vram_gb:.0f}GB GPU)')\n"
"    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True, dtype=torch.bfloat16)\n"
"else:\n"
"    print(f'Loading 4-bit NF4 ({vram_gb:.0f}GB GPU)')\n"
"    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,\n"
"                             bnb_4bit_use_double_quant=True, bnb_4bit_quant_type='nf4')\n"
"    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True,\n"
"                                                 quantization_config=bnb, dtype=torch.bfloat16)\n"
"    model = prepare_model_for_kbit_training(model)\n"
"tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)\n"
"if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token\n"
"print('Model loaded.')\n"
"\n"
"lora_config = LoraConfig(r=LORA_RANK, lora_alpha=16,\n"
"    target_modules=r'.*\\.(in_proj|out_proj|up_proj|down_proj)$',\n"
"    lora_dropout=0.05, bias='none', task_type=TaskType.CAUSAL_LM)\n"
"model = get_peft_model(model, lora_config)\n"
"model.print_trainable_parameters()\n"
"\n"
"if train_data:\n"
"    MAX_SEQ, GA = 2048, 8\n"
"    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\n"
"    dev = next(model.parameters()).device\n"
"    def datum(p, a):\n"
"        pt = tokenizer(p, add_special_tokens=False)['input_ids']\n"
"        at = tokenizer(a, add_special_tokens=False)['input_ids'] + [tokenizer.eos_token_id]\n"
"        t = (pt + at)[:MAX_SEQ]; m = ([0]*len(pt) + [1]*len(at))[:MAX_SEQ]\n"
"        return torch.tensor(t).unsqueeze(0), torch.tensor(m).unsqueeze(0)\n"
"    model.train(); step = 0; rl = 0.0\n"
"    for d in train_data:\n"
"        ids, mask = datum(d['prompt'], d['completion']); ids, mask = ids.to(dev), mask.to(dev)\n"
"        lg = model(input_ids=ids).logits\n"
"        sl, slb, sm = lg[..., :-1, :].contiguous(), ids[..., 1:].contiguous(), mask[..., 1:].contiguous()\n"
"        lf = torch.nn.CrossEntropyLoss(reduction='none')\n"
"        loss = (lf(sl.view(-1, sl.size(-1)), slb.view(-1)) * sm.view(-1)).sum() / sm.sum().clamp(min=1)\n"
"        (loss / GA).backward(); rl += loss.item()\n"
"        if (step + 1) % GA == 0: opt.step(); opt.zero_grad()\n"
"        step += 1\n"
"        if step % 10 == 0: print(f'  step {step}/{len(train_data)} loss={rl/10:.4f}'); rl = 0.0\n"
"    print('Training done.')\n"
"\n"
"print('Saving adapter to', OUTPUT_DIR)\n"
"model.save_pretrained(OUTPUT_DIR)\n"
"cfg = json.load(open(os.path.join(OUTPUT_DIR, 'adapter_config.json')))\n"
"assert cfg.get('r', 999) <= 32\n"
"print('adapter r =', cfg.get('r'))"
))

# Cell 3: quick eval + cv_score
cells.append(code(
"def boxed(t):\n"
"    if not t: return None\n"
"    i = t.rfind(chr(92) + 'boxed{')\n"
"    if i < 0: return None\n"
"    s = i + 7; d = 1\n"
"    for j in range(s, len(t)):\n"
"        if t[j] == '{': d += 1\n"
"        elif t[j] == '}':\n"
"            d -= 1\n"
"            if d == 0: return t[s:j]\n"
"    return None\n"
"def ok(pr, go):\n"
"    p = boxed(pr)\n"
"    if p is None: return False\n"
"    g = boxed(go) or str(go).strip(); p = p.strip()\n"
"    if p == g.strip(): return True\n"
"    try: return abs(float(p) - float(g)) <= 1e-2\n"
"    except: return False\n"
"preds = []\n"
"if train_data:\n"
"    model.eval(); dev = next(model.parameters()).device\n"
"    with torch.no_grad():\n"
"        for d in train_data[:10]:\n"
"            inp = tokenizer(d['prompt'], return_tensors='pt').to(dev)\n"
"            o = model.generate(**inp, max_new_tokens=256, do_sample=False)\n"
"            txt = tokenizer.decode(o[0], skip_special_tokens=True)[len(d['prompt']):].strip()\n"
"            preds.append(ok(txt, d['completion']))\n"
"sc = (sum(preds) / len(preds)) if preds else 0.0\n"
"json.dump({'score': sc, 'n': len(preds), 'correct': sum(preds)}, open('/kaggle/working/cv_score.json', 'w'))\n"
"print(f'=== CV {sc:.4f} ({sum(preds)}/{len(preds)}) ===')"
))

# Cell 4: package submission.zip
cells.append(code(
"import glob as _g\n"
"os.chdir('/kaggle/working')\n"
"wfiles = [os.path.basename(p) for p in _g.glob('/kaggle/working/adapter_model*')]\n"
"subprocess.run('zip -j submission.zip adapter_config.json ' + ' '.join(wfiles), shell=True)\n"
"print('submission.zip exists:', os.path.exists('/kaggle/working/submission.zip'))\n"
"subprocess.run('unzip -l submission.zip', shell=True)"
))

nb["cells"] = cells
Path("_inject_v3.json").write_text(json.dumps(nb), encoding="utf-8")

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

# QuickSave: update the code, user runs via browser (only way to provision GPU+inputs)
args = {"request": {
    "slug": "sai1881/nvidia-nemotron-submission-demo",
    "newTitle": "nvidia-nemotron-submission-demo",
    "text": Path("_inject_v3.json").read_text(encoding="utf-8"),
    "kernelType": "notebook", "language": "python", "isPrivate": True,
    "kernelExecutionType": "QuickSave",
}}
print("push:", call("save_notebook", args))
info = call("get_notebook_info", {"request": {"userName": "sai1881", "kernelSlug": "nvidia-nemotron-submission-demo"}})
obj = json.loads(info)
m = obj.get("metadata", {})
kg = json.loads(obj["blob"]["source"])["metadata"]["kaggle"]
print(f"version: {m.get('current_version_number')} | accelerator: {kg.get('accelerator')} | sources: {len(kg.get('dataSources', []))}")

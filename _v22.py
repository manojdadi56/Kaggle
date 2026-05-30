"""v22: BIG upgrade — chat template + reasoning_on system + full-corpus + drop tiny-sample cap."""
import json, urllib.request
from pathlib import Path

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

info = call("get_notebook_info", {"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}})
nb = json.loads(json.loads(info)["blob"]["source"])

def code(src):
    return {"cell_type": "code", "source": src, "metadata": {"trusted": True}, "outputs": [], "execution_count": None}

# Keep cell 0 (v21 deps) + cell 1 (env/data) as-is; replace cell 2 with the upgraded training cell
upgraded_train = (
"# v22: chat-template + reasoning_on system prompt + full corpus (drop tiny sample cap)\n"
"import kagglehub\n"
"from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training\n"
"from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\n"
"\n"
"MODEL_PATH = kagglehub.model_download('metric/nemotron-3-nano-30b-a3b-bf16/transformers/default')\n"
"OUTPUT_DIR = '/kaggle/working'\n"
"LORA_RANK = 32\n"
"# Tunable knobs (single source of truth; ablations rewrite these)\n"
"USE_FULL_CORPUS = True   # drop the 200-row cap; train on full attached corpus\n"
"MAX_TRAIN = 5000          # safety cap if corpus is huge\n"
"REASONING_ON = True       # winner's system prompt\n"
"\n"
"if total_vram >= 60:\n"
"    print(f'Loading full bf16 ({total_vram:.0f}GB)')\n"
"    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True, dtype=torch.bfloat16)\n"
"else:\n"
"    print(f'Loading 4-bit NF4 ({total_vram:.0f}GB)')\n"
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
"# (a) read FULL corpus this time (cap at MAX_TRAIN for safety)\n"
"if COT_PATH and USE_FULL_CORPUS:\n"
"    train_data = []\n"
"    with open(COT_PATH, encoding='utf-8') as f:\n"
"        for line in f:\n"
"            try:\n"
"                d = json.loads(line)\n"
"                p = d.get('prompt') or d.get('question') or ''\n"
"                a = d.get('completion') or d.get('answer') or ''\n"
"                if p and a: train_data.append({'prompt': p, 'completion': str(a)})\n"
"            except: pass\n"
"            if len(train_data) >= MAX_TRAIN: break\n"
"    print(f're-loaded {len(train_data)} rows (full corpus)')\n"
"\n"
"# (b) render via chat template + reasoning_on system header (winner pattern)\n"
"SYSTEM = ('detailed thinking on' if REASONING_ON else 'detailed thinking off')\n"
"try:\n"
"    # Probe: does the tokenizer have a chat template?\n"
"    has_template = bool(getattr(tokenizer, 'chat_template', None))\n"
"    print(f'tokenizer.chat_template present: {has_template}')\n"
"except Exception:\n"
"    has_template = False\n"
"\n"
"def render(prompt, completion=None):\n"
"    if has_template:\n"
"        msgs = [{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]\n"
"        if completion is not None: msgs.append({'role':'assistant','content':completion})\n"
"        return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=(completion is None))\n"
"    # fallback (template missing): plain concat\n"
"    if completion is None: return prompt\n"
"    return prompt + completion\n"
"\n"
"if train_data:\n"
"    MAX_SEQ, GA = 2048, 8\n"
"    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\n"
"    dev = next(model.parameters()).device\n"
"    def datum(p, a):\n"
"        full = render(p, a)\n"
"        # Find the answer span (the assistant turn) to mask: tokenize prompt-only vs full\n"
"        ids_full = tokenizer(full, add_special_tokens=False)['input_ids']\n"
"        prompt_only = render(p, None)\n"
"        ids_p = tokenizer(prompt_only, add_special_tokens=False)['input_ids']\n"
"        n_p = len(ids_p)\n"
"        t = ids_full[:MAX_SEQ]; m = [0]*min(n_p, MAX_SEQ) + [1]*max(0, len(t) - n_p)\n"
"        m = m[:len(t)]\n"
"        return torch.tensor(t).unsqueeze(0), torch.tensor(m).unsqueeze(0)\n"
"    model.train(); step = 0; rl = 0.0\n"
"    for d in train_data:\n"
"        ids, mask = datum(d['prompt'], d['completion'])\n"
"        ids, mask = ids.to(dev), mask.to(dev)\n"
"        if mask.sum() == 0: continue  # nothing to learn this row\n"
"        lg = model(input_ids=ids).logits\n"
"        sl, slb, sm = lg[..., :-1, :].contiguous(), ids[..., 1:].contiguous(), mask[..., 1:].contiguous()\n"
"        lf = torch.nn.CrossEntropyLoss(reduction='none')\n"
"        loss = (lf(sl.view(-1, sl.size(-1)), slb.view(-1)) * sm.view(-1)).sum() / sm.sum().clamp(min=1)\n"
"        (loss / GA).backward(); rl += loss.item()\n"
"        if (step + 1) % GA == 0: opt.step(); opt.zero_grad()\n"
"        step += 1\n"
"        if step % 25 == 0: print(f'  step {step}/{len(train_data)} loss={rl/25:.4f}'); rl = 0.0\n"
"    print('Training done.')\n"
"\n"
"print('Saving adapter to', OUTPUT_DIR)\n"
"model.save_pretrained(OUTPUT_DIR)\n"
"cfg = json.load(open(os.path.join(OUTPUT_DIR, 'adapter_config.json')))\n"
"assert cfg.get('r', 999) <= 32\n"
"print('adapter r =', cfg.get('r'))"
)

# Upgraded eval: also use render() + system prompt
upgraded_eval = (
"# v22 eval: use chat template + reasoning_on\n"
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
"    EVAL_N = min(20, len(train_data))\n"
"    with torch.no_grad():\n"
"        for d in train_data[:EVAL_N]:\n"
"            prompt_str = render(d['prompt'], None)\n"
"            inp = tokenizer(prompt_str, return_tensors='pt').to(dev)\n"
"            o = model.generate(**inp, max_new_tokens=512, do_sample=False)\n"
"            txt = tokenizer.decode(o[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()\n"
"            preds.append(ok(txt, d['completion']))\n"
"sc = (sum(preds) / len(preds)) if preds else 0.0\n"
"json.dump({'score': sc, 'n': len(preds), 'correct': sum(preds), 'reasoning_on': REASONING_ON}, open('/kaggle/working/cv_score.json', 'w'))\n"
"print(f'=== CV {sc:.4f} ({sum(preds)}/{len(preds)}) reasoning_on={REASONING_ON} ===')"
)

# Replace cells 2 and 3 (training + eval) — keep cell 0 (deps), cell 1 (env/data), cell 4 (package)
new_cells = nb["cells"][:2] + [code(upgraded_train), code(upgraded_eval)] + nb["cells"][4:5]
nb["cells"] = new_cells

Path("_v22.json").write_text(json.dumps(nb), encoding="utf-8")
args = {"request": {
    "slug": "sai1881/nvidia-nemotron-submission-demo",
    "newTitle": "nvidia-nemotron-submission-demo",
    "text": Path("_v22.json").read_text(encoding="utf-8"),
    "kernelType": "notebook", "language": "python", "isPrivate": True,
    "kernelExecutionType": "QuickSave",
}}
print("push:", call("save_notebook", args))
info = call("get_notebook_info", {"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}})
m = json.loads(info)["metadata"]
print(f"version: {m.get('current_version_number')} | cells: {len(json.loads(json.loads(info)['blob']['source'])['cells'])}")

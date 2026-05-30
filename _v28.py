"""v28: align with host_template_spec.md — reasoning_on system + boxed-suffix + thinking + host gen params."""
import json, urllib.request
from pathlib import Path

nb = json.loads(Path("_live.json").read_text(encoding="utf-8"))

def code(src):
    return {"cell_type": "code", "source": src, "metadata": {"trusted": True}, "outputs": [], "execution_count": None}

# Find and replace the model+train cell (typically cell index 2 in v23-v27 structure)
# Strategy: search cells for one containing 'apply_chat_template' OR 'SYSTEM' OR 'detailed thinking', replace it
TARGET_TRAIN_CELL = (
"# v28: host-template-parity training + eval (per eval/host_template_spec.md)\n"
"import kagglehub\n"
"from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training\n"
"from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig\n"
"\n"
"MODEL_PATH = kagglehub.model_download('metric/nemotron-3-nano-30b-a3b-bf16/transformers/default')\n"
"OUTPUT_DIR = '/kaggle/working'\n"
"LORA_RANK = 32\n"
"\n"
"# === Host parity per eval/host_template_spec.md ===\n"
"HOST_SYSTEM = 'reasoning_on'  # NOT 'detailed thinking on' — exact host string\n"
"BOXED_SUFFIX = '\\nPlease put your final answer inside `\\\\boxed{}`. For example: `\\\\boxed{your answer}`'\n"
"GEN_MAX_NEW_TOKENS = 3584\n"
"GEN_TEMPERATURE = 1.0\n"
"GEN_TOP_P = 1.0\n"
"MAX_MODEL_LEN = 4096\n"
"USE_FULL_CORPUS = True\n"
"MAX_TRAIN = 5000\n"
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
"# Re-load full corpus if available\n"
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
"    print(f'full corpus loaded: {len(train_data)} rows')\n"
"\n"
"# === Host-parity render functions ===\n"
"# User prompt always gets boxed-suffix; system is 'reasoning_on'.\n"
"def render_prompt_only(user_prompt: str) -> str:\n"
"    msgs = [{'role': 'system', 'content': HOST_SYSTEM},\n"
"            {'role': 'user',   'content': user_prompt + BOXED_SUFFIX}]\n"
"    try:\n"
"        # enable_thinking=True triggers <think> block per host spec\n"
"        return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)\n"
"    except TypeError:\n"
"        return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)\n"
"\n"
"def render_full(user_prompt: str, assistant_answer: str) -> str:\n"
"    msgs = [{'role': 'system',    'content': HOST_SYSTEM},\n"
"            {'role': 'user',      'content': user_prompt + BOXED_SUFFIX},\n"
"            {'role': 'assistant', 'content': assistant_answer}]\n"
"    try:\n"
"        s = tokenizer.apply_chat_template(msgs, tokenize=False, enable_thinking=True)\n"
"    except TypeError:\n"
"        s = tokenizer.apply_chat_template(msgs, tokenize=False)\n"
"    if not s.endswith(tokenizer.eos_token): s = s + tokenizer.eos_token\n"
"    return s\n"
"\n"
"# Quick render sanity print\n"
"print('--- render_prompt_only sample ---')\n"
"print(render_prompt_only('What is 2+2?')[:400])\n"
"print('---')\n"
"\n"
"if train_data:\n"
"    MAX_SEQ = MAX_MODEL_LEN  # keep within host max_model_len\n"
"    GA = 8\n"
"    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\n"
"    dev = next(model.parameters()).device\n"
"    def datum(p, a):\n"
"        po = render_prompt_only(p)\n"
"        fu = render_full(p, a)\n"
"        ids_p = tokenizer(po, add_special_tokens=False)['input_ids']\n"
"        ids_f = tokenizer(fu, add_special_tokens=False)['input_ids']\n"
"        n_p = len(ids_p)\n"
"        t = ids_f[:MAX_SEQ]; m = [0]*min(n_p, MAX_SEQ) + [1]*max(0, len(t) - n_p)\n"
"        m = m[:len(t)]\n"
"        return torch.tensor(t).unsqueeze(0), torch.tensor(m).unsqueeze(0)\n"
"    total_steps = len(train_data)\n"
"    model.train(); step = 0; rl = 0.0\n"
"    for d in train_data:\n"
"        ids, mask = datum(d['prompt'], d['completion'])\n"
"        if mask.sum() == 0: continue\n"
"        ids, mask = ids.to(dev), mask.to(dev)\n"
"        lg = model(input_ids=ids).logits\n"
"        sl, slb, sm = lg[..., :-1, :].contiguous(), ids[..., 1:].contiguous(), mask[..., 1:].contiguous()\n"
"        lf = torch.nn.CrossEntropyLoss(reduction='none')\n"
"        loss = (lf(sl.view(-1, sl.size(-1)), slb.view(-1)) * sm.view(-1)).sum() / sm.sum().clamp(min=1)\n"
"        # Step-based linear LR decay (winner pattern)\n"
"        lr = 2e-5 + (1e-5 - 2e-5) * (step / max(1, total_steps - 1))\n"
"        for pg in opt.param_groups: pg['lr'] = lr\n"
"        (loss / GA).backward(); rl += loss.item()\n"
"        if (step + 1) % GA == 0: opt.step(); opt.zero_grad()\n"
"        step += 1\n"
"        if step % 25 == 0: print(f'  step {step}/{total_steps} loss={rl/25:.4f} lr={lr:.2e}'); rl = 0.0\n"
"    print('Training done.')\n"
"\n"
"print('Saving adapter to', OUTPUT_DIR)\n"
"model.save_pretrained(OUTPUT_DIR)\n"
"cfg = json.load(open(os.path.join(OUTPUT_DIR, 'adapter_config.json')))\n"
"assert cfg.get('r', 999) <= 32\n"
"print('adapter r =', cfg.get('r'))"
)

# Eval cell upgrade
TARGET_EVAL_CELL = (
"# v28 eval — uses host render + host gen params\n"
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
"    print(f'Eval on {EVAL_N} samples with host gen params')\n"
"    with torch.no_grad():\n"
"        for d in train_data[:EVAL_N]:\n"
"            ps = render_prompt_only(d['prompt'])\n"
"            inp = tokenizer(ps, return_tensors='pt').to(dev)\n"
"            o = model.generate(**inp, max_new_tokens=GEN_MAX_NEW_TOKENS,\n"
"                               do_sample=(GEN_TEMPERATURE != 0.0), temperature=GEN_TEMPERATURE, top_p=GEN_TOP_P)\n"
"            txt = tokenizer.decode(o[0][inp['input_ids'].shape[1]:], skip_special_tokens=True).strip()\n"
"            preds.append(ok(txt, d['completion']))\n"
"sc = (sum(preds) / len(preds)) if preds else 0.0\n"
"json.dump({'score': sc, 'n': len(preds), 'correct': sum(preds), 'reasoning_on': True, 'host_parity': True}, open('/kaggle/working/cv_score.json', 'w'))\n"
"print(f'=== CV {sc:.4f} ({sum(preds)}/{len(preds)}) host_parity=YES ===')"
)

# Strategy: find the "train" cell (contains kagglehub.model_download AND model.train()) and the "eval" cell
# (contains 'boxed' AND 'model.generate'), replace those exact cells.
new_cells = []
replaced_train, replaced_eval = False, False
for c in nb["cells"]:
    src = c.get("source","")
    if isinstance(src, list): src = "".join(src)
    if c.get("cell_type") == "code" and not replaced_train and ("kagglehub.model_download" in src and "model.train()" in src):
        new_cells.append(code(TARGET_TRAIN_CELL))
        replaced_train = True
    elif c.get("cell_type") == "code" and not replaced_eval and ("def boxed" in src and "model.generate" in src):
        new_cells.append(code(TARGET_EVAL_CELL))
        replaced_eval = True
    else:
        new_cells.append(c)
nb["cells"] = new_cells

print(f"replaced train cell: {replaced_train}; eval cell: {replaced_eval}")
Path("_v28.json").write_text(json.dumps(nb), encoding="utf-8")

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
    "text": Path("_v28.json").read_text(encoding="utf-8"),
    "kernelType": "notebook", "language": "python", "isPrivate": True,
    "kernelExecutionType": "QuickSave",
}}
print("push:", call("save_notebook", args))
info = call("get_notebook_info", {"request":{"userName":"sai1881","kernelSlug":"nvidia-nemotron-submission-demo"}})
m = json.loads(info)["metadata"]
print(f"version: {m.get('current_version_number')} | cells: {len(json.loads(json.loads(info)['blob']['source'])['cells'])}")

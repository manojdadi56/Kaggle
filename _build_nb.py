"""Build E-002 notebook mirroring the official demo (RTX Pro 6000, kagglehub model, full bf16)."""
import json
from pathlib import Path

def code(src): return {"cell_type": "code", "source": src, "metadata": {"trusted": True}, "outputs": [], "execution_count": None}
def md(src): return {"cell_type": "markdown", "source": src, "metadata": {}}

cells = []
cells.append(md("# E-002 Baseline - Nemotron-3-Nano-30B + LoRA SFT\nMirrors the official NVIDIA demo: RTX Pro 6000 (96GB), kagglehub model download, full bf16 (no 4-bit)."))

cells.append(code(
"import os, sys, json, subprocess, glob\n"
"import torch\n"
"print('CUDA:', torch.cuda.is_available(), '| count:', torch.cuda.device_count())\n"
"for i in range(torch.cuda.device_count()):\n"
"    p = torch.cuda.get_device_properties(i)\n"
"    print(f'  GPU{i}: {p.name} | {p.total_memory/1024**3:.1f} GB | sm_{p.major}{p.minor}')\n"
"print('=== /kaggle/input ===')\n"
"for root, dirs, files in os.walk('/kaggle/input'):\n"
"    d = root.count(os.sep) - '/kaggle/input'.count(os.sep)\n"
"    if d <= 2: print(' ', root, '| files:', files[:5])\n"
"    if d >= 2: dirs.clear()"
))

cells.append(code(
"# Install Mamba deps (Nemotron is a Mamba-hybrid). Internet is enabled.\n"
"for pkg in ['causal-conv1d', 'mamba-ssm']:\n"
"    mod = pkg.replace('-', '_')\n"
"    try:\n"
"        __import__(mod); print(f'{pkg}: ok')\n"
"    except ImportError:\n"
"        print(f'installing {pkg}...')\n"
"        r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--no-build-isolation', pkg], capture_output=True, text=True)\n"
"        print(f'  rc={r.returncode}', r.stderr[-400:] if r.returncode else '')"
))

cells.append(code(
"# Model via kagglehub (official demo pattern)\n"
"import kagglehub\n"
"MODEL_PATH = kagglehub.model_download('metric/nemotron-3-nano-30b-a3b-bf16/transformers/default')\n"
"print('MODEL_PATH:', MODEL_PATH)\n"
"print('files:', os.listdir(MODEL_PATH)[:10])"
))

cells.append(code(
"from transformers import AutoModelForCausalLM, AutoTokenizer\n"
"# 96GB GPU -> full bf16, no quantization needed\n"
"model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True, dtype=torch.bfloat16)\n"
"tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)\n"
"if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token\n"
"print('Model + tokenizer loaded.')"
))

cells.append(code(
"from peft import LoraConfig, get_peft_model, TaskType\n"
"LORA_RANK = 32\n"
"lora_config = LoraConfig(\n"
"    r=LORA_RANK, lora_alpha=16,\n"
"    target_modules=r'.*\\.(in_proj|out_proj|up_proj|down_proj)$',  # demo's proven targeting\n"
"    lora_dropout=0.05, bias='none', task_type=TaskType.CAUSAL_LM,\n"
")\n"
"model = get_peft_model(model, lora_config)\n"
"model.print_trainable_parameters()"
))

cells.append(code(
"# Load competition train.csv (auto-detect path)\n"
"import csv\n"
"cands = glob.glob('/kaggle/input/*/train.csv')\n"
"assert cands, 'train.csv not found - check competition is attached'\n"
"TRAIN_CSV = cands[0]; print('train.csv:', TRAIN_CSV)\n"
"SAMPLE_SIZE = 50\n"
"train_data = []\n"
"with open(TRAIN_CSV, encoding='utf-8') as f:\n"
"    for row in csv.DictReader(f):\n"
"        p = row.get('prompt') or row.get('question') or ''\n"
"        a = row.get('answer') or row.get('completion') or ''\n"
"        if p and a: train_data.append({'prompt': p, 'completion': str(a)})\n"
"        if len(train_data) >= SAMPLE_SIZE: break\n"
"print(f'Loaded {len(train_data)} examples')"
))

cells.append(code(
"# 1-epoch LoRA SFT (mask: answer tokens only)\n"
"MAX_SEQ, GA = 2048, 8\n"
"opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\n"
"dev = next(model.parameters()).device\n"
"def datum(p, a):\n"
"    pt = tokenizer(p, add_special_tokens=False)['input_ids']\n"
"    at = tokenizer(a, add_special_tokens=False)['input_ids'] + [tokenizer.eos_token_id]\n"
"    t = (pt + at)[:MAX_SEQ]; m = ([0]*len(pt) + [1]*len(at))[:MAX_SEQ]\n"
"    return torch.tensor(t).unsqueeze(0), torch.tensor(m).unsqueeze(0)\n"
"model.train(); step = 0; rl = 0.0\n"
"for d in train_data:\n"
"    ids, mask = datum(d['prompt'], d['completion']); ids, mask = ids.to(dev), mask.to(dev)\n"
"    lg = model(input_ids=ids).logits\n"
"    sl, slb, sm = lg[..., :-1, :].contiguous(), ids[..., 1:].contiguous(), mask[..., 1:].contiguous()\n"
"    lf = torch.nn.CrossEntropyLoss(reduction='none')\n"
"    loss = (lf(sl.view(-1, sl.size(-1)), slb.view(-1)) * sm.view(-1)).sum() / sm.sum().clamp(min=1)\n"
"    (loss / GA).backward(); rl += loss.item()\n"
"    if (step + 1) % GA == 0: opt.step(); opt.zero_grad()\n"
"    step += 1\n"
"    if step % 5 == 0: print(f'  step {step}/{len(train_data)} loss={rl/5:.4f}'); rl = 0.0\n"
"print('Training done.')"
))

cells.append(code(
"# Save adapter to /kaggle/working (host reads this)\n"
"OUT = '/kaggle/working'\n"
"model.save_pretrained(OUT)\n"
"cfg = json.load(open(os.path.join(OUT, 'adapter_config.json')))\n"
"assert cfg.get('r', 999) <= 32, 'rank>32'\n"
"print('adapter saved, r=', cfg.get('r'))\n"
"for f in os.listdir(OUT):\n"
"    if f.startswith('adapter'): print(' ', f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')"
))

cells.append(code(
"# Quick self-eval with boxed extraction\n"
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
"model.eval(); preds = []\n"
"with torch.no_grad():\n"
"    for i, d in enumerate(train_data[:10]):\n"
"        inp = tokenizer(d['prompt'], return_tensors='pt').to(dev)\n"
"        o = model.generate(**inp, max_new_tokens=256, do_sample=False)\n"
"        txt = tokenizer.decode(o[0], skip_special_tokens=True)[len(d['prompt']):].strip()\n"
"        preds.append(ok(txt, d['completion']))\n"
"score = sum(preds) / len(preds)\n"
"json.dump({'score': score, 'n': len(preds), 'correct': sum(preds)}, open(os.path.join(OUT, 'cv_score.json'), 'w'))\n"
"print(f'=== CV {score:.4f} ({sum(preds)}/{len(preds)}) ===')"
))

cells.append(code(
"# Package submission.zip (adapter files at root)\n"
"subprocess.run('cd /kaggle/working && (zip -j submission.zip adapter_config.json adapter_model.safetensors || zip -j submission.zip adapter_config.json adapter_model.bin)', shell=True)\n"
"print('submission.zip exists:', os.path.exists('/kaggle/working/submission.zip'))\n"
"subprocess.run('cd /kaggle/working && unzip -l submission.zip', shell=True)"
))

nb = {
    "metadata": {
        "kernelspec": {"language": "python", "display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.12"},
        "kaggle": {
            "accelerator": "nvidiaRtxPro6000",
            "dataSources": [
                {"sourceType": "competition", "sourceId": 129716},
                {"sourceType": "modelInstanceVersion", "sourceId": 784907, "modelInstanceId": 598905, "modelId": 611168},
            ],
            "dockerImageVersionId": 31287,
            "isInternetEnabled": True,
            "language": "python",
            "sourceType": "notebook",
            "isGpuEnabled": True,
        },
    },
    "nbformat_minor": 4,
    "nbformat": 4,
    "cells": cells,
}
Path("notebook_e002_rtxpro.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
print("wrote notebook_e002_rtxpro.ipynb |", len(cells), "cells")

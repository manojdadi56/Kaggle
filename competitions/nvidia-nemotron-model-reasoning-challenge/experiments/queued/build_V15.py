"""Pre-build the V15 'CoT corpus inline' iteration. Saves as _v15_patch.json ready to apply.
Not pushed yet — queue for after V13/V14 produces first submission.
"""
import base64, gzip, json
from pathlib import Path

# Load corpus
corpus = []
for line in Path("competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v1/corpus.jsonl").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line:
        corpus.append(json.loads(line))
print(f"corpus: {len(corpus)} examples")

# Compress + b64 for inlining
raw = json.dumps(corpus).encode("utf-8")
gz = gzip.compress(raw, compresslevel=9)
b64 = base64.b64encode(gz).decode("ascii")
print(f"raw: {len(raw):,} bytes  gz: {len(gz):,} bytes  b64: {len(b64):,} chars")

# Build the patched cell 0 — load corpus from inline b64 instead of train.csv
# Keep all the env + GPU + offline-pkg-install logic, just swap the data load
new_cell0 = (
    "import os, sys, glob, json, subprocess, base64, gzip\n"
    "import site\n"
    "site.addsitedir('/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/')\n"
    "import torch\n"
    "\n"
    "ngpu = torch.cuda.device_count()\n"
    "props0 = torch.cuda.get_device_properties(0)\n"
    "cc = props0.major + props0.minor/10\n"
    "vram_total_gb = sum(torch.cuda.get_device_properties(i).total_memory for i in range(ngpu)) / 1024**3\n"
    "for i in range(ngpu):\n"
    "    p = torch.cuda.get_device_properties(i)\n"
    "    print(f'  GPU{i}: {p.name} | {p.total_memory/1024**3:.1f} GB | sm_{p.major}{p.minor}')\n"
    "print(f'Total VRAM: {vram_total_gb:.1f} GB')\n"
    "assert cc >= 7.0, f'GPU sm_{props0.major}{props0.minor} INCOMPATIBLE'\n"
    "\n"
    "# Find offline wheel dir + install bitsandbytes if needed\n"
    "OFFLINE_DIR = None\n"
    "for cand in glob.glob('/kaggle/input/*nvidia-offline-packages*/offline_packages'):\n"
    "    OFFLINE_DIR = cand; break\n"
    "if not OFFLINE_DIR:\n"
    "    for cand in glob.glob('/kaggle/input/*/offline_packages'):\n"
    "        OFFLINE_DIR = cand; break\n"
    "print('OFFLINE_DIR:', OFFLINE_DIR)\n"
    "if vram_total_gb < 60:\n"
    "    try: import bitsandbytes\n"
    "    except ImportError:\n"
    "        if OFFLINE_DIR:\n"
    "            r = subprocess.run([sys.executable,'-m','pip','install','--no-index','--find-links', OFFLINE_DIR, 'bitsandbytes'], capture_output=True, text=True)\n"
    "            print(f'bnb install rc={r.returncode}')\n"
    "            if r.returncode: print(r.stderr[-1200:])\n"
    "\n"
    "# === CoT CORPUS (inlined, gz+b64, 91 examples with pre-tokenized mask) ===\n"
    f"CORPUS_GZ_B64 = '{b64}'\n"
    "train_data = json.loads(gzip.decompress(base64.b64decode(CORPUS_GZ_B64)).decode('utf-8'))\n"
    "print(f'loaded {len(train_data)} CoT examples (synthesized corpus, pre-tokenized)')\n"
    "print(f'example: {train_data[0][\"prompt\"][:150]} -> answer={train_data[0][\"answer\"]}')\n"
    "\n"
    "os.makedirs('/kaggle/working/offload', exist_ok=True)"
)

# Build cell 1 — model + LoRA + train on CoT (use pre-tokenized tokens+mask directly)
new_cell1 = (
    "import kagglehub\n"
    "from peft import LoraConfig, get_peft_model, TaskType\n"
    "from transformers import AutoModelForCausalLM, AutoTokenizer\n"
    "\n"
    "MODEL_PATH = kagglehub.model_download('metric/nemotron-3-nano-30b-a3b-bf16/transformers/default')\n"
    "OUTPUT_DIR = '/kaggle/working'\n"
    "LORA_RANK = 32\n"
    "print('MODEL_PATH:', MODEL_PATH)\n"
    "\n"
    "if vram_total_gb >= 60:\n"
    "    print('>=60GB -> full bf16')\n"
    "    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True, dtype=torch.bfloat16, offload_folder='/kaggle/working/offload')\n"
    "else:\n"
    "    from transformers import BitsAndBytesConfig\n"
    "    from peft import prepare_model_for_kbit_training\n"
    "    print('<60GB -> 4-bit NF4')\n"
    "    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type='nf4', llm_int8_enable_fp32_cpu_offload=True)\n"
    "    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map='auto', trust_remote_code=True, quantization_config=bnb, dtype=torch.bfloat16, offload_folder='/kaggle/working/offload')\n"
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
    "# Training: use the PRE-TOKENIZED tokens + mask from the corpus (winner's exact format)\n"
    "MAX_SEQ = 2048\n"
    "GA = 8\n"
    "opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\n"
    "dev = next(model.parameters()).device\n"
    "model.train(); step=0; rl=0.0\n"
    "for d in train_data:\n"
    "    # Corpus has pre-tokenized 'tokens' + 'mask' (mask=1 on answer tokens)\n"
    "    toks = d.get('tokens') or tokenizer(d['prompt']+d.get('completion',''),add_special_tokens=False)['input_ids']\n"
    "    mask = d.get('mask') or [0]*len(tokenizer(d['prompt'],add_special_tokens=False)['input_ids'])+[1]*(len(toks)-len(tokenizer(d['prompt'],add_special_tokens=False)['input_ids']))\n"
    "    toks = toks[:MAX_SEQ]; mask = mask[:MAX_SEQ]\n"
    "    if sum(mask) == 0: continue  # skip if no answer tokens\n"
    "    ids = torch.tensor(toks).unsqueeze(0).to(dev)\n"
    "    msk = torch.tensor(mask).unsqueeze(0).to(dev)\n"
    "    lg = model(input_ids=ids).logits\n"
    "    sl, slb, sm = lg[..., :-1, :].contiguous(), ids[..., 1:].contiguous(), msk[..., 1:].contiguous()\n"
    "    lf = torch.nn.CrossEntropyLoss(reduction='none')\n"
    "    loss = (lf(sl.view(-1, sl.size(-1)), slb.view(-1)) * sm.view(-1)).sum() / sm.sum().clamp(min=1)\n"
    "    (loss/GA).backward(); rl += loss.item()\n"
    "    if (step+1)%GA == 0: opt.step(); opt.zero_grad()\n"
    "    step += 1\n"
    "    if step%10==0: print(f'  step {step}/{len(train_data)} loss={rl/10:.4f}'); rl=0.0\n"
    "print('Training done.')\n"
    "\n"
    "model.save_pretrained(OUTPUT_DIR)\n"
    "cfg = json.load(open(os.path.join(OUTPUT_DIR,'adapter_config.json')))\n"
    "assert cfg.get('r',999) <= 32\n"
    "print('adapter r =', cfg.get('r'))"
)

# Patch dict for iterate_notebook
patch = {"cells": {"0": new_cell0, "1": new_cell1}}
Path("_v15_patch.json").write_text(json.dumps(patch), encoding="utf-8")
print(f"\nv15 patch ready: _v15_patch.json ({Path('_v15_patch.json').stat().st_size:,} bytes)")
print("Apply after first submission lands:")
print("  python tools/iterate_notebook.py --slug nvidia-nemotron-submission-demo --patch-file _v15_patch.json")
print("Then user clicks browser Save & Run All.")

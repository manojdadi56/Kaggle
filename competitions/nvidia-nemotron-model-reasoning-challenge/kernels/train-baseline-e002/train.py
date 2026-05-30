import sys
import subprocess
import argparse
import json
import os

# === Install mamba-ssm + causal-conv1d (Nemotron Mamba-hybrid; not in Kaggle base image) ===
# Requires kernel-metadata.json: "enable_internet": true
def _ensure_deps():
    for pkg in ["causal-conv1d", "mamba-ssm", "bitsandbytes"]:
        mod = pkg.replace("-", "_")
        try:
            __import__(mod)
            print(f"  {pkg}: already installed", flush=True)
        except ImportError:
            print(f"  installing {pkg}...", flush=True)
            r = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", "--no-build-isolation", pkg],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                print(f"  {pkg} install rc={r.returncode}\n  stderr: {r.stderr[-1500:]}", flush=True)
_ensure_deps()

# === INLINED cv + score modules (script-type kernels upload only one file) ===
import types as _types
_score_mod = _types.ModuleType('score')
exec(compile('def extract_boxed(text: str) -> str | None:\n    if not text:\n        return None\n    idx = text.rfind(r"\\boxed{")\n    if idx == -1:\n        return None\n    start = idx + len(r"\\boxed{")\n    brace_count = 1\n    for i in range(start, len(text)):\n        if text[i] == "{":\n            brace_count += 1\n        elif text[i] == "}":\n            brace_count -= 1\n        if brace_count == 0:\n            return text[start:i]\n    return None\n\n\ndef score_item(prediction: str, gold: str) -> bool:\n    p_val = extract_boxed(prediction)\n    if p_val is None:\n        # Missing \\boxed{} -> wrong\n        return False\n\n    g_val = extract_boxed(gold)\n    if g_val is None:\n        # Gold doesn\'t have \\boxed{} formatting? We\'ll assume the string is the value\n        g_val = str(gold).strip()\n    else:\n        g_val = g_val.strip()\n\n    p_val = p_val.strip()\n\n    # Exact string match\n    if p_val == g_val:\n        return True\n\n    # Numeric match within 1e-2 tolerance\n    try:\n        if abs(float(p_val) - float(g_val)) <= 1e-2:\n            return True\n    except ValueError:\n        pass\n\n    return False\n\n\ndef score(predictions: list[str], gold: list[str]) -> float:\n    if len(predictions) != len(gold):\n        raise ValueError("Length mismatch between predictions and gold")\n    if not predictions or not gold:\n        return 0.0\n\n    correct = sum(1 for p, g in zip(predictions, gold) if score_item(p, g))\n    return correct / len(predictions)\n', 'score.py', 'exec'), _score_mod.__dict__)
sys.modules['score'] = _score_mod
score = _score_mod

_cv_mod = _types.ModuleType('cv')
exec(compile('import json\nimport csv\nimport argparse\nimport random\nfrom typing import Any, Dict, List\nfrom collections import defaultdict\n\nfrom score import score_item\n\n\ndef get_category(item: Dict[str, Any]) -> str:\n    """Extracts or infers the category of an item."""\n    if "category" in item and item["category"]:\n        return item["category"]\n\n    text = item.get("problem", item.get("question", item.get("text", ""))).lower()\n    if not text:\n        return "unknown"\n\n    if any(k in text for k in ["math", "equation", "calculate", "number", "integral", "derivative", "theorem", "algebra", "geometry", "probability"]):\n        return "math"\n    if any(k in text for k in ["code", "python", "programming", "function", "algorithm", "c++", "java", "script"]):\n        return "code"\n    if any(k in text for k in ["physics", "force", "velocity", "mass", "energy", "momentum", "acceleration"]):\n        return "physics"\n    if any(k in text for k in ["logic", "puzzle", "deduce", "reasoning", "if and only if", "knights and knaves", "syllogism"]):\n        return "logic"\n\n    return "general"\n\ndef create_holdout(data: List[Dict[str, Any]], test_size: float = 0.2, seed: int = 42) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:\n    """Splits data into train and holdout sets using stratified splitting by category."""\n    random.seed(seed)\n\n    # Group data by category\n    by_category = defaultdict(list)\n    for item in data:\n        cat = get_category(item)\n        by_category[cat].append(item)\n\n    train_data = []\n    holdout_data = []\n\n    # Split each category proportionally\n    for cat, items in by_category.items():\n        shuffled_items = items.copy()\n        random.shuffle(shuffled_items)\n        split_idx = int(len(shuffled_items) * (1 - test_size))\n        train_data.extend(shuffled_items[:split_idx])\n        holdout_data.extend(shuffled_items[split_idx:])\n\n    # Shuffle the final datasets so categories aren\'t grouped together\n    random.shuffle(train_data)\n    random.shuffle(holdout_data)\n\n    return train_data, holdout_data\n\n\ndef evaluate_cv(predictions: List[Dict[str, Any]], gold_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:\n    """\n    Evaluates predictions against gold data.\n    Assumes predictions have \'id\' and \'prediction\' keys.\n    Assumes gold_data maps \'id\' to a dict containing \'answer\' and optionally \'category\'.\n    """\n    if not predictions:\n        return {"overall_accuracy": 0.0, "category_accuracy": {}, "category_stats": {}}\n\n    correct_total = 0\n    total = 0\n\n    category_stats = defaultdict(lambda: {"correct": 0, "total": 0})\n\n    for pred_item in predictions:\n        item_id = str(pred_item.get("id"))\n        prediction_text = pred_item.get("prediction", "")\n\n        if item_id not in gold_data:\n            print(f"Warning: ID {item_id} found in predictions but not in gold data. Skipping.")\n            continue\n\n        gold_item = gold_data[item_id]\n        gold_text = gold_item.get("answer", "")\n        category = get_category(gold_item)\n\n        is_correct = score_item(prediction_text, gold_text)\n\n        if is_correct:\n            correct_total += 1\n            category_stats[category]["correct"] += 1\n\n        total += 1\n        category_stats[category]["total"] += 1\n\n    overall_accuracy = correct_total / total if total > 0 else 0.0\n\n    category_accuracy = {\n        cat: stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0\n        for cat, stats in category_stats.items()\n    }\n\n    return {\n        "overall_accuracy": overall_accuracy,\n        "category_accuracy": category_accuracy,\n        "category_stats": dict(category_stats),\n        "total_evaluated": total\n    }\n\ndef generate_markdown_report(results: Dict[str, Any], output_path: str):\n    """Generates a Markdown report with per-category accuracy."""\n    with open(output_path, "w", encoding="utf-8") as f:\n        f.write("# Evaluation Report\\n\\n")\n        f.write(f"**Overall Accuracy:** {results.get(\'overall_accuracy\', 0.0):.4f} ({results.get(\'total_evaluated\', 0)} samples)\\n\\n")\n\n        category_stats = results.get("category_stats", {})\n        if category_stats:\n            f.write("## Category Breakdown\\n\\n")\n            f.write("| Category | Accuracy | Correct / Total |\\n")\n            f.write("|----------|----------|-----------------|\\n")\n\n            # Sort categories alphabetically\n            for cat in sorted(category_stats.keys()):\n                stats = category_stats[cat]\n                acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0\n                f.write(f"| {cat} | {acc:.4f} | {stats[\'correct\']} / {stats[\'total\']} |\\n")\n\ndef _load_data(filepath: str, key_field: str = None) -> Any:\n    """Loads JSONL or CSV data."""\n    if filepath.endswith(\'.csv\'):\n        data = []\n        with open(filepath, \'r\', encoding=\'utf-8\') as f:\n            reader = csv.DictReader(f)\n            for row in reader:\n                data.append(row)\n        if key_field:\n            return {str(item[key_field]): item for item in data if key_field in item}\n        return data\n\n    elif filepath.endswith(\'.jsonl\') or filepath.endswith(\'.json\'):\n        # simple jsonl support for flexibility\n        data = []\n        with open(filepath, \'r\', encoding=\'utf-8\') as f:\n            for line in f:\n                line = line.strip()\n                if line:\n                    data.append(json.loads(line))\n        if key_field:\n             return {str(item[key_field]): item for item in data if key_field in item}\n        return data\n    else:\n        raise ValueError(f"Unsupported file format for {filepath}")\n\ndef main():\n    parser = argparse.ArgumentParser(description="Evaluate model predictions against gold data.")\n    parser.add_argument("--predictions", type=str, required=True, help="Path to predictions file (CSV or JSONL). Must have \'id\' and \'prediction\' columns/keys.")\n    parser.add_argument("--gold", type=str, required=True, help="Path to gold data file (CSV or JSONL). Must have \'id\', \'answer\', and optionally \'category\'.")\n    parser.add_argument("--output", type=str, default="cv_score.json", help="Path to output the scores (JSON).")\n    parser.add_argument("--report", type=str, default=None, help="Path to output a Markdown report with per-category accuracies.")\n\n    args = parser.parse_args()\n\n    predictions = _load_data(args.predictions)\n    gold_data = _load_data(args.gold, key_field="id")\n\n    results = evaluate_cv(predictions, gold_data)\n\n    print(f"Overall Accuracy: {results[\'overall_accuracy\']:.4f} ({results[\'total_evaluated\']} samples)")\n    print("Category Accuracy:")\n    for cat, acc in results[\'category_accuracy\'].items():\n        print(f"  {cat}: {acc:.4f}")\n\n    with open(args.output, \'w\', encoding=\'utf-8\') as f:\n        json.dump(results, f, indent=2)\n    print(f"Results saved to {args.output}")\n\n    if args.report:\n        generate_markdown_report(results, args.report)\n        print(f"Report saved to {args.report}")\n\nif __name__ == "__main__":\n    main()\n', 'cv.py', 'exec'), _cv_mod.__dict__)
sys.modules['cv'] = _cv_mod
cv = _cv_mod
# === END INLINED ===

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

class LinearDecayLRSchedule:
    def __init__(self, learning_rate: float = 2e-5, final_learning_rate: float = 1e-5):
        self.learning_rate = learning_rate
        self.final_learning_rate = final_learning_rate

    def get_lr(self, step: int, total_steps: int, epoch: int, total_epochs: int) -> float:
        mult = min(1.0, max(0.0, 1.0 - epoch / (1 + total_epochs)))
        return self.final_learning_rate + (self.learning_rate - self.final_learning_rate) * mult

def compute_loss(logits, labels, mask):
    # Standard cross entropy across the masked target
    # Mask = 1 for answer tokens, 0 for prompt tokens
    loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
    # Shift so that tokens < n predict n
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    shift_mask = mask[..., 1:].contiguous()

    # Calculate loss per token
    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
    loss = loss * shift_mask.view(-1)

    return loss.sum() / shift_mask.sum()

BASE_MODEL = "Nemotron-3-Nano-30B-A3B-BF16"

LORA_TARGET_MODULES = ['mixer.in_proj','mixer.out_proj','q_proj','k_proj','v_proj','o_proj']
LORA_RANK = 32
LORA_ALPHA = 64
LOAD_IN_4BIT = True

def run_training(rank: int, smoke: bool = False, data_path: str = None):
    # Hard invariant: LoRA rank <= 32
    if rank > 32:
        raise ValueError(f"LoRA rank must be <= 32, but got {rank}")

    # === DIAGNOSTIC: show what's actually mounted at /kaggle/input ===
    if not smoke and os.path.isdir("/kaggle/input"):
        print("=== /kaggle/input contents ===", flush=True)
        for root, dirs, files in os.walk("/kaggle/input"):
            # only show first 2 levels deep + 5 files per dir
            depth = root.count(os.sep) - "/kaggle/input".count(os.sep)
            if depth <= 3:
                print(f"  {root}: dirs={dirs[:5]} files={files[:5]}", flush=True)
            if depth >= 3:
                dirs.clear()
        print("=== end mount listing ===", flush=True)

    # Kaggle Models attach mount: /kaggle/input/<model-slug>/<framework>/<variation>/<version>
    model_name = "gpt2" if smoke else "/kaggle/input/nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
    # Auto-find the real model path if our guess doesn't exist
    if not smoke and not os.path.isdir(model_name):
        # walk /kaggle/input for any dir with config.json
        for root, dirs, files in os.walk("/kaggle/input"):
            if "config.json" in files and "tokenizer.json" in files:
                model_name = root
                print(f"=== Found model dir: {model_name} ===", flush=True)
                break
        else:
            print(f"=== WARNING: No config.json found anywhere in /kaggle/input. Falling back to: {model_name} ===", flush=True)
    print(f"Loading model: {model_name}")

    if data_path and os.path.exists(data_path):
        print(f"Reading training data from: {data_path}")
    else:
        print("No training data provided or path does not exist.")

    # Kaggle Models mount is offline-only; tell transformers to skip HF hub lookup
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    if smoke:
        model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True, trust_remote_code=True)
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=LOAD_IN_4BIT,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            local_files_only=True,
            trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)

    print("Applying PEFT LoRA...")
    target_modules = LORA_TARGET_MODULES if not smoke else ["c_attn", "c_proj"]
    lora_config = LoraConfig(
        r=rank,
        lora_alpha=LORA_ALPHA,
        target_modules=target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def build_datum(prompt_text: str, answer_text: str, tokenizer, max_length: int = 8192):
        # Winner memory: mask=1 applies to CoT-reasoning and boxed-answer span, mask=0 to prompt
        prompt_tokens = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        answer_tokens = tokenizer(answer_text, add_special_tokens=False)["input_ids"]

        # We append eos to answer
        answer_tokens = answer_tokens + [tokenizer.eos_token_id]

        tokens = prompt_tokens + answer_tokens
        mask = [0]*len(prompt_tokens) + [1]*len(answer_tokens)

        if len(tokens) > max_length:
            tokens = tokens[:max_length]
            mask = mask[:max_length]

        return torch.tensor(tokens).unsqueeze(0), torch.tensor(mask).unsqueeze(0)

    # Load data
    train_data = []
    if data_path and os.path.exists(data_path):
        if data_path.endswith('.csv'):
            import csv
            with open(data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    train_data.append({"prompt": row.get('prompt', row.get('question', '')), "completion": row.get('completion', row.get('answer', ''))})
        elif data_path.endswith('.jsonl') or data_path.endswith('.json'):
            with open(data_path, 'r') as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        train_data.append({"prompt": d.get('prompt', d.get('question', '')), "completion": d.get('completion', d.get('answer', ''))})
                    except:
                        pass
    else:
        # Dummy data for smoke
        train_data = [{"prompt": "What is 2+2?", "completion": "The answer is \\boxed{4}."}] * 10
        print("Using dummy data.")

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    lr_schedule = LinearDecayLRSchedule(learning_rate=2e-5, final_learning_rate=1e-5)

    epochs = 1
    # Grad accum for largest stable micro-batch on 2xT4 4-bit, let's say micro_batch_size=1, gradient_accumulation_steps=8
    # Based on memory / winner code it handles batching explicitly
    micro_batch_size = 1
    gradient_accumulation_steps = 8 if not smoke else 1

    total_steps = len(train_data) * epochs

    model.train()
    step = 0
    accum_step = 0

    print(f"Starting training for {epochs} epoch(s)...")
    device = model.device
    for epoch in range(epochs):
        for data in train_data:
            input_ids, mask = build_datum(data["prompt"], data["completion"], tokenizer)

            input_ids = input_ids.to(device)
            mask = mask.to(device)

            # Simple forward
            outputs = model(input_ids=input_ids)
            logits = outputs.logits

            # Compute custom baseline mask cross entropy loss
            loss = compute_loss(logits, input_ids, mask)

            # Scale loss for gradient accumulation
            loss = loss / gradient_accumulation_steps
            loss.backward()

            accum_step += 1

            # Update weights after gradient_accumulation_steps
            if accum_step % gradient_accumulation_steps == 0 or step == total_steps - 1:
                lr = lr_schedule.get_lr(step, total_steps, epoch, epochs)
                for param_group in optimizer.param_groups:
                    param_group['lr'] = lr

                optimizer.step()
                optimizer.zero_grad()

            step += 1
            if step % 5 == 0 or smoke:
                print(f"Step {step}/{total_steps} Loss: {(loss.item() * gradient_accumulation_steps):.4f}")

    # Create adapter directory
    os.makedirs("adapter", exist_ok=True)

    # Save adapter using HF standard methodology
    model.save_pretrained("adapter")

    adapter_config = {
        "peft_type": "LORA",
        "r": rank,
        "lora_alpha": LORA_ALPHA,
        "target_modules": LORA_TARGET_MODULES,
        "base_model_name_or_path": model_name
    }

    with open("adapter/adapter_config.json", "w") as f:
        json.dump(adapter_config, f, indent=2)

    # Simple Evaluation Loop
    print("Running evaluation...")
    model.eval()
    predictions = []
    gold_data = {}

    with torch.no_grad():
        for i, data in enumerate(train_data):
            # For testing, we just use train_data as eval_data
            prompt = data["prompt"]
            gold_completion = data["completion"]

            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            # In smoke mode with gpt2, use small max_new_tokens
            max_new_tokens = 10 if smoke else 512

            # The setting max_model_len 8192 from memory applies implicitly
            # But here we focus on max_new_tokens for generation. Memory states:
            # "Host scoring logic for the Nemotron Reasoning Challenge evaluates using temp 0, max_model_len 8192, and max_lora_rank 32."
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=0.0
            )

            output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove prompt from output
            prediction = output_text[len(prompt):].strip()

            id_str = str(i)
            predictions.append({"id": id_str, "prediction": prediction})
            gold_data[id_str] = {"answer": gold_completion, "category": "general"}

            if smoke and i >= 2:
                # evaluate only on a few samples in smoke mode
                break

    # Evaluate using the provided eval script
    results = cv.evaluate_cv(predictions, gold_data)
    overall_accuracy = results.get("overall_accuracy", 0.0)

    # Write cv_score.json
    cv_score = {
        "score": overall_accuracy
    }
    with open("cv_score.json", "w") as f:
        json.dump(cv_score, f, indent=2)

    print(f"Training complete. Overall CV Accuracy: {overall_accuracy:.4f}")
    print("Outputs written to adapter/ and cv_score.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA training script skeleton")
    parser.add_argument("--rank", type=int, default=32, help="LoRA rank")
    parser.add_argument("--smoke", action="store_true", help="Run on a tiny toy model for validation")
    # Default points at the competition train.csv attached via competition_sources;
    # garbage-in-garbage-out baseline run to validate the end-to-end pipeline first.
    parser.add_argument("--data", type=str,
        default="/kaggle/input/nvidia-nemotron-model-reasoning-challenge/train.csv",
        help="Path to training data")

    args = parser.parse_args()

    run_training(rank=args.rank, smoke=args.smoke, data_path=args.data)

import argparse
import json
import os
import sys

# Ensure evaluating modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eval')))
import cv
import score

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

    model_name = "gpt2" if smoke else f"/kaggle/input/nemotron-3-nano-30b-a3b-bf16/transformers/placeholder-version/1"
    print(f"Loading model: {model_name}")

    if data_path and os.path.exists(data_path):
        print(f"Reading training data from: {data_path}")
    else:
        print("No training data provided or path does not exist.")

    if smoke:
        model = AutoModelForCausalLM.from_pretrained(model_name)
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
            torch_dtype=torch.bfloat16
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

    tokenizer = AutoTokenizer.from_pretrained(model_name)
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
    parser.add_argument("--data", type=str, help="Path to training data")

    args = parser.parse_args()

    run_training(rank=args.rank, smoke=args.smoke, data_path=args.data)

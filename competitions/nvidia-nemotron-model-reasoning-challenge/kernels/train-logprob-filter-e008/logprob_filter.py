import argparse
import json
import os
import sys
import torch
import torch.nn.functional as F
from collections import defaultdict
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Ensure evaluating modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eval')))

BASE_MODEL = "Nemotron-3-Nano-30B-A3B-BF16"
THRESHOLD = -0.05

def build_datum(prompt_text: str, answer_text: str, tokenizer, max_length: int = 8192):
    # Same as in train.py: mask=1 applies to CoT-reasoning and boxed-answer span, mask=0 to prompt
    prompt_tokens = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    answer_tokens = tokenizer(answer_text, add_special_tokens=False)["input_ids"]

    # We append eos to answer
    answer_tokens = answer_tokens + [tokenizer.eos_token_id]

    all_tokens = prompt_tokens + answer_tokens
    mask = [0] * len(prompt_tokens) + [1] * len(answer_tokens)

    # truncation
    if len(all_tokens) > max_length:
        all_tokens = all_tokens[:max_length]
        mask = mask[:max_length]

    return all_tokens, mask

def compute_logprobs(logits, labels, mask):
    # Standard cross entropy across the masked target
    # Mask = 1 for answer tokens, 0 for prompt tokens

    # Shift so that tokens < n predict n
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()
    shift_mask = mask[..., 1:].contiguous()

    log_probs = F.log_softmax(shift_logits, dim=-1)

    # Get logprob of the correct token
    token_log_probs = log_probs.gather(dim=-1, index=shift_labels.unsqueeze(-1)).squeeze(-1)

    # Filter by mask
    masked_log_probs = token_log_probs * shift_mask

    return masked_log_probs, shift_mask

def run_filter(input_path: str, output_path: str, smoke: bool = False):
    model_name = "gpt2" if smoke else f"/kaggle/input/nvidia-nemotron-3-nano-30b-a3b-bf16/transformers/default/1"
    print(f"Loading model: {model_name}")

    if smoke:
        model = AutoModelForCausalLM.from_pretrained(model_name)
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
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

    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = model.device

    print(f"Reading data from: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    filtered_data = []
    dropped_counts = defaultdict(int)

    with torch.no_grad():
        for i, item in enumerate(data):
            prompt = item.get("prompt", "")
            completion = item.get("completion", "")
            category = item.get("category", "unknown")

            # Use max_model_len 8192 from memory
            tokens, mask = build_datum(prompt, completion, tokenizer, max_length=8192)

            input_ids = torch.tensor([tokens]).to(device)
            mask_tensor = torch.tensor([mask]).to(device)

            outputs = model(input_ids=input_ids)
            logits = outputs.logits

            token_log_probs, shift_mask = compute_logprobs(logits, input_ids, mask_tensor)

            # Extract logprobs where mask == 1
            unmasked_lps = token_log_probs[shift_mask == 1].cpu().tolist()

            if not unmasked_lps:
                min_logprob = 0.0
            else:
                min_logprob = min(unmasked_lps)

            if min_logprob > THRESHOLD:
                # Drop the row
                dropped_counts[category] += 1
            else:
                filtered_data.append(item)

            if i % 10 == 0:
                print(f"Processed {i}/{len(data)} rows...")

            if smoke and i >= 20: # Limit for smoke testing to be fast
                break

    print(f"Original dataset size: {len(data)}")
    print(f"Filtered dataset size: {len(filtered_data)}")

    print("\nDropped Rows Histogram by Category:")
    for cat, count in dropped_counts.items():
        print(f"  {cat}: {count}")

    print(f"\nWriting filtered data to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in filtered_data:
            f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter dataset by base-model logprob")
    parser.add_argument("--input", type=str, required=True, help="Path to input corpus.jsonl")
    parser.add_argument("--output", type=str, required=True, help="Path to output filtered corpus.jsonl")
    parser.add_argument("--smoke", action="store_true", help="Run on a tiny toy model for validation")

    args = parser.parse_args()

    run_filter(input_path=args.input, output_path=args.output, smoke=args.smoke)

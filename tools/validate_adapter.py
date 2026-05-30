#!/usr/bin/env python3
import argparse
import sys
import os
import json
import re

def fail(code, message=""):
    if message:
        print(f"Error: {message}", file=sys.stderr)
    print(f"CODE={code}")
    sys.exit(1)

def check_boxed(text: str) -> bool:
    # Look for \boxed{
    idx = text.find("\\boxed{")
    if idx == -1:
        return False
    # Validate there's a matching closing brace
    brace_count = 0
    for i in range(idx + 7, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            if brace_count == 0:
                return True
            brace_count -= 1
    return False

def main():
    parser = argparse.ArgumentParser(description="Validate LoRA adapter for Nemotron Reasoning Challenge.")
    parser.add_argument("--adapter", required=True, help="Path to adapter directory")
    parser.add_argument("--base", required=True, help="Path to base model")
    parser.add_argument("--prompts", help="Path to 5 smoke prompts JSONL file")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no GPU/model loading)")

    args = parser.parse_args()

    adapter_dir = args.adapter
    config_path = os.path.join(adapter_dir, "adapter_config.json")
    model_st = os.path.join(adapter_dir, "adapter_model.safetensors")
    model_bin = os.path.join(adapter_dir, "adapter_model.bin")

    if not os.path.exists(config_path):
        fail("MISSING_FILES", f"Missing {config_path}")

    if not (os.path.exists(model_st) or os.path.exists(model_bin)):
        fail("MISSING_FILES", "Missing adapter_model.safetensors or adapter_model.bin")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        fail("INVALID_CONFIG", f"Failed to parse config: {e}")

    rank = config.get("r")
    if rank is None:
        fail("INVALID_CONFIG", "Missing 'r' in adapter_config.json")

    if not isinstance(rank, int) or rank > 32:
        fail("RANK_TOO_HIGH", f"Rank {rank} exceeds max of 32")

    n_smoke = 0
    n_boxed_ok = 0

    if not args.mock:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        if not args.prompts or not os.path.exists(args.prompts):
            fail("MISSING_PROMPTS", "Prompts file required in non-mock mode")

        print("Loading base model...")
        tokenizer = AutoTokenizer.from_pretrained(args.base)
        base_model = AutoModelForCausalLM.from_pretrained(
            args.base,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        print("Loading adapter...")
        model = PeftModel.from_pretrained(base_model, args.adapter)
        model.eval()

        with open(args.prompts, "r") as f:
            prompts_data = [json.loads(line) for line in f if line.strip()]

        n_smoke = len(prompts_data)

        for i, item in enumerate(prompts_data):
            prompt = item.get("prompt", "")
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.0,
                    do_sample=False
                )
            # Decode only the generated part
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            completion = tokenizer.decode(generated_ids, skip_special_tokens=True)

            if not check_boxed(completion):
                fail("BOXED_MISSING", f"Prompt {i} missing \\boxed{{...}} in output. Completion: {completion}")

            n_boxed_ok += 1
    else:
        # Mock mode
        n_smoke = 5
        n_boxed_ok = 5

    report = {
        "ok": True,
        "code": None,
        "rank": rank,
        "n_smoke": n_smoke,
        "n_boxed_ok": n_boxed_ok
    }

    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()

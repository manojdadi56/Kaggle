import argparse
import json
import logging
import sys
import os
import re
from collections import defaultdict
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_boxed(text: str) -> str | None:
    if not text:
        return None
    idx = text.rfind(r"\boxed{")
    if idx == -1:
        return None
    start = idx + len(r"\boxed{")
    brace_count = 1
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
        if brace_count == 0:
            return text[start:i]
    return None

def score_item(prediction: str, gold: str) -> bool:
    p_val = extract_boxed(prediction)
    if p_val is None:
        return False

    g_val = extract_boxed(gold)
    if g_val is None:
        g_val = str(gold).strip()
    else:
        g_val = g_val.strip()

    p_val = p_val.strip()

    if p_val == g_val:
        return True

    try:
        if abs(float(p_val) - float(g_val)) <= 1e-2:
            return True
    except ValueError:
        pass

    return False

def get_category(item: Dict[str, Any]) -> str:
    """Extracts or infers the category of an item."""
    if "category" in item and item["category"]:
        return item["category"]

    text = item.get("problem", item.get("question", item.get("text", ""))).lower()
    if not text:
        return "unknown"

    if any(k in text for k in ["math", "equation", "calculate", "number", "integral", "derivative", "theorem", "algebra", "geometry", "probability"]):
        return "math"
    if any(k in text for k in ["code", "python", "programming", "function", "algorithm", "c++", "java", "script"]):
        return "code"
    if any(k in text for k in ["physics", "force", "velocity", "mass", "energy", "momentum", "acceleration"]):
        return "physics"
    if any(k in text for k in ["logic", "puzzle", "deduce", "reasoning", "if and only if", "knights and knaves", "syllogism"]):
        return "logic"

    return "general"

def load_jsonl(filepath: str, max_samples: int = None) -> List[Dict[str, Any]]:
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_samples is not None and i >= max_samples:
                break
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

def build_prompt(item: Dict[str, Any]) -> str:
    """Construct a chat template prompt for the model."""
    problem = item.get("problem", item.get("question", item.get("text", "")))

    # Very simple standard template if tokenizer isn't available
    prompt = f"<|im_start|>user\n{problem}<|im_end|>\n<|im_start|>assistant\n"
    return prompt

def evaluate_mock(data: List[Dict[str, Any]]) -> List[str]:
    """Mock inference that doesn't require GPU/vLLM."""
    logger.info("Running in MOCK mode. Generating dummy responses.")
    predictions = []
    for i, item in enumerate(data):
        answer = str(item.get("answer", ""))

        if i % 3 == 0:
            predictions.append(f"Here is the answer: \\boxed{{{answer}}}")
        elif i % 3 == 1:
            predictions.append(f"I think it is \\boxed{{WRONG}}")
        else:
            predictions.append(f"No box here, just {answer}")
    return predictions

def evaluate_vllm(data: List[Dict[str, Any]], args) -> List[str]:
    """Run real inference using vLLM."""
    try:
        from vllm import LLM, SamplingParams
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
    except ImportError as e:
        logger.error(f"Failed to import vllm or transformers: {e}. Are they installed? Use --mock to run without GPU.")
        sys.exit(1)

    logger.info(f"Loading base model from: {args.base}")
    # Initialize vLLM with host faithful parameters
    llm = LLM(
        model=args.base,
        max_model_len=8192,
        enable_lora=bool(args.adapter),
        max_lora_rank=32,
        gpu_memory_utilization=0.85,
        max_num_seqs=64,
        tensor_parallel_size=1, # Default
        trust_remote_code=True,
    )

    try:
        tokenizer = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    except Exception:
        tokenizer = None

    lora_request = None
    if args.adapter:
        logger.info(f"Loading LoRA adapter from: {args.adapter}")
        lora_request = LoRARequest("adapter", 1, args.adapter)

    # Host sampling parameters
    sampling_params = SamplingParams(
        temperature=0.0,
        top_p=1.0,
        max_tokens=7680,
    )

    prompts = []
    for item in data:
        problem = item.get("problem", item.get("question", item.get("text", "")))
        if tokenizer and hasattr(tokenizer, "apply_chat_template"):
            messages = [{"role": "user", "content": problem}]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            prompts.append(prompt)
        else:
            prompts.append(build_prompt(item))

    logger.info(f"Generating completions for {len(prompts)} prompts...")

    # Generate
    outputs = llm.generate(
        prompts,
        sampling_params=sampling_params,
        lora_request=lora_request
    )

    predictions = [out.outputs[0].text for out in outputs]
    return predictions

def main():
    parser = argparse.ArgumentParser(description="Evaluate Nemotron reasoning using vLLM")
    parser.add_argument("--base", type=str, default="Nemotron-3-Nano-30B-A3B-BF16", help="Path to base model")
    parser.add_argument("--adapter", type=str, help="Path to LoRA adapter directory")
    parser.add_argument("--eval-jsonl", type=str, required=True, help="Path to evaluation dataset (.jsonl)")
    parser.add_argument("--out", type=str, default="cv_score.json", help="Output JSON path")
    parser.add_argument("--max-samples", type=int, default=None, help="Max samples to evaluate")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without vLLM/GPU")

    args = parser.parse_args()

    # Load data
    logger.info(f"Loading data from {args.eval_jsonl}...")
    data = load_jsonl(args.eval_jsonl, args.max_samples)
    logger.info(f"Loaded {len(data)} samples.")

    if not data:
        logger.warning("No data found. Exiting.")
        return

    # Generate predictions
    if args.mock:
        predictions_text = evaluate_mock(data)
    else:
        predictions_text = evaluate_vllm(data, args)

    # Score
    logger.info("Scoring predictions...")
    n_total = len(data)
    n_correct = 0
    n_boxed_missing = 0

    category_stats = defaultdict(lambda: {"total": 0, "correct": 0, "missing": 0})

    for item, pred_text in zip(data, predictions_text):
        gold = str(item.get("answer", ""))
        category = get_category(item)

        category_stats[category]["total"] += 1

        # Check if box is missing
        boxed_val = extract_boxed(pred_text)
        if boxed_val is None:
            n_boxed_missing += 1
            category_stats[category]["missing"] += 1
            is_correct = False
        else:
            is_correct = score_item(pred_text, gold)

        if is_correct:
            n_correct += 1
            category_stats[category]["correct"] += 1

    # Aggregate
    overall_acc = n_correct / n_total if n_total > 0 else 0.0
    per_category = {}
    for cat, stats in category_stats.items():
        per_category[cat] = {
            "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0,
            "total": stats["total"],
            "correct": stats["correct"],
            "missing_box": stats["missing"]
        }

    results = {
        "aggregate": {
            "n_total": n_total,
            "n_correct": n_correct,
            "n_boxed_missing": n_boxed_missing,
            "overall_accuracy": overall_acc
        },
        "per_category": per_category
    }

    # Save
    logger.info(f"Saving results to {args.out}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Print summary
    logger.info("=== Evaluation Summary ===")
    logger.info(f"Total Evaluated: {n_total}")
    logger.info(f"Correct: {n_correct}")
    logger.info(f"Missing \\boxed{{}}: {n_boxed_missing}")
    logger.info(f"Overall Accuracy: {overall_acc:.4f}")
    logger.info("Category Breakdown:")
    for cat, stats in per_category.items():
        logger.info(f"  {cat}: {stats['accuracy']:.4f} ({stats['correct']}/{stats['total']}) [Missing box: {stats['missing_box']}]")

if __name__ == "__main__":
    main()

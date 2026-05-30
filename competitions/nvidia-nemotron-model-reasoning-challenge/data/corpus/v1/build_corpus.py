import sys
import os
import json
import random
import importlib.util
from pathlib import Path
from transformers import AutoTokenizer

TOKEN_LIMIT = 8192
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

def load_module(name: str, path: Path):
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def generate_examples(solvers_dir: Path, synthetic_dir: Path, num_examples=20):
    all_examples = []

    # ensure we check all 7+ categories in data/solvers
    categories = [d for d in solvers_dir.iterdir() if d.is_dir()]
    for category_dir in categories:
        category = category_dir.name
        print(f"Generating for category: {category}")

        solve_module = load_module("solve", category_dir / "solve.py")
        if not solve_module:
            continue

        # Try finding generate.py
        gen_module = load_module("generate", category_dir / "generate.py")
        if not gen_module and category == "bit_manipulation":
            gen_module = load_module("generate", synthetic_dir / "generate.py")

        if not gen_module:
            print(f"No generator found for {category}")
            continue

        raw_examples = []
        if hasattr(gen_module, "generate_dataset"):
            puzzles = gen_module.generate_dataset(num_examples * 2)
            for p in puzzles:
                if "type" in p.get("metadata", {}) and p["metadata"]["type"] == category:
                    raw_examples.append({
                        "prompt": p["question"],
                        "answer": p["answer"]
                    })
        elif hasattr(gen_module, f"generate_{category}_problem"):
            func = getattr(gen_module, f"generate_{category}_problem")
            for i in range(num_examples):
                p = func(i)
                raw_examples.append(p)
        elif hasattr(gen_module, "generate"):
            try:
                puzzles = gen_module.generate(num_examples)
                if isinstance(puzzles, list):
                    raw_examples.extend(puzzles)
                else:
                    raw_examples.append(puzzles)
            except TypeError:
                for i in range(num_examples):
                    p = gen_module.generate()
                    raw_examples.append(p)


        for i, example in enumerate(raw_examples):
            if i >= num_examples:
                break

            prompt = example.get("prompt") or example.get("question")
            if not prompt:
                continue

            # Run solve module to get reasoning and final answer
            try:
                cot = solve_module.solve(prompt)
                if not cot or "Could not parse" in cot or cot == "Cannot parse prompt\n\\boxed{ERROR}":
                    continue
            except Exception as e:
                print(f"Error solving {category} problem: {e}")
                continue

            all_examples.append({
                "id": f"{category}_synth_{i:04d}",
                "category": category,
                "prompt": prompt,
                "completion": cot,
                "answer": example.get("answer") # We don't really use this if we use cot's answer
            })

    return all_examples

def tokenize_prompt(prompt_text: str, tokenizer: AutoTokenizer) -> list[int]:
    messages = [{"role": "user", "content": prompt_text + PROMPT_SUFFIX}]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )

def build_segments(tokens: list[int], mask: list[int]) -> list[dict]:
    if not tokens:
        return []

    segments = []
    seg_start = 0
    current_type = "unmasked" if mask[0] == 1 else "masked"

    for i in range(1, len(tokens)):
        token_type = "unmasked" if mask[i] == 1 else "masked"
        if token_type != current_type:
            segments.append({
                "type": current_type,
                "pos": seg_start,
                "tokens": tokens[seg_start:i]
            })
            seg_start = i
            current_type = token_type

    segments.append({
        "type": current_type,
        "pos": seg_start,
        "tokens": tokens[seg_start:]
    })

    return segments

def main():
    base_dir = Path(__file__).parent.parent.parent.parent
    data_dir = base_dir / "data"
    solvers_dir = data_dir / "solvers"
    synthetic_dir = data_dir / "synthetic"
    corpus_dir = data_dir / "corpus" / "v1"

    tokenizer = AutoTokenizer.from_pretrained(
        "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16", trust_remote_code=True
    )

    examples = generate_examples(solvers_dir, synthetic_dir, num_examples=25)
    print(f"Generated {len(examples)} solvable examples across categories.")

    # Shuffle for stratification
    random.seed(42)
    random.shuffle(examples)

    # 90/10 split stratified by category
    category_examples = {}
    for ex in examples:
        category_examples.setdefault(ex["category"], []).append(ex)

    train_split = []
    dev_split = []

    for cat, ex_list in category_examples.items():
        split_idx = int(len(ex_list) * 0.9)
        train_split.extend(ex_list[:split_idx])
        dev_split.extend(ex_list[split_idx:])

    all_final_entries = train_split + dev_split

    corpus_index_path = corpus_dir / "corpus_index.jsonl"
    corpus_path = corpus_dir / "corpus.jsonl"

    with open(corpus_index_path, "w") as index_f, open(corpus_path, "w") as corpus_f:
        for i, ex in enumerate(all_final_entries):
            prompt_ids = tokenize_prompt(ex["prompt"], tokenizer)
            # handle BatchEncoding or list of list
            if hasattr(prompt_ids, "tolist"):
                prompt_ids = prompt_ids.tolist()
            elif hasattr(prompt_ids, "__getitem__") and hasattr(prompt_ids, "keys") and "input_ids" in prompt_ids.keys():
                prompt_ids = prompt_ids["input_ids"]

            # if it's a list of list
            if isinstance(prompt_ids, list) and len(prompt_ids) > 0 and isinstance(prompt_ids[0], list):
                prompt_ids = prompt_ids[0]
            elif hasattr(prompt_ids, "tolist"):
                prompt_ids = prompt_ids.tolist()

            # fallback if it's still an object that doesn't add to list
            if not isinstance(prompt_ids, list):
                prompt_ids = list(prompt_ids)

            completion_text = f"{ex['completion']}\n</think><|im_end|>"
            completion_ids = tokenizer.encode(completion_text, add_special_tokens=False)

            all_tokens = prompt_ids + completion_ids
            mask = [0] * len(prompt_ids) + [1] * len(completion_ids)

            if len(all_tokens) > TOKEN_LIMIT:
                all_tokens = all_tokens[:TOKEN_LIMIT]
                mask = mask[:TOKEN_LIMIT]

            unmasked_count = sum(mask)
            masked_count = len(mask) - unmasked_count

            segments = build_segments(all_tokens, mask)

            problem_id = ex["id"]
            is_train = i < len(train_split)

            problem_dir = corpus_dir / problem_id
            problem_dir.mkdir(parents=True, exist_ok=True)

            # Write segment files (for index-based reading)
            with open(problem_dir / "synthetic.jsonl", "w") as f:
                for seg in segments:
                    json.dump(seg, f)
                    f.write("\n")

            # Also write to corpus.jsonl as the direct dataset format
            corpus_entry = {
                "id": problem_id,
                "category": ex["category"],
                "prompt": ex["prompt"],
                "completion": ex["completion"],
                "tokens": all_tokens,
                "mask": mask,
                "answer": ex["answer"]
            }
            json.dump(corpus_entry, corpus_f)
            corpus_f.write("\n")

            index_entry = {
                "problem_id": problem_id,
                "segment": "synthetic.jsonl",
                "category": ex["category"],
                "masked_token_count": masked_count,
                "unmasked_token_count": unmasked_count,
                "token_count": len(all_tokens),
                "answer": ex["answer"],
                "included": True,
                "split": "train" if is_train else "dev"
            }
            json.dump(index_entry, index_f)
            index_f.write("\n")

    print(f"Wrote {len(all_final_entries)} entries to {corpus_index_path}")

if __name__ == "__main__":
    main()

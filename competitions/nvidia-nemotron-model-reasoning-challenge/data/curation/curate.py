import json
import re
from typing import List, Dict, Any, Tuple

def validate_format(item: Dict[str, Any]) -> bool:
    """
    Validates the format of a dataset item.
    - is_correct must be True.
    - completion must contain \boxed{...}
    - completion must contain </think>\n (as per schema expectation)
    """
    if not item.get("is_correct", False):
        return False

    completion = item.get("completion", "")

    # Check for \boxed{...}
    if "\\boxed{" not in completion:
        return False

    # Check for </think>
    if "</think>" not in completion:
        return False

    # Simple regex to ensure it has boxed format
    boxed_match = re.search(r"\\boxed\{([^}]*)\}", completion)
    if not boxed_match:
        return False

    return True

def deduplicate(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates items by exact prompt string matching.
    """
    seen_prompts = set()
    filtered = []

    for item in items:
        prompt = item.get("prompt")
        if prompt not in seen_prompts:
            seen_prompts.add(prompt)
            filtered.append(item)

    return filtered

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Loads a JSONL file."""
    items = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def save_jsonl(items: List[Dict[str, Any]], filepath: str):
    """Saves a list of dictionaries to a JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

import random
from collections import defaultdict
import math

def calculate_difficulty(item: Dict[str, Any]) -> int:
    """
    Calculates difficulty proxy based on completion length.
    Using character length as proxy. We can bin this.
    """
    completion = item.get("completion", "")
    return len(completion)

def balance_and_split(items: List[Dict[str, Any]], val_ratio: float = 0.1, seed: int = 42) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Balances data by category and difficulty, then splits into train and val.

    Returns: (train_items, val_items, stats)
    """
    random.seed(seed)

    # Add difficulty proxy
    for item in items:
        item["_difficulty"] = calculate_difficulty(item)

    # Group by category
    by_category = defaultdict(list)
    for item in items:
        cat = item.get("category", "unknown")
        by_category[cat].append(item)

    train_out = []
    val_out = []

    stats = {
        "total": len(items),
        "by_category": {},
        "difficulty_histogram": defaultdict(int)
    }

    # Process each category
    for cat, cat_items in by_category.items():
        # Sort by difficulty to stratify
        cat_items.sort(key=lambda x: x["_difficulty"])

        # Calculate stats for the category
        stats["by_category"][cat] = len(cat_items)
        for item in cat_items:
            # Bin difficulty for histogram (e.g., bins of 500 chars)
            bin_idx = (item["_difficulty"] // 500) * 500
            stats["difficulty_histogram"][f"{bin_idx}-{bin_idx+500}"] += 1

        # We can just do a stratified split (e.g. pick every 10th item for val, or shuffle and pick)
        # To maintain difficulty distribution in both, we can group into small chunks and split within them
        chunk_size = max(2, int(1.0 / max(0.001, val_ratio)))

        cat_train = []
        cat_val = []

        # For small categories, just do simple random split
        if len(cat_items) < chunk_size * 2:
            shuffled = list(cat_items)
            random.shuffle(shuffled)
            split_idx = int(len(shuffled) * (1 - val_ratio))
            cat_train.extend(shuffled[:split_idx])
            cat_val.extend(shuffled[split_idx:])
        else:
            # Chunking to keep difficulty distribution similar
            for i in range(0, len(cat_items), chunk_size):
                chunk = cat_items[i:i+chunk_size]
                if not chunk:
                    break
                # pick one random index for val
                val_idx = random.randint(0, len(chunk)-1)

                for j, item in enumerate(chunk):
                    if j == val_idx:
                        cat_val.append(item)
                    else:
                        cat_train.append(item)

        train_out.extend(cat_train)
        val_out.extend(cat_val)

    # Remove temporary _difficulty key
    for item in train_out + val_out:
        item.pop("_difficulty", None)

    stats["train_size"] = len(train_out)
    stats["val_size"] = len(val_out)

    # Shuffle outputs so categories are mixed
    random.shuffle(train_out)
    random.shuffle(val_out)

    return train_out, val_out, stats

def process_pipeline(input_paths: List[str], output_train: str, output_val: str, output_stats: str):
    """
    Runs the full curation pipeline.
    """
    all_items = []
    for path in input_paths:
        try:
            all_items.extend(load_jsonl(path))
        except FileNotFoundError:
            print(f"Warning: File {path} not found.")

    print(f"Loaded {len(all_items)} total items.")

    # 1. Filter
    filtered_items = [item for item in all_items if validate_format(item)]
    print(f"Items after format validation: {len(filtered_items)}")

    # 2. Dedup
    deduped_items = deduplicate(filtered_items)
    print(f"Items after deduplication: {len(deduped_items)}")

    # 3. Balance and Split
    train_items, val_items, stats = balance_and_split(deduped_items)

    # 4. Save
    save_jsonl(train_items, output_train)
    save_jsonl(val_items, output_val)
    with open(output_stats, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"Saved {len(train_items)} to {output_train}")
    print(f"Saved {len(val_items)} to {output_val}")
    print(f"Saved stats to {output_stats}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Curate CoT dataset.")
    parser.add_argument("--inputs", nargs='+', required=True, help="Input JSONL files")
    parser.add_argument("--train", default="train.jsonl", help="Output train file")
    parser.add_argument("--val", default="val.jsonl", help="Output val file")
    parser.add_argument("--stats", default="stats.json", help="Output stats file")

    args = parser.parse_args()
    process_pipeline(args.inputs, args.train, args.val, args.stats)

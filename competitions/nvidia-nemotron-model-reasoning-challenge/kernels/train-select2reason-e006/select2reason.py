import json
import re
from typing import List, Dict, Any
from collections import Counter
import math

def calculate_utility(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scores each corpus row by utility:
    - trace length
    - category novelty (inverse frequency)
    """
    if not items:
        return []

    # Category frequency for novelty
    category_counts = Counter(item.get("category", "unknown") for item in items)
    total_items = len(items)

    scored_items = []
    for item in items:
        completion = item.get("completion", "")

        # 1. Trace length (log scale can help flatten extreme outliers, but raw length is fine too)
        length_score = float(len(completion))

        # 2. Category novelty (inverse of probability)
        category = item.get("category", "unknown")
        cat_freq = category_counts[category] / total_items
        novelty_score = 1.0 / (cat_freq + 1e-5) # avoid div by zero

        # Optionally use confidence if available, else 1.0
        confidence = item.get("solver_confidence", 1.0)

        # Composite score
        # Using a balanced approach: log(length) * novelty
        # or just length * novelty
        score = length_score * math.log1p(novelty_score) * confidence

        item_copy = dict(item)
        item_copy["_utility_score"] = score
        scored_items.append(item_copy)

    return scored_items

def deduplicate_fingerprint(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates based on exact prompt match, keeping the one with the highest utility score.
    Assumes items already have '_utility_score'.
    """
    best_items: Dict[str, Dict[str, Any]] = {}

    for item in items:
        prompt = item.get("prompt", "")
        # Remove whitespace to make deduplication slightly more robust
        fingerprint = re.sub(r'\s+', '', prompt)

        score = item.get("_utility_score", 0.0)

        if fingerprint not in best_items:
            best_items[fingerprint] = item
        else:
            if score > best_items[fingerprint].get("_utility_score", 0.0):
                best_items[fingerprint] = item

    return list(best_items.values())

def curate_top_p(items: List[Dict[str, Any]], keep_percent: float = 0.3) -> List[Dict[str, Any]]:
    """
    Scores items, deduplicates, and keeps top `keep_percent`% of items,
    preserving stratification by applying the cut per-category.
    """
    # 1. Score
    scored = calculate_utility(items)

    # 2. Dedup
    deduped = deduplicate_fingerprint(scored)

    # 3. Group by category to preserve stratification
    from collections import defaultdict
    by_category = defaultdict(list)
    for item in deduped:
        by_category[item.get("category", "unknown")].append(item)

    kept_items = []
    # 4. Keep top P within each category
    for cat, cat_items in by_category.items():
        cat_items.sort(key=lambda x: x["_utility_score"], reverse=True)
        keep_count = int(len(cat_items) * keep_percent)
        if keep_count == 0 and len(cat_items) > 0:
            keep_count = 1 # Keep at least one if there's any
        kept_items.extend(cat_items[:keep_count])

    # Clean up temp fields
    for item in kept_items:
        item.pop("_utility_score", None)

    return kept_items

def process_file(input_path: str, output_path: str, keep_percent: float = 0.3):
    items = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))

    curated = curate_top_p(items, keep_percent)

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in curated:
            f.write(json.dumps(item) + "\n")

    print(f"Curated {input_path}: {len(items)} -> {len(curated)} items ({keep_percent*100}%)")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--keep_percent", type=float, default=0.3)
    args = parser.parse_args()
    process_file(args.input, args.output, args.keep_percent)

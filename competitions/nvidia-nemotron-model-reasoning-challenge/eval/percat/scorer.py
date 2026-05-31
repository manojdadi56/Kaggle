import re
import math
import json
import random

def extract_boxed(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"

    matches = list(re.finditer(r"\\boxed\{", text))
    if matches:
        last_match = matches[-1]
        start_idx = last_match.end()
        depth = 1
        end_idx = start_idx
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            if depth == 0:
                end_idx = i
                break

        if depth == 0:
            return text[start_idx:end_idx].strip()
        else:
            return text[start_idx:].strip()

    patterns = [
        r"The final answer is:\s*([^\n]+)",
        r"Final answer is:\s*([^\n]+)",
        r"Final answer\s*[:：]\s*([^\n]+)",
        r"final answer\s*[:：]\s*([^\n]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].strip()

    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if matches:
        return matches[-1]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"

def is_correct(pred: str, gold: str) -> bool:
    gold = gold.strip()
    pred = pred.strip()

    if re.fullmatch(r"[01]+", gold):
        return pred.lower() == gold.lower()

    try:
        gold_num = float(gold)
        pred_num = float(pred)
        return math.isclose(gold_num, pred_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return pred.lower() == gold.lower()


def score_by_category(records: list[dict]) -> dict:
    results = {
        "aggregate": {"correct": 0, "total": 0, "accuracy": 0.0},
        "by_category": {}
    }

    for record in records:
        category = record["category"]
        pred_text = record.get("pred_text")
        gold = record["gold"]

        extracted = extract_boxed(pred_text)
        correct = is_correct(extracted, gold)

        if category not in results["by_category"]:
            results["by_category"][category] = {"correct": 0, "total": 0, "accuracy": 0.0}

        results["aggregate"]["total"] += 1
        results["by_category"][category]["total"] += 1

        if correct:
            results["aggregate"]["correct"] += 1
            results["by_category"][category]["correct"] += 1

    if results["aggregate"]["total"] > 0:
        results["aggregate"]["accuracy"] = results["aggregate"]["correct"] / results["aggregate"]["total"]

    for cat, stats in results["by_category"].items():
        if stats["total"] > 0:
            stats["accuracy"] = stats["correct"] / stats["total"]

    return results

def stratified_dev_split(rows: list[dict], per_cat: int, seed: int) -> tuple[list[dict], list[dict]]:
    # Sort deterministically
    sorted_rows = sorted(rows, key=lambda x: json.dumps(x, sort_keys=True))

    # Group by category
    by_category = {}
    for row in sorted_rows:
        cat = row["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(row)

    rng = random.Random(seed)

    train_split = []
    dev_split = []

    for cat in sorted(by_category.keys()):
        cat_rows = by_category[cat]
        rng.shuffle(cat_rows)

        dev_split.extend(cat_rows[:per_cat])
        train_split.extend(cat_rows[per_cat:])

    return train_split, dev_split

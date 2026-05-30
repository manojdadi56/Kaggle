import json
import csv
import argparse
import random
from typing import Any, Dict, List
from collections import defaultdict

from score import score_item

def create_holdout(data: List[Dict[str, Any]], test_size: float = 0.2, seed: int = 42) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Splits data into train and holdout sets."""
    random.seed(seed)
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)

    split_idx = int(len(shuffled_data) * (1 - test_size))
    train_data = shuffled_data[:split_idx]
    holdout_data = shuffled_data[split_idx:]

    return train_data, holdout_data


def evaluate_cv(predictions: List[Dict[str, Any]], gold_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates predictions against gold data.
    Assumes predictions have 'id' and 'prediction' keys.
    Assumes gold_data maps 'id' to a dict containing 'answer' and optionally 'category'.
    """
    if not predictions:
        return {"overall_accuracy": 0.0, "category_accuracy": {}}

    correct_total = 0
    total = 0

    category_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for pred_item in predictions:
        item_id = str(pred_item.get("id"))
        prediction_text = pred_item.get("prediction", "")

        if item_id not in gold_data:
            print(f"Warning: ID {item_id} found in predictions but not in gold data. Skipping.")
            continue

        gold_item = gold_data[item_id]
        gold_text = gold_item.get("answer", "")
        category = gold_item.get("category", "unknown")

        is_correct = score_item(prediction_text, gold_text)

        if is_correct:
            correct_total += 1
            category_stats[category]["correct"] += 1

        total += 1
        category_stats[category]["total"] += 1

    overall_accuracy = correct_total / total if total > 0 else 0.0

    category_accuracy = {
        cat: stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
        for cat, stats in category_stats.items()
    }

    return {
        "overall_accuracy": overall_accuracy,
        "category_accuracy": category_accuracy,
        "total_evaluated": total
    }

def _load_data(filepath: str, key_field: str = None) -> Any:
    """Loads JSONL or CSV data."""
    if filepath.endswith('.csv'):
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        if key_field:
            return {str(item[key_field]): item for item in data if key_field in item}
        return data

    elif filepath.endswith('.jsonl') or filepath.endswith('.json'):
        # simple jsonl support for flexibility
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        if key_field:
             return {str(item[key_field]): item for item in data if key_field in item}
        return data
    else:
        raise ValueError(f"Unsupported file format for {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate model predictions against gold data.")
    parser.add_argument("--predictions", type=str, required=True, help="Path to predictions file (CSV or JSONL). Must have 'id' and 'prediction' columns/keys.")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold data file (CSV or JSONL). Must have 'id', 'answer', and optionally 'category'.")
    parser.add_argument("--output", type=str, default="cv_score.json", help="Path to output the scores (JSON).")

    args = parser.parse_args()

    predictions = _load_data(args.predictions)
    gold_data = _load_data(args.gold, key_field="id")

    results = evaluate_cv(predictions, gold_data)

    print(f"Overall Accuracy: {results['overall_accuracy']:.4f} ({results['total_evaluated']} samples)")
    print("Category Accuracy:")
    for cat, acc in results['category_accuracy'].items():
        print(f"  {cat}: {acc:.4f}")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()

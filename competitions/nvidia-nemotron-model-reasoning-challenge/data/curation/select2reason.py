import json
import re
import argparse
from typing import List, Dict, Any, Tuple
from collections import defaultdict


def get_signature(prompt: str) -> str:
    """
    Creates a normalized structural template from a prompt string.
    Replaces numbers with <NUM> and collapses extra whitespace.
    """
    if not prompt:
        return ""

    # Replace numbers with a placeholder
    sig = re.sub(r'\b\d+(?:\.\d+)?\b', '<NUM>', prompt)

    # Collapse whitespace and convert to lowercase for better matching
    sig = re.sub(r'\s+', ' ', sig).strip().lower()
    return sig


def calculate_utility(row: Dict[str, Any]) -> float:
    """
    Calculates a utility score for a row.
    Currently, prioritizing the length of the CoT completion.
    """
    completion = row.get("completion", "")
    return float(len(completion))


def curate(
    rows: List[Dict[str, Any]],
    per_cat_cap: int = None,
    max_per_signature: int = 1
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Curates a dataset by grouping by (category, signature), keeping the top rows per
    group, and then enforcing a per-category cap, based on utility scores.

    Returns:
        (kept_rows, dropped_rows, report)
    """
    # Decorate rows with utility and signature
    decorated_rows = []
    for row in rows:
        decorated = dict(row)
        decorated["_utility"] = calculate_utility(row)
        decorated["_signature"] = get_signature(row.get("prompt", ""))
        decorated_rows.append(decorated)

    # 1. Group by (category, signature)
    grouped = defaultdict(list)
    for row in decorated_rows:
        cat = row.get("category", "unknown")
        sig = row["_signature"]
        grouped[(cat, sig)].append(row)

    candidates = []
    dropped = []

    report = {
        "total_input": len(rows),
        "total_kept": 0,
        "total_dropped": 0,
        "dropped_by_reason": {
            "duplicate_signature": 0,
            "category_cap_exceeded": 0
        },
        "kept_by_category": defaultdict(int),
        "dropped_by_category": defaultdict(int),
    }

    # 2. Retain top max_per_signature per group
    for (cat, sig), group_rows in grouped.items():
        # Sort by utility descending
        group_rows.sort(key=lambda x: x["_utility"], reverse=True)

        kept_for_sig = group_rows[:max_per_signature]
        dropped_for_sig = group_rows[max_per_signature:]

        candidates.extend(kept_for_sig)

        for d in dropped_for_sig:
            # Create a dropped record
            drop_record = dict(d)
            drop_record["_drop_reason"] = "duplicate_signature"
            dropped.append(drop_record)

            report["dropped_by_reason"]["duplicate_signature"] += 1
            report["dropped_by_category"][cat] += 1

    # 3. Group remaining candidates by category
    cat_candidates = defaultdict(list)
    for row in candidates:
        cat = row.get("category", "unknown")
        cat_candidates[cat].append(row)

    final_kept = []

    # 4. Enforce per_cat_cap
    for cat, cat_rows in cat_candidates.items():
        cat_rows.sort(key=lambda x: x["_utility"], reverse=True)

        if per_cat_cap is not None:
            kept_for_cat = cat_rows[:per_cat_cap]
            dropped_for_cat = cat_rows[per_cat_cap:]
        else:
            kept_for_cat = cat_rows
            dropped_for_cat = []

        final_kept.extend(kept_for_cat)

        for d in dropped_for_cat:
            drop_record = dict(d)
            drop_record["_drop_reason"] = "category_cap_exceeded"
            dropped.append(drop_record)

            report["dropped_by_reason"]["category_cap_exceeded"] += 1
            report["dropped_by_category"][cat] += 1

        report["kept_by_category"][cat] += len(kept_for_cat)

    report["total_kept"] = len(final_kept)
    report["total_dropped"] = len(dropped)

    # Clean up internal fields
    for row in final_kept:
        row.pop("_utility", None)
        row.pop("_signature", None)
        row.pop("_drop_reason", None)

    for row in dropped:
        row.pop("_utility", None)
        row.pop("_signature", None)

    # Convert defaultdicts to regular dicts for JSON serialization
    report["kept_by_category"] = dict(report["kept_by_category"])
    report["dropped_by_category"] = dict(report["dropped_by_category"])

    return final_kept, dropped, report


def main():
    parser = argparse.ArgumentParser(description="Select2Reason Curation Filter")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file for kept rows")
    parser.add_argument("--report", required=True, help="Output JSON file for curation report")
    parser.add_argument("--per_cat_cap", type=int, default=None, help="Maximum number of rows to keep per category")
    parser.add_argument("--max_per_signature", type=int, default=1, help="Maximum number of rows to keep per prompt signature")

    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    kept, dropped, report = curate(
        rows=rows,
        per_cat_cap=args.per_cat_cap,
        max_per_signature=args.max_per_signature
    )

    with open(args.output, "w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row) + "\n")

    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Curation complete.")
    print(f"Input rows:   {report['total_input']}")
    print(f"Kept rows:    {report['total_kept']}")
    print(f"Dropped rows: {report['total_dropped']}")


if __name__ == "__main__":
    main()

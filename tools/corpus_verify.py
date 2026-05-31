"""Corpus quality probe — counts rows per category that have a parseable \\boxed{X} answer,
plus whether the prompt exactly matches a train.csv row.

NOTE on Jules-generated corpora: discovered in C27 that Jules synthesizes new prompts
(not extracted from train.csv), so the "unmatched_in_train" count for those corpora will
be near-100% — that's expected, not a bug. The useful signals from this tool are:
  - no_boxed_in_completion: rows where my extractor can't find a final \\boxed{X} — bug indicator
  - wrong_prediction: rows where prompt MATCHES train.csv but predicted differs from gold — solver bug

For operator-built corpora (v5_local, v6_local) the prompts ARE from train.csv so wrong_prediction
is the meaningful column.

Usage:
    python tools/corpus_verify.py competitions/.../data/corpus/v11_local/corpus.jsonl
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parents[1]
COMP = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge"
TRAIN = COMP / "data" / "raw" / "train.csv"


def extract_boxed(text: str) -> str | None:
    """Extract the LAST \\boxed{X} value, unwrapping nested boxes once."""
    if not text:
        return None
    i = text.rfind("\\boxed{")
    if i < 0:
        return None
    s = i + 7
    depth = 1
    for j in range(s, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                v = text[s:j].strip()
                # unwrap nested \boxed{...}
                if v.startswith("\\boxed{") and v.endswith("}"):
                    v = v[7:-1].strip()
                return v
    return None


def normalize(v: str) -> str:
    """Lightweight normalization for string comparison."""
    return v.strip().rstrip(".0").rstrip(".") if v else v


def numeric_match(a: str, b: str, tol: float = 1e-2) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (ValueError, TypeError):
        return False


def load_train_index() -> dict[str, str]:
    """Index train.csv by prompt → answer (prompts are unique)."""
    out: dict[str, str] = {}
    with TRAIN.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["prompt"].strip()] = row["answer"].strip()
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("corpus_jsonl", help="path to corpus.jsonl")
    p.add_argument("--report-out", default=None, help="write detailed report json here")
    args = p.parse_args(argv)

    train_idx = load_train_index()
    print(f"loaded {len(train_idx)} train.csv rows")

    per_cat = defaultdict(lambda: {"n_total": 0, "predicted_match": 0,
                                    "unmatched_in_train": 0, "wrong_prediction": 0,
                                    "no_boxed_in_completion": 0})
    examples_wrong: dict[str, list] = defaultdict(list)

    with Path(args.corpus_jsonl).open(encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            cat = r.get("category", "?")
            per_cat[cat]["n_total"] += 1
            prompt = r.get("prompt", "").strip()
            completion = r.get("completion", "")
            predicted = extract_boxed(completion)
            if predicted is None:
                per_cat[cat]["no_boxed_in_completion"] += 1
                continue
            gold = train_idx.get(prompt)
            if gold is None:
                per_cat[cat]["unmatched_in_train"] += 1
                continue
            # exact or numeric match
            if predicted == gold or numeric_match(predicted, gold) or normalize(predicted) == normalize(gold):
                per_cat[cat]["predicted_match"] += 1
            else:
                per_cat[cat]["wrong_prediction"] += 1
                if len(examples_wrong[cat]) < 3:
                    examples_wrong[cat].append({
                        "prompt_tail": prompt[-150:],
                        "gold": gold,
                        "predicted": predicted,
                    })

    print("\n=== quality per category ===")
    print(f"{'category':<22} {'total':>6} {'verified':>9} {'wrong':>7} {'unmatched':>10} {'no_boxed':>9}")
    rows = []
    for cat, d in sorted(per_cat.items()):
        v_pct = 100 * d["predicted_match"] / d["n_total"] if d["n_total"] else 0
        print(f"{cat:<22} {d['n_total']:>6} {d['predicted_match']:>9} {d['wrong_prediction']:>7} {d['unmatched_in_train']:>10} {d['no_boxed_in_completion']:>9}  ({v_pct:.1f}%)")
        rows.append({"category": cat, **d, "verified_pct": v_pct})

    if examples_wrong:
        print("\n=== samples of wrong predictions ===")
        for cat, exs in examples_wrong.items():
            print(f"\n-- {cat} --")
            for ex in exs:
                print(f"  prompt tail: ...{ex['prompt_tail']}")
                print(f"    gold: {ex['gold']!r}  predicted: {ex['predicted']!r}")

    if args.report_out:
        Path(args.report_out).write_text(json.dumps({
            "per_category": rows,
            "examples_wrong": dict(examples_wrong),
        }, indent=2), encoding="utf-8")
        print(f"\nreport saved: {args.report_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

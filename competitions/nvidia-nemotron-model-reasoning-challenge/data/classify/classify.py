"""train.csv category classifier (OPERATOR-OWNED — needs raw train.csv, which Jules VMs lack).

train.csv has only id/prompt/answer — NO category column. This assigns each of the 9500
rows to one of the puzzle categories by prompt-format pattern, so we can run the existing
deterministic solvers on the REAL rows (solve-mode) and verify each answer against gold —
converting the 6 currently-synthetic categories into train.csv-VERIFIED corpus rows.

Categories (formats learned from labeled corpus samples, 2026-05-31):
  gravity            "gravitational constant" / "For t = Xs, distance = Y m"
  numeral            "numeral system" / "write the number N in the Wonderland numeral system"
  unit_conversion    "unit conversion" / "m becomes" / "convert the following measurement"
  bit_manipulation   "Nicknames for bits" / hex 0x.. / xor|and|or
  cipher             "WORD WORD -> WORD WORD" substitution + "Decrypt:"
  cryptarithm        letter sums "XX+XX = XXXX" + "determine the result" (no '?')
  cryptarithm_guess  "XX?GG = GGXX" — '?' operator (the category the winner SKIPPED)
  equation_numeric   "transformation rule for the equation" / numeric "NN+NN = NN" / "What is a+b?"

Usage:
    python -m ... (run directly)
    python competitions/.../data/classify/classify.py            # classify all + report
    python competitions/.../data/classify/classify.py --out id_category.json
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
TRAIN = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "raw" / "train.csv"

# ordered (cat, predicate) — first match wins. Most specific first.
_CRYPT_GUESS = re.compile(r"[A-Za-z]{1,4}\?[A-Za-z]{1,4}\s*=")   # 'TN?GG = GGTN'
_CRYPT_PLUS  = re.compile(r"[A-Za-z]{1,4}\+[A-Za-z]{1,4}\s*=")   # 'YU+MX = YUMX' (letters)
_NUM_PLUS    = re.compile(r"\d+\s*\+\s*\d+\s*=")                 # '34+28 = 26'  (digits)
_HEX         = re.compile(r"0x[0-9a-fA-F]+")
_ARROW_WORDS = re.compile(r"[A-Z]{2,}\s+[A-Z]{2,}.*->.*[A-Z]{2,}")


def classify(prompt: str) -> str:
    """Classify by the train.csv 'In Alice's Wonderland, a secret ___' signature phrase.

    VERIFIED 2026-05-31: train.csv has EXACTLY 6 categories (each phrase below is unique
    and the 6 partition all 9500 rows). cryptarithm / cryptarithm_guess / select2reason
    DO NOT EXIST in train.csv (0 matches) — those were fabricated synthetic categories.
    """
    p = prompt or ""
    low = p.lower()
    if "gravitational constant" in low or ("for t =" in low and "distance" in low):
        return "gravity"
    if "numeral system" in low:
        return "numeral"
    if "unit conversion" in low or "m becomes" in low:
        return "unit_conversion"
    if "bit manipulation rule" in low or "8-bit binary" in low:
        return "bit_manipulation"          # REAL format: 8-bit binary 'NNNNNNNN -> MMMMMMMM'
    if "encryption rule" in low:
        return "cipher"                     # REAL format: word substitution 'w w -> w w' + Decrypt
    if "set of transformation" in low:
        return "equation_numeric"           # REAL format: SYMBOLIC transform '`!*[{ = ...' (NOT numeric)
    return "unknown"


def _load_verified_seed() -> dict[str, str]:
    """Exact-prompt -> category from the 3 verified operator corpora (sanity check)."""
    seed: dict[str, str] = {}
    cdir = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "corpus"
    for ver in ("v6_local", "v12_local"):
        fp = cdir / ver / "corpus.jsonl"
        if not fp.exists():
            continue
        for line in fp.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            cat = r.get("category")
            pr = (r.get("prompt") or "").strip()
            if cat in ("gravity", "numeral", "unit_conversion") and pr:
                seed.setdefault(pr, cat)
    return seed


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write id->category JSON here")
    args = ap.parse_args(argv)

    if not TRAIN.exists():
        print(f"ERROR: {TRAIN} not found (raw data is gitignored; this is operator-only).", file=sys.stderr)
        return 2

    rows = list(csv.DictReader(TRAIN.open(encoding="utf-8")))
    seed = _load_verified_seed()
    print(f"loaded {len(rows)} train rows; {len(seed)} verified seed prompts")

    dist = Counter()
    id_cat: dict[str, str] = {}
    # sanity: classifier vs verified seed agreement
    seed_total = seed_agree = 0
    for r in rows:
        pr = (r.get("prompt") or "").strip()
        cat = classify(pr)
        id_cat[r["id"]] = cat
        dist[cat] += 1
        if pr in seed:
            seed_total += 1
            if seed[pr] == cat:
                seed_agree += 1

    print("\n=== category distribution (9500 rows) ===")
    for c, n in dist.most_common():
        print(f"  {c:<18} {n:>5}")
    if seed_total:
        print(f"\nseed agreement (classifier vs verified labels): {seed_agree}/{seed_total} "
              f"({100*seed_agree/seed_total:.1f}%)")

    if args.out:
        Path(args.out).write_text(json.dumps(id_cat), encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

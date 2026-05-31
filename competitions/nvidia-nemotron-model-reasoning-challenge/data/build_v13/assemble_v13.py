"""Assemble the all-VERIFIED v13 corpus from per-category verified sources.

v13 = 100% train.csv-matched, guaranteed-correct CoT, NO synthetic, NO fabricated categories.
  base (from v6_local, operator-verified): gravity, numeral, unit_conversion
  build_v13/cipher_verified.jsonl:         cipher        (~1568, 99.5%)
  build_v13/bit_verified.jsonl:            bit_manipulation (~665, 41.5%)
  DROPPED: cryptarithm / cryptarithm_guess / select2reason (absent from train.csv),
           equation_numeric (symbol-arithmetic solver not yet built — held out, not synthetic).

Run the per-category builders first (cipher_verified.py, bit_verified.py). Output corpus.jsonl
is gitignored (raw-derived). Verify with tools/corpus_verify.py (expect 100% per category).

Usage: python competitions/.../data/build_v13/assemble_v13.py
"""
from __future__ import annotations
import collections
import json
import sys
from pathlib import Path

COMP = Path(__file__).resolve().parents[2]
DATA = COMP / "data"
BASE_CATS = ("gravity", "numeral", "unit_conversion")


def main() -> int:
    out, cnt = [], collections.Counter()
    # base categories: prefer the full build_v13/base_verified.jsonl; fall back to v6_local
    base_full = DATA / "build_v13" / "base_verified.jsonl"
    if base_full.exists():
        for line in base_full.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            out.append(r)
            cnt[r.get("category", "?")] += 1
    else:
        v6 = DATA / "corpus" / "v6_local" / "corpus.jsonl"
        if v6.exists():
            for line in v6.read_text(encoding="utf-8").splitlines():
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("category") in BASE_CATS:
                    out.append({"prompt": r["prompt"], "completion": r["completion"], "category": r["category"]})
                    cnt[r["category"]] += 1
    for fn in ("cipher_verified.jsonl", "bit_verified.jsonl"):
        p = DATA / "build_v13" / fn
        if not p.exists():
            print(f"WARN: {p} missing — run the builder first", file=sys.stderr)
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            out.append(r)
            cnt[r.get("category", "?")] += 1
    dest = DATA / "corpus" / "v13_local"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "corpus.jsonl").write_text("\n".join(json.dumps(r) for r in out) + "\n", encoding="utf-8")
    print(f"v13 assembled: {dict(cnt)} TOTAL {len(out)} -> {dest/'corpus.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

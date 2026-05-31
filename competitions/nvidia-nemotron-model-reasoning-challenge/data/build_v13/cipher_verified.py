"""Build VERIFIED cipher corpus rows from real train.csv (operator-owned; needs raw data).

Strategy (validated 2026-05-31): each cipher puzzle is a consistent letter substitution.
Build the char-map from the in-prompt 'ciphertext -> plaintext' example pairs, decrypt the
target, and KEEP ONLY rows whose target uses letters all present in the examples (so the
decryption is fully determined). On those, exact-match vs gold is 100% (605/1576 = 38.4%).
The remaining ~62% need letter-completion (comprehensive English wordlist) — future work
(H-CIPHER-DICT). Emitting only the 605 fully-determined rows gives guaranteed-correct CoT.

Output: verified rows {prompt, completion, category:'cipher'} with a concise CoT ending in
\\boxed{answer}. corpus jsonl is gitignored (operator-built; not committed).

Usage:
    python competitions/.../data/build_v13/cipher_verified.py            # report
    python competitions/.../data/build_v13/cipher_verified.py --out cipher_verified.jsonl
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
COMP = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge"
TRAIN = COMP / "data" / "raw" / "train.csv"
sys.path.insert(0, str(COMP / "data" / "classify"))


def _parse(prompt: str):
    """Return (mapping cipher->plain lowercase, target_ciphertext) or (None,None)."""
    mapping, target = {}, None
    for line in prompt.split("\n"):
        line = line.strip()
        if " -> " in line:
            src, dst = line.split(" -> ", 1)
            for s, d in zip(src, dst):
                if s.isalpha() and d.isalpha():
                    mapping[s.lower()] = d.lower()
        elif "decrypt the following text:" in line.lower():
            target = line.split(":", 1)[1].strip()
    return mapping, target


def _cot(mapping: dict, target: str, answer: str) -> str:
    pairs = ", ".join(f"{s}->{mapping[s]}" for s in sorted(mapping))
    return (
        "The same ciphertext letter always maps to the same plaintext letter, so this is a "
        "fixed substitution cipher.\n"
        f"From the examples, the letter map is: {pairs}.\n"
        f"Applying it to '{target}' character by character gives the plaintext.\n"
        f"\\boxed{{{answer}}}"
    )


def build(limit: int | None = None):
    import classify as C
    rows = list(csv.DictReader(TRAIN.open(encoding="utf-8")))
    ciph = [r for r in rows if C.classify(r["prompt"]) == "cipher"]
    out, kept, total, mismatch = [], 0, 0, 0
    for r in ciph:
        mapping, target = _parse(r["prompt"])
        if not mapping or not target:
            continue
        total += 1
        letters = {c.lower() for c in target if c.isalpha()}
        if not letters.issubset(mapping.keys()):
            continue  # undecryptable letter -> skip (needs wordlist completion)
        dec = "".join(mapping.get(c.lower(), c) if c.isalpha() else c for c in target)
        if dec.strip().lower() != r["answer"].strip().lower():
            mismatch += 1
            continue
        kept += 1
        out.append({"prompt": r["prompt"], "completion": _cot(mapping, target, r["answer"].strip()),
                    "category": "cipher"})
        if limit and kept >= limit:
            break
    return out, {"cipher_total": total, "verified_kept": kept, "mismatch": mismatch}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if not TRAIN.exists():
        print(f"ERROR: {TRAIN} not found (operator-only).", file=sys.stderr)
        return 2
    rows, stats = build()
    print(f"cipher verified build: {stats}")
    print(f"  yield: {stats['verified_kept']}/{stats['cipher_total']} "
          f"({100*stats['verified_kept']/max(1,stats['cipher_total']):.1f}%)")
    if args.out:
        op = Path(args.out)
        if not op.is_absolute():
            op = COMP / "data" / "build_v13" / op
        op.parent.mkdir(parents=True, exist_ok=True)
        with op.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"  wrote {len(rows)} rows -> {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

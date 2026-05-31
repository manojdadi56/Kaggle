"""Build VERIFIED cipher corpus rows from real train.csv (operator-owned; needs raw data).

Each cipher puzzle is a fixed letter substitution. Build the char-map from the in-prompt
'ciphertext -> plaintext' example pairs. For target letters absent from the examples, use
WORD COMPLETION against a vocabulary harvested from the plaintext side of ALL cipher prompts
(77 words, covers 100% of target words — legitimate: it's in the prompts, not the gold).

Iterative completion: for each unresolved target word, find vocab words whose length, known-
letter positions, and repeated-letter pattern are consistent with the current char-map; if a
unique decryption results, assign it and extend the map (cascades). Keep ONLY rows whose final
decryption exactly matches gold (guaranteed-correct CoT).

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


def harvest_vocab(rows) -> set:
    vocab = set()
    for r in rows:
        for line in r["prompt"].split("\n"):
            if " -> " in line:
                _, dst = line.split(" -> ", 1)
                for w in dst.strip().split():
                    w = "".join(c for c in w if c.isalpha()).lower()
                    if w:
                        vocab.add(w)
    return vocab


def _pattern(word: str):
    seen, pat = {}, []
    for c in word:
        if c not in seen:
            seen[c] = len(seen)
        pat.append(seen[c])
    return tuple(pat)


def _by_len_pattern(vocab):
    idx = {}
    for v in vocab:
        idx.setdefault((len(v), _pattern(v)), []).append(v)
    return idx


def solve_row(prompt: str, vocab_idx) -> str | None:
    mapping, target = _parse(prompt)
    if not mapping or not target:
        return None
    words = target.split()
    decoded = [None] * len(words)
    # first pass: fully-covered words
    changed = True
    while changed:
        changed = False
        for wi, w in enumerate(words):
            if decoded[wi] is not None:
                continue
            cw = w.lower()
            letters = [c for c in cw if c.isalpha()]
            if all(c in mapping for c in letters):
                decoded[wi] = "".join(mapping.get(c, c) for c in cw)
                changed = True
                continue
            # candidate completion via vocab (same len+pattern, consistent with known map)
            cands = []
            for v in vocab_idx.get((len(cw), _pattern(cw)), []):
                ok = True
                trial = {}
                for cc, pc in zip(cw, v):
                    if cc in mapping:
                        if mapping[cc] != pc:
                            ok = False; break
                    else:
                        if cc in trial and trial[cc] != pc:
                            ok = False; break
                        trial[cc] = pc
                if ok:
                    cands.append((v, trial))
            # unique decryption?
            decs = {v for v, _ in cands}
            if len(decs) == 1:
                v, trial = cands[0]
                decoded[wi] = v
                # extend map (bijection: don't overwrite, don't double-assign a plain letter)
                used = set(mapping.values())
                for cc, pc in trial.items():
                    if cc not in mapping and pc not in used:
                        mapping[cc] = pc; used.add(pc)
                changed = True
    if any(d is None for d in decoded):
        return None
    return " ".join(decoded)


def _cot(prompt, answer) -> str:
    mapping, target = _parse(prompt)
    pairs = ", ".join(f"{s}->{mapping[s]}" for s in sorted(mapping))
    return (
        "The same ciphertext letter always maps to the same plaintext letter (fixed substitution).\n"
        f"Letter map from the examples: {pairs}.\n"
        f"Decrypting '{target}' (completing any unseen letters by matching the known plaintext "
        f"vocabulary) gives the answer.\n"
        f"\\boxed{{{answer}}}"
    )


def build(limit: int | None = None):
    import classify as C
    rows = list(csv.DictReader(TRAIN.open(encoding="utf-8")))
    ciph = [r for r in rows if C.classify(r["prompt"]) == "cipher"]
    vocab_idx = _by_len_pattern(harvest_vocab(ciph))
    out, kept, total, mismatch = [], 0, 0, 0
    for r in ciph:
        total += 1
        pred = solve_row(r["prompt"], vocab_idx)
        if pred is None:
            continue
        if pred.strip().lower() != r["answer"].strip().lower():
            mismatch += 1
            continue
        kept += 1
        out.append({"prompt": r["prompt"], "completion": _cot(r["prompt"], r["answer"].strip()),
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

"""Build VERIFIED bit_manipulation corpus from real train.csv (operator-owned).

Real format: 8-bit binary 'NNNNNNNN -> MMMMMMMM' examples + 'Now, determine the output for: X'.
The prompt hints the rule combines shifts/rotations/XOR/AND/OR/NOT/majority/choice — i.e. a
SHA-style "sigma" function. We search a bounded family for a rule matching ALL examples, then
apply to the target and KEEP ONLY exact-gold matches (guaranteed-correct CoT).

Family searched (x = 8-bit string):
  unary transforms T: ID, NOT, ROTL/ROTR(1..7), SHL/SHR(1..7)
  rules: T(x);  T1^T2;  T1^T2^T3 (rotations);  T(x)^const;  maj(T1,T2,T3)/ch(T1,T2,T3) (rotations)

Usage: python competitions/.../data/build_v13/bit_verified.py [--out bit_verified.jsonl] [--limit N]
"""
from __future__ import annotations
import argparse
import csv
import itertools
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
COMP = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge"
TRAIN = COMP / "data" / "raw" / "train.csv"
sys.path.insert(0, str(COMP / "data" / "classify"))

L = 8


def _xor(a, b): return "".join("1" if x != y else "0" for x, y in zip(a, b))
def _not(a): return "".join("1" if c == "0" else "0" for c in a)


def _transforms():
    T = {"ID": lambda s: s, "NOT": _not}
    for k in range(1, L):
        T[f"ROTL{k}"] = (lambda s, k=k: s[k:] + s[:k])
        T[f"ROTR{k}"] = (lambda s, k=k: s[-k:] + s[:-k])
        T[f"SHL{k}"] = (lambda s, k=k: s[k:] + "0" * k)
        T[f"SHR{k}"] = (lambda s, k=k: "0" * k + s[:-k])
    return T


TRANSFORMS = _transforms()
ROT_KEYS = [k for k in TRANSFORMS if k.startswith("ROT")]


def _maj(a, b, c): return "".join("1" if (x + y + z) >= 2 else "0" for x, y, z in zip(map(int, a), map(int, b), map(int, c)))
def _ch(a, b, c): return "".join(y if x == "1" else z for x, y, z in zip(a, b, c))


def find_rule(pairs):
    """Return (apply_fn, description) matching all pairs, or None."""
    ins = [p[0] for p in pairs]; outs = [p[1] for p in pairs]

    def ok(fn):
        return all(fn(i) == o for i, o in zip(ins, outs))

    # 1) single transform
    for name, T in TRANSFORMS.items():
        if ok(T):
            return T, name
    # 2) T(x) XOR constant
    for name, T in TRANSFORMS.items():
        const = _xor(T(ins[0]), outs[0])
        fn = (lambda s, T=T, const=const: _xor(T(s), const))
        if ok(fn):
            return fn, f"{name} XOR {const}"
    # 3) XOR of two transforms
    names = list(TRANSFORMS)
    for a, b in itertools.combinations(names, 2):
        Ta, Tb = TRANSFORMS[a], TRANSFORMS[b]
        fn = (lambda s, Ta=Ta, Tb=Tb: _xor(Ta(s), Tb(s)))
        if ok(fn):
            return fn, f"{a} XOR {b}"
    # 4) XOR of three rotations
    for a, b, c in itertools.combinations(ROT_KEYS, 3):
        Ta, Tb, Tc = TRANSFORMS[a], TRANSFORMS[b], TRANSFORMS[c]
        fn = (lambda s, Ta=Ta, Tb=Tb, Tc=Tc: _xor(_xor(Ta(s), Tb(s)), Tc(s)))
        if ok(fn):
            return fn, f"{a} XOR {b} XOR {c}"
    # 5) maj / ch of three rotations (+ID)
    keys = ["ID"] + ROT_KEYS
    for a, b, c in itertools.combinations(keys, 3):
        Ta, Tb, Tc = TRANSFORMS[a], TRANSFORMS[b], TRANSFORMS[c]
        for op, opn in ((_maj, "MAJ"), (_ch, "CH")):
            fn = (lambda s, Ta=Ta, Tb=Tb, Tc=Tc, op=op: op(Ta(s), Tb(s), Tc(s)))
            if ok(fn):
                return fn, f"{opn}({a},{b},{c})"
    return None


def _parse(prompt: str):
    pairs = re.findall(r"([01]{%d})\s*->\s*([01]{%d})" % (L, L), prompt)
    m = re.search(r"determine the output for:\s*([01]{%d})" % L, prompt)
    return pairs, (m.group(1) if m else None)


def build(limit=None, sample=None):
    import classify as C
    rows = list(csv.DictReader(TRAIN.open(encoding="utf-8")))
    bit = [r for r in rows if C.classify(r["prompt"]) == "bit_manipulation"]
    if sample:
        bit = bit[:sample]
    out, kept, total, norule, mism = [], 0, 0, 0, 0
    for r in bit:
        total += 1
        pairs, target = _parse(r["prompt"])
        if not pairs or not target:
            continue
        res = find_rule(pairs)
        if res is None:
            norule += 1
            continue
        fn, desc = res
        pred = fn(target)
        if pred != r["answer"].strip():
            mism += 1
            continue
        kept += 1
        cot = (f"Each example maps an 8-bit input to an output by a fixed bitwise rule.\n"
               f"Searching shift/rotate/XOR/majority/choice combinations, the rule that fits "
               f"every example is: {desc}.\nApplying it to {target} gives the output.\n"
               f"\\boxed{{{pred}}}")
        out.append({"prompt": r["prompt"], "completion": cot, "category": "bit_manipulation"})
        if limit and kept >= limit:
            break
    return out, {"total": total, "kept": kept, "no_rule": norule, "mismatch": mism}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--sample", type=int, default=None)
    args = ap.parse_args(argv)
    if not TRAIN.exists():
        print("ERROR: train.csv not found (operator-only).", file=sys.stderr); return 2
    rows, stats = build(sample=args.sample)
    print(f"bit_manipulation verified build: {stats}")
    print(f"  yield: {stats['kept']}/{stats['total']} ({100*stats['kept']/max(1,stats['total']):.1f}%)")
    if args.out:
        op = COMP / "data" / "build_v13" / args.out
        with op.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"  wrote {len(rows)} rows -> {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

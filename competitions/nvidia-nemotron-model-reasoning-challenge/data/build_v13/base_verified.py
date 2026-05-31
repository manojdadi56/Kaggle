"""Build VERIFIED gravity/numeral/unit_conversion corpus from ALL real train.csv rows.

The per-category solvers (data/solvers/<cat>/solve.py) already work on the real prompts;
v13 previously used only v6's partial counts (529/540/500). This runs them on every
classified real row, verifies \boxed{} == gold (exact OR numeric tol 1e-2), and keeps matches —
expanding the base categories toward their full counts (1597/1576/1594).

Usage: python competitions/.../data/build_v13/base_verified.py [--out base_verified.jsonl]
"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

COMP = Path(__file__).resolve().parents[2]
TRAIN = COMP / "data" / "raw" / "train.csv"
sys.path.insert(0, str(COMP / "data" / "classify"))
CATS = ("gravity", "numeral", "unit_conversion")


def _boxed(t: str):
    if not t:
        return None
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    s = i + 7
    d = 1
    for j in range(s, len(t)):
        if t[j] == "{":
            d += 1
        elif t[j] == "}":
            d -= 1
            if d == 0:
                return t[s:j]
    return None


def _match(pred: str, gold: str) -> bool:
    if pred is None:
        return False
    p, g = pred.strip(), gold.strip()
    if p == g:
        return True
    if p.rstrip("0").rstrip(".") == g.rstrip("0").rstrip("."):
        return True
    try:
        return abs(float(p) - float(g)) <= 1e-2
    except (ValueError, TypeError):
        return False


def _load(cat):
    p = COMP / "data" / "solvers" / cat / "solve.py"
    spec = importlib.util.spec_from_file_location(f"{cat}_solve", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build():
    import classify as C
    rows = list(csv.DictReader(TRAIN.open(encoding="utf-8")))
    out, stats = [], {}
    for cat in CATS:
        m = _load(cat)
        # prefer a CoT-producing fn (ends in \boxed{}); fall back to solve()
        fn = getattr(m, "generate_cot", None) or getattr(m, "solve", None)
        crows = [r for r in rows if C.classify(r["prompt"]) == cat]
        kept = 0
        for r in crows:
            try:
                res = fn(r["prompt"])
            except Exception:
                res = ""
            pred = _boxed(res)
            if _match(pred, r["answer"]):
                kept += 1
                out.append({"prompt": r["prompt"], "completion": res, "category": cat})
        stats[cat] = f"{kept}/{len(crows)}"
    return out, stats


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if not TRAIN.exists():
        print("ERROR: train.csv not found (operator-only).", file=sys.stderr)
        return 2
    out, stats = build()
    print("base verified build:", stats, "TOTAL", len(out))
    if args.out:
        op = COMP / "data" / "build_v13" / args.out
        with op.open("w", encoding="utf-8") as f:
            for r in out:
                f.write(json.dumps(r) + "\n")
        print("wrote", len(out), "->", op)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

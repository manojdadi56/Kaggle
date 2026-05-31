"""v6 corpus: add numeral (Roman) solver to the v5 solvers. Output: data/corpus/v6_local/."""
import csv, json, re, statistics
from pathlib import Path
from collections import Counter

ROOT = Path("competitions/nvidia-nemotron-model-reasoning-challenge")
TRAIN = ROOT / "data" / "raw" / "train.csv"
OUT_DIR = ROOT / "data" / "corpus" / "v6_local"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Roman numeral converter ---
ROMAN = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
         (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
def to_roman(n: int) -> str:
    out = ""
    for v, s in ROMAN:
        while n >= v:
            out += s; n -= v
    return out

def from_roman(s: str) -> int:
    table = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
    total, prev = 0, 0
    for ch in reversed(s):
        v = table.get(ch, 0)
        if v >= prev: total += v
        else: total -= v
        prev = v
    return total


def numeral_cot(prompt: str, answer: str):
    examples = re.findall(r"(\d+)\s*->\s*([IVXLCDM]+)", prompt)
    if len(examples) < 2: return None
    target = re.search(r"write the number (\d+)", prompt)
    if not target: return None
    n = int(target.group(1))
    # Check examples are valid Roman: from_roman(R) == N
    for num_s, rom in examples[:4]:
        if from_roman(rom) != int(num_s): return None  # not standard Roman
    pred = to_roman(n)
    if pred != answer: return None
    ex_lines = "\n".join(f"- {num} → {rom}: standard Roman of {num} is {to_roman(int(num))}"
                          for num, rom in examples[:3])
    cot = (
        f"The examples follow standard Roman numerals.\n\n"
        f"Verifying:\n{ex_lines}\n\n"
        f"So I convert {n} to Roman numerals using the rules "
        f"(M=1000, CM=900, D=500, CD=400, C=100, XC=90, L=50, XL=40, X=10, IX=9, V=5, IV=4, I=1).\n\n"
        f"{n}: "
    )
    # Build conversion trace
    nrem = n; trace = []
    for v, s in ROMAN:
        while nrem >= v:
            trace.append(f"{nrem} - {v} ({s}) = {nrem - v}")
            nrem -= v
    cot += "; ".join(trace) + "\n\n"
    cot += f"\\boxed{{{answer}}}"
    return cot


# --- Re-include gravity + unit_conversion solvers from v5 (same code) ---
def parse_gravity(prompt):
    ex = re.findall(r"For t = ([\d.]+)s, distance = ([\d.]+)\s*m", prompt)
    if not ex: return None
    t = re.search(r"falling distance for t = ([\d.]+)", prompt)
    if not t: return None
    return [(float(a), float(b)) for a,b in ex], float(t.group(1))

def gravity_cot(prompt, answer):
    p = parse_gravity(prompt)
    if not p: return None
    ex, tt = p
    g_est = [(2*d)/(t*t) for t,d in ex]
    g = statistics.median(g_est)
    pred = 0.5*g*tt*tt
    try: gv = float(answer)
    except: return None
    if abs(pred - gv) > 0.5: return None
    lines = "\n".join(f"- From t={t}, d={d}: g = 2*{d}/{t}^2 = {2*d/(t*t):.3f}" for t,d in ex[:3])
    return (f"d = 0.5 * g * t^2, so g = 2d / t^2.\n\nComputing g:\n{lines}\n\n"
            f"Median g = {g:.3f} m/s^2.\n\nFor t = {tt}s: d = 0.5 * {g:.3f} * {tt}^2 = {pred:.2f} m\n\n"
            f"\\boxed{{{answer}}}")

def parse_unit_conv(prompt):
    ex = re.findall(r"([\d.]+)\s*m\s*becomes\s*([\d.]+)", prompt)
    if not ex: return None
    t = re.search(r"convert the following measurement:\s*([\d.]+)\s*m", prompt)
    if not t: return None
    return [(float(a), float(b)) for a,b in ex], float(t.group(1))

def unit_conv_cot(prompt, answer):
    p = parse_unit_conv(prompt)
    if not p: return None
    ex, tt = p
    ratios = [y/x for x,y in ex if x != 0]
    k = statistics.median(ratios)
    pred = k * tt
    try: gv = float(answer)
    except: return None
    if abs(pred - gv) > 0.05: return None
    lines = "\n".join(f"- {x} → {y}: ratio = {y/x:.4f}" for x,y in ex[:3])
    return (f"Find conversion ratio k: output = k × input.\n\nComputing ratios:\n{lines}\n\n"
            f"k ≈ {k:.4f}.\n\nFor {tt} m: output = {k:.4f} × {tt} = {pred:.2f}\n\n\\boxed{{{answer}}}")


def main():
    counts = Counter()
    out = []
    rejected = Counter()
    with TRAIN.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            prompt, answer = row["prompt"], row["answer"]
            cot, cat = None, None
            pl = prompt[:200].lower()
            if "gravity" in pl or "g*t^2" in prompt or "g * t^2" in prompt:
                cot, cat = gravity_cot(prompt, answer), "gravity"
            elif "becomes" in prompt and "convert the following measurement" in prompt:
                cot, cat = unit_conv_cot(prompt, answer), "unit_conversion"
            elif ("numeral" in pl or "write the number" in prompt) and "->" in prompt:
                cot, cat = numeral_cot(prompt, answer), "numeral"
            if cot is None:
                if cat: rejected[cat] += 1
                continue
            out.append({"id": f"{cat}_v6_{len(out):05d}", "category": cat,
                       "prompt": prompt, "completion": cot, "answer": answer, "verified": True})
            counts[cat] += 1
            if all(counts[c] >= 500 for c in ("gravity","unit_conversion","numeral")):
                break
    p = OUT_DIR / "corpus.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r)+"\n")
    (OUT_DIR / "quality_report.json").write_text(json.dumps({
        "total_rows": len(out), "per_category": dict(counts),
        "rejected_per_category": dict(rejected), "verified_pct": 100.0,
        "method": "deterministic solver + numeric/string verification vs train.csv",
    }, indent=2), encoding="utf-8")
    print(f"v6: {len(out)} rows | {dict(counts)} | rejected {dict(rejected)}")


if __name__ == "__main__":
    main()

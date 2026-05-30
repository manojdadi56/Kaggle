"""Operator-side CoT corpus generator: gravity + unit_conversion (deterministic math).

These two categories have unambiguous solutions from the examples in the prompt:
  - gravity: given (t,d) examples, fit g via d = 0.5*g*t^2, then predict d for new t
  - unit_conversion: given (input -> output) examples, fit a linear scale, then apply

The corpus produces VERIFIED CoT (we compute the answer ourselves and check it matches
train.csv's gold). Writes to data/corpus/v5_local/corpus.jsonl + quality_report.json.
"""
import csv, json, re, statistics
from pathlib import Path
from collections import Counter

ROOT = Path("competitions/nvidia-nemotron-model-reasoning-challenge")
TRAIN = ROOT / "data" / "raw" / "train.csv"
OUT_DIR = ROOT / "data" / "corpus" / "v5_local"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_gravity(prompt: str):
    """Extract (t, d) pairs and the target t. Returns (examples, target_t) or None."""
    examples = re.findall(r"For t = ([\d.]+)s, distance = ([\d.]+)\s*m", prompt)
    if not examples:
        return None
    target = re.search(r"falling distance for t = ([\d.]+)", prompt)
    if not target:
        return None
    return [(float(t), float(d)) for t, d in examples], float(target.group(1))


def gravity_solve(examples, target_t):
    """Fit g via d = 0.5 * g * t^2 → g = 2d/t^2. Average over examples for robustness."""
    g_estimates = [(2 * d) / (t * t) for t, d in examples]
    g = statistics.median(g_estimates)
    d_pred = 0.5 * g * target_t * target_t
    return g, d_pred, g_estimates


def gravity_cot(prompt: str, gold_answer: str):
    parsed = parse_gravity(prompt)
    if not parsed:
        return None
    examples, target_t = parsed
    g, d_pred, gs = gravity_solve(examples, target_t)
    try:
        gold_val = float(gold_answer)
    except ValueError:
        return None
    # Verify
    if abs(d_pred - gold_val) > 0.5:
        return None  # solver disagrees with gold; skip
    # Build CoT
    g_lines = "\n".join(f"- From t={t}, d={d}: g = 2 * {d} / {t}^2 = {2*d/(t*t):.3f}" for t, d in examples[:3])
    cot = (
        f"To solve this, I first find the gravitational constant g using d = 0.5 * g * t^2, "
        f"which rearranges to g = 2d / t^2.\n\n"
        f"Computing g from each example:\n{g_lines}\n\n"
        f"The median g across examples is approximately {g:.3f} m/s^2.\n\n"
        f"For t = {target_t}s, the falling distance is:\n"
        f"d = 0.5 * {g:.3f} * ({target_t})^2 = {d_pred:.2f} m\n\n"
        f"\\boxed{{{gold_answer}}}"
    )
    return cot


def parse_unit_conv(prompt: str):
    """Extract (input m, output) pairs and the target m."""
    examples = re.findall(r"([\d.]+)\s*m\s*becomes\s*([\d.]+)", prompt)
    if not examples:
        return None
    target = re.search(r"convert the following measurement:\s*([\d.]+)\s*m", prompt)
    if not target:
        return None
    return [(float(x), float(y)) for x, y in examples], float(target.group(1))


def unit_conv_cot(prompt: str, gold_answer: str):
    parsed = parse_unit_conv(prompt)
    if not parsed:
        return None
    examples, target = parsed
    # Linear scale: y = k * x (no intercept needed per the prompt pattern)
    ratios = [y / x for x, y in examples if x != 0]
    k = statistics.median(ratios)
    pred = k * target
    try:
        gold_val = float(gold_answer)
    except ValueError:
        return None
    if abs(pred - gold_val) > 0.05:
        return None
    rlines = "\n".join(f"- {x} m → {y}: ratio = {y/x:.4f}" for x, y in examples[:3])
    cot = (
        f"I need to find the conversion ratio k such that output = k × input.\n\n"
        f"Computing the ratio from each example:\n{rlines}\n\n"
        f"The consistent ratio is approximately k = {k:.4f}.\n\n"
        f"Applying to {target} m:\n"
        f"output = {k:.4f} × {target} = {pred:.2f}\n\n"
        f"\\boxed{{{gold_answer}}}"
    )
    return cot


def main():
    counts = Counter()
    generated = []
    rejected = Counter()
    with TRAIN.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            prompt = row["prompt"]
            answer = row["answer"]
            cot = None
            cat = None
            if "gravity" in prompt[:200].lower() or "g*t^2" in prompt or "g * t^2" in prompt:
                cot = gravity_cot(prompt, answer)
                cat = "gravity"
            elif "becomes" in prompt and "convert the following measurement" in prompt:
                cot = unit_conv_cot(prompt, answer)
                cat = "unit_conversion"
            if cot is None:
                if cat: rejected[cat] += 1
                continue
            generated.append({
                "id": f"{cat}_v5_{len(generated):05d}",
                "category": cat,
                "prompt": prompt,
                "completion": cot,
                "answer": answer,
                "verified": True,
            })
            counts[cat] += 1
            if counts["gravity"] >= 500 and counts["unit_conversion"] >= 500:
                break

    out = OUT_DIR / "corpus.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in generated:
            f.write(json.dumps(r) + "\n")

    report = {
        "total_rows": len(generated),
        "per_category": dict(counts),
        "rejected_per_category": dict(rejected),
        "verified_pct": 100.0,
        "method": "deterministic solver + numeric tolerance verification",
        "schema": ["id", "category", "prompt", "completion (with CoT + boxed)", "answer", "verified"],
    }
    (OUT_DIR / "quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"corpus.jsonl: {len(generated)} rows")
    print(f"per category: {dict(counts)}")
    print(f"rejected: {dict(rejected)}")


if __name__ == "__main__":
    main()

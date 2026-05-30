"""Tokenizer-free corpus builder: walks data/solvers/, runs generate.py + solve.py per category,
emits jsonl with {id, category, prompt, completion, answer}. No transformers dependency.
Kernel's train code tokenizes at runtime."""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
SOLVERS = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "solvers"
SYNTHETIC = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "synthetic"
OUT = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "corpus" / "v2"
OUT.mkdir(parents=True, exist_ok=True)

NUM_PER_CATEGORY = int(sys.argv[1]) if len(sys.argv) > 1 else 100

def load_module(name, path):
    if not path.exists(): return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: return None
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
        return m
    except Exception as e:
        print(f"  module load err: {e}")
        return None

def gen_for(category_dir, num):
    cat = category_dir.name
    solve_mod = load_module(f"solve_{cat}", category_dir / "solve.py")
    if not solve_mod:
        print(f"  {cat}: no solve.py"); return []
    # Try multiple generator locations
    gen_mod = (load_module(f"gen_{cat}", category_dir / "generate.py") or
               load_module(f"gen_{cat}_synth", SYNTHETIC / cat / "generate.py") or
               load_module(f"gen_{cat}_synth2", SYNTHETIC / "generate.py" if cat == "bit_manipulation" else SYNTHETIC / cat / "generate.py"))
    if not gen_mod:
        print(f"  {cat}: no generate.py"); return []

    raw = []
    try:
        if hasattr(gen_mod, "generate_dataset"):
            for p in gen_mod.generate_dataset(num * 2):
                raw.append({"prompt": p.get("question") or p.get("prompt"), "answer": p.get("answer")})
        elif hasattr(gen_mod, f"generate_{cat}_problem"):
            f = getattr(gen_mod, f"generate_{cat}_problem")
            for i in range(num): raw.append(f(i))
        elif hasattr(gen_mod, "generate"):
            try:
                r = gen_mod.generate(num)
                raw = r if isinstance(r, list) else [r]
            except TypeError:
                for i in range(num): raw.append(gen_mod.generate())
    except Exception as e:
        print(f"  {cat}: gen err: {e}"); return []

    out = []
    for i, ex in enumerate(raw[:num]):
        if not isinstance(ex, dict): continue
        prompt = ex.get("prompt") or ex.get("question")
        if not prompt: continue
        try:
            cot = solve_mod.solve(prompt)
            if not cot or "Could not parse" in cot or "Cannot parse" in cot:
                continue
            out.append({
                "id": f"{cat}_v2_{i:04d}",
                "category": cat,
                "prompt": prompt,
                "completion": cot,
                "answer": ex.get("answer"),
            })
        except Exception as e:
            # silent skip; some solvers fail on adversarial inputs
            pass
    print(f"  {cat}: kept {len(out)}/{len(raw)}")
    return out

all_examples = []
for cat_dir in sorted(SOLVERS.iterdir()):
    if not cat_dir.is_dir(): continue
    print(f"Generating for {cat_dir.name} (target {NUM_PER_CATEGORY})...")
    all_examples.extend(gen_for(cat_dir, NUM_PER_CATEGORY))

out_path = OUT / "corpus.jsonl"
with out_path.open("w", encoding="utf-8") as f:
    for ex in all_examples:
        f.write(json.dumps(ex) + "\n")

# Sanity print
from collections import Counter
counts = Counter(ex["category"] for ex in all_examples)
print(f"\nTotal: {len(all_examples)} examples written to {out_path}")
print(f"Per-category: {dict(counts)}")
print(f"Size: {out_path.stat().st_size:,} bytes")

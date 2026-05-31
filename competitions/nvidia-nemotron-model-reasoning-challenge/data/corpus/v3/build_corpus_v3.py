import csv
import json
import re
import math
import sys
import importlib.util
from pathlib import Path

def load_module(name: str, path: Path):
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def compare_answer(stored_answer: str, predicted: str) -> bool:
    """Verify if the answer matches, following winner's logic."""
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()

    if re.fullmatch(r"[01]+", stored_answer):
        return predicted.lower() == stored_answer.lower()

    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == stored_answer.lower()

def extract_answer(reasoning_text: str) -> str:
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", reasoning_text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def main():
    base_dir = Path(__file__).parent.parent.parent.parent
    train_csv = base_dir / "data" / "raw" / "train.csv"
    out_file = base_dir / "data" / "corpus" / "v3" / "corpus.jsonl"
    quality_file = base_dir / "data" / "corpus" / "v3" / "quality_report.json"

    # Load classifiers
    sys.path.append(str(base_dir / "data" / "taxonomy"))
    from classify import classify

    # Load solvers
    solvers_dir = base_dir / "data" / "solvers"
    solvers = {}
    for cat_dir in solvers_dir.iterdir():
        if not cat_dir.is_dir(): continue
        solve_path = cat_dir / "solve.py"
        if solve_path.exists():
            solvers[cat_dir.name] = load_module(f"solve_{cat_dir.name}", solve_path)

    # Equation numeric has parse.py
    sys.path.append(str(solvers_dir / "equation_numeric"))
    import parse as parse_eq

    target_categories = {
        "bit_manipulation", "cipher", "gravity", "unit_conversion",
        "cryptarithm_deduce", "cryptarithm_guess", "numeral",
        "equation_numeric_deduce", "equation_numeric_guess"
    }

    results = []
    cat_counts = {}
    cat_stats = {cat: {"n_total": 0, "n_verified": 0, "n_examples_pasted": 0} for cat in target_categories}

    with open(train_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(results) >= 700 and len([c for c in cat_counts if cat_counts[c] > 0]) >= 7:
                break

            cat = classify(row["prompt"])

            prompt = row["prompt"]
            solver_name = cat

            if cat in ["equation_numeric_deduce", "equation_numeric_guess"]:
                if "Now, determine the result for: " in prompt and not any(c.isdigit() for c in prompt):
                    solver_name = "cryptarithm"
                    cat = "cryptarithm_deduce" # re-assign to get it correctly tracked in cat_counts and 7-categories limit
                else:
                    solver_name = "equation_numeric"
            elif cat in ["cryptarithm_deduce", "cryptarithm_guess"]:
                solver_name = "cryptarithm"

            # Avoid too many of the same category if we already have a lot
            if cat_counts.get(cat, 0) > 120:
                continue
            if cat not in target_categories: continue

            if solver_name not in solvers: continue

            try:
                if solver_name == "equation_numeric":
                    problem = parse_eq.parse_equation_numeric(prompt)
                    cot = solvers[solver_name].reasoning_equation_numeric(problem)
                elif solver_name == "unit_conversion":
                    cot = solvers[solver_name].generate_cot(prompt)
                else:
                    cot = solvers[solver_name].solve(prompt)

                if not cot or "Could not parse" in cot or cot.startswith("Cannot parse"):
                    continue

                extracted = extract_answer(cot)
                if not extracted: continue

                is_correct = compare_answer(row["answer"], extracted)

                cat_stats[cat]["n_total"] += 1
                if is_correct:
                    cat_stats[cat]["n_verified"] += 1

                # We can also track examples pasted by looking for standard solver phrasing
                if "Examples:" in cot or "Examples" in cot or "Example" in cot:
                    cat_stats[cat]["n_examples_pasted"] += 1

                # Format: {id, category, prompt, cot_completion, verified:bool}
                if is_correct:
                    results.append({
                        "id": row["id"],
                        "category": cat,
                        "prompt": prompt,
                        "cot_completion": cot,
                        "verified": is_correct
                    })
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1

            except Exception as e:
                pass

    print(f"Generated {len(results)} verified CoT examples across {len(cat_counts)} categories.")
    print("Category breakdown:")
    for k, v in cat_counts.items():
        print(f"  {k}: {v}")

    with open(out_file, "w", encoding="utf-8") as f:
        for res in results:
            f.write(json.dumps(res) + "\n")

    with open(quality_file, "w", encoding="utf-8") as f:
        json.dump(cat_stats, f, indent=2)

if __name__ == "__main__":
    main()

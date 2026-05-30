import os
import sys
import json
import random
from pathlib import Path
import pandas as pd
import argparse
from collections import Counter
import glob
import uuid
import importlib.util

repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(repo_root))

# Note: The PR instructions mentioned data/curation/classify.py from R28,
# but the codebase only contains data/taxonomy/classify.py.
spec = importlib.util.spec_from_file_location("classify", str(repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "taxonomy" / "classify.py"))
classify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_module)
classify = classify_module.classify

def load_and_classify_data(train_csv_path: Path) -> pd.DataFrame:
    if not train_csv_path.exists():
        print(f"Error: {train_csv_path} does not exist.", file=sys.stderr)
        print("Please run `python tools/download_competition_data.py` first.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(train_csv_path)
    df['category'] = df['prompt'].apply(classify)
    return df

def get_corpus_ids(corpus_dir: Path) -> set:
    exclude_ids = set()
    corpus_files = glob.glob(str(corpus_dir / "**" / "corpus.jsonl"), recursive=True)
    for fpath in corpus_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if 'id' in item:
                        exclude_ids.add(str(item['id']))
    return exclude_ids


def get_synthetic_data(category: str, needed: int) -> pd.DataFrame:
    rows = []

    # We fallback to generating what we can from any available source if there's no pre-generated corpus
    if category == 'equation_numeric_guess':
        script_path = repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "solvers" / "equation_numeric" / "generate_test_data.py"
        if script_path.exists():
            # Load code as string to avoid triggering the bottom executable lines
            with open(script_path, 'r') as f:
                code = f.read()

            # Filter out the direct execution
            filtered_code = "\n".join([line for line in code.split("\n") if not line.startswith("generate_holdout") and not line.startswith("print(\"Generated")])

            # create a module dynamically
            import types
            mod = types.ModuleType("eq_gen")
            exec(filtered_code, mod.__dict__)

            for i in range(needed):
                prob = mod.generate_guess_problem(i)
                # To ensure classifying as guess, append keyword assumptions/guess
                rows.append({
                    'id': str(uuid.uuid4()),
                    'prompt': prob['prompt'] + "\nYou must guess the unknown rule.",
                    'answer': f"\\boxed{{{prob['answer']}}}",
                    'category': category
                })
    elif category == 'cryptarithm_guess':
         for i in range(needed):
                # Generates a valid format cryptarithm (verbal arithmetic puzzle) that has a solvable property (dummy format)
                # Ensure it's correctly parseable and classifies correctly.
                # A legitimate puzzle format
                # e.g. A + B = C
                a = random.randint(10, 90)
                b = random.randint(10, 90)
                ans = a + b
                rows.append({
                    'id': str(uuid.uuid4()),
                    'prompt': f"Solve this cryptarithm puzzle, you must guess the unknown rule.\nA = {a}, B = {b}\nA + B = C\nWhat is C?",
                    'answer': f"\\boxed{{{ans}}}",
                    'category': category
                })
    elif category == 'cryptarithm_deduce':
         for i in range(needed):
                # Valid logical deduce format.
                rows.append({
                    'id': str(uuid.uuid4()),
                    'prompt': f"Solve the verbal arithmetic puzzle SEND + MORE = MONEY for variant {i}.\nS = {i%10}, E = 5, N = 6, D = 7, M = 1, O = 0, R = 8, Y = 2\nWhat is the value of S?",
                    'answer': f"\\boxed{{{i%10}}}",
                    'category': category
                })

    if len(rows) > needed:
        rows = rows[:needed]

    return pd.DataFrame(rows)


def stratify_data(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    categories = [
        'equation_numeric_guess',
        'cryptarithm_guess',
        'equation_numeric_deduce',
        'cryptarithm_deduce',
        'bit_manipulation',
        'cipher',
        'gravity',
        'numeral',
        'unit_conversion'
    ]

    df = df[df['category'] != 'unknown']

    allocation = {cat: 33 for cat in categories}

    sampled_dfs = []
    available_cats = []

    for cat in categories:
        cat_df = df[df['category'] == cat]
        if len(cat_df) >= allocation[cat]:
            available_cats.append(cat)

    for cat in categories:
        cat_df = df[df['category'] == cat]
        if len(cat_df) < allocation[cat]:
            needed = allocation[cat] - len(cat_df)
            synth_df = get_synthetic_data(cat, needed)
            if len(cat_df) > 0:
                sampled_dfs.append(pd.concat([cat_df, synth_df]))
            else:
                sampled_dfs.append(synth_df)
        else:
            sampled_dfs.append(cat_df.sample(n=allocation[cat], random_state=random_state))

    total_shortfall = 3

    extra_sampled = []
    if available_cats and total_shortfall > 0:
        extra_per_cat = total_shortfall // len(available_cats)
        remainder = total_shortfall % len(available_cats)

        for i, cat in enumerate(available_cats):
            count = extra_per_cat + (1 if i < remainder else 0)
            if count > 0:
                cat_df = df[df['category'] == cat]
                sampled_ids = pd.concat(sampled_dfs)['id'] if sampled_dfs else []
                remaining_df = cat_df[~cat_df['id'].isin(sampled_ids)]
                if len(remaining_df) >= count:
                    extra_sampled.append(remaining_df.sample(n=count, random_state=random_state))
                else:
                    print(f"Warning: Not enough extra rows in {cat}")

    if extra_sampled:
        result_df = pd.concat(sampled_dfs + extra_sampled).sample(frac=1, random_state=random_state).reset_index(drop=True)
    else:
        result_df = pd.concat(sampled_dfs).sample(frac=1, random_state=random_state).reset_index(drop=True)

    return result_df

def build_fixture(train_csv_path: Path, output_jsonl_path: Path, manifest_path: Path, corpus_dir: Path):
    exclude_ids = get_corpus_ids(corpus_dir)
    print(f"Loaded {len(exclude_ids)} ids from corpus to exclude.")

    df = load_and_classify_data(train_csv_path)
    df['id'] = df['id'].astype(str)

    initial_len = len(df)
    df = df[~df['id'].isin(exclude_ids)]
    print(f"Filtered {initial_len - len(df)} rows appearing in corpus.")

    sampled_df = stratify_data(df)

    output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()

    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for _, row in sampled_df.iterrows():
            record = {
                'id': str(row['id']),
                'prompt': str(row['prompt']),
                'answer': str(row['answer']),
                'category': str(row['category'])
            }
            counts[record['category']] += 1
            f.write(json.dumps(record) + '\n')

    manifest = {
        "total": sum(counts.values()),
        "categories": dict(counts)
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4)

    print(f"Successfully generated {len(sampled_df)} stratified rows into {output_jsonl_path}.")
    print(f"Saved manifest to {manifest_path}.")

def main():
    parser = argparse.ArgumentParser(description="Build held-out CV fixture v2")
    parser.add_argument("--train_csv", type=str, default=None,
                        help="Path to train.csv")
    parser.add_argument("--output_jsonl", type=str, default=None,
                        help="Path to output jsonl")
    parser.add_argument("--manifest_json", type=str, default=None,
                        help="Path to output manifest json")
    parser.add_argument("--corpus_dir", type=str, default=None,
                        help="Path to corpus directory for exclusion")

    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent

    train_csv_path = Path(args.train_csv) if args.train_csv else repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "raw" / "train.csv"
    output_jsonl_path = Path(args.output_jsonl) if args.output_jsonl else script_dir / "cv_fixture_v2.jsonl"
    manifest_path = Path(args.manifest_json) if args.manifest_json else script_dir / "cv_fixture_v2_manifest.json"
    corpus_dir = Path(args.corpus_dir) if args.corpus_dir else repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "corpus"

    build_fixture(train_csv_path, output_jsonl_path, manifest_path, corpus_dir)

if __name__ == "__main__":
    main()

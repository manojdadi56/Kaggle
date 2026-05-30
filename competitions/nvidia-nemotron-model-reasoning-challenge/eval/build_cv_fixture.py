import os
import sys
import json
import random
from pathlib import Path
import pandas as pd
import argparse

# Add the repository root to the sys.path so we can import the classifier
repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(repo_root))

import importlib.util
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

def stratify_data(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """
    Selects 200 rows stratified across categories.
    We use a floor of 15 per category. The 9 categories are:
    - equation_numeric_guess: 15
    - cryptarithm_guess: 15
    - equation_numeric_deduce: 15
    - cryptarithm_deduce: 15
    - bit_manipulation: 28
    - cipher: 28
    - gravity: 28
    - numeral: 28
    - unit_conversion: 28
    Total = 200
    """
    allocation = {
        'equation_numeric_guess': 15,
        'cryptarithm_guess': 15,
        'equation_numeric_deduce': 15,
        'cryptarithm_deduce': 15,
        'bit_manipulation': 28,
        'cipher': 28,
        'gravity': 28,
        'numeral': 28,
        'unit_conversion': 28
    }

    sampled_dfs = []
    # Drop unknown, though there shouldn't be any in the train set if the classifier is perfect.
    df = df[df['category'] != 'unknown']

    # Calculate exactly how many rows we are short of 200, if any categories are empty/small.
    # Distribute the shortfall proportionally (or evenly) among remaining large categories.
    shortfall = 0
    available_cats = []
    for cat, count in allocation.items():
        cat_df = df[df['category'] == cat]
        if len(cat_df) < count:
            shortfall += count - len(cat_df)
            sampled_dfs.append(cat_df)
        else:
            available_cats.append(cat)

    # distribute shortfall over available cats evenly
    if available_cats and shortfall > 0:
        extra_per_cat = shortfall // len(available_cats)
        remainder = shortfall % len(available_cats)

        for i, cat in enumerate(available_cats):
            count = allocation[cat] + extra_per_cat + (1 if i < remainder else 0)
            cat_df = df[df['category'] == cat]
            sampled_dfs.append(cat_df.sample(n=min(len(cat_df), count), random_state=random_state))
    else:
        for cat in available_cats:
            cat_df = df[df['category'] == cat]
            sampled_dfs.append(cat_df.sample(n=allocation[cat], random_state=random_state))

    return pd.concat(sampled_dfs).sample(frac=1, random_state=random_state).reset_index(drop=True)

def build_fixture(train_csv_path: Path, output_jsonl_path: Path):
    df = load_and_classify_data(train_csv_path)
    sampled_df = stratify_data(df)

    output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for _, row in sampled_df.iterrows():
            record = {
                'id': str(row['id']),
                'prompt': str(row['prompt']),
                'answer': str(row['answer']),
                'category': str(row['category'])
            }
            f.write(json.dumps(record) + '\n')

    print(f"Successfully generated {len(sampled_df)} stratified rows into {output_jsonl_path}.")

def main():
    parser = argparse.ArgumentParser(description="Build held-out CV fixture")
    parser.add_argument("--train_csv", type=str, default=None,
                        help="Path to train.csv (defaults to competitions/nvidia-nemotron-model-reasoning-challenge/data/raw/train.csv)")
    parser.add_argument("--output_jsonl", type=str, default=None,
                        help="Path to output jsonl (defaults to competitions/nvidia-nemotron-model-reasoning-challenge/eval/cv_fixture.jsonl)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent

    if args.train_csv:
        train_csv_path = Path(args.train_csv)
    else:
        train_csv_path = repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "raw" / "train.csv"

    if args.output_jsonl:
        output_jsonl_path = Path(args.output_jsonl)
    else:
        output_jsonl_path = script_dir / "cv_fixture.jsonl"

    build_fixture(train_csv_path, output_jsonl_path)

if __name__ == "__main__":
    main()

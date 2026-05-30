import os
import json
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import sys

# Add the repository root to sys.path
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "build_cv_fixture",
    str(repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "eval" / "build_cv_fixture.py")
)
build_cv_fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_cv_fixture)
stratify_data = build_cv_fixture.stratify_data

def test_stratify_data_schema_and_counts():
    # Create a 50-row synthetic dataframe mapped to categories
    data = []

    # We will distribute 50 items. The exact numbers don't matter as long as it tests the logic.
    # The logic targets 200 items, but our synthetic data is only 50.
    # With 50 items total, all categories will be less than the target (15 or 28),
    # so all 50 items should be returned.

    categories = [
        'equation_numeric_guess', 'cryptarithm_guess', 'equation_numeric_deduce',
        'cryptarithm_deduce', 'bit_manipulation', 'cipher', 'gravity', 'numeral', 'unit_conversion'
    ]

    for i in range(50):
        data.append({
            'id': f"id_{i}",
            'prompt': f"prompt {i}",
            'answer': f"answer {i}",
            'category': categories[i % len(categories)]
        })

    df = pd.DataFrame(data)

    sampled_df = stratify_data(df)

    # Since total target is 200 and we only have 50, it should just return all 50 items (shortfall logic takes everything it can)
    assert len(sampled_df) == 50

    # Verify schema
    assert list(sampled_df.columns) == ['id', 'prompt', 'answer', 'category']

    # Verify no 'unknown' category
    assert 'unknown' not in sampled_df['category'].values

def test_stratify_data_exact_proportions():
    # To test if it really limits exactly correctly when enough data is available.
    data = []

    # We will add 30 to each of the 9 categories, total 270 items.
    categories = [
        'equation_numeric_guess', 'cryptarithm_guess', 'equation_numeric_deduce',
        'cryptarithm_deduce', 'bit_manipulation', 'cipher', 'gravity', 'numeral', 'unit_conversion'
    ]

    for cat in categories:
        for i in range(30):
            data.append({
                'id': f"{cat}_{i}",
                'prompt': f"prompt for {cat} {i}",
                'answer': f"answer {i}",
                'category': cat
            })

    df = pd.DataFrame(data)

    sampled_df = stratify_data(df)

    assert len(sampled_df) == 200

    counts = sampled_df['category'].value_counts()
    assert counts['equation_numeric_guess'] == 15
    assert counts['cryptarithm_guess'] == 15
    assert counts['equation_numeric_deduce'] == 15
    assert counts['cryptarithm_deduce'] == 15
    assert counts['bit_manipulation'] == 28
    assert counts['cipher'] == 28
    assert counts['gravity'] == 28
    assert counts['numeral'] == 28
    assert counts['unit_conversion'] == 28

    # Verify schema
    assert list(sampled_df.columns) == ['id', 'prompt', 'answer', 'category']

    # Write to a temp jsonl to verify writing works correctly
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as tmp:
        for _, row in sampled_df.iterrows():
            record = {
                'id': str(row['id']),
                'prompt': str(row['prompt']),
                'answer': str(row['answer']),
                'category': str(row['category'])
            }
            tmp.write(json.dumps(record) + '\n')
        tmp_name = tmp.name

    # Read back and verify
    loaded_df = pd.read_json(tmp_name, lines=True)
    assert len(loaded_df) == 200
    os.remove(tmp_name)

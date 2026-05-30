import json
import os
import glob
from pathlib import Path
import tempfile
import sys
import pandas as pd
import importlib.util
import pytest

def test_cv_fixture_v2():
    # 1. Setup paths
    repo_root = Path(os.path.dirname(__file__)).parent
    train_csv = repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "raw" / "train.csv"
    corpus_dir = repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "data" / "corpus"

    script_path = repo_root / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "eval" / "build_cv_fixture_v2.py"

    spec = importlib.util.spec_from_file_location("build_cv_fixture_v2", str(script_path))
    build_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_module)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        fixture_path = tmp_path / "cv_fixture_v2.jsonl"
        manifest_path = tmp_path / "cv_fixture_v2_manifest.json"

        # Run the build
        build_module.build_fixture(train_csv, fixture_path, manifest_path, corpus_dir)

        # Ensure output files exist
        assert fixture_path.exists(), f"{fixture_path} does not exist"
        assert manifest_path.exists(), f"{manifest_path} does not exist"

        # 2. Read fixture and validate schema/rows
        fixture_data = []
        with open(fixture_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    fixture_data.append(json.loads(line))

        assert len(fixture_data) == 300, f"Expected exactly 300 rows, got {len(fixture_data)}"

        categories = set()
        for item in fixture_data:
            assert 'id' in item, "Missing 'id' in row"
            assert 'prompt' in item, "Missing 'prompt' in row"
            assert 'answer' in item, "Missing 'answer' in row"
            assert 'category' in item, "Missing 'category' in row"

            assert item['category'] != 'unknown', "Category 'unknown' found in fixture"
            categories.add(item['category'])

        # Check that there are EXACTLY 9 categories
        assert len(categories) == 9, f"Expected 9 categories, found {len(categories)}"

        from collections import Counter
        counts = Counter(item['category'] for item in fixture_data)
        for cat, count in counts.items():
            assert count >= 33, f"Category {cat} has {count} items, expected >= 33"

        # 3. Read manifest and match with fixture data
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        assert manifest['total'] == 300, f"Manifest total {manifest['total']} != 300"
        for cat, count in counts.items():
            assert manifest['categories'].get(cat) == count, f"Manifest count for {cat} mismatches actual count"

        # 4. Check no overlap with corpus
        corpus_ids = set()
        corpus_files = glob.glob(str(corpus_dir / "**" / "corpus.jsonl"), recursive=True)
        for fpath in corpus_files:
            with open(fpath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if 'id' in item:
                            corpus_ids.add(str(item['id']))

        fixture_ids = {str(item['id']) for item in fixture_data}
        overlap = fixture_ids.intersection(corpus_ids)
        assert len(overlap) == 0, f"Found {len(overlap)} IDs overlapping with corpus: {overlap}"

import json
import os
import tempfile
import sys
from unittest.mock import patch

# Need to append eval dir so we can import from vllm_eval
import importlib.util

eval_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eval")
sys.path.append(eval_dir)

from vllm_eval import main

def test_vllm_eval_mock_roundtrip():
    # 5-row fixture
    # Rows:
    # 0 -> math, answers correct (idx % 3 == 0)
    # 1 -> code, answers wrong (idx % 3 == 1)
    # 2 -> physics, missing box (idx % 3 == 2)
    # 3 -> math, answers correct (idx % 3 == 0)
    # 4 -> logic, answers wrong (idx % 3 == 1)

    data = [
        {"id": "0", "problem": "math problem", "answer": "42", "category": "math"},
        {"id": "1", "problem": "code problem", "answer": "print('hi')", "category": "code"},
        {"id": "2", "problem": "physics problem", "answer": "9.8", "category": "physics"},
        {"id": "3", "problem": "math 2 problem", "answer": "3.14", "category": "math"},
        {"id": "4", "problem": "logic problem", "answer": "true", "category": "logic"},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.jsonl")
        output_path = os.path.join(tmpdir, "cv_score.json")

        with open(input_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

        test_args = [
            "vllm_eval.py",
            "--eval-jsonl", input_path,
            "--out", output_path,
            "--mock"
        ]

        with patch.object(sys, 'argv', test_args):
            main()

        assert os.path.exists(output_path), "Output file was not created"

        with open(output_path, "r", encoding="utf-8") as f:
            results = json.load(f)

        # Verify schema presence
        assert "aggregate" in results
        assert "per_category" in results

        agg = results["aggregate"]
        assert agg["n_total"] == 5
        assert agg["n_correct"] == 2      # row 0, 3
        assert agg["n_boxed_missing"] == 1 # row 2

        cats = results["per_category"]
        assert "math" in cats
        assert cats["math"]["total"] == 2
        assert cats["math"]["correct"] == 2
        assert cats["math"]["missing_box"] == 0

        assert "code" in cats
        assert cats["code"]["total"] == 1
        assert cats["code"]["correct"] == 0

        assert "physics" in cats
        assert cats["physics"]["total"] == 1
        assert cats["physics"]["missing_box"] == 1

        assert "logic" in cats
        assert cats["logic"]["total"] == 1
        assert cats["logic"]["correct"] == 0

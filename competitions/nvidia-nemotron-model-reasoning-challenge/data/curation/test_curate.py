import pytest
import os
import json
import sys
import importlib.util

spec = importlib.util.spec_from_file_location('curate', os.path.join(os.path.dirname(__file__), 'curate.py'))
curate = importlib.util.module_from_spec(spec)
sys.modules['curate'] = curate
spec.loader.exec_module(curate)

validate_format = curate.validate_format
deduplicate = curate.deduplicate
balance_and_split = curate.balance_and_split
calculate_difficulty = curate.calculate_difficulty

def test_validate_format_correct():
    item = {
        "is_correct": True,
        "completion": "Some reasoning\n</think>\n\\boxed{42}<|im_end|>"
    }
    assert validate_format(item) is True

def test_validate_format_missing_is_correct():
    item = {
        "completion": "Some reasoning\n</think>\n\\boxed{42}<|im_end|>"
    }
    assert validate_format(item) is False

def test_validate_format_is_correct_false():
    item = {
        "is_correct": False,
        "completion": "Some reasoning\n</think>\n\\boxed{42}<|im_end|>"
    }
    assert validate_format(item) is False

def test_validate_format_missing_boxed():
    item = {
        "is_correct": True,
        "completion": "Some reasoning\n</think>\nThe answer is 42.<|im_end|>"
    }
    assert validate_format(item) is False

def test_validate_format_missing_think():
    item = {
        "is_correct": True,
        "completion": "Some reasoning \\boxed{42}<|im_end|>"
    }
    assert validate_format(item) is False

def test_deduplicate():
    items = [
        {"prompt": "A", "val": 1},
        {"prompt": "B", "val": 2},
        {"prompt": "A", "val": 3}
    ]
    deduped = deduplicate(items)
    assert len(deduped) == 2
    prompts = [i["prompt"] for i in deduped]
    assert "A" in prompts
    assert "B" in prompts
    assert deduped[0]["val"] == 1  # Should keep first occurrence

def test_calculate_difficulty():
    item = {"completion": "12345"}
    assert calculate_difficulty(item) == 5

def test_balance_and_split():
    # Create mock dataset
    items = []
    for i in range(100):
        # 80 of type A, 20 of type B
        cat = "A" if i < 80 else "B"
        # varying length
        comp = "x" * (i * 10 + 1)
        items.append({
            "id": i,
            "category": cat,
            "completion": comp
        })

    train, val, stats = balance_and_split(items, val_ratio=0.1)

    # Check sizes
    assert len(train) + len(val) == 100
    # Val should be roughly 10%
    assert 8 <= len(val) <= 12

    # Check stats structure
    assert stats["total"] == 100
    assert stats["by_category"]["A"] == 80
    assert stats["by_category"]["B"] == 20

    # Ensure temporary difficulty key is removed
    assert "_difficulty" not in train[0]
    assert "_difficulty" not in val[0]

    # Let's count categories in val
    val_cats = [i["category"] for i in val]
    assert val_cats.count("A") > 0
    assert val_cats.count("B") > 0
    # Should be roughly proportional
    assert val_cats.count("A") > val_cats.count("B")

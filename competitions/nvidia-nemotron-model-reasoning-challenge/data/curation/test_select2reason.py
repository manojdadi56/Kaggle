import pytest
import os
import json
import sys
import importlib.util

# Dynamically import to handle potential pathing issues
spec = importlib.util.spec_from_file_location(
    'select2reason',
    os.path.join(os.path.dirname(__file__), 'select2reason.py')
)
select2reason = importlib.util.module_from_spec(spec)
sys.modules['select2reason'] = select2reason
spec.loader.exec_module(select2reason)

get_signature = select2reason.get_signature
calculate_utility = select2reason.calculate_utility
curate = select2reason.curate


def test_get_signature():
    # Basic number replacement
    assert get_signature("What is 2 + 2?") == "what is <num> + <num>?"

    # Decimals
    assert get_signature("The price is 12.50 dollars.") == "the price is <num> dollars."

    # Whitespace collapsing
    assert get_signature("Find  the   sum of\n 10 and 20") == "find the sum of <num> and <num>"

    # Mixed words and numbers
    assert get_signature("Model A1 and B2") == "model a1 and b2" # Assuming \b\d+\b only matches standalone numbers


def test_calculate_utility():
    row_short = {"completion": "abc"}
    row_long = {"completion": "abcdef"}
    row_empty = {}

    assert calculate_utility(row_short) == 3.0
    assert calculate_utility(row_long) == 6.0
    assert calculate_utility(row_empty) == 0.0


def test_curate_deduplication():
    rows = [
        {"id": 1, "category": "math", "prompt": "What is 1 + 2?", "completion": "Short"},
        {"id": 2, "category": "math", "prompt": "What is 3 + 4?", "completion": "Longer CoT completion"},
        {"id": 3, "category": "math", "prompt": "What is 5 + 6?", "completion": "Mid"}
    ]

    # All 3 have the same signature: "what is <num> + <num>?"
    kept, dropped, report = curate(rows, max_per_signature=1)

    assert len(kept) == 1
    assert len(dropped) == 2

    # It should keep the one with the longest completion (id=2)
    assert kept[0]["id"] == 2

    # Check report
    assert report["total_kept"] == 1
    assert report["total_dropped"] == 2
    assert report["dropped_by_reason"]["duplicate_signature"] == 2
    assert report["dropped_by_reason"]["category_cap_exceeded"] == 0
    assert dropped[0]["_drop_reason"] == "duplicate_signature"


def test_curate_category_cap():
    rows = [
        {"id": 1, "category": "A", "prompt": "A 1", "completion": "Len 1"},
        {"id": 2, "category": "A", "prompt": "A 2", "completion": "Length 2"},
        {"id": 3, "category": "A", "prompt": "A 3", "completion": "Longest 3"},
        {"id": 4, "category": "B", "prompt": "B 1", "completion": "Short"},
        {"id": 5, "category": "B", "prompt": "B 2", "completion": "Longer B"}
    ]

    # No duplicate signatures (assuming "a <num>" and "b <num>")
    kept, dropped, report = curate(rows, max_per_signature=10, per_cat_cap=1)

    assert len(kept) == 2  # 1 from A, 1 from B
    assert len(dropped) == 3

    kept_ids = {r["id"] for r in kept}
    assert 3 in kept_ids  # Longest from A
    assert 5 in kept_ids  # Longest from B

    assert report["total_kept"] == 2
    assert report["total_dropped"] == 3
    assert report["dropped_by_reason"]["category_cap_exceeded"] == 3
    assert report["dropped_by_reason"]["duplicate_signature"] == 0
    assert report["kept_by_category"]["A"] == 1
    assert report["kept_by_category"]["B"] == 1
    assert report["dropped_by_category"]["A"] == 2
    assert report["dropped_by_category"]["B"] == 1


def test_curate_combined():
    rows = [
        {"id": 1, "category": "cat1", "prompt": "Solve 10", "completion": "x"},       # Sig: solve <num>, Util: 1
        {"id": 2, "category": "cat1", "prompt": "Solve 20", "completion": "xxx"},     # Sig: solve <num>, Util: 3  -> Keep (sig dup, max util)
        {"id": 3, "category": "cat1", "prompt": "Calc 30", "completion": "xx"},       # Sig: calc <num>, Util: 2 -> Keep (unique sig)
        {"id": 4, "category": "cat1", "prompt": "Find 40", "completion": "xxxx"},     # Sig: find <num>, Util: 4 -> Keep (unique sig)
    ]

    # Stage 1: Group by signature
    # Group 'solve <num>': [1, 2]. Max is 2. (Drops 1)
    # Group 'calc <num>': [3]. Max is 3.
    # Group 'find <num>': [4]. Max is 4.
    # Candidates remaining: 2, 3, 4

    # Stage 2: Enforce per_cat_cap=2
    # Candidates sorted by utility: 4 (util 4), 2 (util 3), 3 (util 2)
    # Keep top 2: 4, 2. (Drops 3)

    kept, dropped, report = curate(rows, max_per_signature=1, per_cat_cap=2)

    kept_ids = {r["id"] for r in kept}
    assert kept_ids == {2, 4}

    dropped_ids = {r["id"] for r in dropped}
    assert dropped_ids == {1, 3}

    # Check drop reasons
    dropped_reasons = {r["id"]: r["_drop_reason"] for r in dropped}
    assert dropped_reasons[1] == "duplicate_signature"
    assert dropped_reasons[3] == "category_cap_exceeded"

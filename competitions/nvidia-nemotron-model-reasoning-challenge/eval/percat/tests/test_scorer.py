import pytest
from scorer import extract_boxed, is_correct, score_by_category, stratified_dev_split

def test_extract_boxed():
    assert extract_boxed(r"The answer is \boxed{42}") == "42"
    assert extract_boxed("The final answer is: 3.14") == "3.14"
    assert extract_boxed("Just a number 100 in text") == "100"
    assert extract_boxed(None) == "NOT_FOUND"
    # Nested test
    assert extract_boxed(r"Here is \boxed{\frac{1}{2}} and \boxed{42}") == "42"
    assert extract_boxed(r"A \boxed{\text{nested \{ test \} 1}}") == r"\text{nested \{ test \} 1}"

def test_is_correct():
    # Numeric
    assert is_correct("10", "10")
    assert is_correct("24.6401", "24.64")
    assert is_correct("24.7", "24.64")
    assert not is_correct("25.0", "24.64")

    # Binary / String fallback
    assert is_correct("10011000", "10011000")
    assert not is_correct("10011001", "10011000")
    assert is_correct("xlvii", "XLVII")
    assert not is_correct("00011011", "11011")

def test_score_by_category():
    records = [
        {"category": "cat_a", "pred_text": "The answer is \\boxed{10}", "gold": "10"},
        {"category": "cat_a", "pred_text": "The answer is \\boxed{20}", "gold": "10"},
        {"category": "cat_b", "pred_text": "Final answer is: 3.14", "gold": "3.14"},
    ]

    res = score_by_category(records)

    assert res["aggregate"]["correct"] == 2
    assert res["aggregate"]["total"] == 3
    assert res["aggregate"]["accuracy"] == 2.0 / 3.0

    assert res["by_category"]["cat_a"]["correct"] == 1
    assert res["by_category"]["cat_a"]["total"] == 2
    assert res["by_category"]["cat_a"]["accuracy"] == 0.5

    assert res["by_category"]["cat_b"]["correct"] == 1
    assert res["by_category"]["cat_b"]["total"] == 1
    assert res["by_category"]["cat_b"]["accuracy"] == 1.0

def test_stratified_dev_split():
    rows = [
        {"category": "cat_a", "id": 1},
        {"category": "cat_a", "id": 2},
        {"category": "cat_a", "id": 3},
        {"category": "cat_b", "id": 4},
        {"category": "cat_b", "id": 5},
    ]

    train, dev = stratified_dev_split(rows, per_cat=1, seed=42)

    # 1 from cat_a, 1 from cat_b in dev
    assert len(dev) == 2
    dev_cats = [r["category"] for r in dev]
    assert dev_cats.count("cat_a") == 1
    assert dev_cats.count("cat_b") == 1

    # Remaining in train
    assert len(train) == 3
    train_cats = [r["category"] for r in train]
    assert train_cats.count("cat_a") == 2
    assert train_cats.count("cat_b") == 1

    # Test determinism
    train2, dev2 = stratified_dev_split(rows, per_cat=1, seed=42)
    assert train == train2
    assert dev == dev2

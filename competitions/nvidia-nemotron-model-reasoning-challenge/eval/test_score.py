import pytest
from score import extract_boxed, score_item, score

def test_extract_boxed_simple():
    text = "The answer is \\boxed{42}."
    assert extract_boxed(text) == "42"

def test_extract_boxed_nested():
    text = "Here is a fraction: \\boxed{\\frac{1}{2}}."
    assert extract_boxed(text) == "\\frac{1}{2}"

def test_extract_boxed_multiple_last_chosen():
    text = "Maybe \\boxed{1}. No, it's \\boxed{2}."
    assert extract_boxed(text) == "2"

def test_extract_boxed_missing():
    text = "The answer is 42."
    assert extract_boxed(text) is None

def test_extract_boxed_empty_input():
    assert extract_boxed("") is None
    assert extract_boxed(None) is None

def test_score_item_exact_match():
    assert score_item("\\boxed{hello}", "\\boxed{hello}") is True
    assert score_item("\\boxed{hello}", "hello") is True
    assert score_item("\\boxed{ hello }", "hello") is True # .strip() makes it match

def test_score_item_numeric_match():
    # Exact numeric
    assert score_item("\\boxed{3.1415}", "3.1415") is True
    # Within tolerance
    assert score_item("\\boxed{3.1415}", "3.14") is True
    assert score_item("\\boxed{3.14}", "3.15") is True # 0.01 is <= 1e-2
    # Outside tolerance
    assert score_item("\\boxed{3.14}", "3.16") is False

def test_score_item_missing_box():
    # Prediction missing box is always wrong
    assert score_item("42", "42") is False

def test_score_batch():
    preds = [
        "\\boxed{1}",
        "\\boxed{2.005}",
        "\\boxed{wrong}",
        "no box"
    ]
    golds = [
        "1",
        "2.00",
        "right",
        "anything"
    ]
    # 1: Correct (exact match)
    # 2: Correct (2.005 - 2.00 = 0.005 <= 1e-2)
    # 3: Incorrect
    # 4: Incorrect (no box)
    assert score(preds, golds) == 0.5

import pytest
import sys
import os

# Add the competition folder to sys.path so we can import eval.score
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../competitions/nvidia-nemotron-model-reasoning-challenge")))

from eval.score import extract_boxed, score

def test_extract_boxed():
    assert extract_boxed(r"abc \boxed{123}") == "123"
    assert extract_boxed(r"abc \boxed{123} def \boxed{456}") == "456"
    assert extract_boxed(r"\boxed{a {b {c}} d}") == "a {b {c}} d"
    assert extract_boxed(r"no box here") is None
    assert extract_boxed(r"\boxed{missing close") is None

def test_score_exact_match():
    assert score([r"ans \boxed{123}"], [r"123"]) == 1.0
    assert score([r"ans \boxed{123}"], [r"\boxed{123}"]) == 1.0
    assert score([r"ans \boxed{hello}"], [r"\boxed{hello}"]) == 1.0
    assert score([r"ans \boxed{hello}"], [r"hello"]) == 1.0

def test_score_numeric_tolerance():
    assert score([r"ans \boxed{123.001}"], [r"123.004"]) == 1.0
    assert score([r"ans \boxed{123.05}"], [r"123.00"]) == 0.0
    assert score([r"ans \boxed{-5.0}"], [r"-5.009"]) == 1.0

def test_score_missing_boxed_wrong():
    assert score([r"ans 123"], [r"123"]) == 0.0

def test_score_mixed_batch():
    predictions = [
        r"\boxed{1}",
        r"\boxed{2.005}",
        r"3",
        r"\boxed{text}",
        r"no match \boxed{wrong}",
    ]
    gold = [
        r"1",
        r"2.01",
        r"3",
        r"text",
        r"right",
    ]
    # Prediction 1: exact string match (correct)
    # Prediction 2: numeric match (2.005 vs 2.01, diff is 0.005 <= 0.01) (correct)
    # Prediction 3: missing boxed -> wrong
    # Prediction 4: exact string match (correct)
    # Prediction 5: exact string fail, numeric fail (correct=0)
    # Total correct = 3 / 5 = 0.6
    assert score(predictions, gold) == 0.6

def test_score_empty_or_mismatch():
    assert score([], []) == 0.0
    with pytest.raises(ValueError):
        score([r"\boxed{1}"], [])

import pytest
from generate_cot import extract_answer, compare_answer, verify_and_format_cot

def test_extract_answer():
    assert extract_answer("The answer is \\boxed{42}.") == "42"
    assert extract_answer("Multiple boxes \\boxed{1} and \\boxed{2}") == "2"
    assert extract_answer("Empty box \\boxed{}") == ""
    assert extract_answer("No box here") == ""
    assert extract_answer("\\boxed{123.45}") == "123.45"
    assert extract_answer("\\boxed{ XLVII }") == "XLVII"

def test_compare_answer():
    # Exact match
    assert compare_answer("42", "42") is True
    assert compare_answer("hello", "hello") is True

    # Case insensitive
    assert compare_answer("XLVII", "xlvii") is True
    assert compare_answer("ABC", "abc") is True

    # Binary strings
    assert compare_answer("10011000", "10011000") is True
    assert compare_answer("10011000", "10011001") is False
    assert compare_answer("11011", "00011011") is False # Note: strict exact match for binary as per winner logic

    # Floats with tolerance
    assert compare_answer("24.64", "24.6401") is True
    assert compare_answer("24.64", "25.0") is False
    assert compare_answer("0.0001", "0.000101") is True

def test_verify_and_format_cot_success():
    problem_id = "test-1"
    category = "math"
    prompt = "What is 2+2?"
    expected_answer = "4"
    reasoning_text = "It is 4. \\boxed{4}"

    result = verify_and_format_cot(problem_id, category, prompt, expected_answer, reasoning_text)

    assert result is not None
    assert result["problem_id"] == "test-1"
    assert result["category"] == "math"
    assert result["prompt"] == prompt
    assert result["extracted_answer"] == "4"
    assert result["is_correct"] is True
    assert result["completion"] == "It is 4. \\boxed{4}\n</think>\n\\boxed{4}<|im_end|>"

def test_verify_and_format_cot_failure():
    problem_id = "test-2"
    category = "math"
    prompt = "What is 2+2?"
    expected_answer = "4"
    reasoning_text = "It is 5. \\boxed{5}"

    result = verify_and_format_cot(problem_id, category, prompt, expected_answer, reasoning_text)

    assert result is None

import pytest
import re
import sys
import os

# Ensure the module can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'competitions', 'nvidia-nemotron-model-reasoning-challenge', 'data', 'synthetic'))
import generate

def test_bit_manipulation_puzzle_format_and_correctness():
    puzzle = generate.generate_bit_manipulation_puzzle()
    assert "question" in puzzle
    assert "answer" in puzzle
    assert "metadata" in puzzle

    # Check that answer format is \boxed{...}
    match = re.search(r"\\boxed\{(.+)\}", puzzle["answer"])
    assert match is not None

    # Check that the answer is a number
    ans = int(match.group(1))
    assert isinstance(ans, int)

    # Check correct calculation
    meta = puzzle["metadata"]
    expected_ans = meta["ans"]

    if meta["op"] == "AND":
        assert meta["a"] & meta["b"] == expected_ans
    elif meta["op"] == "OR":
        assert meta["a"] | meta["b"] == expected_ans
    elif meta["op"] == "XOR":
        assert meta["a"] ^ meta["b"] == expected_ans

    assert ans == expected_ans
    assert f"bitwise {meta['op']} operation between {meta['a']} and {meta['b']}" in puzzle["question"]


def test_linear_algebra_puzzle_format_and_correctness():
    puzzle = generate.generate_linear_algebra_puzzle()
    assert "question" in puzzle
    assert "answer" in puzzle
    assert "metadata" in puzzle

    match = re.search(r"\\boxed\{(.+)\}", puzzle["answer"])
    assert match is not None

    ans = int(match.group(1))
    assert isinstance(ans, int)

    meta = puzzle["metadata"]
    v1, v2 = meta["v1"], meta["v2"]
    expected_ans = v1[0]*v2[0] + v1[1]*v2[1]

    assert expected_ans == meta["ans"]
    assert ans == expected_ans
    assert f"dot product of the vectors {v1} and {v2}" in puzzle["question"]

def test_transformation_table_puzzle_format_and_correctness():
    puzzle = generate.generate_transformation_table_puzzle()
    assert "question" in puzzle
    assert "answer" in puzzle
    assert "metadata" in puzzle

    match = re.search(r"\\boxed\{(.+)\}", puzzle["answer"])
    assert match is not None

    ans = int(match.group(1))
    assert isinstance(ans, int)

    meta = puzzle["metadata"]
    factor = meta["factor"]
    offset = meta["offset"]
    target_input = meta["target_input"]
    expected_ans = target_input * factor + offset

    assert expected_ans == meta["target_output"]
    assert ans == expected_ans
    assert f"what is the output for {target_input}" in puzzle["question"]

def test_deduplication():
    # Setup mock data with duplicates
    puzzles = [
        {"question": "What is 1+1?", "answer": "\\boxed{2}"},
        {"question": "What is 1+1?", "answer": "\\boxed{2}"}, # duplicate
        {"question": "What is 2+2?", "answer": "\\boxed{4}"}
    ]

    filtered = generate.deduplicate_and_filter(puzzles)

    assert len(filtered) == 2
    assert filtered[0]["question"] == "What is 1+1?"
    assert filtered[1]["question"] == "What is 2+2?"

def test_answer_in_boxed_all():
    # Generate a few puzzles and make sure all are in boxed
    puzzles = generate.generate_dataset(num_samples=5)
    for p in puzzles:
        match = re.search(r"\\boxed\{(.+)\}", p["answer"])
        assert match is not None, f"Answer missing boxed format: {p['answer']}"

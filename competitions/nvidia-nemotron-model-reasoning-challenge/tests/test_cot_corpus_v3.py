import json
import math
import re
import os

def compare_answer(stored_answer: str, predicted: str) -> bool:
    """Verify if the answer matches, following winner's logic."""
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()

    if re.fullmatch(r"[01]+", stored_answer):
        return predicted.lower() == stored_answer.lower()

    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == stored_answer.lower()

def extract_answer(reasoning_text: str) -> str:
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", reasoning_text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def test_cot_corpus_v3_quality():
    corpus_path = os.path.join(os.path.dirname(__file__), "..", "data", "corpus", "v3", "corpus.jsonl")
    train_csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "train.csv")
    quality_path = os.path.join(os.path.dirname(__file__), "..", "data", "corpus", "v3", "quality_report.json")

    assert os.path.exists(corpus_path), f"Corpus not found at {corpus_path}"
    assert os.path.exists(train_csv_path), f"Train CSV not found at {train_csv_path}"
    assert os.path.exists(quality_path), f"Quality report not found at {quality_path}"

    # Load original answers from train.csv
    import csv
    original_answers = {}
    with open(train_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_answers[row["id"]] = row["answer"]

    categories = set()
    total_rows = 0
    verified_correct = 0

    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            total_rows += 1
            entry = json.loads(line)

            categories.add(entry["category"])

            # Assert schema
            assert "id" in entry
            assert "category" in entry
            assert "prompt" in entry
            assert "cot_completion" in entry
            assert "verified" in entry

            row_id = entry["id"]
            cot = entry["cot_completion"]

            # Extract boxed answer and verify
            extracted = extract_answer(cot)

            original_ans = original_answers[row_id]
            is_correct = compare_answer(original_ans, extracted)

            assert entry["verified"] is True, f"Row {row_id} is marked as not verified"
            assert is_correct is True, f"Row {row_id} has mismatched answers: extracted '{extracted}' vs original '{original_ans}'"

            verified_correct += 1

    assert total_rows >= 700, f"Expected >= 700 rows, got {total_rows}"
    assert len(categories) >= 6, f"Expected >= 6 categories, got {len(categories)} ({categories})"
    assert verified_correct == total_rows, "Not all rows were correctly verified"

    print(f"Test passed! {total_rows} rows verified across {len(categories)} categories: {categories}")

if __name__ == "__main__":
    test_cot_corpus_v3_quality()

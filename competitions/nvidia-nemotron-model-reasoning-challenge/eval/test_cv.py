import pytest
from cv import create_holdout, evaluate_cv

def test_create_holdout():
    data = [{"id": i} for i in range(10)]
    train, holdout = create_holdout(data, test_size=0.2, seed=42)
    assert len(train) == 8
    assert len(holdout) == 2
    # Ensure they are disjoint
    train_ids = {item["id"] for item in train}
    holdout_ids = {item["id"] for item in holdout}
    assert train_ids.isdisjoint(holdout_ids)
    assert len(train_ids.union(holdout_ids)) == 10

def test_evaluate_cv():
    predictions = [
        {"id": "1", "prediction": "\\boxed{10}"},
        {"id": "2", "prediction": "\\boxed{20.005}"},
        {"id": "3", "prediction": "\\boxed{wrong}"},
        {"id": "4", "prediction": "no box"},
        {"id": "5", "prediction": "\\boxed{30}"} # Not in gold
    ]

    gold_data = {
        "1": {"answer": "10", "category": "math"},
        "2": {"answer": "20.00", "category": "math"},
        "3": {"answer": "right", "category": "logic"},
        "4": {"answer": "42", "category": "logic"},
        "6": {"answer": "100", "category": "math"} # Not in preds
    }

    results = evaluate_cv(predictions, gold_data)

    # 1: Correct (math)
    # 2: Correct (math)
    # 3: Incorrect (logic)
    # 4: Incorrect (logic)
    # 5: Skipped

    assert results["total_evaluated"] == 4
    assert results["overall_accuracy"] == 0.5

    assert "math" in results["category_accuracy"]
    assert results["category_accuracy"]["math"] == 1.0 # 2/2

    assert "logic" in results["category_accuracy"]
    assert results["category_accuracy"]["logic"] == 0.0 # 0/2

def test_evaluate_cv_empty():
    results = evaluate_cv([], {})
    assert results["overall_accuracy"] == 0.0
    assert results["category_accuracy"] == {}

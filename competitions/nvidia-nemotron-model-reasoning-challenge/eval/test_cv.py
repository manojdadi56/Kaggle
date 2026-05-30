import pytest

from cv import create_holdout, evaluate_cv, get_category

def test_create_holdout():
    # Create 10 math items, 10 code items, and 5 physics items (25 total)
    data = [{"id": f"math_{i}", "category": "math"} for i in range(10)] + \
           [{"id": f"code_{i}", "category": "code"} for i in range(10)] + \
           [{"id": f"phys_{i}", "category": "physics"} for i in range(5)]

    train, holdout = create_holdout(data, test_size=0.2, seed=42)

    assert len(train) == 20
    assert len(holdout) == 5

    # Ensure they are disjoint
    train_ids = {item["id"] for item in train}
    holdout_ids = {item["id"] for item in holdout}
    assert train_ids.isdisjoint(holdout_ids)
    assert len(train_ids.union(holdout_ids)) == 25

    # Verify stratification (0.2 holdout: 2 math, 2 code, 1 physics)
    holdout_cats = [item["category"] for item in holdout]
    assert holdout_cats.count("math") == 2
    assert holdout_cats.count("code") == 2
    assert holdout_cats.count("physics") == 1

    train_cats = [item["category"] for item in train]
    assert train_cats.count("math") == 8
    assert train_cats.count("code") == 8
    assert train_cats.count("physics") == 4

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

    # Check category_stats
    assert "category_stats" in results
    assert results["category_stats"]["math"]["correct"] == 2
    assert results["category_stats"]["math"]["total"] == 2
    assert results["category_stats"]["logic"]["correct"] == 0
    assert results["category_stats"]["logic"]["total"] == 2

def test_evaluate_cv_empty():
    results = evaluate_cv([], {})
    assert results["overall_accuracy"] == 0.0
    assert results["category_accuracy"] == {}
    assert results["category_stats"] == {}

def test_get_category():
    assert get_category({"category": "explicit"}) == "explicit"
    assert get_category({"problem": "calculate the derivative"}) == "math"
    assert get_category({"question": "write a python function"}) == "code"
    assert get_category({"text": "find the velocity and mass"}) == "physics"
    assert get_category({"problem": "solve this logic puzzle"}) == "logic"
    assert get_category({"problem": "what is the capital of France?"}) == "general"
    assert get_category({}) == "unknown"

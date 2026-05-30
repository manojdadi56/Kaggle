from typing import List, Dict, Any

CATEGORY_DIFFICULTY_WEIGHTS = {
    "cipher": 1.5,
    "rule_unknown": 1.5,
    "equation_transform": 1.2,
    "binary": 1.2,
    "numeral": 1.0,
    "gravity": 1.0,
    "unit_conversion": 1.0,
}

def calculate_difficulty_score(item: Dict[str, Any]) -> float:
    """
    Calculate a composite difficulty score for a given dataset item.
    Factors:
    - length of completion (primary driver)
    - category fingerprint (some categories are inherently harder)
    - solver-confidence (if available in item metadata)
    """
    completion = item.get("completion", "")
    length_score = float(len(completion))

    category = item.get("category", "unknown")
    cat_weight = CATEGORY_DIFFICULTY_WEIGHTS.get(category, 1.0)

    # solver_confidence could be a float between 0.0 and 1.0. Lower confidence -> higher difficulty
    confidence = item.get("solver_confidence", 1.0)
    confidence_penalty = 2.0 - confidence # scale 1.0 to 2.0 multiplier for low confidence

    score = length_score * cat_weight * confidence_penalty
    return score

def sort_by_difficulty(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts training data from easy to hard.
    """
    decorated = [(calculate_difficulty_score(item), item) for item in items]
    decorated.sort(key=lambda x: x[0])
    return [item for score, item in decorated]

def assign_curriculum_tiers(items: List[Dict[str, Any]], num_tiers: int = 3) -> List[Dict[str, Any]]:
    """
    Assigns each item a 'tier' (e.g. 'easy', 'medium', 'hard') based on relative difficulty.
    Mutates/creates a new list of items with a 'tier' key.
    """
    sorted_items = sort_by_difficulty(items)
    n = len(sorted_items)

    if n == 0:
        return []

    tier_size = n // num_tiers
    remainder = n % num_tiers

    tiers = ["easy", "medium", "hard"] if num_tiers == 3 else [f"tier_{i}" for i in range(num_tiers)]

    result = []
    idx = 0
    for i in range(num_tiers):
        current_tier_size = tier_size + (1 if i < remainder else 0)
        for _ in range(current_tier_size):
            item_copy = dict(sorted_items[idx])
            item_copy["difficulty_tier"] = tiers[i]
            item_copy["difficulty_score"] = calculate_difficulty_score(item_copy)
            result.append(item_copy)
            idx += 1

    return result

def apply_curriculum(items: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Entry point for the training kernel to opt into curriculum sorting.
    config = {"enabled": True, "method": "sort_easy_to_hard", "num_tiers": 3}
    """
    if not config.get("enabled", False):
        return items

    method = config.get("method", "sort_easy_to_hard")
    if method == "sort_easy_to_hard":
        return sort_by_difficulty(items)
    elif method == "tier_assignment":
        return assign_curriculum_tiers(items, num_tiers=config.get("num_tiers", 3))

    return items

if __name__ == '__main__':
    # Offline synthetic tests
    def run_tests():
        # Test 1: Difficulty Score
        item_short = {"completion": "123", "category": "numeral"} # len=3, wt=1.0, conf_pen=1.0 -> 3.0
        item_long = {"completion": "12345", "category": "numeral"} # len=5 -> 5.0
        item_cipher = {"completion": "123", "category": "cipher"} # len=3, wt=1.5 -> 4.5
        item_low_conf = {"completion": "123", "category": "numeral", "solver_confidence": 0.5} # len=3, wt=1.0, conf=1.5 -> 4.5

        assert calculate_difficulty_score(item_short) == 3.0, "Score test 1 failed"
        assert calculate_difficulty_score(item_long) == 5.0, "Score test 2 failed"
        assert calculate_difficulty_score(item_cipher) == 4.5, "Score test 3 failed"
        assert calculate_difficulty_score(item_low_conf) == 4.5, "Score test 4 failed"

        # Test 2: Sort
        items = [
            {"id": 1, "completion": "123456", "category": "cipher"}, # len=6*1.5=9.0
            {"id": 2, "completion": "123", "category": "numeral"}, # len=3*1.0=3.0
            {"id": 3, "completion": "1234", "category": "equation_transform"} # len=4*1.2=4.8
        ]
        sorted_items = sort_by_difficulty(items)
        assert sorted_items[0]["id"] == 2, "Sort test 1 failed"
        assert sorted_items[1]["id"] == 3, "Sort test 2 failed"
        assert sorted_items[2]["id"] == 1, "Sort test 3 failed"

        # Test 3: Tiers
        items_for_tiers = [
            {"id": 1, "completion": "1"}, # len 1
            {"id": 2, "completion": "12"}, # len 2
            {"id": 3, "completion": "123"}, # len 3
            {"id": 4, "completion": "1234"}, # len 4
            {"id": 5, "completion": "12345"}, # len 5
        ]
        tiered = assign_curriculum_tiers(items_for_tiers, num_tiers=3)
        assert len(tiered) == 5, "Tier test 1 failed"
        assert tiered[0]["difficulty_tier"] == "easy", "Tier test 2 failed"
        assert tiered[1]["difficulty_tier"] == "easy", "Tier test 3 failed"
        assert tiered[2]["difficulty_tier"] == "medium", "Tier test 4 failed"
        assert tiered[3]["difficulty_tier"] == "medium", "Tier test 5 failed"
        assert tiered[4]["difficulty_tier"] == "hard", "Tier test 6 failed"

        # Test 4: Apply config
        res_sort = apply_curriculum(items, {"enabled": True, "method": "sort_easy_to_hard"})
        assert res_sort[0]["id"] == 2, "Apply config sort failed"

        res_tier = apply_curriculum(items, {"enabled": True, "method": "tier_assignment"})
        assert res_tier[0]["id"] == 2, "Apply config tier failed"
        assert "difficulty_tier" in res_tier[0], "Apply config tier missing key failed"

        print("All offline synthetic tests passed!")

    run_tests()

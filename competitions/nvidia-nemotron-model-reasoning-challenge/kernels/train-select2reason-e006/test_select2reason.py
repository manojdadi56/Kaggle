import unittest
from select2reason import calculate_utility, deduplicate_fingerprint, curate_top_p

class TestSelect2Reason(unittest.TestCase):
    def setUp(self):
        self.dummy_data = [
            {"prompt": "A", "completion": "12345", "category": "math"}, # len 5, novelty low (3/6)
            {"prompt": "B", "completion": "123", "category": "science"}, # len 3, novelty high (1/6)
            {"prompt": "C", "completion": "123456789", "category": "math"}, # len 9
            {"prompt": "A", "completion": "1", "category": "math"}, # duplicate A, len 1
            {"prompt": "D", "completion": "12", "category": "math"}, # len 2
            {"prompt": "E", "completion": "1234567", "category": "history"}, # len 7, novelty high (1/6)
            {"prompt": "E ", "completion": "1", "category": "history"}, # duplicate E with space
        ]

    def test_calculate_utility(self):
        scored = calculate_utility(self.dummy_data)
        self.assertEqual(len(scored), 7)
        self.assertIn("_utility_score", scored[0])

    def test_deduplicate_fingerprint(self):
        scored = calculate_utility(self.dummy_data)
        deduped = deduplicate_fingerprint(scored)

        # 'A' should be deduped, keeping the longer completion (12345 over 1)
        # 'E' should be deduped, keeping the longer completion (1234567 over 1)
        self.assertEqual(len(deduped), 5)

        a_items = [i for i in deduped if i["prompt"].strip() == "A"]
        self.assertEqual(len(a_items), 1)
        self.assertEqual(a_items[0]["completion"], "12345")

        e_items = [i for i in deduped if i["prompt"].strip() == "E"]
        self.assertEqual(len(e_items), 1)
        self.assertEqual(e_items[0]["completion"], "1234567")

    def test_curate_top_p_stratification(self):
        # We have 3 categories in deduped: math (A, C, D -> 3 items), science (B -> 1 item), history (E -> 1 item)
        # 40% keep:
        # math: int(3 * 0.4) = int(1.2) = 1 (top is C)
        # science: int(1 * 0.4) = int(0.4) = 0 -> keeps at least 1 (B)
        # history: int(1 * 0.4) = int(0.4) = 0 -> keeps at least 1 (E)
        curated = curate_top_p(self.dummy_data, keep_percent=0.4)

        self.assertEqual(len(curated), 3)
        categories = [i["category"] for i in curated]
        self.assertIn("math", categories)
        self.assertIn("science", categories)
        self.assertIn("history", categories)

        math_item = [i for i in curated if i["category"] == "math"][0]
        self.assertEqual(math_item["prompt"], "C", "Math top item by utility should be C")

        # Ensure _utility_score is cleaned up
        for item in curated:
            self.assertNotIn("_utility_score", item)

if __name__ == '__main__':
    unittest.main()

import json
import os

def test_corpus_v4_quality():
    corpus_file = "competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v4/corpus.jsonl"
    report_file = "competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v4/quality_report.json"

    assert os.path.exists(report_file), f"Report file {report_file} does not exist"

    with open(report_file) as f:
        report = json.load(f)

    assert "categories" in report
    cats_present = list(report["categories"].keys())
    assert len(cats_present) == 9, f"Expected 9 categories, found {len(cats_present)}"

    expected_categories = [
        "bit_manipulation", "cipher", "gravity", "numeral",
        "cryptarithm", "cryptarithm_guess", "equation_numeric",
        "unit_conversion", "select2reason"
    ]

    for c in expected_categories:
        assert c in cats_present, f"Category {c} missing from report"

    for cat, stats in report["categories"].items():
        assert stats["verified"] >= 100, f"Category {cat} has only {stats['verified']} verified rows"
        if stats["generated"] > 0:
            rate = stats["verified"] / stats["generated"]
            assert rate >= 0.95, f"Category {cat} verification rate {rate} below 95%"

    assert os.path.exists(corpus_file), f"Corpus file {corpus_file} does not exist"

    with open(corpus_file) as f:
        lines = f.readlines()

    assert len(lines) >= 3000, f"Corpus has {len(lines)} lines, which is less than 3000"

    cats = set()
    for line in lines:
        data = json.loads(line)
        cats.add(data["category"])
        assert "\\boxed{" in data["completion"]
        assert "</think>" in data["completion"]

    for c in expected_categories:
        assert c in cats, f"Category {c} missing from corpus"

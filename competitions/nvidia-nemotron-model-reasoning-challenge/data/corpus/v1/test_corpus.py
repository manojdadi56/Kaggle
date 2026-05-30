import json
from pathlib import Path

def test_corpus_index():
    index_path = Path(__file__).parent / "corpus_index.jsonl"
    assert index_path.exists(), "corpus_index.jsonl missing"

    with open(index_path) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    assert len(entries) > 0, "Index is empty"

    categories = set()
    splits = {"train": 0, "dev": 0}

    for e in entries:
        assert "problem_id" in e
        assert "segment" in e
        assert "category" in e
        assert "masked_token_count" in e
        assert "unmasked_token_count" in e
        assert "split" in e
        assert "answer" in e

        categories.add(e["category"])
        splits[e["split"]] += 1

    # Assert multiple categories were loaded
    assert len(categories) >= 4, f"Found only {len(categories)} categories"

    # Assert ~90/10 split
    total = splits["train"] + splits["dev"]
    train_ratio = splits["train"] / total
    assert 0.8 <= train_ratio <= 1.0, f"Train split ratio {train_ratio} out of bounds"

def test_segments_format():
    index_path = Path(__file__).parent / "corpus_index.jsonl"
    with open(index_path) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    for e in entries[:5]: # test first 5
        seg_path = Path(__file__).parent / e["problem_id"] / e["segment"]
        assert seg_path.exists(), f"Segment file {seg_path} missing"

        with open(seg_path) as f:
            segments = [json.loads(line) for line in f if line.strip()]

        assert len(segments) >= 2, "Should have at least masked and unmasked segments"
        for seg in segments:
            assert "type" in seg
            assert seg["type"] in ("masked", "unmasked")
            assert "pos" in seg
            assert "tokens" in seg

def test_corpus_jsonl():
    corpus_path = Path(__file__).parent / "corpus.jsonl"
    assert corpus_path.exists(), "corpus.jsonl missing"

    with open(corpus_path) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    assert len(entries) > 0, "Corpus is empty"

    for e in entries:
        assert "id" in e
        assert "category" in e
        assert "prompt" in e
        assert "completion" in e
        assert "tokens" in e
        assert "mask" in e
        assert "answer" in e
        assert len(e["tokens"]) == len(e["mask"])

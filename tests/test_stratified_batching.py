import sys
import importlib.util
import pytest

spec = importlib.util.spec_from_file_location(
    "v25_stratified",
    "competitions/nvidia-nemotron-model-reasoning-challenge/experiments/notebook_patches/v25_stratified.py"
)
v25_stratified = importlib.util.module_from_spec(spec)
sys.modules["v25_stratified"] = v25_stratified
spec.loader.exec_module(v25_stratified)

stratified_batches = v25_stratified.stratified_batches
apply_patch = v25_stratified.apply_patch

def test_stratified_batching():
    # 9 categories, 3 examples each = 27 examples
    categories = [f"cat_{i}" for i in range(9)]
    train_data = []
    for cat in categories:
        for j in range(3):
            train_data.append({"category": cat, "id": f"{cat}_{j}"})

    # Batch size 9 (so exactly 3 batches)
    batches = stratified_batches(train_data, batch_size=9)

    assert len(batches) == 3
    for batch in batches:
        assert len(batch) == 9

        # Check that each batch has exactly 1 example from each category
        batch_categories = [train_data[i]["category"] for i in batch]
        assert set(batch_categories) == set(categories)

def test_missing_category():
    train_data = [
        {"id": "1"}, {"id": "2"}, {"id": "3"}
    ]
    batches = stratified_batches(train_data, batch_size=2)
    assert len(batches) == 2
    assert len(batches[0]) + len(batches[1]) == 3

def test_apply_patch():
    # A simplified version of the notebook content
    mock_notebook = r"""   "source": "# Load competition train.csv (auto-detect path)\nimport csv\ncands = glob.glob('/kaggle/input/*/train.csv')\nassert cands, 'train.csv not found - check competition is attached'\nTRAIN_CSV = cands[0]; print('train.csv:', TRAIN_CSV)\nSAMPLE_SIZE = 50\ntrain_data = []\nwith open(TRAIN_CSV, encoding='utf-8') as f:\n    for row in csv.DictReader(f):\n        p = row.get('prompt') or row.get('question') or ''\n        a = row.get('answer') or row.get('completion') or ''\n        if p and a: train_data.append({'prompt': p, 'completion': str(a)})\n        if len(train_data) >= SAMPLE_SIZE: break\nprint(f'Loaded {len(train_data)} examples')",
   "source": "# 1-epoch LoRA SFT (mask: answer tokens only)\nMAX_SEQ, GA = 2048, 8\nopt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)\ndev = next(model.parameters()).device\ndef datum(p, a):\n    pt = tokenizer(p, add_special_tokens=False)['input_ids']\n    at = tokenizer(a, add_special_tokens=False)['input_ids'] + [tokenizer.eos_token_id]\n    t = (pt + at)[:MAX_SEQ]; m = ([0]*len(pt) + [1]*len(at))[:MAX_SEQ]\n    return torch.tensor(t).unsqueeze(0), torch.tensor(m).unsqueeze(0)\nmodel.train(); step = 0; rl = 0.0\nfor d in train_data:\n    ids, mask = datum(d['prompt'], d['completion']); ids, mask = ids.to(dev), mask.to(dev)\n    lg = model(input_ids=ids).logits"""

    patched = apply_patch(mock_notebook)

    assert "'category': row.get('category', 'unknown')" in patched
    assert "def stratified_batches(train_data" in patched
    assert "stratified_data = [train_data[i] for b in stratified_batches(train_data, GA) for i in b]" in patched
    assert "for d in stratified_data:" in patched

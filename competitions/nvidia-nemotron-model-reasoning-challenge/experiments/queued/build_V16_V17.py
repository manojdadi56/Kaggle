"""Build V16 (rank=16 ablation, faster training) and V17 (Select2Reason curation: longest CoTs only).
Each is a tiny diff on top of V15's CoT-corpus patch.
"""
import json
from pathlib import Path

V15 = json.loads(Path("competitions/nvidia-nemotron-model-reasoning-challenge/experiments/queued/V15-cot-corpus.json").read_text(encoding="utf-8"))
HERE = Path("competitions/nvidia-nemotron-model-reasoning-challenge/experiments/queued")

# ===== V16: rank=16 (faster training, lower-rank baseline for comparison) =====
v16_cell1 = V15["cells"]["1"].replace("LORA_RANK = 32", "LORA_RANK = 16")
v16 = {"cells": {"0": V15["cells"]["0"], "1": v16_cell1}}
(HERE / "V16-rank16-ablation.json").write_text(json.dumps(v16), encoding="utf-8")
print("V16 (rank=16):", (HERE / "V16-rank16-ablation.json").stat().st_size, "bytes")

# ===== V17: Select2Reason - keep only top 50% by completion length (highest-utility CoT) =====
# Patch cell 0 to filter train_data after load
patch_v17 = (
    "\n# === Select2Reason curation: keep only top-50% longest completions ===\n"
    "train_data.sort(key=lambda d: len(d.get('completion','')), reverse=True)\n"
    "train_data = train_data[:len(train_data)//2]\n"
    "print(f'Select2Reason kept top {len(train_data)} examples by completion length')"
)
v17_cell0 = V15["cells"]["0"] + patch_v17
v17 = {"cells": {"0": v17_cell0, "1": V15["cells"]["1"]}}
(HERE / "V17-select2reason.json").write_text(json.dumps(v17), encoding="utf-8")
print("V17 (Select2Reason):", (HERE / "V17-select2reason.json").stat().st_size, "bytes")

# ===== Manifest for the operator: what to apply when =====
manifest = {
    "queue": [
        {"name": "V15", "patch": "V15-cot-corpus.json",
         "purpose": "BIG LEVER: train on 91 inline CoT examples (pre-tokenized) instead of raw train.csv rows. Expected LB delta per technique-backlog: 0.65 -> 0.85.",
         "depends_on": "v13/v16 baseline submission landing first to anchor best_cv"},
        {"name": "V16", "patch": "V16-rank16-ablation.json",
         "purpose": "Ablation: rank=16 LoRA (half the params, ~2x faster training). Tests speed/quality tradeoff. Same corpus as V15.",
         "depends_on": "V15 submitted"},
        {"name": "V17", "patch": "V17-select2reason.json",
         "purpose": "Select2Reason: keep only top-50% longest CoTs (highest-utility curation per konbu17 community insight). Same rank=32 + V15 corpus.",
         "depends_on": "V15 submitted; ideally compare against V15 cv to validate curation hypothesis"},
    ],
    "apply_command": "python tools/iterate_notebook.py --slug nvidia-nemotron-submission-demo --patch-file competitions/nvidia-nemotron-model-reasoning-challenge/experiments/queued/<patch>.json",
    "post_iteration": "user clicks browser Save & Run All; operator runs python tools/auto_submit.py --slug nvidia-nemotron-submission-demo --force when COMPLETE",
}
(HERE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("MANIFEST written")
print()
print("Queue ready:")
for q in manifest["queue"]:
    print(f"  {q['name']}: {q['purpose'][:90]}")

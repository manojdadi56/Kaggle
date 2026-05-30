"""Deploy 2 more tasks from master_roadmap CurrentNotebookGaps."""
import json
from pathlib import Path

TICK = "CAMP-ROADMAP-1"
TS = "2026-05-31T03:45:00Z"

tasks = [
  {
    "id": "TASK-NOTEBOOK-target-masking",
    "title": "Add target-masking + step-based LR decay tunable block to notebook (winner pattern)",
    "spec": (
      "Per analysis/master_roadmap.xlsx CurrentNotebookGaps + winner_code_analysis.xlsx KeyImprovements: "
      "our notebook trains on all tokens (unmasked) and uses epoch-based LR decay. Winner uses (a) target "
      "masking — loss only on CoT + answer span, not the user prompt; (b) STEP-based LinearDecayLRSchedule "
      "decaying per step within an epoch. Add to "
      "competitions/nvidia-nemotron-model-reasoning-challenge/experiments/notebook_patches/v24_target_masking.py "
      "a Python script that, when given the current notebook source as text input, returns an updated "
      "source with: (1) the datum() function correctly masks prompt tokens to 0, completion to 1 "
      "(currently broken when using chat templates — the prompt-only render may have different offsets); "
      "(2) the LR schedule decays per STEP not per epoch: lr = lr_initial + (lr_final - lr_initial) * "
      "(step / total_steps); (3) preserves the chat-template rendering already in v23. "
      "Add tests/test_notebook_patch_v24.py asserting that applying the patch to a stub notebook produces "
      "the expected diff (no exceptions, mask is 0 for system+user tokens, 1 for assistant)."
    ),
    "allowed_area": (
      "competitions/nvidia-nemotron-model-reasoning-challenge/experiments/notebook_patches/v24_target_masking.py, "
      "tests/test_notebook_patch_v24.py"
    ),
    "priority": "P0", "est_hours": 1.0, "status": "BACKLOG",
  },
  {
    "id": "TASK-NOTEBOOK-stratified-batching",
    "title": "Add stratified-batching sampler tunable block to notebook (winner pattern, per-category mix)",
    "spec": (
      "Per master_roadmap CurrentNotebookGaps + winner_code_analysis.xlsx: winner uses stratified batching "
      "across 9 categories — every gradient-accumulation window sees a mix of categories rather than one "
      "category in a contiguous block. Build "
      "competitions/nvidia-nemotron-model-reasoning-challenge/experiments/notebook_patches/v25_stratified.py "
      "(another patch script) that replaces the simple `for d in train_data` loop with: (1) groups train_data "
      "by row.category; (2) round-robin one row per category per micro-batch within a GA window; (3) shuffles "
      "categories at epoch start with a fixed seed. Falls back to plain iteration when 'category' is missing. "
      "Add tests/test_stratified_batching.py asserting category-balance within each GA window on a 9-cat stub. "
      "Acceptance: patch script exists; tests green."
    ),
    "allowed_area": (
      "competitions/nvidia-nemotron-model-reasoning-challenge/experiments/notebook_patches/v25_stratified.py, "
      "tests/test_stratified_batching.py"
    ),
    "priority": "P1", "est_hours": 0.75, "status": "BACKLOG",
  },
]

ops = []
for t in tasks:
    ops.append({"op":"create_task","idempotency_key":f"{TICK}:{t['id']}",
      "data":{**t, "hypothesis_id":"H-FINAL-PREP-PARALLEL", "created_at":TS}})

decision = {"tick_id":TICK,"status":"complete",
  "summary":"campaign ROADMAP-1: 2 notebook-patch tasks from master_roadmap CurrentNotebookGaps",
  "state_patch":{"tick_id":TICK,"operations":ops}}
Path("_roadmap.json").write_text(json.dumps(decision), encoding="utf-8")
print(f"wrote {len(ops)} ops ({len(tasks)} tasks)")

# TASK-R8 — Local CV eval harness mirroring host scoring
- hypothesis: H-004
- story: US-2
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/eval
- starting_branch: main
- gpu: no
- dependencies: none
- parallel_with: TASK-R1, TASK-R10, TASK-R11, TASK-R12

## Goal
Extend the merged `eval/score.py` into a full offline CV harness that faithfully mirrors host scoring so every experiment is trustworthy: hold-out split from train, `\boxed{}` extraction (last boxed, nested-brace safe), exact OR ±1e-2 numeric match, per-category accuracy breakdown, and a CLI that scores a predictions file.

## Mine first
`references/winner-eval.py.md`, `references/analysis-data-and-scoring.md` (host params: temp 0, max_lora_rank 32, max_model_len 8192), the merged `eval/score.py`.

## Acceptance criteria
- `eval/cv.py` (+ extend `eval/score.py`): holdout creation, scoring, per-category report.
- Offline tests: exact match, numeric tolerance, missing-boxed, nested braces, per-category aggregation.
- `eval/README.md` documenting how a training run reports `cv_score.json` in the host-comparable metric.

## Definition of done
Harness + tests committed via one PR; tests green; output format pinned so the GPU executor can emit `cv_score.json` the operator trusts.

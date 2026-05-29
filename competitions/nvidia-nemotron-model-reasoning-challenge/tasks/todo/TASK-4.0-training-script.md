# TASK-4.0 — Author the QLoRA training script + Kaggle kernel
- story: US-4
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/kernels
- starting_branch: main
- gpu: no  (authoring only — training runs on the GPU executor)
- dependencies: TASK-1.4, TASK-2.1

## Goal
Author a QLoRA training script (rank ≤ 32, target modules per analysis,
multi-GPU aware) + a Kaggle kernel-metadata so the operator can push it to the
`kaggle_gpu` backend. Writes `adapter/` + `cv_score.json` on completion.

## Acceptance criteria
- `kernels/train/` with the script, `kernel-metadata.json` (GPU enabled, base model + data attached), and a config that asserts rank ≤ 32 at runtime.
- A `--smoke` path runnable on dev_local with a toy model (no 30B) for validation.

## Definition of done
- Committed via one PR; the `--smoke` path is exercised in an offline test/mock.

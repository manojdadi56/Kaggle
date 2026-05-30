# TASK-R10 — Author the QLoRA SFT training kernel (GPU-ready; runs later)
- hypothesis: H-006
- story: US-4
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/kernels
- starting_branch: main
- gpu: no   (authoring only; trains later on kaggle_gpu / local_40g)
- dependencies: none (refine after TASK-R8)
- parallel_with: TASK-R1, TASK-R8, TASK-R11, TASK-R12

## Goal
Port the winner's training recipe into a clean, runnable training kernel for our pipeline: 1-epoch LoRA SFT on `Nemotron-3-Nano-30B-A3B-BF16`, **rank ≤ 32, alpha 64** (assert at runtime), reads a CoT corpus, writes `adapter/` + `cv_score.json`. Include a `--smoke` path that runs on a tiny toy model (no GPU) so it can be validated offline.

## Mine first
`references/winner-train_sft.py.md`, `references/winner-train_common.py.md`, `references/winner-loss_config.py.md`, `references/winner-lr_schedule.py.md`, `references/winner-upload_adapter.py.md`.

## Acceptance criteria
- `kernels/train/train.py` (QLoRA SFT, rank≤32/alpha64 asserted), `kernels/train/kernel-metadata.json` (GPU enabled, base model + dataset attached as placeholders), `kernels/train/README.md`.
- Offline test exercising the `--smoke` path + the rank≤32 assertion (rejects rank 64).

## Definition of done
Kernel + smoke test committed via one PR; tests green. When `KAGGLE_KEY` is set, the operator can `kaggle kernels push` this to train for real.

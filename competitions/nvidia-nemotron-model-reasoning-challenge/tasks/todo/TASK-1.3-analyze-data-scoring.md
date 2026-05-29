# TASK-1.3 — Analyze data schema + scoring harness
- story: US-1
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/references/analysis-data-and-scoring.md
- starting_branch: main
- gpu: no
- dependencies: TASK-1.0
- parallel_with: TASK-1.1, TASK-1.2

## Goal
Document `train.csv`/`test.csv` columns, the `\boxed{}` answer format, the fixed
host vLLM params (temp 0, max_lora_rank 32, max_model_len 8192, ...), and the
local CV eval harness we should replicate.

## Acceptance criteria
- `references/analysis-data-and-scoring.md` with the schema + a spec for the local eval harness.

## Definition of done
- File committed via one PR with the standard PR body.

# TASK-3.1 — Synthetic reasoning data generator
- story: US-3
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/data/synthetic
- starting_branch: main
- gpu: no
- dependencies: TASK-1.3

## Goal
Author a CPU script that generates reasoning puzzles (bit manipulation, algebra,
transformation tables) with verified `\boxed{}` answers, plus filtering/dedup.

## Acceptance criteria
- `data/synthetic/generate.py` + a small generated sample + a validity check (answers parse + are correct).
- Offline tests for the generator.

## Definition of done
- Committed via one PR; tests green.

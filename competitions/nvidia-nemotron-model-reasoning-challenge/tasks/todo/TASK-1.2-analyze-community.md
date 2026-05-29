# TASK-1.2 — Analyze community repos + official starter
- story: US-1
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/references/analysis-community.md
- starting_branch: main
- gpu: no
- dependencies: TASK-1.0
- parallel_with: TASK-1.1, TASK-1.3

## Goal
Compare the competitor repos + official starter; extract the common pipeline
(load base → QLoRA → package submission.zip), divergences, and the canonical
packaging/validation steps (rank ≤ 32, adapter_config.json).

## Acceptance criteria
- `references/analysis-community.md` with a side-by-side of approaches + citations.

## Definition of done
- File committed via one PR with the standard PR body.

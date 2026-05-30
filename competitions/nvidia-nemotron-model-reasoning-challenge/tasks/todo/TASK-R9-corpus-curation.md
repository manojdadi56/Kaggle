# TASK-R9 — Corpus curation: filter, dedup, difficulty-balance
- hypothesis: H-005
- story: US-3
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/data/curation
- starting_branch: main
- gpu: no
- dependencies: TASK-R7 (CoT format)  [design now]
- parallel_with: data-gen tasks

## Goal
Build the curation pipeline that turns raw generated CoT into a clean SFT corpus: exact/near dedup, format validation (every example ends in a valid `\boxed{}`), difficulty + category balancing, train/holdout split that the CV harness (TASK-R8) consumes. Generalization to the hidden test set is the goal.

## Mine first
`references/winner-corpus.py.md`, `references/winner-augmentation.py.md`, `references/technique-backlog.md`.

## Acceptance criteria
- `data/curation/curate.py` — dedup + validate + balance + split; emits corpus stats (per-category counts, difficulty histogram).
- Offline tests for dedup, format-rejection, and balanced split.

## Definition of done
Pipeline + tests committed via one PR; stats reported; output is the canonical corpus the training kernel (TASK-R10) trains on.

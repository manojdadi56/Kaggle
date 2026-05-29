# TASK-1.1 — Analyze the winning solution
- story: US-1
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/references/analysis-winner.md
- starting_branch: main
- gpu: no
- dependencies: TASK-1.0
- parallel_with: TASK-1.2, TASK-1.3

## Goal
Read `references/tonghuikang-nemotron/**`; produce `references/analysis-winner.md`:
data strategy, LoRA config (rank/target modules/hyperparams), training recipe,
decoding/prompt tricks, and what drove the score.

## Acceptance criteria
- Every claim cites a file/line in the reference.
- Flags the LoRA rank vs the ≤32 cap + compute assumptions.
- Ends with a ranked "techniques to adopt for our compute (40 GB 2-GPU / 2×T4)".

## Definition of done
- `analysis-winner.md` committed via one PR; PR body has Summary/Evidence/Risks/DoD.

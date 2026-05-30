# TASK-R7 — Verified `\boxed{}` chain-of-thought generator
- hypothesis: H-003
- story: US-3
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/data/cot
- starting_branch: main
- gpu: no
- dependencies: TASK-R1 (taxonomy), TASK-R2.* (solvers)  [start design now; wire to solvers as they land]
- parallel_with: data-gen tasks

## Goal
Build the pipeline that turns solver outputs into high-quality SFT examples: for each problem, a clean step-by-step chain-of-thought ending in `\boxed{answer}`, with the answer **verified** against the deterministic solver. This is the winner's core lever (data quality).

## Mine first
`references/winner-reasoning.py.md`, `references/winner-corpus.py.md`, `references/winner-augmentation.py.md`, `references/winner-generate_csv.py.md`.

## Acceptance criteria
- `data/cot/generate_cot.py` — solver-output → verified CoT example (prompt, CoT, `\boxed{}`); rejects any example whose boxed answer ≠ solver answer.
- `data/cot/schema.md` (SFT example format) + offline tests (format + verification correctness + a small generated sample).

## Definition of done
Generator + verifier + tests committed via one PR; sample examples verified correct; format matches what TASK-R10's training kernel consumes.

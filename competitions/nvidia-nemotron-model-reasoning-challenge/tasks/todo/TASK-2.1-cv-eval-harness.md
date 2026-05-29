# TASK-2.1 — Build local CV eval harness
- story: US-2
- actor: jules
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/eval
- starting_branch: main
- gpu: no
- dependencies: TASK-1.3

## Goal
Implement an offline eval harness mirroring host scoring: parse model output for
`\boxed{...}`, compare to gold by exact / ±1e-2 numeric match, report accuracy on
a held-out split. Pure CPU; runs on a tiny sample for tests.

## Acceptance criteria
- `eval/score.py` with a `score(predictions, gold) -> accuracy` + `\boxed{}` extractor.
- Unit tests (offline) covering exact + numeric-tolerance matches.

## Definition of done
- Committed via one PR; `pytest -q` green.

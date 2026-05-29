# TASK-1.0 — Vendor reference solutions into references/
- story: US-1
- actor: operator
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/references
- gpu: no
- dependencies: none

## Goal
Clone/copy reference solutions into `references/` so Jules can analyze them in-repo
(keeps Kaggle creds off the Jules VM): `tonghuikang/nemotron` (winner),
`yunior123/nvidia-nemotron-reasoning`, `SebAustin/NVIDIA-Nemotron-Model-Reasoning-Challenge`,
the official starter (ryanholbrook), + 2–3 top public Kaggle notebooks. Drop the
`train.csv`/`test.csv` schema and base-model card into `data/`/`references/`.

## Acceptance criteria
- `references/<repo>/` present for each source (gitignored content ok; keep a stub if large).
- `references/INDEX.md` lists each source with URL + license.

## Definition of done
- INDEX.md committed; references available for TASK-1.1/1.2/1.3.

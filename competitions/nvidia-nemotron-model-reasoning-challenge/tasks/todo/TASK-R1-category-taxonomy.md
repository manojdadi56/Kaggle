# TASK-R1 — Derive the problem-category taxonomy + classifier
- hypothesis: H-001
- story: US-1
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/data/taxonomy
- starting_branch: main
- gpu: no
- dependencies: none
- parallel_with: TASK-R8, TASK-R10, TASK-R11, TASK-R12

## Goal
Build a clean taxonomy of the reasoning problem categories in this competition (bit manipulation, algebra, transformation tables, etc.), grounded in `train.csv` + the discussions + winner `reasoning.py`. Then a lightweight rule/heuristic **classifier** that labels each train row with its category.

## Mine first
`references/winner-reasoning.py.md` (winner's category logic), `references/technique-backlog.md`, `references/DIGEST-community.md`, relevant `references/discussion-*.md`, and `data/` train schema (`references/analysis-data-and-scoring.md`).

## Acceptance criteria
- `data/taxonomy/taxonomy.md` — the category list with definitions, examples, and approximate frequency in train.
- `data/taxonomy/classify.py` + offline tests — labels a prompt → category; reports coverage (% of train confidently classified).
- A ranked note on which categories are highest-value to solve first (frequency × expected gain).

## Definition of done
Taxonomy + classifier committed via one PR; tests green; ranking documented. This unblocks the per-category solver tasks (TASK-R2.*).

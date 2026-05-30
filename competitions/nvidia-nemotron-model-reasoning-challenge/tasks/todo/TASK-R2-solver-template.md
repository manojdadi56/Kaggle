# TASK-R2.<cat> — Per-category deterministic solver  (TEMPLATE — operator clones one per category)
- hypothesis: H-002
- story: US-3
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/<category>
- starting_branch: main
- gpu: no
- dependencies: TASK-R1 (taxonomy)
- parallel_with: other TASK-R2.<cat> (disjoint solver dirs → fully parallel)

## Note to operator
This is the template for the highest-value lever (winner's per-category deterministic solvers). After TASK-R1 lands the taxonomy + ranking, clone ONE deep task per category into `data/solvers/<category>/`, ordered by the TASK-R1 value ranking, and dispatch them in parallel (disjoint areas).

## Goal (per category)
Implement a deterministic solver that, given a `<category>` problem prompt, parses it and computes the exact answer, plus a generator that produces fresh valid `<category>` problems with known answers (for data scale). 100% correctness on the category is the bar.

## Mine first
`references/winner-reasoning.py.md` (the winner's solver patterns), the category definition in `data/taxonomy/taxonomy.md`, relevant `references/discussion-*.md`.

## Acceptance criteria
- `data/solvers/<category>/solve.py` (prompt → exact answer) + `generate.py` (fresh problems + answers).
- Offline tests proving correctness on held-out examples of that category (target 100% on solvable instances; document any unsolved sub-types).

## Definition of done
Solver + generator + tests committed via one PR; correctness demonstrated; outputs feed TASK-R7 (CoT) → TASK-R9 (curation) → TASK-R10 (training).

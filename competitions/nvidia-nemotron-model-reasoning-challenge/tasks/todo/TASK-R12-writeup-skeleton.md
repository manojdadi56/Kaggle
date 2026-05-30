# TASK-R12 — Public notebook + writeup skeleton (prize eligibility)
- hypothesis: H-008
- story: US-6
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/writeup
- starting_branch: main
- gpu: no
- dependencies: none
- parallel_with: TASK-R1, TASK-R8, TASK-R10, TASK-R11

## Why
Per the scraped rules: prize eligibility REQUIRES a public Kaggle notebook + a solution writeup under an OSI/CC-BY-4.0 license. Draft early, keep updated as the method evolves.

## Goal
Create a living writeup + a public-notebook skeleton documenting our method (data-quality thesis → per-category solvers → verified `\boxed{}` CoT → 1-epoch LoRA SFT rank≤32), with placeholders for final numbers.

## Acceptance criteria
- `writeup/SOLUTION.md` — method, data pipeline, training config, CV methodology, results table (placeholders), reproducibility steps, license note (CC BY 4.0).
- `writeup/public_notebook.ipynb` (or `.py` skeleton) that loads the adapter + runs the documented inference, ready to publish.

## Definition of done
Writeup + notebook skeleton committed via one PR; structure complete; marked as living docs the operator updates each milestone.

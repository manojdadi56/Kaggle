# US-1 — Analyze existing solutions

> As the system, I want a structured understanding of the best existing Nemotron solutions and the competition's data/scoring, so training starts from proven techniques.

**Initial story.** Highest-leverage, no-GPU → ideal for Jules. References are vendored by the operator (TASK-1.0); Jules analyzes them in-repo. A Phase-0 probe (TASK-0.P) optionally tests whether Jules can self-fetch from the internet.

Tasks: TASK-1.0 (operator vendor refs) → TASK-1.1 ∥ TASK-1.2 ∥ TASK-1.3 (parallel Jules analysis) → TASK-1.4 (operator synthesize → plan + technique backlog).
Done when `references/analysis-*.md` exist and `plan.md` names a chosen baseline approach + ranked techniques.

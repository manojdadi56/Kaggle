# Plan — Nemotron (rolling; operator-owned)

Strategy: **baseline-first**, then iterate. Prove a real submission, then let the loop improve it.

## Phase A — Analyze (US-1)
Operator vendors reference solutions; Jules analyzes them in parallel; operator synthesizes a chosen approach + technique backlog.

## Phase B — Validate (US-2)
Build a local CV harness that mirrors host scoring; smoke-test packaging (rank ≤ 32 → valid zip) before spending GPU.

## Phase C — Baseline train + submit (US-4 first pass)
Fork the winner's recipe, train a small adapter on Kaggle GPU, package, submit once → first leaderboard score.

## Phase D — Iterate
Synthetic data (US-3), better recipes, debug/improve stories (US-5). Submit only when local CV beats best and budget allows.

## Current focus
TASK-1.0 (vendor references) → TASK-1.1/1.2/1.3 (parallel analysis) → TASK-1.4 (synthesize).

## Decisions log
See `decisions/`. Record every "tried X, chose Y because Z" as a short ADR.

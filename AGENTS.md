# AGENTS.md — standing context for Jules (and any coding agent) in this repo

This repo runs an **autonomous Kaggle-competition loop**. You (Jules) are the **Worker**: you author and iterate code. You do **not** train models (the VM has no GPU), do **not** submit to Kaggle, and do **not** touch `state/`, `.env`, or any secret.

## Hard invariants (never violate)
- **Competition base model is fixed:** `Nemotron-3-Nano-30B-A3B-BF16`. Never swap or full-fine-tune it.
- **Submission is a LoRA adapter, rank ≤ 32**, packaged as `submission.zip` with a valid `adapter_config.json`. An over-rank config is rejected — always validate rank ≤ 32.
- **Answers must be emitted inside `\boxed{...}`** (host scoring extracts from there; exact/numeric match).
- **One task per session.** Stay inside your task's `allowed_area`. Open exactly one PR.
- **No secrets, ever.** Never read/write `.env`, never hardcode keys, never call Kaggle/Jules/Anthropic APIs directly.

## Repo layout
- `orchestrator/` — the local Python loop + clients (do not edit unless your task says so).
- `prompts/` — trigger prompts for worker + operator.
- `competitions/<slug>/` — one self-contained folder per competition: `plan.md`, `tasks/`, `user-stories/`, `decisions/`, `experiments/`, `kernels/`, `submissions/`, `references/`, `data/`.
- `state/` — orchestrator state (operator-only; never modify).

## How to work a task
1. Read the task file (under `competitions/<slug>/tasks/...`) and its `allowed_area`, acceptance criteria, and definition-of-done.
2. Make the smallest correct change; add/adjust tests or a runnable validation.
3. Run what the no-GPU VM allows: `pip install -r requirements.txt`, `pytest -q`, lints, tiny-sample dry-runs.
4. Open ONE PR. PR body must have: `## Summary`, `## Evidence` (tests run), `## Risks`, `## Definition-of-done check`, and `NEEDS_INFO:` (if blocked — state the exact question, do not guess).

## Orchestration model (context)
This repo is run by an SDLC-style mesh: the **operator** (a Claude Code session) plays one role per tick using the `/sdlc` project skill (`.claude/skills/sdlc/`), and **you (Jules) are the `owner` role — the only code writer**. The operator dispatches you one task, reviews your PR against acceptance criteria + the invariants below, and merges it. State is git-JSON (`state/`, `orchestrator.tools`) — never edit it.

## Conventions
- Python ≥ 3.10. Keep diffs scoped; no unrelated refactors. Audit-safe rationale only in PRs (what/why/evidence/risks) — no hidden chain-of-thought.
- Tests must be offline (mock external services). Never make live network calls in tests.

## Run commands
- Install: `pip install -r requirements.txt`
- Tests: `pytest -q`
- Mock end-to-end dry-run: `python -m orchestrator.dryrun`
- Status/monitoring: `python -m orchestrator.status`

---
name: sdlc
description: >
  Run ONE orchestration cycle (operator tick) for this Kaggle-competition project. Selects exactly one feasible role/move (planner / innovator / owner=Jules / reviewer / validator / reporter), drives the git-JSON toolkit, and closes the handoff cleanly. Use when advancing the autonomous loop: "run an sdlc cycle", "run an operator tick", "advance the competition", "review/merge the open PRs", "generate the next experiments", "plan the next move". This is the operator's per-tick playbook — the role/contract DNA lives in references/. NOTE: in THIS project, state is git-JSON via `python -m orchestrator.tools`, NOT the Excel ledger; the Excel machinery under _legacy_excel/ is reference-only and must NOT be run.
---

# sdlc — operator tick for the Kaggle orchestrator (project-integrated)

You (the Claude Code session) are the **operator**. One invocation = **one tick**: reconcile state, pick exactly one primary role/move (+ certified-independent parallel fan-out), drive the toolkit, commit. This skill provides the **role contracts**; the runtime is our **git-JSON toolkit**, not Excel.

## Critical project adaptation (read first — this differs from the generic SDLC skill)
| Generic SDLC concept | In THIS project |
|---|---|
| Router (scheduled entry) | **The operator tick** (this skill, fired by goal-loop / scheduled wakeup / Python tracker) |
| State-ledger = `scripts/state_ledger.py` (Excel) | **`python -m orchestrator.tools apply decision.json`** (git-JSON: `state/state.json` + `events.jsonl`). **Never run the Excel scripts.** |
| `state.xlsx` sheets (Tasks/Suggestions/…) | git files: `competitions/<slug>/tasks/`, `hypotheses/`, `experiments/`, `decisions/`, `submissions/`; `state/state.json`; `events.jsonl` |
| **owner** role (only code writer) | **Jules** (the worker) — the operator dispatches Jules sessions; Jules opens PRs; the operator reviews/merges |
| StatePatch schema | `operator_decision.schema.json` (validated by `tools apply`) |
| Excel writer is the only mutator | **Only the operator** mutates state (via `tools`); **only Jules** writes project code |
| Auth | Claude Code **subscription** — NO `ANTHROPIC_API_KEY` |

Full mapping: `INTEGRATION.md`. Role/capability DNA: `references/`.

## Roles (pick ONE primary per tick; references/ has the full contract for each)
- **planner** (`references/role_planner.md`) — backlog: convert hypotheses/feedback into deep Jules tasks; keep the queue full.
- **innovator** (`references/role_innovator.md`, `cap_research_miner.md`) — mine `competitions/<slug>/references/` (winner source, 217 discussions, technique-backlog) + recent results → rank new **hypotheses** (H-IDs) → propose experiments.
- **owner = Jules** (`references/role_owner.md`) — the operator does NOT write code; it dispatches a Jules session (deep-worker prompt) for the task.
- **reviewer** (`references/role_reviewer.md`, `cap_diff_analyzer.md`) — review open Jules PRs vs acceptance criteria + hard invariants; merge clean ones (`pr_merges`), else spawn a fix task.
- **validator** (`references/role_validator.md`) — judge a proposed change/experiment before spending GPU.
- **reporter** (`references/role_reporter.md`) — status digest when nothing else is productive.

## Task sizing rule (R-005 — non-negotiable)
**Every task you append to the ledger must be sized for ~1 hour of Jules work** — a single substantive deliverable a careful worker can plan, build, self-verify, and PR in one session. Calibrate against the deep-worker SOP (`prompts/jules_deep_worker.md`).

- **Too small** (≤15 min each) — **club 2–3 related items** into one task (e.g. "analyze winner training + LR schedule + loss config" → one task), keep their distinct acceptance criteria as a checklist, keep the `allowed_area` covering all the files they touch.
- **Right-sized** (~30–90 min) — ship as one task.
- **Too big** (>2 hours / a whole pipeline / >5 files of substantive new code) — **split** into independent siblings the planner can fan out in parallel: per-category, per-stage, or per-file. Each split is itself a ~1-hour task with its own acceptance criteria.
- **Clubbing safe-pair test:** items may club only if they (a) share the same `allowed_area` (or fit cleanly under one), (b) read the same references, and (c) have a coherent single deliverable. If "Summary / Evidence / DoD" would naturally fragment into separate sections per item, prefer splitting instead.
- **Concrete heuristics:** ≤1 new module + tests · ≤3 short analysis files into one digest · 1 deterministic solver per category · 1 ablation per task · 1 review-and-merge cluster per task.

The planner role enforces this every time it appends `create_task` ops; the reviewer rejects PRs that grew past scope and spawns follow-up tasks instead.

## The single work ledger (R-004 — this is the "Excel sheet", git-JSON)
ALL work lives in ONE store: `state/state.json` (+ append-only `events.jsonl`), with collections **tasks / hypotheses / experiments / suggestions / decisions / metrics** (the "sheets"). Planner & innovator **append** work here via ops (`create_task`, `create_hypothesis`, …) — never as hand-authored `.md` files. A read-only Excel view is `state/dashboard.xlsx` (`python -m orchestrator.tools dashboard`).

## Tick SOP
1. `python -m orchestrator.tools context --tick RUN-<ts>` → read the decision-context, then `python -m orchestrator.tools next` → the **role-selector** returns the next feasible role + work item from the ledger (ported `score_roles`; `references/infra_role_selector.md`).
2. **Reconcile** finished Jules PRs / experiment results into the ledger (`set_status` / `update_entity`); update best-CV.
3. **Act on the selected role/move**: unblock → review&merge a ready PR → trigger/pull a GPU run → gated submit → else **innovator** appends new hypotheses + **planner** appends new tasks to keep ~5 Jules sessions in flight. (You append work to the ledger; you do NOT scatter task files.)
4. **Parallel fan-out** (optional): dispatch additional certified-independent deep Jules tasks (disjoint `allowed_area`) up to the concurrency cap.
5. Write `decision.json` (schema `operator_decision.schema.json`) → `python -m orchestrator.tools apply decision.json` → it does the state patch, Jules dispatch (cap+locks), GPU runs, approved merges, gated submit, and git commit.
6. Audit-safe one-paragraph summary; stop.

## Hard boundaries (from `references/operating_contract.md`, adapted)
- One primary role per tick; no adjacent-repeat thrash.
- Only the operator mutates state (via `tools`); only Jules writes code; **no Excel; no API key**.
- Audit-safe rationale only (facts/decision/evidence/risks/next) — no hidden chain-of-thought in artifacts.
- Invariants: LoRA rank ≤ 32; base `Nemotron-3-Nano-30B-A3B-BF16`; answers in `\boxed{}`; submit only beats-best-CV + ≤ min(3, live cap 5)/day.
- `_legacy_excel/` is **reference only** — never execute it.

## Quality gate (before returning)
Exactly one primary move (+ only certified-independent parallel dispatches) · every state change traces to evidence · invariants + caps respected · feedback acknowledged · next move named · state committed via `tools`.

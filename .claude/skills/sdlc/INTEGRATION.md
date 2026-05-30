# SDLC skill — project integration notes (R-003)

This is the user's SDLC orchestration skill, **adapted** for the Kaggle orchestrator. We kept the role/contract DNA and **replaced the Excel state machinery with our git-JSON toolkit**. This file is the authoritative mapping.

## Why adapted, not copied verbatim
The generic SDLC skill mutates an Excel workbook (`state.xlsx`) via `scripts/state_ledger.py` and tracks work across ~21 sheets. This project already has an **event-sourced git-JSON** state layer (`orchestrator/state.py` → `state/state.json` + `events.jsonl`) driven by the operator via `orchestrator.tools`. Running both would create two conflicting sources of truth. So: **DNA kept, Excel quarantined.**

## What lives where
- `SKILL.md` — the project-integrated operator-tick playbook (this is what runs).
- `references/` — the original role/capability/infra/contract files (planner, owner, reviewer, tester, maintainer, innovator, validator, reporter; cap_*; infra_*; operating_contract, schemas, validation_policy, workbook_schema, role_permissions, role_selector). **Used as guidance**; ignore their Excel-specific mechanics, apply the concepts.
- `_legacy_excel/` — the original `scripts/` (state_ledger, workbook_*, role_selector, score_roles, lock_manager, …) + `assets/` (schemas, templates). **Reference only. Never execute.** Superseded by the toolkit.

## Concept → project mechanism (authoritative)
| SDLC concept | Project mechanism |
|---|---|
| Router / scheduled entry | Operator tick: goal-loop / scheduled wakeup / Python tracker |
| `state_ledger.py` apply-patch (Excel) | `python -m orchestrator.tools apply decision.json` (git-JSON) |
| `load_project_state.py` | `python -m orchestrator.tools context` |
| StatePatch JSON | `operator_decision.schema.json` (state_patch.operations[]) |
| Events sheet (append-only) | `state/events.jsonl` (append-only, idempotency keys) |
| Projection sheets (Tasks/…) | `state/state.json` + `competitions/<slug>/{tasks,hypotheses,experiments,decisions,submissions}/` |
| owner role (code writer) | **Jules** worker (deep-worker prompt → PR) |
| reviewer merges | `pr_merges` in the decision → `orchestrator.github_ops.merge_pr` |
| lock_manager.py | `orchestrator/locks.py` (concurrency cap + per-area locks) |
| role_selector / score_roles | operator judgment per tick (feasibility + urgency), per `references/infra_role_selector.md` |
| validation_policy (early majority) | submit gate + reviewer judgment (`orchestrator/submit_gate.py`) |
| Excel snapshots | git commits per tick |
| roles: planner/innovator/reviewer/validator/reporter | the operator plays these each tick (fused single-cycle) |
| auth | Claude Code subscription — **no `ANTHROPIC_API_KEY`** |

## How the project uses it
- The operator (Claude Code) invokes **`/sdlc`** (or follows `prompts/operator_tick.md`, which points here) to run one tick.
- AGENTS.md (Jules-facing) notes that task contracts follow the SDLC owner-role discipline.
- Do not invoke the Excel scripts; do not create `state.xlsx`.

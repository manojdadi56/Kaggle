# BUILD_PROGRESS — resume cursor for the Ralph build loop

Update every iteration. Spec: `research-jules-orchestration/BUILD_RALPH_PROMPT.md` (§4 = Definition of Done).

## Status
| DoD | Item | State |
|-----|------|-------|
| 1 | Repo scaffold + AGENTS.md | ✅ done (commit 0d8a381) |
| 4 | State layer (events/state/locks) | ▶ in progress |
| 3 | Executor registry | ⬜ todo |
| 2 | Thin clients (jules/kaggle/git) | ⬜ todo |
| 5 | Operator integration | ⬜ todo |
| 7 | Prompts + decision schema | ⬜ todo |
| 6 | Tick loop + submit gate + packaging | ⬜ todo |
| 9 | Seed initial backlog | ⬜ todo |
| 10 | Tests + mock dry-run | ⬜ todo (grows alongside each module) |
| 11 | RUNBOOK + monitoring | ⬜ todo |

## Resume cursor
Next: build `orchestrator/state.py` (event-sourced: append events.jsonl with idempotency dedup; project to state.json) + `orchestrator/locks.py` (concurrency cap + per-area path-prefix locks) + tests.

## Notes / decisions
- All external integrations use dependency-injected transports → tests run offline.
- pytest green required before each commit. Do not push during build.
- Tooling confirmed: Python 3.13.12, pytest 9.0.3, git 2.47, claude CLI 2.1.132.

# Worker pool — registry of Jules workers in this SDLC

This project's worker pool is **all in-flight Jules sessions on `manojdadi56/Kaggle`**, regardless of how they were started:

| Source | How it joins the pool |
|---|---|
| **Orchestrator dispatch** (`tools dispatch`) | Recorded automatically by the dispatcher into `state/state.json` `sessions`. |
| **Manually started** (e.g. you opened a session on jules.google directly) | Register it once with `python -m orchestrator.tools register-session <session_id> [--task <id>] [--area <allowed_area>]`. After that, the operator's poll loop treats it identically — polls it, auto-merges its PR on COMPLETED, releases its lock. |

The operator (this Claude Code session) drives the **single** SDLC tick: poll every session in the pool, auto-merge every COMPLETED PR (R-007 unsupervised), role-select, top up the pool. Every worker — dispatched or manual — gets the same treatment.

## How to send work to a specific worker
- **New work in a new session** (the usual path): the operator's `tools dispatch` picks the next READY task and creates a fresh Jules session. The new session runs the deep-worker prompt with that task's `allowed_area`.
- **Steer an existing in-flight session** (refine mid-run, add a follow-up requirement, redirect scope): `python -m orchestrator.tools sendmessage <session_id> "<prompt>"`. The deep-worker keeps running but with the new instruction folded in. Use sparingly — Jules workers do best on a single clear directive.

## Avoiding file conflicts in the pool
- Every dispatched task carries an `allowed_area` (a single file or folder). Per-area locks block the orchestrator from dispatching two concurrent sessions over the same area.
- For **manually started** sessions: when you register them, pass `--area <allowed_area>` so the lock manager treats them like dispatched sessions. If you don't, the operator will still poll/merge them, but two streams could end up editing the same file. The R-007 force-merge (`-X theirs`) resolves the conflict, but the later PR wins — design accordingly.

## The single SDLC tick (reference)
Every operator tick (whether fired by Ralph, ScheduleWakeup, /loop, or interactive) does this:
1. `tools status` — snapshot.
2. `tools context` — polls every session in the pool, auto-merges COMPLETED PRs, sets linked tasks to DONE, releases locks.
3. Clear any stale terminal sessions (`clear_session` ops).
4. `tools promote` — unblock children of DONE tasks.
5. `tools next` — role-selector.
6. Act on selected role: `tools dispatch` (owner), or innovator/planner ops (`create_hypothesis`, `create_task`).
7. `tools dashboard` — regenerate `state/dashboard.xlsx`.
8. `git add -A && git commit && git push`.

State lives in `state/state.json` + `events.jsonl`. All work is one ledger; planner/innovator append to it; each tick role-selects the next item. See `.claude/skills/sdlc/SKILL.md` for the playbook.

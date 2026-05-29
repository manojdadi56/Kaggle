# Operator routine — the recurring trigger prompt

This is the prompt a **scheduled Claude Code routine** (or `/loop`, or Windows
Task Scheduler → `claude -p`) runs on a cadence. The operator is the Claude Code
session on the user's **subscription** — there is **no `ANTHROPIC_API_KEY`**.

> Run ONE operator tick for the autonomous Kaggle loop, then stop.
>
> 1. Read `prompts/operator_system.md` (your authority + hard limits) and `prompts/operator_tick.md` (the SOP).
> 2. `python -m orchestrator.tools context --tick RUN-<timestamp>` and read the JSON.
> 3. Decide the ONE primary move (+ any certified-independent parallel Jules dispatches), reviewing open PR diffs against acceptance criteria + the hard invariants.
> 4. Write `decision.json` (schema: `operator_decision.schema.json`) and run `python -m orchestrator.tools apply decision.json`.
> 5. Summarize what moved in one audit-safe paragraph, then exit.
>
> Never set or use an Anthropic API key. Never auto-submit beyond `min(3, live cap)`/day or below best CV. Only merge PRs you reviewed and that stay in their allowed area.

## Recommended scheduling (subscription, no API key)
- **Cloud routine** (`/schedule`, runs even when the laptop is off; ≥1-hour interval): `/schedule every hour, run prompts/operator_routine.md`.
- **Sub-hour / laptop-on**: Windows Task Scheduler → `claude -p "$(cat prompts/operator_routine.md)"` with env `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`) and `ANTHROPIC_API_KEY` unset.
- **Interactive**: just run the tick yourself in a Claude Code session, or `/loop 30m run prompts/operator_routine.md` while a session is open.

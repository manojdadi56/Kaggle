# Quickstart — Using the sdlc Skill

Read this when the user is new to the skill or wants a fast orientation.

## What this skill does in one sentence

It runs **one** SDLC role per invocation against a workbook-tracked project and updates state through an append-only audit trail.

## Before the first cycle

1. Make sure the projects root exists: `~/.sdlc/projects/` (created automatically the first time the skill runs).
2. Pick a `project_id` (uppercase, no spaces). Example: `MYPROJECT`.
3. Initialize a workbook:
   ```bash
   python3 ~/.claude/skills/sdlc/scripts/state_ledger.py init \
     --workbook ~/.sdlc/projects/MYPROJECT/state.xlsx \
     --project-id MYPROJECT
   ```
4. Optionally drop a `project.yaml` and `AGENTS.md` from `assets/templates/` into `~/.sdlc/projects/MYPROJECT/`.

## Running one cycle

The user invokes the skill (e.g. via slash-command or natural language) and the cycle walks the 5 stages in `SKILL.md`. Each cycle:

- Loads project state into a JSON snapshot (read-only).
- Selects exactly one role via `score_roles.py`.
- Reads the matching `references/role_<role>.md` and any capability references it needs.
- Produces `RunResult` + `StatePatch`.
- Validates and applies the patch.
- Closes attendance.

## Inspecting state

```bash
python3 ~/.claude/skills/sdlc/scripts/load_project_state.py \
  --workbook ~/.sdlc/projects/MYPROJECT/state.xlsx \
  --limit-events 50
```

## Scheduling cycles

To run cycles on a cadence (e.g. every 90 minutes), use the `schedule` skill or the `scheduled-tasks` MCP and have it invoke `/sdlc cycle MYPROJECT`. Confirm the schedule with the user before creating it — scheduled tasks run autonomously.

Recommended cadences:
- **Active development**: `90m` while working hours, paused overnight.
- **Maintenance projects**: daily at the same time.
- **Manual only**: `manual` (cadence stored in attendance for telemetry; no automatic firing).

## Recovery

If a projection sheet looks corrupted:

```bash
python3 ~/.claude/skills/sdlc/scripts/workbook_recover.py \
  --workbook ~/.sdlc/projects/MYPROJECT/state.xlsx \
  --dry-run
```

Then drop `--dry-run` to actually rebuild. A timestamped backup is created automatically.

## What the user sees per cycle

A Handoff frame:

```
Run ID: RUN-20260508-103015
Role: planner
Work item: PHASE-001 backlog triage
Status: complete
Saturation status: complete
What moved forward: 3 blocked tasks reclassified; 2 follow-up tasks created
Evidence: Events 1875-1880; Tasks rows 53-54
Artifacts: projects/MYPROJECT/exports/triage-RUN-20260508-103015.md
Risks: PHASE-002 dependency unclear
StatePatch summary: 2 create_task, 3 update_status, 1 register_artifact
Next recommended role: owner
```

## Common pitfalls

- **Don't edit `state.xlsx` directly.** Use `UserContext` or `UserFeedback_Inbox` sheets — those are user-input rows the planner will pick up.
- **Don't call sub-roles directly.** The skill's design requires the router stage to select roles. Bypassing it skips lock/permission/adjacency checks.
- **Don't request hidden chain-of-thought.** Audit-check will fail the run.

## Where to look for deeper context

- `references/operating_contract.md` — authority, audit-safe reasoning, prompt architecture
- `references/schemas.md` — RunEnvelope / RunResult / StatePatch shapes
- `references/workbook_schema.md` — the 22 sheets and their meaning
- `references/role_<role>.md` — the role's full SOP
- `references/infra_<unit>.md` — infrastructure contracts (state-ledger, lock-manager, etc.)
- `references/cap_<capability>.md` — capability playbooks (diff-analyzer, task-decomposer, etc.)

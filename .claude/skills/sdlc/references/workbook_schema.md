# Workbook Schema — Excel state.xlsx Layout

Every project has one `state.xlsx` workbook at `projects/<project-id>/state.xlsx`. The authoritative schema is in `scripts/workbook_schema.py:SHEETS` — this file documents intent.

## Core Pattern

```text
Events  = append-only truth
Other sheets = current projections / views derived from Events
```

If a projection sheet is corrupted, it can be rebuilt from `Events` alone (`scripts/workbook_recover.py`). **Therefore: never modify Events except by appending.**

## Sheets

| Sheet | Purpose | Update Mode |
|---|---|---|
| `Events` | Append-only record of every meaningful state change | event-only |
| `Runs_Attendance` | Run lifecycle and outcome | event + projection |
| `Locks` | Current locks and stale/reclaim history | projection with events |
| `RoleHistory` | Role choices and reasons | projection |
| `Phases` | High-level goals | projection |
| `UserStories` | User stories under phases | projection |
| `Tasks` | Owner/support tasks and statuses | projection |
| `SupportWork` | Non-owner support work | projection |
| `TaskProgressDocs` | Progress docs registry | projection |
| `Suggestions` | Maintainer/innovator/reviewer/tester suggestions | projection |
| `Validations` | Validator votes and majority status | projection |
| `Decisions` | Final accepted/rejected directions | projection |
| `UserFeedback_Inbox` | User-editable feedback intake | user input + projection |
| `UserContext` | User-provided context | user input |
| `ArtifactRegistry` | Files, logs, commits, reports | projection |
| `InnovationLog` | Research notes and source annotations | projection |
| `MaintainerFindings` | Simplification / reuse / cognitive-load findings | projection |
| `ReviewFindings` | Review findings | projection |
| `TestFindings` | Test results and coverage gaps | projection |
| `ProjectMemory_Index` | Durable memory pointers | projection |
| `Metrics` | Flow, quality, review, test, cognitive-load metrics | projection |
| `Dashboard` | Human-readable summary | generated view |

## Event Row Required Fields

Every projection update has a matching `Events` row with:

- `event_id` (auto-generated as `EVT-<run_id>-<row_index>`)
- `project_id`
- `run_id`
- `created_at` (ISO 8601 UTC)
- `event_type` (UPPERCASE, e.g. `REVIEW_COMPLETED`)
- `entity_type` (e.g. `task`, `suggestion`, `run`)
- `entity_id`
- `summary` (one line, audit-safe)
- `idempotency_key`
- `details_json` (optional structured payload)

## Recovery Rule

If a projection sheet is missing or inconsistent:

1. Drop and recreate the sheet from headers.
2. Replay all relevant `Events` rows in `created_at` order.
3. Apply each event's mutation to the projection.
4. Re-derive computed columns (counts, dashboards).

`scripts/workbook_recover.py` automates this.

## Atomicity

`scripts/state_ledger.py` writes the workbook to a temp file in the same directory, fsyncs, then atomically renames over the live workbook. This ensures readers never see a partial write.

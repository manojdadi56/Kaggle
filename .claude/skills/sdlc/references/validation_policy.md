# Validation Policy

## Workflow

```text
Suggestion created
  -> Planner triages and classifies size
  -> Validation request created
  -> Validator runs one pass at a time (one vote per run)
  -> Early majority check
  -> Planner finalizes decision
  -> Owner task created only after accepted decision
```

## Required Vote Counts by Change Size

| Change Size | Required Passes | Majority |
|---|---|---|
| `minor` | 1 | 1 |
| `small` | 3 | 2 |
| `medium` | 5 | 3 |
| `large` | 7 | 4 |
| `very_large` | 9 | 5 |

(Authoritative values: `scripts/workbook_schema.py:VALIDATION_COUNTS`.)

## Early Stop Logic

```text
if accept_votes >= majority:
    accept immediately
if reject_votes >= majority:
    reject immediately
if remaining_votes_possible cannot change outcome:
    decide immediately
```

## Validator Perspectives (rotate across runs)

```
technical_fit
maintainability
testability
security
operations
migration_risk
business_value
cost_to_value
innovation_relevance
```

A given suggestion's validation passes should rotate perspectives to avoid repeated viewpoints.

## Guardrails

- Owner tasks are created **only** after an accepted decision or explicit user override.
- A validator may not vote twice on the same suggestion.
- A validator may not vote on a suggestion they themselves authored.
- Any rejection must include `risk_notes` referencing concrete evidence.

## Change Size Classification (planner default heuristics)

- `minor`: < 25 LOC, single file, no new dependencies, no schema change.
- `small`: < 100 LOC, ≤ 3 files, no schema or interface change.
- `medium`: < 400 LOC, ≤ 10 files, may include test scaffolding, no breaking change.
- `large`: < 1500 LOC, includes interface or schema change, or cross-cutting refactor.
- `very_large`: ≥ 1500 LOC, breaking change, multi-day work, or external integration.

These are guides — the planner records the chosen size with rationale.

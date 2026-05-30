# RunEnvelope, RunResult, StatePatch — Schemas

These are the structured-data contracts every role stage must respect.

## RunEnvelope

The router builds this and hands it to the selected role.

```json
{
  "run_id": "RUN-20260430-101500",
  "project_id": "PROJECT-A",
  "triggered_at": "2026-04-30T10:15:00+05:30",
  "cadence": "90m",
  "previous_role": "owner",
  "selected_role": "reviewer",
  "role_selection_reason": "Owner completed TASK-0042 and marked it READY_FOR_REVIEW; owner cannot repeat; reviewer has no conflict lock.",
  "work_item_id": "REVIEW-0091",
  "task_id": "TASK-0042",
  "phase_id": "PHASE-001",
  "story_id": "STORY-0017",
  "locks_required": ["workbook_write_lock", "review_lock:TASK-0042"],
  "permissions": {
    "can_edit_code": false,
    "can_write_excel_directly": false,
    "can_create_state_patch": true,
    "can_commit": false,
    "can_browse": false
  },
  "definition_of_done": [
    "Review diff against acceptance criteria",
    "Record risks and missing tests",
    "Create follow-up tasks if required",
    "Produce state patch",
    "Write progress note"
  ]
}
```

### Required Semantics

- `run_id` is globally unique. Format: `RUN-<YYYYMMDD>-<HHMMSS>`.
- `project_id` maps to a directory under `projects/`.
- `previous_role` is used to enforce the no-adjacent-repeat rule.
- `selected_role` is exactly one role.
- `role_selection_reason` is human-readable.
- `locks_required` is checked before role work begins.
- `permissions` are enforced by the policy-gate stage.
- `definition_of_done` is role-specific and task-specific.

## RunResult

Every role stage returns this to the router.

```json
{
  "run_id": "RUN-20260430-101500",
  "role": "reviewer",
  "status": "complete | blocked | saturated | needs_info | failed",
  "saturation": {
    "saturated": false,
    "completed": ["..."],
    "remaining": ["..."],
    "resume_cursor": "..."
  },
  "high_level_completed": "Reviewed TASK-0042; 2 findings created; 1 follow-up task proposed.",
  "rationale": {
    "facts": "...",
    "decision": "...",
    "evidence": "...",
    "risks": "...",
    "next": "..."
  },
  "state_patch_ref": "patch.json",
  "artifacts": [
    {"path": "projects/PROJECT-A/exports/review-RUN-20260430-101500.md", "type": "review_note", "sha256": "..."}
  ],
  "next_recommended_role": "owner",
  "memory_candidates": [],
  "errors": []
}
```

## StatePatch

The role stage emits this; the policy-gate validates it; the state-ledger applies it.

```json
{
  "patch_id": "PATCH-RUN-20260430-101500",
  "run_id": "RUN-20260430-101500",
  "project_id": "PROJECT-A",
  "operations": [
    {
      "op": "append_event",
      "data": {
        "event_type": "REVIEW_COMPLETED",
        "entity_type": "task",
        "entity_id": "TASK-0042",
        "summary": "Review completed with changes requested."
      },
      "idempotency_key": "RUN-20260430-101500:REVIEW-0091:event"
    },
    {
      "op": "update_status",
      "sheet": "Tasks",
      "entity_id": "TASK-0042",
      "from_status": "READY_FOR_REVIEW",
      "to_status": "CHANGES_REQUESTED",
      "expected_version": 7,
      "idempotency_key": "RUN-20260430-101500:TASK-0042:MARK_CHANGES_REQUESTED"
    },
    {
      "op": "create_task",
      "data": {
        "task_id": "TASK-0049",
        "title": "Add regression test for concurrent token refresh",
        "created_from": "REVIEW-0091",
        "role_owner": "owner",
        "status": "READY"
      },
      "idempotency_key": "RUN-20260430-101500:TASK-0049:create"
    }
  ]
}
```

### Operation Classes

| op | Targets sheet | Purpose |
|---|---|---|
| `append_event` | `Events` | Add an immutable event row |
| `update_status` | any | Status transition with optimistic locking |
| `update_row_by_id` | any | Generic field updates with version bump |
| `create_task` | `Tasks` | New task |
| `create_support_work` | `SupportWork` | Support / non-owner work item |
| `create_suggestion` | `Suggestions` | Reviewer/maintainer/etc. suggestion |
| `create_validation` | `Validations` | Validator vote |
| `create_decision` | `Decisions` | Final decision (planner) |
| `register_artifact` | `ArtifactRegistry` | File / commit / report |
| `add_metric` | `Metrics` | Flow / quality / cognitive-load metric |
| `add_memory_candidate` | `ProjectMemory_Index` | Durable memory pointer |
| `start_attendance` / `close_attendance` | `Runs_Attendance` | Run lifecycle |

Every operation **automatically appends a matching Events row** (the state-ledger does this transparently — do not also emit a separate `append_event` for the same operation, only for events that are not tied to one of the above ops).

### Idempotency Keys

Every operation MUST carry an `idempotency_key`. The state-ledger silently skips operations whose key is already present in the Events sheet. Keys must be deterministic from `(run_id, entity, action)` so retries collapse cleanly.

### Rejection Cases (policy-gate must reject)

- Missing required fields.
- Role not allowed to perform this op (per `references/role_permissions.md`).
- Required lock not held.
- Status / version mismatch (optimistic-lock failure).
- Duplicate idempotency key (warn but don't fail).
- Dependency violation (e.g. tester output without code change present).
- Validation majority already reached for the suggestion.
- Owner task completion lacks evidence (no progress doc, no test result).

## Status Transition Vocabulary

```
NOT_STARTED -> READY -> CLAIMED -> IN_PROGRESS -> SATURATED | BLOCKED
                                              -> READY_FOR_REVIEW -> CHANGES_REQUESTED
                                                                  -> READY_FOR_TEST
                                              -> DONE_PENDING_REVIEW
                                              -> DONE_PENDING_TEST
                                              -> DONE
SUPERSEDED | REJECTED | VALIDATION_REQUIRED | ACCEPTED   (administrative)
```

Allowed values are pinned in `scripts/workbook_schema.py:STATUS_VALUES`.

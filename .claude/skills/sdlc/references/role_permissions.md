# Role Permission Matrix

| Operation | Planner | Owner | Reviewer | Tester | Maintainer | Innovator | Validator | Reporter | StateLedger |
|---|---|---|---|---|---|---|---|---|---|
| Edit code | No | **Yes** | No | No | No | No | No | No | No |
| Commit | No | Yes (if policy allows) | No | No | No | No | No | No | No |
| Create task proposal | Yes | Limited | Yes | Yes | Yes | Yes | No | No | No |
| Create suggestion | Yes | Limited | Yes | Yes | Yes | Yes | No | No | No |
| Vote validation | No | No | No | No | No | No | **Yes** | No | No |
| Final decision | **Yes** | No | No | No | No | No | No | No | No |
| Direct Excel write | No | No | No | No | No | No | No | No | **Yes** |
| Submit StatePatch | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Applies only |
| Browse research sources | Limited | No (default) | Limited | No (default) | Limited | **Yes** | Limited | No (default) | No |
| Register artifact | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Applies only |

## Hard Invariants

- Only **Owner** edits code.
- Only **StateLedger** (the `scripts/state_ledger.py` invocation) writes Excel.
- **Planner** finalizes decisions after validation.
- **Validator** votes but does not implement.
- The router orchestrates but does not directly mutate project code or Excel.

## Default Permission Block

Every RunEnvelope.permissions block defaults to `false` for any operation not explicitly granted. The role stage must check permissions before acting; the policy-gate enforces them again before state-ledger applies the patch.

```json
{
  "can_edit_code": false,
  "can_write_excel_directly": false,
  "can_create_state_patch": true,
  "can_commit": false,
  "can_browse": false
}
```

Only Owner gets `can_edit_code: true` and conditionally `can_commit: true`. Only the state-ledger stage gets `can_write_excel_directly: true`.

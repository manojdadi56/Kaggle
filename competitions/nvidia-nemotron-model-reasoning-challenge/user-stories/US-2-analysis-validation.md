# US-2 — Analysis validation (gate before GPU)

> As the system, I want analysis conclusions validated as reproducible, so we don't build training on a misread.

Tasks: TASK-2.1 (local CV eval harness mirroring host scoring) · TASK-2.2 (packaging smoke-test on dev_local: dummy rank-≤32 adapter → valid zip) · TASK-2.3 (operator: confirm the winner recipe runs end-to-end on a toy model before committing GPU hours).
Gate: must pass before US-4 spends real GPU.

# TASK-R11 — Meta-analysis of the 217 discussion threads
- hypothesis: H-007
- story: US-1
- actor: jules
- mode: deep
- status: todo
- allowed_area: competitions/nvidia-nemotron-model-reasoning-challenge/references/analysis-discussions.md
- starting_branch: main
- gpu: no
- dependencies: none
- parallel_with: TASK-R1, TASK-R8, TASK-R10, TASK-R12

## Goal
Read across the 217 `references/discussion-*.md` threads and produce a single ranked intelligence digest: techniques that worked, ideas that were tried-and-failed (to avoid), scoring pitfalls, data tricks, and any leaked category insights. Cross-reference against the winner's approach.

## Mine first
All `references/discussion-*.md`, `references/DIGEST-community.md`, `references/technique-backlog.md`.

## Acceptance criteria
- `references/analysis-discussions.md`: ranked "do" list + "avoid" list, each item citing the discussion id(s); a short section "deltas vs the winner approach" and "new hypotheses to test" (feed the operator's hypothesis ledger).

## Definition of done
Digest committed via one PR; every claim cites a discussion id; ends with ≥5 concrete candidate hypotheses for the operator to queue.

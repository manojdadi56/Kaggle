# 08 — Progress Snapshots

## Snapshot 1 — investigation complete (2026-05-30)
- **Findings:** 36 logged (F-001..F-036). By confidence: Well-established ~28, Supported ~6, Plausible ~2.
- **Sources:** 31 logged (S-001..S-031); 1 live primary probe (S-001) decisively confirmed the Jules contract and that the target repo is connected.
- **Assumptions:** 15 (A-001..A-015). Validated 6, Invalidated 2 (A-001 Jules-can-train, A-002 repo-not-connected), Active 5, Flagged 2.
- **Open questions:** 13 (Q-001..Q-013). High-priority: Q-001 (submission cap), Q-002 (automation policy), Q-010 (GPU), Q-011 (scope/time), Q-012 (free-GPU feasibility) — most escalated to the user or to a setup-time live check.
- **Contradictions:** 5 analyzed (C-001..C-005); 4 resolved, 1 (cap) deferred to runtime read.
- **Trajectory revision:** The question evolved from "wire 3 APIs to make Jules do the work" to "wire 3 APIs **plus a GPU executor**, baseline-first, under a deadline" — driven by F-024 (Jules has no GPU; the comp is GPU training).
- **Next:** Synthesis → REPORT (implementation plan) + surface the 3 user decisions.

## Snapshot 2 — synthesis complete (2026-05-30)
- All 11 workspace artifacts written + REPORT. Steel-man engaged (6 counter-arguments; 2 conceded design changes: baseline-first sequencing, git-JSON-not-Excel as state of record).
- Deliverable state: **implementation plan ready; awaiting 3 user decisions (D-1 compute, D-2 scope/sequencing, D-3 feedback channel) before any code.**

## Snapshot 3 — built, live-proven, and re-architected (2026-05-30, same day)
- **Built:** full orchestrator (9+ commits) pushed to GitHub `main`; 84 pytest green; mock dry-run exits 0.
- **Live-proven:** real Jules sessions via our client — TASK-2.1/1.3/1.2 COMPLETED → PRs #1/#2/#3 **merged** via the new `github_ops.merge_pr`; 3 more sessions (1.1/3.1/4.0) ran in parallel. Tier confirmed **paid** (4+ concurrent; cap set to 15). Jules internet confirmed **yes** (Q-015 resolved live).
- **R-001 re-architecture:** operator = Claude Code session on the subscription (NO API key); Python = toolkit (`orchestrator.tools`); trigger = scheduled Routine / Task-Scheduler `claude -p` via OAuth token. Findings F-039..F-044, source S-032, contradiction C-006, assumptions A-005(superseded)/A-019/A-020, Q-016/Q-017, glossary G-007/G-008/G-019..G-022.
- **Findings:** now 44 (F-001..F-044). **Sources:** 32. **Open Qs:** 17 (Q-015 resolved). 
- **Next:** stand up the recurring operator trigger (routine or Task Scheduler) + human-gated Phase 0 (rotate Jules/Kaggle keys, confirm submission cap) before live submits.

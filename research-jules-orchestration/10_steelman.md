# 10 — Steel-Man (strongest counter-case to the plan)

Before finalizing, argue against the emerging plan as a sharp skeptic would.

## Counter-argument 1 — "This is over-engineered for a 16-day window. The orchestrator will eat the whole runway."
A full SDLC-style mesh (event-sourced state, planner/worker prompts, policy gate, locks) is weeks of work. The competition ends **2026-06-15**; today is **2026-05-30**. Every hour on orchestration is an hour not spent training a better adapter. A human forking `tonghuikang/nemotron` (F-026), training once, and submitting could outscore the autonomous system before it takes its first tick.
- **Engagement — CONCEDED, and it reshapes sequencing.** The plan must be **baseline-first**: get a *manual* end-to-end submission (fork winner → train → package zip → submit) working in days 1–2, *then* automate around the proven pipeline. The orchestrator is the long-game asset (reused across competitions), but it must not block a first leaderboard score. This becomes Decision D-2 and Phase 0 of the roadmap.

## Counter-argument 2 — "Jules can't train, so what is it even for here?"
If the bottleneck is GPU training (F-024) and Jules has no GPU (F-008), Jules is sidelined from the core task. Maybe Jules adds little for *this* competition.
- **Engagement — PARTIALLY CONCEDED.** Jules' value is real but narrower than the original vision: it authors and iterates the **non-GPU** code that surrounds training — synthetic data generation, data filtering/curation, the training script itself, the packaging/validation script, the eval harness, prompt-template experiments. That is a large, parallelizable, genuinely useful share of the work, and it is exactly what an async PR-based agent is good at. But we must not pretend Jules "does the competition"; the GPU executor does the decisive step. The architecture reflects this split honestly.

## Counter-argument 3 — "Kaggle free GPU can't train a 30B MoE competitively, so the autonomous loop produces junk submissions."
2×T4 in 4-bit is the floor; the winner used stronger compute. An automated loop that submits weak free-GPU adapters wastes the (possibly 1–3/day) submission budget.
- **Engagement — VALID; mitigated by the submission gate.** This is why the user's submit policy (auto only if it beats current best; cap at 3/day; else queue for approval) is correct, and why we read remaining submissions at runtime (Q-001). The loop's job on free GPU is to validate the *pipeline* and produce a *baseline*; competitive scores likely need a compute decision (D-1). The system never burns a submission on a candidate that doesn't beat local CV.

## Counter-argument 4 — "Event-sourced Excel state is brittle on Windows — the user opens the file and the writer crashes."
A-009/Q-013: Excel holds an exclusive lock when open. A single-writer design assumes the file is always writable.
- **Engagement — CONCEDED; design changed.** State of record is **git-committed JSON/markdown** (`state.json`, `tasks/*.md`, `decisions/*.md`), which never has a lock problem. `feedback.xlsx` is treated as an **inbox the operator reads and the user edits** — and to avoid the lock trap entirely, the *primary* feedback channel is the Claude chat (operator transcribes into a git-tracked `feedback.md`/`.xlsx`), exactly as the user described. Excel becomes optional sugar, not the source of truth.

## Counter-argument 5 — "Three vendor dependencies that are all <1 year old will drift and break unattended."
Jules `v1alpha`, Kaggle MCP (~Nov 2025), Agent SDK billing change (2026-06-15). Unattended systems rot when APIs move.
- **Engagement — VALID; bounded.** Mitigations: pin to the documented REST surface (not the unofficial SDK), prefer the mature kaggle **CLI** for the load-bearing submit (F-020), centralize each contract behind one thin client module so a drift fixes in one place, and keep a human-readable run log so failures are diagnosable. The `2026-06-15` Agent-SDK billing change is noted so cost doesn't surprise mid-competition.

## Counter-argument 6 — "'No supervision' is impossible here — first-run auth, rule confirmation, and compute choice all need a human."
The user wants seamless, minimal supervision (C-005).
- **Engagement — REFRAMED, not refuted.** Steady-state supervision can be near-zero: once set up, the loop ticks, Jules PRs land, the operator reviews/merges/queues, and the user only approves submissions beyond the daily budget — via chat. What *cannot* be zero is the **one-time setup**: connect creds, confirm the submission cap/rules (Q-001/Q-002), and choose the compute path (D-1). The plan separates "one-time human setup" from "steady-state autonomy" so the promise is honest.

## Residual unresolved (→ Open Questions / Decisions)
- Whether free-GPU training yields any competitive signal (Q-012).
- The real submission cap (Q-001) and automation-policy clause (Q-002).
- The compute path (D-1) and build-scope/sequencing (D-2) — **user decisions**.

# INDEX — Autonomous Kaggle Loop (Jules × Claude × local orchestrator)

Research workspace for the implementation plan. **The plan is [REPORT.md](REPORT.md).**

## Current state
- **Phase:** BUILT + LIVE-PROVEN + re-architected (R-001). The system exists on GitHub `main`, runs real Jules sessions, and merged 3 real PRs. Now: stand up the recurring operator trigger + human-gated Phase-0 setup.
- **Last updated:** 2026-05-30.
- **R-001 (operator execution):** the operator is the **Claude Code session on the user's subscription — NO `ANTHROPIC_API_KEY`** (if set it overrides the subscription, F-039). Python is a **toolkit** (`orchestrator.tools`: context/apply/status) the operator drives. Recurring trigger = scheduled Routine (`/schedule`, cloud, ≥1h, no key) or Task-Scheduler `claude -p` via `CLAUDE_CODE_OAUTH_TOKEN`.
- **Decisions locked:** D-1 = 40 GB 2-GPU box primary (configure later) + Kaggle free GPU + RTX-3050 dev-only + paid-cloud upgrade (multi-account pooling rejected, F-037); D-2 = baseline-first; D-3 = chat feedback; repo = `C:\Users\Manoj Sai\Ksggle` (pushed).
- **Live status:** Jules tier **paid** (cap 15); Jules **has internet** (Q-015 resolved); PRs #1/#2/#3 merged via `github_ops`; 84 pytest green; mock dry-run exits 0.
- **Immediate next action:** rotate Jules/Kaggle keys into `.env`, keep `ANTHROPIC_API_KEY` unset, confirm submission cap (Q-001/Q-002), set up the routine/Task-Scheduler trigger. Then unattended.

## The one-paragraph answer (R-001)
The **operator is the Claude Code session on the user's subscription** (no API key). On a recurring trigger (a scheduled Routine, or Task-Scheduler `claude -p` via an OAuth token), it runs one **tick**: `tools context` → review open PRs + decide → `tools apply`. That drives a pure Python **toolkit** which triggers **Jules** (worker, `POST /v1alpha/sessions` with `AUTO_CREATE_PR` + auto-approved plans) to author non-GPU code and open PRs, **reviews/merges** those PRs, drives a **GPU executor** (Kaggle / the 40 GB box — Jules has no GPU and the comp is LoRA training), packages the adapter, and submits within budget. State is git-committed JSON/markdown using the SDLC event-sourced, idempotent, single-writer patterns. Real constraints: **compute** + **~16-day deadline** → **baseline-first**.

## Key metrics
- Findings **36** · Sources **31** (1 live primary probe) · Assumptions **15** (2 invalidated) · Open Qs **13** (5 High) · Contradictions **5** · Steel-man counter-args **6**.

## Navigation
| File | What's in it |
|------|--------------|
| **[REPORT.md](REPORT.md)** | **The implementation plan** — architecture, contracts, state machine, trigger prompts, roadmap, decisions |
| **[initial_backlog.md](initial_backlog.md)** | **The starting user stories** — US-1 analyze solutions → US-2 validation → US-3 synthetic data → US-4 training → US-5 debug/improve; dependency + parallelism map |
| [00_research_plan](00_research_plan.md) | Question, scope, methodology, gates |
| [01_pre_registration](01_pre_registration.md) | Expectations vs reality (4/7 disconfirmed — the surprises) |
| [02_findings_log](02_findings_log.md) | All 36 findings (F-001..F-036) with sources + confidence |
| [03_assumption_log](03_assumption_log.md) | 15 assumptions incl. the two invalidated cornerstones |
| [04_open_questions](04_open_questions.md) | 13 open questions + how to resolve each |
| [05_contradictions](05_contradictions.md) | 5 conflicts and their resolutions |
| [06_source_log](06_source_log.md) | 31 sources with quality ratings |
| [07_glossary](07_glossary.md) | Terms (Jules Source/Session, operator, GPU executor, LoRA, StatePatch…) |
| [08_progress_snapshots](08_progress_snapshots.md) | Checkpoints |
| [09_meta_log](09_meta_log.md) | Process notes, dead ends, what worked |
| [10_steelman](10_steelman.md) | The strongest counter-case (6 args; 2 design changes adopted) |

## The five things that matter most
1. **Jules cannot train the model** (no GPU) and the competition **is** GPU LoRA training → a separate **GPU executor** is mandatory (F-024 × F-008).
2. The Nemotron submission is a **LoRA adapter zip**, host-scored — not a predictions CSV (F-021/F-022).
3. The Jules API contract is **clean and verified live**; the target repo is already connected (F-001/F-016).
4. The dominant risks are **compute** and **~16 days left** — so **baseline-first**, automate second (F-024/F-025, steel-man #1).
5. **Submission cap & automation policy are unconfirmed** (login-gated) — read the cap live, never hard-code; confirm before unattended submits (Q-001/Q-002).
6. **(R-001) The operator is the Claude Code session on the subscription — no API key.** Python is a toolkit it drives; `ANTHROPIC_API_KEY` must stay unset; recurring trigger = a scheduled Routine or Task-Scheduler `claude -p` via `CLAUDE_CODE_OAUTH_TOKEN` (F-039..F-044).

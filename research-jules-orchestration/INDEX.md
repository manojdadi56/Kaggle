# INDEX — Autonomous Kaggle Loop (Jules × Claude × local orchestrator)

Research workspace for the implementation plan. **The plan is [REPORT.md](REPORT.md).**

## Current state
- **Phase:** 4 (Final report delivered); all decisions LOCKED → awaiting user green light to start Phase 0/1 implementation.
- **Last updated:** 2026-05-30.
- **Decisions locked:** D-1 = pluggable trainer pool — **user's 40 GB 2-GPU box = primary (configure later, Q-014/A-017)** + Kaggle free GPU (2×T4, available now) + RTX-3050-4GB dev-only + paid-cloud upgrade (multi-account pooling rejected, F-037); D-2 = baseline-first; D-3 = chat-only feedback; repo = `C:\Users\Manoj Sai\Ksggle`.
- **Concurrency/isolation:** parallel Jules sessions allowed for certified-independent tasks (cap = tier limit, free = 3; per-area locks); each competition is a self-contained `competitions/<slug>/` folder, one active at a time.
- **Handoff:** the user will trigger the actual build in a **separate session** with a stated goal; this workspace + project memory are the spec to load first.
- **Immediate next action:** Phase 0 (creds/`.env` + confirm submission cap & automation policy on gated pages, Q-001/Q-002) → Phase 1 (manual baseline submission). No build until user says go.
- **Verification highlight:** Jules API contract confirmed **live**; `manojdadi56/Kaggle` is **already a connected Jules source** (no GitHub-App setup needed).

## The one-paragraph answer
A local Python **orchestrator** ticks continuously: it triggers **Jules** (worker, via `POST /v1alpha/sessions` with `AUTO_CREATE_PR` + auto-approved plans) to author non-GPU code and open PRs, and wakes **Claude Code headless** (operator) each tick to plan, review/merge PRs, drive a **GPU executor** (Kaggle Notebooks — because Jules has no GPU and the competition is LoRA training), package the adapter, and submit within a budget. State lives as git-committed JSON/markdown using the SDLC skill's event-sourced, idempotent, single-writer, 8-surface-prompt patterns. The real constraints are **compute** and a **~16-day deadline**, so the plan is **baseline-first**.

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

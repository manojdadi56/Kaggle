# BUILD LOOP — Ralph prompt for building the Autonomous Kaggle Orchestrator

> This file is fed (effectively) identically every Ralph iteration. It is **idempotent**: each pass you re-orient from disk + git, do the next unfinished step, verify, commit, and exit. You only finish by emitting the promise tag (see §6). Do **one focused step per iteration** — small diffs, always green.

---

## 1. GOAL

Build and self-test the **autonomous Kaggle-competition orchestration system** specified in `research-jules-orchestration/REPORT.md` (+ `INDEX.md`, `initial_backlog.md`), inside the `manojdadi56/Kaggle` repo cloned at `C:\Users\Manoj Sai\Ksggle`.

Deliver a working **local Python orchestrator** that triggers **Jules** (worker) and **Claude Code headless** (operator), with a **pluggable GPU-executor registry**, **event-sourced git state**, the **two trigger prompts**, the **initial backlog seeded**, and a **mock-based end-to-end dry-run that passes** — **without ever making a real Jules session, real Kaggle submission, real kernel push, or any live network call to Jules/Kaggle/Anthropic.** Those live steps stay human-gated (Phase 0/1).

First competition target: **NVIDIA Nemotron Model Reasoning Challenge** (LoRA-adapter training, rank ≤ 32, base `Nemotron-3-Nano-30B-A3B-BF16`, answers in `\boxed{}`; deadline 2026-06-15).

## 2. EACH ITERATION — procedure
1. **Re-orient (always):** read `MEMORY` (auto-loaded), `research-jules-orchestration/INDEX.md`, `REPORT.md` (§2 architecture, §4 contracts, §5 state machine, §6 prompts, §7 roadmap), `initial_backlog.md`, and `BUILD_PROGRESS.md` if it exists. Run `git log --oneline -15` and inspect the tree to see what's already built.
2. **Pick the next unfinished item** from the Definition of Done (§4), respecting dependencies. If `BUILD_PROGRESS.md` names a resume cursor, start there.
3. **Implement that one item** — scoped diff only, within `C:\Users\Manoj Sai\Ksggle`. Follow REPORT.md exactly (field names, op names, flags, tool names).
4. **Verify:** run `pytest -q` (and the mock dry-run once it exists). Fix until green before committing.
5. **Record:** update `BUILD_PROGRESS.md` (done / in-progress / next-cursor / evidence). Commit locally with a clear message (`build: <item>`). **Do not push** during the build.
6. **Exit.** Ralph re-feeds this prompt; the next pass continues from your committed work.

## 3. GUARDRAILS (non-negotiable)
- **No live external calls.** All Jules/Kaggle/Anthropic interactions in code are real, but **tests and the dry-run use mocks/fakes** — zero network. Never create a real session, submit, or kernel push.
- **No secrets in git.** Ship `.env.example` with placeholders; `.gitignore` must exclude `.env`. Never write the real Jules/Kaggle/Anthropic keys into any committed file. (Reminder in README: rotate the keys pasted in chat.)
- **Respect the invariants** the system enforces: LoRA rank ≤ 32, base model fixed, `\boxed{}` answers, submit only beats-best-CV + within daily cap (cap read at runtime, never hard-coded), one competition active, parallel Jules sessions only for certified-independent tasks (cap = tier limit, per-area locks).
- **No human-judgment blocking.** On a design ambiguity, choose the safest default consistent with `REPORT.md`, write a 4-line ADR in `competitions/<slug>/decisions/`, and continue.
- **Single-writer & authority separation** (REPORT §2): only the operator writes state; only Jules writes project code; the orchestrator writes only its run log.
- Keep diffs small; tests green every commit; audit-safe commit messages (what/why/evidence), no hidden chain-of-thought.

## 4. DEFINITION OF DONE (the build is complete when ALL are true)
1. **Repo scaffold** per REPORT §5: `orchestrator/`, `prompts/`, `state/`, `competitions/nvidia-nemotron-model-reasoning-challenge/{README.md,plan.md,tasks/{todo,in-progress,done},user-stories,decisions,experiments,kernels,submissions/{pending,submitted},references,data}`, `feedback.md`, `.env.example`, `.gitignore`, `AGENTS.md`.
2. **Thin clients:** `orchestrator/jules_client.py` (REST: list_sources, create_session, get_session, list_activities, send_message — header `X-Goog-Api-Key`, base `…/v1alpha`, `AUTO_CREATE_PR`, `requirePlanApproval:false`), `orchestrator/kaggle_client.py` (CLI wrappers: submit, submissions/remaining-cap, kernels push/status/output), `orchestrator/git_ops.py`.
3. **Executor registry:** `orchestrator/executors/{base.py,kaggle_gpu.py,dev_local.py,local_40g.py,cloud_paid.py}` implementing `submit_run/poll/fetch`; `local_40g`+`cloud_paid` are stubs that raise `NotConfigured`. Selection driven by `state.json`.
4. **State layer:** `state.json` (active_competition, in-flight sessions/runs, daily submit counter UTC, cursors), append-only `events.jsonl` with idempotency-key dedup, `locks.json` (concurrency cap + per-area path-prefix locks), projection/replay helpers.
5. **Operator integration:** invoke Claude headless (CLI `claude -p --output-format json --json-schema operator_decision.schema.json …` or `claude-agent-sdk`); parse `.structured_output`; persistent session id per competition.
6. **Tick loop:** `orchestrator/loop.py` implementing REPORT §5 (poll all in-flight; fire operator on any-terminal/feedback-change/30-min heartbeat; apply StatePatch → commit; launch sessions/runs within cap + per-area locks).
7. **Prompts + schema:** `prompts/jules_worker.md`, `prompts/operator_system.md`, `prompts/operator_tick.md` (REPORT §6), `operator_decision.schema.json`.
8. **AGENTS.md** at repo root with standing context + hard invariants for every Jules session.
9. **Backlog seeded:** US-1…US-5 from `initial_backlog.md` written as task files under `competitions/<slug>/tasks/todo/` + `user-stories/`; `plan.md` drafted.
10. **Tests (mocked, no network) all green:** idempotency, locks/concurrency-cap, state transitions, executor selection, submit-gate logic, and a **full mock dry-run tick** that: creates a fake Jules session → polls to COMPLETED → operator "reviews/merges" → produces a fake rank-≤32 adapter → packages `submission.zip` → validates it → records a (mock) submission. `pytest -q` exits 0; `python -m orchestrator.dryrun` exits 0.
11. **RUNBOOK.md:** how to set creds in `.env`, run a real dry-run, the human-gated Phase-0 live probe (one real Jules session to confirm PR JSON shape) and Phase-1 baseline, and the key-rotation reminder.

## 5. SUGGESTED ORDER (dependency-aware)
Scaffold (1, 8) → state layer (4) → thin clients (2) → executor registry (3) → prompts+schema (7) → operator integration (5) → tick loop (6) → backlog seed (9) → tests + dry-run (10) → RUNBOOK (11). Write tests alongside each module, not only at the end.

## 6. COMPLETION PROMISE
Emit the tag **only** when every item in §4 is true, `pytest -q` is green, and `python -m orchestrator.dryrun` exits 0. Otherwise do the next step and exit (Ralph will re-feed). When truly done, finish your message with exactly:

```
<promise>BUILD COMPLETE</promise>
```

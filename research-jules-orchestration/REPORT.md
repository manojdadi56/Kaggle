# Implementation Plan — Autonomous Kaggle Loop (Jules worker × Claude operator × local orchestrator)

**Status:** Plan only — no code written, no Jules session created, no submission made.
**Date:** 2026-05-30 · **First target:** NVIDIA Nemotron Model Reasoning Challenge (deadline 2026-06-15).
**Verification level:** Jules API contract confirmed against the **live** API with the user's key; the target repo `manojdadi56/Kaggle` is **already connected** as a Jules source.

---

## 1. Executive summary

The system is three actors plus glue:

- **Orchestrator** (local Python, always-on) — dumb scheduler. Polls Jules, watches the feedback inbox, fires the operator each tick, enforces "one Jules session at a time, one competition active."
- **Operator** (Claude Code headless) — the brain. Each tick it plans the next move, reviews/merges Jules PRs, manages git-committed state, triggers the GPU executor, packages the adapter, and submits (within budget). Returns a machine-readable decision the orchestrator logs.
- **Worker** (Jules) — the code author. Picks up one task spec, writes/iterates the *non-GPU* code (synthetic-data generation, data curation, training script, packaging/validation, eval harness), opens a PR.
- **GPU executor** (NOT Jules) — the component that actually trains the LoRA adapter, because **Jules has no GPU and the competition is GPU LoRA training** (the central finding, F-024 × F-008). Default candidate: **Kaggle Notebooks**, driven via the kaggle kernels API.

Two research surprises define the plan: **(1)** the competition is *train-a-LoRA-adapter-and-upload-a-zip*, host-scored — not predict-a-CSV (F-021/F-022); **(2)** Jules cannot do the decisive GPU step. So the real bottlenecks are **compute** and **time** (~16 days), not API wiring — the API wiring is clean and partly proven live. The plan is therefore **baseline-first**: prove a manual end-to-end submission, then automate around the proven pipeline.

The trigger prompts are built from the user's SDLC skill DNA: a single-actor-per-cycle router, an 8-surface role-prompt skeleton, event-sourced state with idempotency keys, an explicit permission matrix, and audit-safe rationale.

---

## 2. Corrected architecture

```
            ┌──────────────────────────── you ────────────────────────────┐
            │  talk only to Claude Code chat → feedback (git-tracked)        │
            └───────────────────────────────────────────────────────────────┘
                                        │  feedback.md / feedback.xlsx (inbox)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR  (local Python, always-on)                                      │
│  • loop: poll Jules session state every 60s while one is in-flight            │
│  • event/heartbeat: fire operator when (PR opened) | (feedback changed) | 30m │
│  • enforces: 1 session in flight, 1 active competition, idempotent ticks      │
└───────────────┬─────────────────────────────────────────────┬───────────────┘
                │ shells `claude -p`/SDK each tick              │ REST (httpx)
                ▼                                               ▼
┌──────────────────────────────┐                ┌──────────────────────────────┐
│  OPERATOR  (Claude headless)  │   creates →    │  JULES  (worker)              │
│  plan → review PR → merge →   │  POST /sessions│  one task → writes non-GPU    │
│  trigger GPU run → package →  │◀── poll/PR ────│  code → opens GitHub PR       │
│  submit (≤budget) → state     │                │  (no GPU; AGENTS.md-guided)   │
└───────┬───────────────┬───────┘                └──────────────────────────────┘
        │ kaggle CLI/API │ git commit (state of record)
        ▼                ▼
┌──────────────────────────────┐   ┌──────────────────────────────────────────┐
│  GPU EXECUTOR                 │   │  STATE (git):                              │
│  Kaggle Notebook (GPU) /      │   │  state.json · tasks/ · plan.md ·           │
│  local GPU / cloud            │   │  decisions/ · experiments/ · submissions/  │
│  → trains LoRA adapter        │   │  feedback.md(.xlsx) · events.jsonl         │
└──────────────────────────────┘   └──────────────────────────────────────────┘
```

**Authority separation (from SDLC F-031):** only **Jules** writes project code; only the **operator** writes state files and submits; the **orchestrator** writes nothing but its own run log. Git is the rollback safety net.

---

## 3. Decisions — LOCKED (2026-05-30)

- **D-1 — Compute path: a pluggable trainer pool — local 40 GB 2-GPU box (primary, to be configured) + Kaggle free GPU; 4 GB laptop is dev-only; paid cloud is the further upgrade.**
  - Jules can't train (F-024). Compute backends are a **registry** (§4.4) the operator picks from per run:
    - **`local_40g` — user's 40 GB 2-GPU system (primary trainer once configured, A-017).** 40 GB across 2 GPUs holds a 4-bit 30B QLoRA → the strongest *free* option and likely better than 2×T4. Details TBD (Q-014); design keeps a slot ready so wiring it in later is trivial.
    - **`kaggle_gpu` — Kaggle Notebooks free GPU (2×T4 ≈ 32 GB), one account, API-driven** (push→poll→pull). Always-available fallback / parallel capacity. Working baseline, not necessarily top score.
    - **`dev_local` — RTX 3050 Laptop, 4 GB (F-038):** data-gen/curation + tiny-toy-model script validation + `adapter_config.json` rank checks only. Never the real 30B run.
    - **`cloud_paid` — RunPod / Lambda / Colab Pro:** further upgrade if the baseline shows promise.
  - **Rejected: multi-Kaggle-account pooling** — violates Kaggle's one-account rule; risks DQ from the ~$106k prize + bans across all linked accounts (F-037/A-016). Not built. (Note: the 40 GB box and 4 GB laptop are the user's own *hardware*, not alt accounts — fully fine.)
- **D-2 — Baseline-first**, then automate (Phase roadmap §7).
- **D-3 — Chat-only feedback:** you talk to Claude; the operator writes a git-tracked `feedback.md` and generates a read-only `feedback.xlsx` view. No Windows file-lock risk.
- **Repo location:** clone `manojdadi56/Kaggle` into `C:\Users\Manoj Sai\Ksggle`; move this research workspace inside it.

**Concurrency & isolation (updated per user):**
- **Parallel Jules sessions allowed for independent work.** The hard "one session in flight" rule is relaxed to a **bounded concurrent pool** capped at the Jules tier limit (free = 3 concurrent, F-007). The operator may launch parallel sessions **only** for tasks it certifies independent — **disjoint `allowed_area` file globs, each on its own branch** — guarded by per-area locks in `locks.json` (no two in-flight tasks may overlap a path prefix; SDLC F-030/F-033). PRs are still merged one at a time by the operator; disjoint areas merge cleanly, overlaps rebase/queue.
- **One competition active at a time, but every competition is a fully self-contained folder** `competitions/<comp-slug>/` (own `plan.md`, `tasks/`, `decisions/`, `experiments/`, `submissions/`, `kernels/`). `state.json` holds the `active_competition` pointer; adding a new competition = a new isolated folder, no entanglement.

(Operational sub-decisions already fixed by you: local Python scheduler that re-triggers continuously and wakes Claude each tick; submit policy = 3 auto/day then approval — **clamped to the real cap, Q-001**; Excel+markdown state; operator has full autonomy incl. submit; event-driven + 30-min heartbeat.)

> **Handoff note:** the actual implementation will be kicked off by the user in a **separate session** with a stated goal. This workspace (`REPORT.md` + `INDEX.md` + logs) and the saved project memory are the self-contained spec that session should load first.

---

## 4. Operational contracts

### 4.1 Jules — the worker trigger (verified live)

- **Base URL:** `https://jules.googleapis.com/v1alpha` · **Auth:** header `X-Goog-Api-Key: $JULES_API_KEY`.
- **Source (confirmed connected):** `sources/github/manojdadi56/Kaggle`.
- **Create a session (the trigger):**
  ```
  POST /v1alpha/sessions
  X-Goog-Api-Key: $JULES_API_KEY   Content-Type: application/json
  {
    "prompt": "<task spec rendered from tasks/<id>.md + standing context>",
    "title": "<task id + short title>",
    "sourceContext": {
      "source": "sources/github/manojdadi56/Kaggle",
      "githubRepoContext": { "startingBranch": "main" }
    },
    "automationMode": "AUTO_CREATE_PR",
    "requirePlanApproval": false
  }
  ```
  → returns `{ "name": "sessions/<id>", "id": "<id>", ... }`. With `requirePlanApproval:false` + `AUTO_CREATE_PR`, Jules runs **fully autonomously** and opens a PR (F-004).
- **Poll:** `GET /v1alpha/sessions/{id}` → `state` ∈ {QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, FAILED, COMPLETED}. Live progress: `GET /v1alpha/sessions/{id}/activities?filter=createTime>"<cursor>"`. **Poll-only — no webhooks** (F-005).
- **Output:** on COMPLETED, PR URL at `session.outputs[].pullRequest.url`; raw diff at artifact `changeSet.gitPatch.unidiffPatch` (F-006; confirm exact nesting at setup — Q-003).
- **Steer / continue:** `POST /v1alpha/sessions/{id}:sendMessage {"prompt":"…"}`. (Approve only if you ever set `requirePlanApproval:true`: `POST …:approvePlan {}`.)
- **Standing context:** ship a repo-root **`AGENTS.md`** — Jules auto-reads it (F-008/F-013-source). It carries competition rules, the hard invariants (LoRA rank ≤ 32, base = Nemotron-3-Nano-30B-A3B-BF16, answers in `\boxed{}`), repo conventions, how to run tests, and the "never do" list.
- **Limits/guards:** Free 15 tasks/day, 3 concurrent (F-007). Orchestrator enforces ≤1 in flight, exponential backoff on HTTP 429, a client-side wall-clock timeout (Q-005) with a `:sendMessage` nudge then re-trigger on stall.
- **Client:** raw REST via `httpx` behind one `jules_client.py` module (F-009) — not the unofficial SDK.

### 4.2 Operator — Claude Code headless contract

- **Invocation each tick (CLI form):**
  ```
  claude -p "<operator tick prompt>" \
    --output-format json --json-schema operator_decision.schema.json \
    --permission-mode acceptEdits \
    --allowedTools "Read,Edit,Write,Bash(git *),Bash(kaggle *),mcp__kaggle__competition_submissions,mcp__kaggle__competition_leaderboard_view" \
    --mcp-config .mcp.json --strict-mcp-config \
    --session-id <persistent-uuid-per-competition> \
    --append-system-prompt-file prompts/operator_system.md \
    --max-turns 60 --max-budget-usd <cap> --model opus
  ```
  Parse `.structured_output` for the decision; `.session_id`/`.total_cost_usd` for bookkeeping (F-011). First tick uses `--session-id <uuid>`; later ticks `--resume <uuid>` for continuity (F-015).
- **Recommended embedding:** the **Python `claude-agent-sdk`** (`query(prompt, options=ClaudeAgentOptions(allowed_tools=, permission_mode=, resume=, mcp_servers=, hooks=))`) over shelling out — native messages, no NDJSON parsing, and in-process **permission hooks to gate the submit tool** (F-014). Billing note: from **2026-06-15** Agent-SDK/`-p` usage on subscription plans draws a separate Agent-SDK credit (F-014).
- **Unattended permissions:** `acceptEdits` + explicit `--allowedTools`, or `dontAsk`; never broad `bypassPermissions` outside a sandbox (F-012). Auth: `ANTHROPIC_API_KEY` or `claude setup-token`.
- **Structured output schema** (`operator_decision.schema.json`) — the operator's RunResult (SDLC-style, F-032): `{ tick_id, status: complete|blocked|saturated|needs_user, actions_taken:[], jules_action: {create_session|none, task_id, prompt_ref}, gpu_action, submit_action: {submit|queue|none, reason, cv_score, beats_best}, state_patch:[ops], next_recommended_action, evidence:[], risks:[] }`.

### 4.3 Kaggle — submission & inspection contract

- **Submit (deterministic path — preferred, F-020):** kaggle CLI with env auth (`KAGGLE_USERNAME`, `KAGGLE_KEY`), no browser.
  - Adapter-zip / file comp: `kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -f submission.zip -m "<msg>"`.
  - Read remaining budget / history: `kaggle competitions submissions nvidia-nemotron-model-reasoning-challenge` (drives Q-001 at runtime — never hard-code the cap).
- **Inspect (agentic path — MCP):** load the Kaggle MCP for leaderboard/comp browsing. Real tool name is **`competition_submit`** (params `competition`, `blob_file_tokens`, `message`) + an upload-URL tool + `create_code_competition_submission`; surfaced to Claude as `mcp__kaggle__<tool>` (F-018). Correction: ignore the `kaggle_mcp_submit_to_competition` name from the notes (C-001).
- **Headless MCP auth (no browser):** either direct HTTP in `.mcp.json` — `{"kaggle":{"type":"http","url":"https://www.kaggle.com/mcp","headers":{"Authorization":"Bearer $KGAT"}}}` — or `npx -y mcp-remote https://www.kaggle.com/mcp --header "Authorization:Bearer $KGAT"` (no space after colon) (F-019). Verify the live tool schema once with `/mcp` (Q-008).
- **Submit gate (your policy):** the operator submits autonomously only if local CV beats current best AND today's auto-submit count < min(3, real_cap); else it writes a `submissions/pending/` card + a `feedback` row asking for approval.

### 4.4 GPU executor contract — a pluggable backend registry

The executor is an abstraction with one interface — `submit_run(config) → run_handle`, `poll(run_handle) → state`, `fetch(run_handle) → {adapter/, cv_score.json, logs}` — and several interchangeable backends the operator selects per run (D-1):

| Backend key | Implementation | Status |
|---|---|---|
| `local_40g` | User's 40 GB 2-GPU box, reached as an execution endpoint (SSH/job-runner or a tiny local agent the orchestrator drives). Same push→poll→fetch shape. | **Primary once configured** (Q-014; "keep ready") |
| `kaggle_gpu` | `kaggle kernels push -p <kernel_dir>` (notebook + metadata, GPU on, base model + data attached as Kaggle datasets/models) → `kaggle kernels status <owner/kernel>` → `kaggle kernels output <owner/kernel> -p <dest>` | **Available now** (fallback / parallel capacity) |
| `dev_local` | RTX 3050 4 GB — tiny-model smoke tests + data-gen + rank checks only | Available now (dev only) |
| `cloud_paid` | RunPod / Lambda / Colab Pro endpoint, same interface | Upgrade if baseline promising |

- The operator owns the run: render the training config, `submit_run`, poll, fetch `adapter/` + `cv_score.json`, then package `submission.zip` and validate `adapter_config.json` rank ≤ 32 **before** any submit (hard invariant, F-022/F-023).
- **Multiple training runs can be in flight on different backends** (e.g. a heavy run on `local_40g` while a variant trains on `kaggle_gpu`) — the executor pool mirrors the parallel-Jules-session model. Each run is keyed by an `experiment_id` and writes to its own `experiments/<id>/` folder.
- A backend is added by dropping one adapter module implementing the interface + a `state.json` registry entry — no loop changes. This is what makes the 40 GB box "ready to plug in later."

---

## 5. File-based state machine (SDLC event-sourcing, adapted)

**State of record = git-committed files** (lock-safe, diffable, the orchestrator commits after every operator tick). Excel is a generated view / optional inbox, never the source of truth (steel-man #4).

```
Kaggle/                                   (repo root = the Jules source)
├── AGENTS.md                             standing context + hard invariants for every Jules session
├── orchestrator/                         local Python loop + thin clients (jules, kaggle, git, operator)
├── prompts/
│   ├── jules_worker.md                   the worker trigger prompt (§6.1)
│   ├── operator_system.md                operator system prompt (§6.2)
│   └── operator_tick.md                  per-tick operator instruction (§6.2)
├── state/
│   ├── state.json                        active comp, in-flight session id, daily submit counter (UTC), cursors
│   ├── events.jsonl                      append-only event log (truth; F-028)
│   └── locks.json                        concurrency cap + per-area (path-prefix) locks for parallel sessions/runs; active-competition guard (F-030/F-033)
├── feedback.md  (+ feedback.xlsx view)   your inputs; operator-written, you-readable (D-3)
├── competitions/
│   └── nvidia-nemotron-model-reasoning-challenge/
│       ├── README.md  plan.md            comp facts; rolling plan (operator owns)
│       ├── tasks/{todo,in-progress,done}/<TASK-id>.md   one task spec per file (worker contract)
│       ├── user-stories/  decisions/     stories; ADR-style "tried X, chose Y because…" (audit-safe, F-034)
│       ├── experiments/<run>/            training config, cv_score.json, notes, adapter ref
│       ├── kernels/                      Kaggle training-notebook + metadata (GPU executor input)
│       └── submissions/{pending,submitted}/  submission cards + log.md
└── .env.example  .gitignore              secrets are local-only, never committed (A-014)
```

**State ops (StatePatch, F-029):** every operator action emits operations with deterministic `idempotency_key = <tick_id>:<entity>:<action>`; the orchestrator appends to `events.jsonl` then updates projections; re-applying a seen key is a silent no-op (safe retries). **Task status vocabulary** (subset of SDLC F-...): `TODO → IN_PROGRESS(jules) → READY_FOR_REVIEW(PR open) → CHANGES_REQUESTED | MERGED → (training) → READY_TO_SUBMIT → SUBMITTED | DONE`, plus `BLOCKED`, `SATURATED` (resumable, F-035).

**The tick (orchestrator pseudo-logic, no code):**
1. Poll **all** in-flight Jules sessions (`GET /sessions/{id}`) and all in-flight GPU runs. None terminal and no new feedback → sleep 60s, loop. **Any** session/run terminal → fire operator with the results.
2. Else if `feedback.md` changed since last cursor → fire operator (user input path).
3. Else on 30-min heartbeat → fire operator (maintenance/plan path).
4. **Operator tick** (SDLC F-027): read state + feedback + plan + open PRs + in-flight pool → reconcile, then choose moves. It picks **one primary move** (review&merge a PR · package+submit within budget · update plan) **and may additionally dispatch up to `(concurrency_cap − in_flight)` parallel Jules sessions or GPU runs for tasks it certifies independent** (disjoint `allowed_area`, free per-area locks). Emit decision + StatePatch listing every session/run to launch.
5. Apply patch → `git commit` → orchestrator creates the requested Jules sessions / GPU runs (respecting the concurrency cap and per-area locks) and records their in-flight ids. Repeat.

---

## 6. Trigger prompts (SDLC 8-surface skeleton, F-032)

### 6.1 Jules worker prompt (`prompts/jules_worker.md`, rendered per task)
The orchestrator fills `{{...}}` from the chosen `tasks/<id>.md` and sends it as the session `prompt`. (AGENTS.md supplies standing context so this stays lean.)

1. **Identity:** "You are the Worker. You author and iterate the non-GPU code for `{{task_id}}` only. You do NOT train models (no GPU here), do NOT submit to Kaggle, do NOT edit files outside `{{allowed_area}}`, do NOT touch `state/` or `secrets`."
2. **Activation:** "Work this single task. If the task is ambiguous, under-specified, or needs a decision above your authority, STOP and open a PR whose description states `NEEDS_INFO:` with the exact question — do not guess."
3. **Inputs:** task goal, acceptance criteria, allowed area, definition-of-done, relevant repo files, AGENTS.md invariants.
4. **SOP:** read context → make the smallest correct change → add/adjust tests or a runnable validation (e.g. `adapter_config.json` rank-check, data-schema check) → run what you can on the no-GPU VM (lint, unit tests, dry-run on a tiny sample) → keep the diff scoped.
5. **Reasoning discipline:** put only audit-safe rationale in the PR (what changed, why, evidence, risks, how to verify) — no hidden chain-of-thought (F-034).
6. **Output contract:** open ONE PR via `AUTO_CREATE_PR`; PR body = `## Summary / ## Evidence (tests run) / ## Risks / ## Definition-of-done check / NEEDS_INFO (if any)`.
7. **Failure handling:** if blocked, still open a PR (or message) documenting the blocker + smallest unblocking step; if too large, stop at a clean boundary and state Completed / Remaining / Resume-cursor (F-035).
8. **Eval checklist:** one task only · diff within allowed area · tests/validation run or reason given · invariants respected (rank ≤ 32, base model, `\boxed{}`) · PR body complete.

### 6.2 Operator prompt (`operator_system.md` + `operator_tick.md`)
**System (identity + boundaries):** "You are the Operator for the autonomous Kaggle loop. Authority: read/write state files, review & merge Jules PRs, create the next Jules task, trigger the GPU executor, package and submit to Kaggle within the budget, and curate the plan/backlog/feedback. You are the ONLY writer of `state/`, `decisions/`, `submissions/`, and the feedback view; Jules is the ONLY code author. Never exceed `min(3, real_daily_cap)` auto-submits/day (read the remaining cap live before submitting); never submit a candidate that doesn't beat current best local CV; never violate the hard invariants (LoRA rank ≤ 32, base = Nemotron-3-Nano-30B-A3B-BF16, answers in `\boxed{}`). Keep all rationale audit-safe."

**Tick (the per-invocation SOP — planner + reviewer + submitter fused, single-actor F-027):**
1. **Intake & reconcile (always first):** load `state.json`, `plan.md`, open tasks, open PRs, new `feedback.md` rows, last Jules result. Do maintenance — prune/merge/update tasks, fold user feedback into the backlog, fix the plan if the direction is wrong.
2. **Select the primary move** by feasibility+urgency (SDLC F-036), in this rough priority: unblock a blocker → review & merge a ready Jules PR (against acceptance criteria + invariants; request changes via a follow-up task if needed) → if a mergeable training change exists, trigger a GPU run / pull a finished run → if a fresh adapter beats best CV and budget remains, package + submit (else queue for approval) → else create the next Jules task from the backlog → else update plan / write a status note (never a no-op without reason).
   - **Then, parallel fan-out:** if the backlog holds tasks that are independent of the primary move and of each other (disjoint `allowed_area`, free per-area locks) and the pool has free slots `(concurrency_cap − in_flight)`, dispatch them as **additional concurrent Jules sessions / GPU runs**. Certify independence explicitly in the rationale; if unsure, do NOT parallelize.
3. **Emit** the structured decision (`operator_decision.schema.json`) + StatePatch ops with idempotency keys; for each session/run to launch, include the rendered worker prompt ref + the `allowed_area` it locks, so the orchestrator fires them.
4. **Permissions/guards:** enforce the submit gate + the concurrency cap + per-area locks; refuse + escalate to a `feedback`/`needs_user` card for anything irreversible beyond policy.
5. **Eval checklist:** one primary move (+ only certified-independent parallel dispatches) · every state change traceable to evidence · invariants + submit budget + concurrency cap respected · feedback acknowledged · next action named.

---

## 7. Phased roadmap (baseline-first, steel-man #1)

- **Phase 0 — One-time human setup (~hours):** confirm/rotate secrets into local `.env`; confirm the **submission cap + automation policy** on the gated pages (Q-001/Q-002); pick **D-1/D-2/D-3**; (optional) run one real Jules session to capture the COMPLETED-PR JSON shape (Q-003) and one tiny Kaggle-GPU QLoRA dry-run (Q-012).
- **Phase 1 — Manual baseline (days 1–2):** fork `tonghuikang/nemotron` (F-026), train a small LoRA on the chosen GPU, package `submission.zip`, validate rank ≤ 32, submit once via kaggle CLI → **a real leaderboard score and a proven pipeline.** Everything after automates *this*.
- **Phase 2 — Orchestrator skeleton:** `state.json`/`events.jsonl`, the three thin clients (jules/kaggle/git), the tick loop, AGENTS.md, the two prompts. Dry-run with a trivial Jules task ("add a README section") end-to-end: create→poll→PR→operator-review→merge→commit.
- **Phase 3 — GPU executor in the loop:** operator drives push→poll→pull on Kaggle kernels (or the D-1 endpoint), writes `experiments/<run>/cv_score.json`, packages the zip.
- **Phase 4 — Submit gate + feedback loop:** wire the budget-gated submit, the `submissions/pending` approval cards, and the chat→`feedback.md` channel. Now it ticks unattended.
- **Phase 5 — Hardening:** backoff/timeouts/idempotency soak-test, run-log dashboards, then let it iterate (data-gen, curation, hyperparams) within the deadline.

---

## 8. Risks & limitations

- **Compute is the binding constraint** (F-024/Q-012): free Kaggle GPU may not yield competitive scores on a 30B MoE; D-1 may require paid compute.
- **Time** (F-025): ~16 days; the orchestrator must not starve the model work — hence baseline-first.
- **Unconfirmed cap/rules** (Q-001/Q-002): must be read live + confirmed before unattended submits.
- **Vendor drift** (steel-man #5): three <1-year-old surfaces; isolated behind thin clients; prefer kaggle CLI for the load-bearing submit.
- **Windows file lock** (A-009): solved by git-JSON-as-truth + chat feedback channel.
- **Secrets** (A-014/A-015): pasted keys are in the transcript — rotate after setup; `.env` gitignored; the operator's submit tool gated by an in-process permission hook.

---

## 9. Decisions needed from you (then code starts)
- **D-1** compute path · **D-2** scope/sequencing · **D-3** feedback channel (see §3).
- Confirm: rotate the two pasted keys after setup; operator may auto-merge clean PRs (you granted full autonomy); auto-submit budget clamps to the live cap.

---

## 10. Workspace map
- [00_research_plan](00_research_plan.md) · [01_pre_registration](01_pre_registration.md) · [02_findings_log](02_findings_log.md) · [03_assumption_log](03_assumption_log.md) · [04_open_questions](04_open_questions.md) · [05_contradictions](05_contradictions.md) · [06_source_log](06_source_log.md) · [07_glossary](07_glossary.md) · [08_progress_snapshots](08_progress_snapshots.md) · [09_meta_log](09_meta_log.md) · [10_steelman](10_steelman.md) · [INDEX](INDEX.md)

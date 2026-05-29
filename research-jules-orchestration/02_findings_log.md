# 02 — Findings Log

Confidence anchors: **Well-established** (≥90%, ≥2 independent A/B sources or live evidence) · **Supported** (70–90%) · **Plausible** (40–70%) · **Speculative** (<40%) · **Contested**.

---

## Cluster A — Jules API contract (the worker trigger)

### F-001 — Jules auth is an API key in `X-Goog-Api-Key`; base URL `https://jules.googleapis.com/v1alpha`
The API authenticates with a raw API key in the `X-Goog-Api-Key` header (not OAuth). Keys are generated at jules.google settings. Confirmed **live** — the user's key returned a 200 with real data on `GET /v1alpha/sources`.
Sources: S-001 (live), S-002, S-006. **Confidence: Well-established.**

### F-002 — Repos are first-class `Source` objects; format `sources/github/{owner}/{repo}`; list-only via API
`GET /v1alpha/sources` lists connected repos. The resource `name` uses forward slashes: `sources/github/{owner}/{repo}` (the dash form seen in one community write-up is wrong). There is **no API endpoint to create/connect a source** — the Jules GitHub App must be installed via the web UI first; the API can only discover already-connected repos.
Sources: S-001 (live, slash format confirmed), S-004, S-006. **Confidence: Well-established.**

### F-003 — Repo binding is event-graphed by `Source` → `Session` → `Activity` → `outputs`
The object model is: a `Source` (repo) hosts a `Session` (one unit of work); a session emits `Activity` events (planGenerated, planApproved, agentMessaged, progressUpdated, sessionCompleted, sessionFailed); a completed session carries `outputs[]`. "Task" is the informal UI word — no separate task resource exists.
Sources: S-003, S-005. **Confidence: Well-established.**

### F-004 — Create a session: `POST /v1alpha/sessions` with prompt + sourceContext + automationMode + requirePlanApproval
Request body fields: `prompt` (required), `title` (optional), `sourceContext.source` (the source name), `sourceContext.githubRepoContext.startingBranch`, `automationMode` (`AUTO_CREATE_PR` opens a PR at the end), `requirePlanApproval` (bool). **API-created sessions auto-approve their plan by default** — so omitting/falsing `requirePlanApproval` + setting `AUTO_CREATE_PR` yields fully autonomous, no-click execution.
Sources: S-003, S-006. **Confidence: Well-established.**

### F-005 — Poll with `GET /v1alpha/sessions/{id}`; state enum is well-defined; poll-only (no webhooks)
Session `state` ∈ {`STATE_UNSPECIFIED`, `QUEUED`, `PLANNING`, `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `IN_PROGRESS`, `PAUSED`, `FAILED`, `COMPLETED`}. Live progress comes from `GET /v1alpha/sessions/{id}/activities` (supports a `createTime` filter as a cursor so only new activities are fetched). **There are no webhooks — polling is the only mechanism.** Steer mid-run with `POST /v1alpha/sessions/{id}:sendMessage`; gate manually only if you set `requirePlanApproval:true` then `POST …:approvePlan`.
Sources: S-003, S-005, S-009. **Confidence: Well-established.**

### F-006 — Output: a GitHub PR (URL in `session.outputs[].pullRequest.url`) and/or a raw git patch
With `AUTO_CREATE_PR`, Jules opens a PR automatically; the URL is read from the COMPLETED session's `outputs[].pullRequest.url`. A raw unified diff is also available via artifacts `changeSet.gitPatch.unidiffPatch` (+ `baseCommitId`, `suggestedCommitMessage`).
Sources: S-003, S-005, S-009. **Confidence: Supported** (exact JSON nesting of `outputs[].pullRequest.url` and the branch-name field should be confirmed against a live COMPLETED session — see Q-003).

### F-007 — Quota: Free 15 tasks/day + 3 concurrent; Pro 100/15; Ultra 300/60 (rolling 24h)
Daily task and concurrency caps by tier. HTTP `429` is a documented error → back off exponentially. Whether the API enforces a separate per-minute HTTP rate limit, and whether API tasks share the UI task quota, is undocumented.
Sources: S-007. **Confidence: Well-established** (the numbers); **Plausible** (API shares UI quota → Q-004).

### F-008 — Jules VM has NO GPU; short-lived; honors `AGENTS.md`; env configured web-side
The per-task VM is secure/ephemeral with Node 22, Bun, Python 3.12, Go, Java 21, Rust, C/C++, Docker preinstalled. **GPU is never mentioned — treat as no GPU.** Jules auto-reads `AGENTS.md` (and `README.md`) for repo-specific instructions and environment hints. A per-repo setup script + snapshot is configured in the web UI, not via an API field. Max runtime per task is undocumented (Q-005).
Sources: S-008. **Confidence: Well-established** (no-GPU is an inference from total silence + the product's positioning, but a safe one).

### F-009 — Integration surface: raw REST (recommended), official TS SDK, official GitHub Action, unofficial Python SDK
Best path for a Python orchestrator is **raw REST via `httpx`/`requests`** — flat, stable. Official `@google/jules-sdk` is TS-only and "not officially supported." A community `pip install jules-agent-sdk` mirrors REST but is early/untagged. An official GitHub Action (`google-labs-code/jules-action`) exists as an alternative trigger surface.
Sources: S-006, S-010, S-011, S-012. **Confidence: Well-established.**

### F-016 — The user's target repo `manojdadi56/Kaggle` is ALREADY connected as a Jules source
Live probe shows `sources/github/manojdadi56/Kaggle` present in the user's source list (alongside 12 other repos). **No manual GitHub-App install step is needed** — the orchestrator can create sessions against it today.
Sources: S-001 (live). **Confidence: Well-established.**

---

## Cluster B — Claude Code headless contract (the operator)

### F-010 — `claude -p "<prompt>"` runs non-interactively, prints to stdout, exits; reads stdin (≤10 MB)
`-p`/`--print` executes the prompt as an agent (full tool loop) and exits. Pipeable stdin (cap 10 MB). `--bare` is now recommended for scripted/SDK/CI calls (skips auto-discovery of hooks/skills/plugins/MCP/CLAUDE.md for determinism) — but then you must pass `--mcp-config`/`--settings` explicitly and auth via `ANTHROPIC_API_KEY`.
Sources: S-013. **Confidence: Well-established.**

### F-011 — `--output-format json` returns `.result`, `.session_id`, `.total_cost_usd`; `--json-schema` → `.structured_output`
JSON output exposes the text result (`.result`), `session_id`, and `total_cost_usd`. Combine `--output-format json --json-schema '<schema>'` to get a validated object in `.structured_output` — **this is how the orchestrator gets machine-readable decisions back from the operator.** `stream-json` (NDJSON, needs `--verbose`) is for live event streaming.
Sources: S-013, S-014. **Confidence: Well-established** (other fields like `num_turns`/`is_error` exist in practice but were not individually confirmed → Q-006).

### F-012 — Unattended permission modes: `acceptEdits` / `dontAsk` + `--allowedTools`, or `--dangerously-skip-permissions`
`--permission-mode` ∈ {`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`}. For unattended runs: `acceptEdits` (auto-approve file writes) + explicit `--allowedTools` for shell/MCP tools, **or** `dontAsk` (denies anything not allow-listed — good for CI), **or** `--dangerously-skip-permissions` (= bypassPermissions) only inside a disposable sandbox. Guardrails: `--max-turns`, `--max-budget-usd`, `--fallback-model`.
Sources: S-013, S-014. **Confidence: Well-established.**

### F-013 — MCP in headless: `--mcp-config <file>` + `--strict-mcp-config`; tools are `mcp__<server>__<tool>`
Load MCP servers from a JSON file (`mcpServers` key). `--strict-mcp-config` ignores all other MCP config for reproducibility. Tools surface as `mcp__kaggle__competition_submit` etc.; allow-list per-tool in `--allowedTools` (whole-server prefix `mcp__kaggle` likely allows all, not verbatim-confirmed → Q-007). Claude Code natively supports remote HTTP MCP with bearer `headers`, so mcp-remote may be unnecessary.
Sources: S-014, S-015. **Confidence: Well-established.**

### F-014 — The Python `claude-agent-sdk` is the recommended way to embed Claude Code programmatically
`pip install claude-agent-sdk` (Py ≥3.10): `query(prompt=..., options=ClaudeAgentOptions(allowed_tools=, permission_mode=, resume=, mcp_servers=, hooks=, agents=, setting_sources=))`. Advantages over shelling `claude -p`: native message objects (no NDJSON parsing), `session_id` from the init message, in-process permission/tool callbacks (e.g. gate the Kaggle submit tool), programmatic resume/fork. Docs explicitly recommend SDK for production automation, CLI for one-offs. **Billing caveat: from 2026-06-15, Agent SDK & `claude -p` on subscription plans draw from a separate monthly "Agent SDK credit."**
Sources: S-016, S-017. **Confidence: Well-established.**

### F-015 — Session continuity: pre-generate a UUID, pass `--session-id` first tick, `--resume <uuid>` after
`--session-id <uuid>` forces an ID; `--resume <id>`/`--continue` reload it; `--fork-session` branches. Sessions persist as JSONL under `~/.claude`/project dir. **Pattern for a ticking orchestrator: assign one persistent operator session ID per competition and resume it each tick** so the operator keeps continuity of plan/decisions.
Sources: S-014. **Confidence: Well-established.**

---

## Cluster C — Kaggle submission contract

### F-017 — Nemotron is host-scored; the kaggle CLI `-k/--kernel -v/--version` path submits a notebook version
The classic CLI submits file comps with `kaggle competitions submit <comp> -f <file> -m "<msg>"` and **code/notebook comps via `-k/--kernel <owner/kernel> -v/--version <n>`**. Auth is pure env (`KAGGLE_USERNAME`/`KAGGLE_KEY`) — no browser. This is the most battle-tested, deterministic automation path.
Sources: S-024. **Confidence: Well-established.**

### F-018 — Kaggle MCP is official (`https://www.kaggle.com/mcp`), bearer-KGAT auth, ~57 tools; submit tool is `competition_submit`
Tools include `competitions_list`, `competition_list_files`, `competition_download_file(s)`, `competition_submit` (params: `competition`, `blob_file_tokens`, `message`), `competition_submissions`, `competition_leaderboard_view/download`, an upload-URL tool (generates a presigned URL → returns `blob_file_tokens`), and `create_code_competition_submission` (for code comps: notebook owner/slug/version). **The submit tool is `competition_submit`, NOT `kaggle_mcp_submit_to_competition`** (the name in the user's notes is wrong).
Sources: S-018, S-019, S-020, S-021, S-022. **Confidence: Well-established** (the `competition_submit` name + correction); **Supported** (exact upload-tool name / 57 count → Q-008).

### F-019 — For headless MCP, bypass the mcp-remote browser OAuth with a static bearer header
`npx mcp-remote` defaults to an OAuth **browser** flow (caches tokens in `~/.mcp-auth/`) — a blocker for unattended runs. Fixes: pass `--header "Authorization:Bearer KGAT_..."` (no space after colon to dodge an npx escaping bug), **or** skip mcp-remote and point Claude Code's `--mcp-config` directly at the HTTP endpoint with `{"type":"http","headers":{"Authorization":"Bearer KGAT_..."}}`. Stale `~/.mcp-auth` → connection fails; fix is to clear it.
Sources: S-020, S-023. **Confidence: Well-established** (the browser problem + `--header` fix); **Supported** (direct-HTTP combo against Kaggle inferred → Q-009).

### F-020 — Recommendation: use kaggle CLI for the deterministic submit; reserve MCP for agentic browsing
The CLI/API is more reliable for the actual submit (stable flags, env auth, scriptable exit codes, years of CI use). The MCP is newer and better for LLM-driven exploration (leaderboards, comp/notebook inspection). Best design: **CLI for submit; MCP for read/inspect.**
Sources: S-020, S-024. **Confidence: Supported** (judgment from maturity, not a benchmark).

---

## Cluster D — Nemotron competition mechanics (ARCHITECTURE-DEFINING)

### F-021 — The task is LoRA fine-tuning, not prediction: train a rank-≤32 adapter on a FIXED Nemotron base
You train a LoRA adapter (rank ≤ 32) on top of the fixed base **Nemotron-3-Nano-30B-A3B-BF16** (30B total / 3B active Mamba-Transformer MoE) to maximize accuracy on logical-reasoning puzzles. Any technique allowed: prompt strategy baked into training, data filtering, **synthetic data generation**, RL, SFT. **The deliverable is the adapter — not a predictions CSV.**
Sources: S-025, S-026, S-027, S-028. **Confidence: Well-established** (4 independent sources agree).

### F-022 — Submission is `submission.zip` (LoRA adapter + `adapter_config.json`), scored HOST-SIDE via vLLM
You upload a `submission.zip` containing the adapter weights + `adapter_config.json` (rank ≤ 32). Kaggle/NVIDIA loads the adapter into the fixed base and runs vLLM inference on a hidden test set host-side. **No self-contained no-internet inference notebook is required** for scoring; the usual notebook-runtime limits don't govern the submission. An over-rank `adapter_config.json` is rejected — a hard invariant.
Sources: S-026, S-027. **Confidence: Well-established** (submission shape); **Medium** on exact interplay with notebook limits (Q-002).

### F-023 — Metric: accuracy via `\boxed{}` extraction; fixed host inference params (temp 0, max_lora_rank 32)
Final answer must be in `\boxed{...}`; scored by exact string or numeric match (±1e-2). Host vLLM config is fixed: `temperature=0.0, top_p=1.0, max_tokens=7680, max_model_len=8192, max_lora_rank=32, gpu_memory_utilization=0.85, max_num_seqs=64`. Hidden test set (`test.csv` columns `id, prompt` swapped for private).
Sources: S-026. **Confidence: Well-established.**

### F-024 — TRAINING NEEDS A REAL GPU — and Jules has none (the central architectural constraint)
The 30B MoE needs ≥2×T4 in 4-bit (QLoRA) just to fit on Kaggle's free GPU, and competitors recommend stronger GPUs (RTX PRO 6000 / cloud) for competitive results. Kaggle free GPU ≈ 30 GPU-hrs/week, T4×2. **Combined with F-008 (Jules = no GPU): Jules cannot train the model. A separate GPU executor is mandatory.** This invalidates the naive "Jules does the work end-to-end" assumption (A-001).
Sources: S-024(comp), S-026, S-027, S-008. **Confidence: Well-established.**

### F-025 — Timeline is TIGHT: final deadline 2026-06-15; today is 2026-05-30 (~16 days); entry/merger 2026-06-08
Start 2026-03-16; Open Progress Prize midpoint 2026-04-09 (passed; won by tonghuikang); team-merger deadline 2026-06-08 (~9 days out); final submission 2026-06-15 (~16 days out). **Status: OPEN.** The build-out window for the orchestrator competes directly with the competition window.
Sources: S-025, S-026. **Confidence: Well-established.**

### F-038 — The user's local GPU (RTX 3050 Laptop, 4 GB VRAM) cannot train the 30B model; it's a dev/smoke-test box only
Detected hardware: RTX 3050 Laptop GPU **4 GB VRAM**, 15.4 GB system RAM, Ryzen 5 5600H (6 cores). A 30B MoE in 4-bit QLoRA needs ~20–30 GB+ VRAM — it won't even load on 4 GB. **Role reassignment:** local box = data-gen/curation + tiny-toy-model training-script validation + `adapter_config.json` rank checks (cheap, fast, saves Kaggle quota); **Kaggle free GPU (2×T4 ≈ 32 GB) is the real training compute**; paid cloud is the upgrade path if the baseline is promising. Note: 30B QLoRA on 2×T4 is itself tight/slow, so free-GPU scores are likely a working baseline, not top-tier (consistent with the winner using stronger compute, F-026).
Sources: live hardware probe (PowerShell `nvidia-smi`), F-024. **Confidence: Well-established.**

### F-037 — Multiple Kaggle accounts are prohibited; pooling them for compute risks DQ + linked-account bans
Kaggle enforces "one account per participant." Using alt accounts to multiply free GPU quota for a single competition — even for experiments only — is a Terms-of-Use violation: accounts are linked by phone/payment/IP/behavior, and a flagged ring leads to **disqualification from the prize (~$106k here) and permanent bans across all linked accounts, including the main one.** The compute upside (a few extra T4-hours/account) is marginal vs. the catastrophic, hard-to-reverse downside. **Decision: do not build cross-account pooling; use one account plus the user's own or paid compute for heavier runs.**
Sources: Kaggle Terms of Use / competition rules (one-account rule, S-031-adjacent); engineering judgment. **Confidence: Well-established** (the rule); **Well-established** (the risk asymmetry).

### F-026 — Official starter + a fully open-sourced progress-prize-winning solution exist as baselines
Official "NVIDIA Nemotron Submission Demo" notebook (ryanholbrook) shows how to package the adapter zip. The progress-prize winner (tonghuikang/nemotron) is fully open-sourced and is the best reference baseline to fork. Multiple community SFT/LoRA baselines exist.
Sources: S-028, S-029. **Confidence: Well-established.**

---

## Cluster E — SDLC skill patterns (the contract DNA for the trigger prompts)

### F-027 — Single-role-per-cycle: the router selects exactly ONE actor each tick (no multi-role runs)
The SDLC kernel turns one trigger into one auditable run by selecting exactly one feasible role, with hard exclusions (no adjacent repeat, no held-lock, no role-without-work) then numeric scoring + alphabetical tie-break. **Maps directly to "one Jules session in flight at a time" + "operator picks the single next action each tick."**
Sources: S-030. **Confidence: Well-established** (direct read).

### F-028 — Event-sourced state: append-only `Events` is truth; all other sheets are rebuildable projections
Every state change appends an immutable `Events` row; projection sheets (Tasks, Suggestions, Decisions, …) are derived and can be rebuilt by replaying events. Enables crash recovery + full audit. **Maps to making the orchestrator's state a git-committed event log, not mutable scratch.**
Sources: S-030. **Confidence: Well-established.**

### F-029 — Idempotency keys on every operation make retries safe (flaky external agents collapse cleanly)
Each StatePatch op carries a deterministic `idempotency_key` from `(run_id, entity, action)`; the ledger silently skips already-seen keys. **Critical for a poll-and-retry orchestrator where a Jules poll or a Claude tick may re-fire.**
Sources: S-030. **Confidence: Well-established.**

### F-030 — Optimistic version locking + snapshots guard concurrent/clobbering writes
Rows carry a `version` that bumps on write; `update_status` checks `expected_version`/`from_status`. The workbook is snapshotted before every mutating cycle. **Maps to git-commit-before-act + a single-writer rule.**
Sources: S-030. **Confidence: Well-established.**

### F-031 — Single-writer invariant: exactly one component may mutate the state store
In SDLC, only `state_ledger.py` writes the Excel; only the `owner` role writes code. **Maps to: only Claude (operator) writes `feedback.xlsx`/`state.json`; only Jules (worker) writes project code.** Clean authority separation prevents races.
Sources: S-030. **Confidence: Well-established.**

### F-032 — The 8-surface role-prompt skeleton: Identity · Activation · Inputs · SOP · Reasoning discipline · Output contract · Failure handling · Eval checklist
Every role prompt is built from the same 8 surfaces, giving predictable guardrails, self-checks, and structured handoffs. **This is the template for the Jules-worker and Claude-planner trigger prompts.**
Sources: S-030. **Confidence: Well-established.**

### F-033 — Permission matrix as an explicit per-role bitmask, enforced by a policy gate before apply
Each role gets `{can_edit_code, can_write_excel_directly, can_create_state_patch, can_commit, can_browse}` defaulting to false; the policy gate rejects any patch op outside the role's authority, with explicit reasons. **Maps to a RunEnvelope-style permission block the operator enforces on Jules output before merge/submit.**
Sources: S-030. **Confidence: Well-established.**

### F-034 — Audit-safe rationale only: artifacts carry Facts/Decision/Evidence/Risks/Next, never hidden chain-of-thought
Public artifacts (logs, decisions, progress) must contain only audit-safe rationale; hidden CoT/scratchpad is rejected by an audit check. **Maps to ADR-style `decisions/` files and commit messages that record why, traceably, without dumping reasoning.**
Sources: S-030. **Confidence: Well-established.**

### F-035 — Saturation boundaries make multi-tick tasks resumable (Completed / Remaining / Resume-cursor)
When a role can't finish in one run it stops at a clean boundary and records Completed/Remaining/Resume-cursor/Evidence/Risks/Next. **Maps to Jules tasks that exceed one session: the operator records a resume cursor and re-triggers continuation.**
Sources: S-030. **Confidence: Well-established.**

### F-036 — Feasibility scoring + always-feasible fallback (`reporter`) guarantees every tick does something useful
Roles score by urgency (pending feedback ×5, ready tasks ×8, review queue ×7, …); if none feasible, `reporter` documents the blocker (score floor 0). **Maps to: the planner always has a productive move — advance, unblock, improve backlog, or explain why it's blocked.**
Sources: S-030. **Confidence: Well-established.**

---

## Cluster F — Operator execution model (R-001: operator = Claude Code session, NO API key)

### F-039 — The operator is the Claude Code session on the user's SUBSCRIPTION; `ANTHROPIC_API_KEY` must stay UNSET
The user mandates no API key. Claude Code's auth precedence puts `ANTHROPIC_API_KEY` (and `ANTHROPIC_AUTH_TOKEN`) ABOVE subscription OAuth — so if the key is set it silently overrides the subscription and bills pay-per-token. Therefore the env var must be unset (or cleared in `/config`). The operator runs on the Pro/Max subscription via Claude Code.
Sources: S-032. **Confidence: Well-established.**

### F-040 — Scheduled **Routines** (`/schedule`) run on Anthropic cloud on the subscription, no API key — but ≥1-hour interval
Routines (claude.ai/code/routines) execute remotely as full Claude Code sessions, survive the laptop being off, and are subscription-only (no API key, cannot use API billing). Minimum schedule interval is **1 hour** (cron supported); they draw on the account's daily run allowance. This is the cleanest unattended operator trigger — at the cost of the original 30-min heartbeat (→ Q-016).
Sources: S-032. **Confidence: Supported** (single authoritative digest; verify exact daily allowance live).

### F-041 — `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN` gives headless `claude -p` on the subscription (no API key)
`claude setup-token` mints a ~1-year subscription OAuth token (inference-only). Exported as `CLAUDE_CODE_OAUTH_TOKEN`, it lets `claude -p` run non-interactively billed to the subscription — enabling sub-hour ticks via Windows Task Scheduler. Caveat: it does NOT work with `--bare` (bare requires API key/apiKeyHelper). This is the OPTIONAL `operator.py` self-drive adapter path.
Sources: S-032. **Confidence: Supported.**

### F-042 — `/loop` runs locally and is session-scoped — fine for interactive ticking, fragile for unattended
`/loop <interval> <prompt>` keeps the current session alive and fires between turns; bills to whatever auth is active (subscription if logged in). It stops when the terminal/session closes and auto-expires recurring tasks after 7 days → not robust for true unattended operation; use a Routine or Task Scheduler for that.
Sources: S-032. **Confidence: Supported.**

### F-043 — Python is now a TOOLKIT the operator drives, not a brain that spawns an LLM
Re-architecture: the tick is `tools context` → operator (Claude Code) decides → `tools apply decision.json`. `gather_context`/`apply_decision`/`poll_in_flight` are pure mechanics; the intelligence is the Claude Code session. The old `operator.py` (shells `claude -p`) is demoted to an optional unattended adapter (subscription-OAuth). This removes the only component that needed an API key.
Sources: S-032, S-013/S-014 (headless flags), design. **Confidence: Well-established** (it's our design decision, grounded in F-039..F-042).

### F-044 — Billing note: from 2026-06-15, subscription `claude -p` / Agent SDK draws from a separate monthly Agent-SDK credit pool
Unattended operator usage on the subscription will consume a distinct monthly credit allotment (separate from interactive limits). Cadence should be budgeted accordingly (favors the 1-hour routine over very frequent ticks).
Sources: S-032, S-017. **Confidence: Supported.**

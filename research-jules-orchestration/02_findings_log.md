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

---

## Cluster G — SDLC skill integration (R-003)

### F-045 — The SDLC skill cleanly splits into reusable DNA vs Excel machinery; only the DNA fits this project
The skill (55 files) = (a) **role/contract DNA**: `operating_contract.md`, 8 `role_*.md`, 9 `cap_*.md`, `infra_*.md`, `schemas.md`, `validation_policy.md`, `role_permissions.md`, `workbook_schema.md` — domain-agnostic orchestration guidance; and (b) **Excel state machinery**: `scripts/state_ledger.py`/`workbook_*`/`role_selector`/`score_roles`/`lock_manager` + `assets/schemas|templates` — tied to `state.xlsx`. Our project already has git-JSON event-sourced state (F-028/F-043), so importing (b) would create a conflicting second source of truth. **Decision: import (a) as guidance, quarantine (b) as `_legacy_excel/` reference-only.**
Sources: S-030 (the skill, read directly). **Confidence: Well-established.**

### F-046 — Project skills live at `.claude/skills/<name>/SKILL.md` (valid YAML frontmatter) and are committable
Claude Code discovers project skills under `.claude/skills/`; `name` + `description` frontmatter make `/sdlc` invokable. `.gitignore` only excludes `.claude/*.local.md` + `settings.local.json`, so `.claude/skills/**` commits normally. The skill is discovered at session start → `/sdlc` becomes available to the operator in a **new** session (not retroactively in the current one).
Sources: S-032 (Claude Code skills docs), live `.gitignore`. **Confidence: Supported.**

### F-048 — The SDLC value is the single-ledger automation, not the file format; behavior is portable to git-JSON
The skill's power (user's insight): ONE workbook is the single source of truth; planner/innovator **write work rows into it**; each run role-selects (`score_roles.py`: feasibility gate → numeric score → alphabetical tie-break → no-adjacent-repeat) and completes the top item. This BEHAVIOR is substrate-independent. `score_roles.py` reads sheets as row-dicts — trivially reproducible on JSON collections. **Decision (R-004): port the model to git-JSON, not Excel-as-truth.**
Sources: S-030 (score_roles.py, workbook_schema, role_selector — read directly). **Confidence: Well-established.**

### F-049 — git-JSON ledger + generated Excel view beats Excel-as-truth for this agent+git system
Excel-as-truth = binary (no git diff/merge), openpyxl-as-critical-writer, file-lock risk if opened mid-write. git-JSON = diffable, merges with Jules PRs, no lock, event-sourced replay (already built). The user's literal "see everything in an Excel sheet" want is satisfied by a **read-only generated `dashboard.xlsx`** (regenerated each tick) — keeping JSON as truth. Chat-only feedback (D-3) means the user never opens the truth-file mid-write, so the original anti-Excel risk (A-009) is moot for the view.
Sources: F-028, F-043, A-009, design. **Confidence: Well-established.**

### F-052 — KGAT is the SINGLE Kaggle credential the orchestrator needs (no `kaggle.json` `key` required)
The user provided `KAGGLE_API_TOKEN=KGAT_...` repeatedly; I incorrectly kept asking for the legacy `kaggle.json` `key`. The KGAT is the Bearer for the Kaggle MCP at `https://www.kaggle.com/mcp` and for the official Kaggle web API; it covers everything our pipeline needs: read leaderboard, list/download competition files, push/poll/pull GPU kernels, presigned submission upload. **Live verified 2026-05-30:** POST `https://www.kaggle.com/mcp` with `Authorization: Bearer $KGAT` and the MCP `initialize` payload returned **HTTP 200** with a valid serverInfo response. No second `KAGGLE_KEY` needed. Updated `.env` (`KAGGLE_API_TOKEN` + legacy `KGAT` for backward compat with anything reading the old name). RUNBOOK + docs must stop asking for `kaggle.json`. Operator error charged to me, not user.
Sources: live MCP probe (HTTP 200), Kaggle MCP docs at kaggle.com/docs/mcp. **Confidence: Well-established (live primary evidence).**

### F-051 — Task sizing rule (R-005): every ledger task ≈1 hour; club smalls, split bigs
Per user direction: deep-worker tasks must be sized for ~1 hour of Jules work — one substantive deliverable, planned + built + self-verified + PR'd in one session. Smaller items (≤15 min) are **clubbed** 2–3 into one coherent task; bigger items (>2h / whole pipelines / >5 files of new code) are **split** into independent siblings the planner fans out in parallel. Reviewer enforces scope (PRs that grew past ~1 hour become follow-up tasks, not monster merges). Implemented in `.claude/skills/sdlc/SKILL.md` (Task sizing rule), `INTEGRATION.md`, `prompts/jules_deep_worker.md` (+ `NEEDS_SPLIT:` PR slot). **Backlog resized live:** R1/R10/R11 SUPERSEDED → R1a/R1b, R10a/R10b, R11a/R11b children created; small winner-file reviews clubbed into TASK-R13 trio digest; size_hint stamped on all right-sized tasks. Ledger now: 20 BACKLOG · 3 BLOCKED · 3 SUPERSEDED. Selector still picks `owner` (40); 93 tests green.
Sources: user direction + execution. **Confidence: Well-established.**

### F-050 — Implemented: ledger ops + role-selector + Excel dashboard; verified live
`state.py` gained collections (tasks/hypotheses/experiments/suggestions/decisions/metrics) + ops (`create_task`/`create_hypothesis`/`create_experiment`/`create_suggestion`/`create_decision`/`add_metric`/`set_status`/`update_entity`). `selector.py` ports `score_roles` feasibility/scoring to JSON. `dashboard.py` renders `state/dashboard.xlsx`. `tools` gained `next`/`dashboard`/`seed`. **Verified live:** `tools seed` ingested all R-tasks into the ledger; `tools next` selected `owner` (score 40, "5 dispatchable vs 5 free slots"); `dashboard.xlsx` written. 93 tests green. The operator now appends work to ONE store and role-selects the next item — no hand-authored task .md as source of truth.
Sources: this revision (execution + live run). **Confidence: Well-established.**

### F-047 — Integration = new project SKILL.md + INTEGRATION.md mapping, DNA kept, Excel quarantined
Installed at `.claude/skills/sdlc/`: a rewritten **SKILL.md** (the operator-tick playbook: router→tick, state-ledger→`orchestrator.tools`, owner→Jules, no Excel, no API key), an **INTEGRATION.md** mapping table, `references/` (31 DNA files, kept), and `_legacy_excel/` (scripts+assets, do-not-run README). Operator prompts + AGENTS.md now point at it. This gives the project the SDLC orchestration discipline without a second state system.
Sources: this revision (execution). **Confidence: Well-established** (design decision, implemented + committed).

---

## Cluster Z — Audit 2026-05-30 (full-system review, max rigor)

### F-053 — All 7 `kernel-metadata.json` files in `kernels/` carry literal `username/` and `placeholder` values — first-submission BLOCKER
Audit of every `competitions/.../kernels/*/kernel-metadata.json` shows the same template stamped repeatedly with no per-account substitution: `"id": "username/..."` (not `sai1881/...`), `"dataset_sources": ["username/placeholder-dataset"]` (no real corpus dataset attached), `"model_sources": ["nvidia/nemotron-3-nano-30b-a3b-bf16/placeholder-version"]` (version literal). `"is_private"`, `"enable_gpu"`, `"enable_internet"` are JSON **strings** (`"true"`/`"false"`), not booleans — Kaggle's kernel-push API rejects string booleans. `enable_internet: "false"` would also block downloading base-model weights at runtime if the model source were correctly referenced. **Net effect:** `kaggle kernels push` would fail at validation time for E-002 and every sibling kernel. The "missing GPU dispatch trigger" the user asked about is a red herring — even if the trigger fired, the push would error.
Sources: live disk read of 7 kernel-metadata.json files; Kaggle API docs require `id: <username>/<slug>` and boolean flags. **Confidence: Well-established (live primary evidence).**

### F-054 — Zero scheduled cron / Task Scheduler triggers exist — the "autonomous loop" is dormant
`CronList` returns "No scheduled jobs." The prior conversation summary referenced a cron job `7,37 * * * *` id `88e9125b` — that job is **not present** in the active scheduler state. There is no Windows Task Scheduler entry firing `python -m orchestrator.tools dispatch|status` either (no evidence in the repo or registry). The system makes forward progress only when the user or this session manually invokes a tick. The current 4 IN_PROGRESS Jules sessions were spawned by past manual dispatch ticks and are draining toward completion with no replenishment of READY tasks. After they finish, the ledger has **0 READY, 0 BACKLOG, 0 BLOCKED** — the loop terminates.
Sources: CronList (empty); ledger task-status count (36 DONE / 15 SUPERSEDED / 4 IN_PROGRESS / 0 elsewhere). **Confidence: Well-established (live primary evidence).**

### F-055 — Ledger has NO task corresponding to "push E-002 to Kaggle GPU and ingest cv_score" — critical path is broken
Critical-path inspection: TASK-OPS-run-kernel-runner (DONE — built `tools/run_kernel.py`), TASK-OPS-gpu-dispatch-op (DONE — wired the `gpu_dispatch` op into `loop.py`/`state.py`), TASK-EVAL-cv-score-ingest (IN_PROGRESS — authoring the ingest path). **Missing:** an explicit task that fires `gpu_dispatch` for `experiment_id=E-002-baseline-rank32` with the right `slug`/`kernel_dir`/`owner`/`out_dir`. The operator-decision schema supports the action (`operator_decision.schema.json` lines 60–71), but no task tells the operator to emit it. Result: even with cron fixed and metadata fixed, the system will never push E-002 unless a task instructs it.
Sources: live ledger query for tasks containing "push"/"E-002"/"gpu_dispatch"/"executor" → 0 matches; operator_decision.schema.json. **Confidence: Well-established.**

### F-056 — `loop.py` line 246 hard-codes POSIX path `/tmp/gpu_run_{slug}.log` — fails on Windows host
The `apply_decision` path for `gpu_dispatch` opens a log file at `/tmp/gpu_run_{slug}.log`. On Windows (this host), `/tmp/` does not exist by default, so `open(...)` raises `FileNotFoundError`. Any operator decision carrying `gpu_dispatch` (the new-code-path branch keyed on `"slug" in g`) will crash mid-tick before the kernel push command launches. Compounds F-055: not only is no task firing `gpu_dispatch`, but the dispatcher would also crash if one did.
Sources: live disk read of `orchestrator/loop.py:246`. **Confidence: Well-established (static analysis).**

### F-057 — E-007 Jules session 13107147469450254389 stuck in out-of-scope edit retry loop, idle ~35 min
Live `list_activities` for session `13107147469450254389`: 30 activities. Plan generated 11:32, approved 11:33; classifier fix landed 11:35 (100% coverage); operator-steer userMessaged 11:48 asked Jules to ship steps 2–4 + PR. From 11:56 through 12:00:47 Jules emitted **26 identical `progressUpdated` artifacts** all containing the same diff for `competitions/.../data/solvers/cryptarithm/solve.py` — a path **outside** the task's `allowed_area` (`competitions/.../kernels/train-e007-cryptarithm`). Jules's write tool keeps rejecting the out-of-scope edit; Jules keeps retrying. No new activity since 12:00:47. The session consumes 1 lock slot for ~35+ minutes with zero forward progress. Root cause: task spec ("extend `data/corpus/v1/build_corpus.py`", "patch the cryptarithm solver") contradicts the locked `allowed_area`.
Sources: live `jules.list_activities` + session JSON read. **Confidence: Well-established (live primary evidence).**

### F-058 — Hypothesis-status casing inconsistency (`proposed` vs `PROPOSED`) — schema drift
Live count: 17 hypotheses with `status: "proposed"`, 3 with `status: "PROPOSED"`, 1 `supported`. Selector code (`selector.py`) and downstream queries that filter on `status == "PROPOSED"` will silently miss 17/21 hypotheses. The drift comes from two code paths (one in `state.py`'s `create_hypothesis`, one in a planner-emitted patch) using different casing. Effect on plan: the role-selector likely under-weights `innovator` because most hypotheses look "absent" from its PROPOSED filter.
Sources: live ledger query: `Counter(h.get('status') for h in state['hypotheses'].values())` → `{'proposed': 17, 'PROPOSED': 3, 'supported': 1}`. **Confidence: Well-established.**

### F-059 — Backlog promotion bottleneck: `cursors.jules_dispatched_2026-05-30 = 40` already at near-saturation vs `DAILY_JULES_BUDGET=200`
The daily-budget cursor shows 40 sessions dispatched today against a 200-cap — comfortable margin. But the in-flight count is only 4. Inference: 36 sessions ran and finished today; the lock manager and Jules pool are healthy. The bottleneck is NOT compute or quota — it's the **empty BACKLOG** (F-054) plus the **missing critical-path task** (F-055). When the planner / innovator role runs, it has no new hypotheses to seed because most of the 21 hypotheses are already attached to experiments — so it doesn't generate new BACKLOG either. The system is in a converged "all designed, nothing executes" state.
Sources: live ledger `cursors` + session count + task-status count. **Confidence: Well-established.**

### F-060 — Two in-flight Jules sessions for IN_PROGRESS tasks remain `QUEUED` (account_idx=0) — likely cold start, not failure
Sessions for TASK-E009-synthesis-kernel and TASK-SUBMIT-gate-decision and TASK-EVAL-cv-score-ingest are all `state: QUEUED` with `created_at` in the last few minutes. No PR URLs yet. Account_idx=0 only — the second Jules account hasn't been routed to. JulesPool round-robin may be account-skewed (need to verify it actually alternates). Not a defect today, but in a sustained run the 100/day cap of one account could clip.
Sources: live ledger sessions table. **Confidence: Supported (would need to inspect `jules_pool.py` round-robin and run-history to be Well-established).**

### F-061 — `state.py` schema is missing migration handling — old `data.experiment_id` vs new `data.slug` mismatch in `update_gpu_run`
`loop.py`'s new-path GPU polling (line 131) emits `update_gpu_run` with `data: {"slug": eid, ...}`, but `state.py` `_apply_op` for `update_gpu_run` keys the state dict by `data["experiment_id"]` (line 100). The two names disagree, so a `gpu_dispatch`-completed kernel's terminal state would be recorded under `state['gpu_runs'][None]` (the `.get("experiment_id")` default) instead of the intended slug. Silent data loss for GPU-run tracking.
Sources: live disk read of `loop.py:131` + `state.py:99-103`. **Confidence: Well-established (static analysis).**

### F-062 — `state.py` OPS set includes `"gpu_dispatch"` but no projection branch handles it in `_apply_op`
`OPS` contains `"gpu_dispatch"`, so `apply_patch` accepts the op without raising "unknown op". But `_apply_op` has no `elif op == "gpu_dispatch"` arm — it falls through to `raise ValueError(f"unknown op: {op}")`. So a `gpu_dispatch` op crashes mid-apply with a misleading error. (Confirms why no GPU run has been recorded yet.)
Sources: live disk read of `state.py:24-156`. **Confidence: Well-established (static analysis).**

### F-063 — The 4 "IN_PROGRESS" tasks ARE the entire pending queue; nothing follows them
Ledger snapshot 2026-05-30T13:00Z:
- TASK-E007-cryptarithm-guess-integration — stuck (F-057)
- TASK-E009-synthesis-kernel — Jules QUEUED, dependency-bound on E-002..E-008 GPU results that don't exist
- TASK-EVAL-cv-score-ingest — Jules QUEUED, no blocker
- TASK-SUBMIT-gate-decision — Jules QUEUED, no blocker
After all four merge, the BACKLOG is empty. With no planner/innovator run scheduled and no cron firing the dispatch loop, the system halts.
Sources: live ledger task-status count + session table. **Confidence: Well-established.**

### F-064 — `package_submission`/`validate_adapter` are coded but never invoked in the live path — first-submission integration untested
`tools/package_submission.py` (4165 bytes) and `tools/validate_adapter.py` (4239 bytes) exist and have tests, but no end-to-end run has chained `kernel-output → adapter/ → validate → package → submission.zip → competition-submit`. There is no `submissions/pending/*.zip` artifact on disk — only `.gitkeep` placeholders. The first time the chain runs will be the first time it's tested live.
Sources: disk read of `competitions/.../submissions/{pending,submitted}/` (only `.gitkeep`); no `submitted/*.json` audit trail. **Confidence: Well-established.**

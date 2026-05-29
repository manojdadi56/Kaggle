# 07 — Glossary

| ID | Term | Working definition |
|----|------|--------------------|
| G-001 | **Jules** | Google's autonomous coding agent (Google Labs). Runs async on an ephemeral Google VM, clones a connected GitHub repo, does coding work, opens a PR. Triggered via REST at `https://jules.googleapis.com/v1alpha`. The **worker** in this design. |
| G-002 | **Source** (Jules) | A GitHub repo connected to Jules, addressed as `sources/github/{owner}/{repo}`. Created via the web UI (GitHub App install); listable via API. |
| G-003 | **Session** (Jules) | One unit of Jules work (the API noun for a "task"). Created with `POST /sessions`; emits `Activity` events; ends `COMPLETED`/`FAILED` with `outputs[]`. |
| G-004 | **Activity** (Jules) | An event within a session (planGenerated, agentMessaged, progressUpdated, sessionCompleted…). Polled via `…/activities` with a `createTime` cursor. |
| G-005 | **automationMode / AUTO_CREATE_PR** | Session setting that makes Jules open a GitHub PR automatically at the end. |
| G-006 | **requirePlanApproval** | Session flag; API sessions auto-approve by default (false ⇒ fully autonomous). |
| G-007 | **Operator** | (R-001) The **Claude Code session itself**, on the user's subscription — the brain that each tick reads context, decides, reviews/merges PRs, dispatches Jules, triggers training, and submits. It is NOT an API key and NOT a `claude -p` subprocess spawned by Python. It drives the toolkit (G-022). Triggered interactively, by a routine (G-019), or by Task-Scheduler `claude -p` via an OAuth token (G-020). |
| G-008 | **Orchestrator / toolkit** | (R-001) The local Python package `orchestrator/` — pure mechanics (state, locks, Jules/Kaggle/GitHub clients, executors, packaging, submit gate) plus the `tools` CLI (`context`/`apply`/`status`). It holds **no intelligence**; the operator (Claude Code) drives it. |
| G-019 | **Routine** (`/schedule`) | A scheduled Claude Code session that runs on Anthropic cloud on the subscription (no API key), survives the laptop being off, min 1-hour interval. The recommended unattended operator trigger. |
| G-020 | **CLAUDE_CODE_OAUTH_TOKEN** | A ~1-year subscription OAuth token from `claude setup-token` that lets `claude -p` run headless billed to the subscription (no API key). Used by the optional Task-Scheduler self-drive path. |
| G-021 | **ANTHROPIC_API_KEY (avoided)** | Pay-per-token API credential. Deliberately NOT used; if set it overrides subscription auth, so it must stay unset (F-039). |
| G-022 | **Operator tick** | One run of the operator: `tools context` → decide → write `decision.json` → `tools apply`. The unit the routine/loop/Task-Scheduler repeats. |
| G-009 | **GPU executor** | The component that actually trains the LoRA adapter (needs a real GPU). NOT Jules. Candidates: Kaggle Notebooks (free GPU, API-driven), user's local GPU, or paid cloud. |
| G-010 | **LoRA adapter** | Low-Rank Adaptation weights fine-tuned on top of a frozen base model. Nemotron submission = a rank-≤32 adapter + `adapter_config.json` zipped. |
| G-011 | **Nemotron-3-Nano-30B-A3B-BF16** | The fixed base model for the competition (30B total / 3B active MoE). Provided as a Kaggle Model; may not be replaced or full-fine-tuned. |
| G-012 | **Host-side scoring** | Kaggle/NVIDIA loads your adapter into the base model and runs vLLM inference on a hidden test set with fixed params. You optimize the adapter, not an inference notebook. |
| G-013 | **StatePatch / Event-sourcing** (from SDLC) | A structured list of operations proposed by an actor; applied atomically to an append-only event log; projections derived from it. Adopted for the orchestrator's state. |
| G-014 | **Idempotency key** | A deterministic key on each state op so retries collapse without double effects. |
| G-015 | **8-surface role prompt** (from SDLC) | The trigger-prompt template: Identity, Activation, Inputs, SOP, Reasoning discipline, Output contract, Failure handling, Eval checklist. |
| G-016 | **RunEnvelope** (from SDLC) | The structured assignment the orchestrator hands an actor: selected role, reason, permissions, locks, definition-of-done. |
| G-017 | **AGENTS.md** | Repo convention Jules auto-reads for build/test/style/setup instructions. Our channel for giving every Jules session standing context + guardrails. |
| G-018 | **KGAT token** | Kaggle Access Token (`KGAT_…`) used as a bearer for the Kaggle MCP. Distinct from the legacy `KAGGLE_USERNAME`/`KAGGLE_KEY` used by the CLI. |

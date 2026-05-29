# Kaggle — Autonomous Competition Loop

A local Python **orchestrator** that runs Kaggle competitions with minimal supervision by coordinating two AI actors and a pluggable GPU backend:

- **Jules** (worker) — authors/iterates non-GPU code, opens GitHub PRs. Triggered via the Jules REST API.
- **Claude Code headless** (operator) — plans, reviews/merges PRs, drives training, packages adapters, submits within a budget. Returns machine-readable decisions.
- **GPU executor registry** — trains the LoRA adapter on Kaggle Notebooks / a local 40 GB box / paid cloud (Jules has no GPU).

State is **event-sourced in git** (`state/`), using single-writer + idempotency + per-area locks. See the full design in [`research-jules-orchestration/REPORT.md`](research-jules-orchestration/REPORT.md).

First competition: **NVIDIA Nemotron Model Reasoning Challenge** (LoRA, rank ≤ 32).

## Quickstart
```bash
pip install -r requirements.txt
cp .env.example .env          # fill in keys (rotate the ones pasted in chat first)
pytest -q                      # offline test suite (mocks only)
python -m orchestrator.dryrun  # full mock end-to-end tick, exits 0
python -m orchestrator.status  # show current state
```
Real runs and the human-gated setup steps are in [`RUNBOOK.md`](RUNBOOK.md).

> Safety: tests and the dry-run make **no live calls** to Jules/Kaggle/Anthropic. Secrets live only in a gitignored `.env`.

# RUNBOOK — running the autonomous Kaggle orchestrator

The build self-tests with **mocks only**. Going live needs a few **human-gated**
one-time steps (creds, confirming the submission cap, the first real Jules
session). Do those once, then the loop ticks unattended.

## 0. Prereqs
```bash
pip install -r requirements.txt
claude --version      # operator (Claude Code headless)
kaggle --version      # submission + GPU kernels
```

## 1. Credentials (local only — never commit)
```bash
cp .env.example .env
```
Fill in `.env`. **Rotate the keys that were pasted into chat first** (Jules + Kaggle):
- `JULES_API_KEY` — from jules.google settings (rotate the old one).
- `KAGGLE_USERNAME` — your Kaggle username.
- `KAGGLE_API_TOKEN` (=KGAT, format `KGAT_…`) — the **single** Kaggle bearer the orchestrator uses for everything: MCP, web API, kernel push/poll/pull, submission upload (no separate `kaggle.json` `key` needed). Live-verified against `https://www.kaggle.com/mcp`.

**The operator is the Claude Code session on your subscription — there is NO `ANTHROPIC_API_KEY`.**
- Do NOT set `ANTHROPIC_API_KEY` (if set, it overrides the subscription). Run `unset ANTHROPIC_API_KEY` / clear it in `/config`.
- For the OPTIONAL unattended self-drive mode only: `claude setup-token` → put the printed token in `CLAUDE_CODE_OAUTH_TOKEN` (subscription OAuth, not an API key).

`.env` is gitignored. Verify nothing secret is staged: `git status`.

## 2. Verify the build (offline, safe)
```bash
pytest -q                      # full suite, no network
python -m orchestrator.dryrun  # full mock end-to-end, exits 0
python -m orchestrator.status  # current state snapshot
```

## 3. Human-gated Phase 0 (do once, before any live submit)
1. **Confirm the submission cap + that scripted submission is allowed** on the
   competition's gated Submit/Rules pages. Set `MAX_AUTO_SUBMITS_PER_DAY` in `.env`
   to `min(your-policy, real-cap)`. The gate also reads remaining submissions live.
2. **One real Jules session probe** (optional but recommended) to capture the
   exact COMPLETED-PR JSON shape (Q-003): create a trivial session against
   `sources/github/manojdadi56/Kaggle`, poll to COMPLETED, inspect `outputs`.
3. **Optional Kaggle-GPU QLoRA dry-run** (Q-012): confirm a rank-≤32 30B QLoRA
   fits + finishes within Kaggle free-GPU limits.

## 4. Phase 1 — manual baseline (get a real score first)
1. Run `TASK-1.0` (operator vendors references into `competitions/<slug>/references/`).
2. Fork `tonghuikang/nemotron`, train a small LoRA on Kaggle GPU.
3. Package: `package_submission(adapter_dir, submission.zip)` (validates rank ≤ 32).
4. Submit once: `kaggle competitions submit nvidia-nemotron-model-reasoning-challenge -f submission.zip -m "baseline"`.
→ first leaderboard score + a proven pipeline the loop then automates.

## 5. Run the operator (the Claude Code session IS the operator — no API key)
The operator drives the toolkit each tick. One tick =
```bash
python -m orchestrator.tools context --tick RUN-<ts>   # read decision-context JSON
#   -> Claude Code (you / routine) decides, writes decision.json (schema: operator_decision.schema.json)
python -m orchestrator.tools apply decision.json        # execute it (dispatch / merge / submit / commit)
python -m orchestrator.tools status                     # monitor
```
Recurring trigger options (all subscription, no API key) — see `prompts/operator_routine.md`:
- **Cloud routine** (survives laptop-off, ≥1h): `/schedule every hour, run prompts/operator_routine.md`.
- **Sub-hour, laptop-on**: Windows Task Scheduler → `claude -p "$(cat prompts/operator_routine.md)"` with `CLAUDE_CODE_OAUTH_TOKEN` set, `ANTHROPIC_API_KEY` unset.
- **Interactive / while a session is open**: `/loop 30m run prompts/operator_routine.md`, or just run a tick yourself.

Feedback channel (D-3): talk to Claude; the operator writes `feedback.md`. Pending
submissions needing your approval appear in `competitions/<slug>/submissions/pending/`.

## 6. Wiring the local 40 GB 2-GPU box later (Q-014)
Implement `orchestrator/executors/local_40g.py` (`submit_run/poll/fetch`) against
your reach mechanism (SSH / a small job-runner). Set it as the preferred backend
in the operator's `gpu_dispatch`. No loop changes needed.

## Safety notes
- Operator auto-submits only when a candidate **beats best local CV** AND under the
  daily cap; otherwise it queues for your approval.
- Single-writer: only the operator writes `state/`; only Jules writes project code.
- Hard invariants enforced: LoRA rank ≤ 32, base `Nemotron-3-Nano-30B-A3B-BF16`, `\boxed{}`.
- Multi-account Kaggle pooling is intentionally **not** supported (ToS / DQ risk).

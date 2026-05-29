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
- `KAGGLE_USERNAME` / `KAGGLE_KEY` — from kaggle.com account (rotate).
- `ANTHROPIC_API_KEY` — Console key, or run `claude setup-token` for a CI token.
- `KGAT` — only if you use the Kaggle MCP for agentic browsing (optional).

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

## 5. Run the loop (after Phase 0/1)
```bash
python -m orchestrator.loop      # run_forever (or call Orchestrator.run_tick in a scheduler)
python -m orchestrator.status    # monitor anytime
```
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

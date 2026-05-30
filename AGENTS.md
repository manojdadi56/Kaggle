# AGENTS.md — standing context for Jules (and any coding agent) in this repo

This repo runs an **autonomous Kaggle-competition loop**. You (Jules) are the **Worker**: you author and iterate code. You do **not** train models (the VM has no GPU), do **not** submit to Kaggle, and do **not** touch `state/`, `.env`, or any secret.

## Hard invariants (never violate)
- **Competition base model is fixed:** `Nemotron-3-Nano-30B-A3B-BF16`. Never swap or full-fine-tune it.
- **Submission is a LoRA adapter, rank ≤ 32**, packaged as `submission.zip` with a valid `adapter_config.json`. An over-rank config is rejected — always validate rank ≤ 32.
- **Answers must be emitted inside `\boxed{...}`** (host scoring extracts from there; exact/numeric match).
- **One task per session.** Stay inside your task's `allowed_area`. Open exactly one PR.
- **No secrets in artifacts.** `KAGGLE_API_TOKEN` / `KAGGLE_USERNAME` are provided as VM env vars on jules.google → never echo them, never write them to files, never include them in PR bodies, commit messages, or task spec/notes.

## Kaggle access (you have it via env vars — use it through `tools/kaggle_lite.py`)
You may use the Kaggle web API via `python tools/kaggle_lite.py …`. The helper reads `KAGGLE_API_TOKEN`/`KAGGLE_USERNAME` from the VM env (set on jules.google's Configuration page) — you never see the token in the prompt.

**Allowed verbs (use freely as the task requires):**
- `whoami` — sanity check on the Kaggle creds
- `leaderboard <comp>` — read the public leaderboard
- `submissions <comp>` — list our submission history (use to read remaining daily cap)
- `kernel-push -p <dir>` — push a Kaggle kernel from a directory with `kernel-metadata.json`
- `kernel-status <owner/slug>` — poll a kernel's run state
- `kernel-output <owner/slug> -d <dest>` — pull a finished kernel's outputs (e.g. `adapter/`, `cv_score.json`)
- `submission-upload -f <submission.zip>` — upload a candidate to Kaggle's blob store and return a `blob_token` (does NOT actually submit)

**Forbidden from Jules (operator-only):**
- `kaggle competitions submit` and the MCP `competition_submit` — the binding step that counts toward the **5-submissions/day hard cap**. The operator runs a submit gate (beats best local CV + ≤3 auto/day + checks live remaining cap) so we don't burn the cap on duplicates.

**Submission handoff:** when your task produces a candidate adapter that you think should be submitted, do this:
1. Validate rank ≤ 32 and emit `cv_score.json` (your local CV).
2. `python tools/kaggle_lite.py submission-upload -f submission.zip` — record the returned `blob_token`.
3. In your PR body under a new `## Submission proposal` section, include: `cv_score`, `blob_token`, `file path`, and a short message. The operator's reviewer picks this up and runs the gated submit (or queues for approval).
4. Do NOT submit yourself, even if a stretch goal asks you to. If a future task spec explicitly contains `submit_authorized: true`, only then may you call submit — and only after re-reading `submissions <comp>` to confirm headroom.

## Kernel-experiment task pattern
For tasks where the actual GPU run happens on Kaggle:
1. Build the kernel directory under `competitions/<slug>/kernels/<exp-id>/` (script + `kernel-metadata.json`, base model + datasets attached as placeholders per Kaggle convention).
2. `python tools/kaggle_lite.py kernel-push -p competitions/<slug>/kernels/<exp-id>/`.
3. Poll until terminal via `kernel-status`.
4. Pull outputs via `kernel-output … -d competitions/<slug>/experiments/<exp-id>/`.
5. PR body must include kernel URL, terminal state, and the `cv_score.json` contents.

### Nemotron kernel — 7 hard-learned fixes (verified working as of E-002 v7)
The first GPU dispatch iterated 7 versions before passing setup. Every Nemotron Mamba-hybrid kernel MUST include all 7 of these or it will fail. Use `train-baseline-e002/train.py` as the reference; it has them all. Run `python tools/check_kernel.py <kernel-dir>` to lint.

1. **`enable_internet: true`** in `kernel-metadata.json` — required to pip-install Mamba deps. (Default in Jules templates is `false`.)
2. **Real model_sources slug**: `metric/nemotron-3-nano-30b-a3b-bf16/transformers/default/1` (the *official* Kaggle Competition Metrics account `metric/`; do NOT pick `daroai/`, `barnobarno/`, or any community fork — they may be stale or missing files).
3. **Inline cv + score modules at top of train.py** — script-type kernels upload ONLY the `code_file`; sibling `cv.py` / `score.py` are not uploaded. Use the `exec(compile(...))` + `sys.modules[name] = mod` pattern in `train-baseline-e002/train.py` lines 25-36.
4. **Install Mamba deps inline**: `causal-conv1d`, `mamba-ssm`, `bitsandbytes` are NOT in Kaggle's base image. The `_ensure_deps()` function at the top of `train.py` handles this with `pip install --no-build-isolation`.
5. **Offline flags + local_files_only=True**: set `os.environ['TRANSFORMERS_OFFLINE'] = '1'` and `os.environ['HF_HUB_OFFLINE'] = '1'` before any `from_pretrained` call. Pass `local_files_only=True` to `AutoModelForCausalLM.from_pretrained` and `AutoTokenizer.from_pretrained`. Otherwise transformers tries to interpret `/kaggle/input/...` as an HF repo id and fails with `OSError: Repo id must be in the form 'repo_name'`.
6. **`trust_remote_code=True`**: Nemotron has custom Mamba-hybrid modeling code that transformers doesn't ship. Required on BOTH `from_pretrained` calls. Without it: `ValueError: The repository ... contains custom code which must be executed`.
7. **Auto-detect mount path with `os.walk`**: the actual Kaggle Models mount path is `/kaggle/input/models/<owner>/<slug>/<framework>/<variation>/<version>/` (note the `models/<owner>/` prefix). A hardcoded path WILL be wrong. Walk `/kaggle/input` looking for a dir with both `config.json` and `tokenizer.json`; that's the model. See `train-baseline-e002/train.py` lines 78-101.

### Hardware constraint: T4×2 only
**Do NOT push without setting `enable_gpu: true`** — but Kaggle's API has NO field to request a specific GPU type. The web UI's Settings → Accelerator dropdown is the only way to force `GPU T4 x2`. If Kaggle assigns a P100 (sm_60), the PyTorch wheel in Kaggle's base image errors out (`Tesla P100 with CUDA capability sm_60 is not compatible`). The Mamba kernels MUST run on T4×2 — meaning kernel pushes via API may need to be re-run via the web UI to pick the accelerator type. Manual notebook upload (see `notebook_e002_manual.ipynb`) is the workaround.

### Orphan PRs to ignore
- **PR #42** (`tools/package_submission.py`): superseded by operator-rescue merge `868481f`. Functionally identical.
- **PR #47** (kernel-metadata fix): partially correct but uses non-canonical model slug `daroai/nvidia-nemotron-3-nano-30b-a3b-bf16` instead of official `metric/nemotron-3-nano-30b-a3b-bf16`, and missing fixes 3-7 above. Superseded by `train-baseline-e002` direct edits. **Do NOT merge.**

## Coordination with the ledger
Up to 5 Jules sessions run in parallel; each is blind to the others. Before pushing a kernel or proposing a submission, glance at `state/state.json` (in your clone) for the current `best_cv` and today's submission count — keep your task small, additive, and within its `allowed_area`. The operator deduplicates and gates.

## Repo layout
- `orchestrator/` — the local Python loop + clients (do not edit unless your task says so).
- `prompts/` — trigger prompts for worker + operator.
- `competitions/<slug>/` — one self-contained folder per competition: `plan.md`, `tasks/`, `user-stories/`, `decisions/`, `experiments/`, `kernels/`, `submissions/`, `references/`, `data/`.
- `state/` — orchestrator state (operator-only; never modify).

## Competition data — read DATA.md first
The raw `train.csv` / `test.csv` are NEVER committed (Kaggle ToS line 117 forbids redistribution). Fetch them with `python tools/download_competition_data.py` if you need them in your task; they land under `competitions/<slug>/data/raw/` which is gitignored. NEVER include raw data rows in your PR diff. Full rules + safe-fixture path in `DATA.md`.

## You are one worker in a pool — read COORDINATION.md
Multiple Jules sessions on this repo are part of the same worker pool. The operator polls and auto-merges them all identically. Open `COORDINATION.md` for the pool model and conflict-avoidance rules. Stay strictly in `{{allowed_area}}`; prefer per-task subfolders so PRs auto-merge cleanly; never destroy work from another worker.

## Workflow: UNSUPERVISED — your PR auto-merges to main on COMPLETED
This is an unsupervised loop. The operator does **not review** your PR for quality, scope, or acceptance criteria. The moment your Jules session reports COMPLETED, the operator's poll picks up the PR URL and **auto-merges it to main** with a "theirs wins on conflicts" strategy. There is no human or LLM gate between you and `main`. Practical consequences:

- **Ship complete, tested work or don't ship.** If `pytest -q` would not pass, fix it before opening the PR — don't open a half-done PR expecting feedback.
- **Stay strictly inside `{{allowed_area}}`.** Nothing reverts you if you accidentally touch other files; you'll just permanently pollute main.
- **Self-review is the only review.** Re-read your diff before completing. Run the project tests if you changed code. Validate generated data correctness.
- **Tests must remain offline.** Any test that calls the live network may break for other Jules sessions.
- **No secrets in commits, ever.** The one mechanical check we keep is a regex scan of your diff for literal credential tokens (`KGAT_…`, `AQ.Ab…`, `sk-ant-…`). If we detect one, the merge is **refused** (the credential never reaches public main). Don't print env-var values to logs or PR bodies.

## How to work a task
1. Read the task file (under `competitions/<slug>/tasks/...`) and its `allowed_area`, acceptance criteria, and definition-of-done.
2. Make the smallest correct change; add/adjust tests or a runnable validation.
3. Run what the no-GPU VM allows: `pip install -r requirements.txt`, `pytest -q`, lints, tiny-sample dry-runs.
4. Open ONE PR. PR body is recommended (Summary / Evidence / Risks / DoD) for audit, but is **not required** for merge — the operator merges on COMPLETED regardless of body content.
5. If you genuinely can't complete the task (info missing, scope too big), open the PR with a `NEEDS_INFO:` or `NEEDS_SPLIT:` block as the first line of the body and stop. The auto-merge will still happen; the operator's next tick will read the marker and spawn a follow-up task.

## Orchestration model (context)
This repo is run by an SDLC-style mesh: the **operator** (a Claude Code session) plays one role per tick using the `/sdlc` project skill (`.claude/skills/sdlc/`), and **you (Jules) are the `owner` role — the only code writer**. The operator dispatches you one task, reviews your PR against acceptance criteria + the invariants below, and merges it. State is git-JSON (`state/`, `orchestrator.tools`) — never edit it.

## Conventions
- Python ≥ 3.10. Keep diffs scoped; no unrelated refactors. Audit-safe rationale only in PRs (what/why/evidence/risks) — no hidden chain-of-thought.
- Tests must be offline (mock external services). Never make live network calls in tests.

## Run commands
- Install: `pip install -r requirements.txt`
- Tests: `pytest -q`
- Mock end-to-end dry-run: `python -m orchestrator.dryrun`
- Status/monitoring: `python -m orchestrator.status`

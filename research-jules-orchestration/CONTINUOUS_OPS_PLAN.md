# Continuous Operations Plan — the autonomous research engine

**Status:** PLAN (no execution). Defines how the operator keeps planning, generating hypotheses, dispatching long parallel Jules tasks, reviewing, and analyzing — continuously — until the deadline. Grounded in the SDLC skill (innovator → planner → reviewer → validator/analyst, one decision per cycle, always-move-forward).

## 1. Confirmed model & locked parameters — R-002 (2026-05-30)
- **Operator = the Claude Code session** (subscription, no API key). **Worker = Jules.** Shared state = the **GitHub repo**.
- **Two-part runtime (user's design):**
  - **Python tracker** (`orchestrator` daemon, mechanical, NO LLM) — continuously polls Jules, records completions/PRs into state, and **keeps the in-flight pool full** by dispatching the next `tasks/todo/*.md` whenever a slot frees (concurrency target). This is the "python script that keeps tracking and triggering."
  - **Claude Code operator** (goal/ralph loop + scheduled wakeups + event triggers) — the brain: reviews/merges Jules PRs, generates new hypotheses → writes new deep task files into the queue, analyzes results, and does gated submits.
- **Trigger:** goal/ralph loop + scheduled wakeups now (this session) → cloud Routine option later.
- **Compute:** **Jules-only research loop first** (non-GPU). Kaggle: `KAGGLE_USERNAME=sai1881` + `KGAT` stored (MCP read/submit); **`KAGGLE_KEY` PENDING** (needed for GPU kernel training + reliable CLI).
- **Throughput (R-002):** **5 concurrent** deep Jules sessions; **100 tasks/day** ceiling (the paid daily cap). Tracker keeps 5 in flight; operator tops the queue.
- **Autonomy:** **full** — operator invents hypotheses, writes tasks, dispatches every tick within budget; escalates only (a) submissions (gated: beats-best-CV + ≤3/day, real cap 5) and (b) genuine strategy forks.
- **Rules locked (scraped `tab-rules.md`):** 5 submissions/day, 2 finals, **one account only** (multi-account = DQ), prize needs a **public notebook + writeup + CC-BY-4.0**.

## 2. The strategic thesis (what we're optimizing)
Cross-validated from the winner + discussions: **the lever is DATA QUALITY, not exotic training.** Winner (LB 0.85): per-category **deterministic solvers** → generate **verified `\boxed{}` chain-of-thought** → **1-epoch LoRA SFT (rank ≤ 32, alpha 64)**; no RL, no distillation. So the engine pours effort into: (a) identifying problem categories, (b) building correct solvers/generators per category, (c) producing large, verified, well-formatted CoT corpora, (d) data filtering/balancing, (e) tight CV that mirrors host scoring, (f) disciplined SFT ablations. Most of (a)–(e) is **non-GPU → Jules can do it now**; (f) needs the GPU executor.

## 3. The continuous tick (SDLC fused single-cycle)
Each operator tick (via `tools context` → decide → `tools apply`) runs these stages and commits one coherent move + a parallel fan-out:
1. **Reconcile** — read state, in-flight sessions, merged PRs, new results, feedback.
2. **Analyst** — fold finished Jules PRs / experiment results into the **experiments ledger**; update best-CV, mark hypotheses supported/refuted.
3. **Innovator** — mine `references/` (technique-backlog, discussions, winner) + recent results → propose/rank new **hypotheses** (H-IDs) with expected effect + how to test.
4. **Planner** — convert top hypotheses into **deep Jules tasks** (and, once Kaggle keys exist, GPU experiments); keep the in-flight pool topped to the concurrency target with **certified-independent** tasks (disjoint `allowed_area`).
5. **Reviewer** — review open Jules PRs vs acceptance criteria + invariants; merge clean ones (`pr_merges`), or spawn a follow-up fix task.
6. **Submitter (gated)** — if a fresh adapter beats best CV and budget remains, package + submit; else queue for approval.
7. **Record** — append events; write an audit-safe paragraph; commit.

The operator never idles: if nothing else is actionable it generates the next hypothesis/experiment or deepens analysis (SDLC always-move-forward).

## 4. New state ledgers (to implement when we "start")
Add to the toolkit/state (small additions to `state.py` + task-file conventions):
- **Hypotheses ledger** `competitions/<slug>/hypotheses/H-XXX.md` + index in `state.json`: `{id, statement, rationale, expected_effect, status: proposed|testing|supported|refuted, source_refs, experiments:[E-IDs]}`.
- **Experiments ledger** `competitions/<slug>/experiments/E-XXX/` + `state.json`: `{id, hypothesis, config (data recipe / LoRA params), backend, jules_sessions:[], cv_score, status, artifact, notes}`.
- Linkage: hypothesis → experiments → Jules sessions / GPU runs → CV → submit decision. This is the SDLC event-sourced pattern extended to research.

## 5. Deep, parallel Jules tasks (your explicit ask)
- **Deep contract:** `prompts/jules_deep_worker.md` — tasks are scoped *big* and Jules is told to take its time, plan, mine references, build in steps, self-verify, self-review, and only PR when truly complete. Each task carries acceptance criteria + a definition-of-done.
- **Parallel + continuous:** the operator keeps ~12 independent deep sessions running (disjoint `allowed_area` + own branch; per-area locks). As each PR lands and merges, a slot frees and the operator dispatches the next hypothesis's task — so the pool stays full continuously.
- **Independence discipline:** tasks are sliced by category / file area so they never collide (e.g. one task per problem-category solver, one per data-augmentation strategy, one for the eval harness, one for corpus tooling).

## 6. Seeded research backlog (Wave 1 — runs NOW, Jules-only, no Kaggle keys)
Stored as deep task files under `competitions/<slug>/tasks/todo/`. Initial hypotheses → tasks:
| H | Hypothesis | Wave-1 Jules task(s) | Area |
|---|-----------|----------------------|------|
| H-001 | A clean problem-**category taxonomy** (from train.csv + discussions) lets us build targeted solvers | TASK-R1: derive category taxonomy + classifier | `references/analysis-categories.md`, `data/taxonomy/` |
| H-002 | Per-category **deterministic solvers** produce verified answers (winner's core lever) | TASK-R2..Rk: one solver task per category (parallel) | `data/solvers/<cat>/` |
| H-003 | **Verified `\boxed{}` CoT** generation at scale beats raw answers | TASK-R7: CoT generator + verifier over solver outputs | `data/cot/` |
| H-004 | A **local CV harness** mirroring host scoring (temp 0, `\boxed{}`, ±1e-2) makes results trustworthy | TASK-R8: eval harness (extends merged eval/score.py) | `eval/` |
| H-005 | **Data filtering/dedup/difficulty-balancing** improves generalization to the hidden set | TASK-R9: corpus curation pipeline | `data/curation/` |
| H-006 | A faithful **SFT training script** (rank≤32, 1-epoch) ported from the winner, GPU-ready | TASK-R10: training kernel authoring (runs later on GPU) | `kernels/train/` |
| H-007 | Mining the **217 discussions** surfaces tried/failed ideas to avoid + winning tricks | TASK-R11: discussion meta-analysis → ranked idea list | `references/analysis-discussions.md` |
| H-008 | Prize needs a **public notebook + writeup** — draft early, keep updated | TASK-R12: writeup + public-notebook skeleton | `writeup/` |

(The operator expands this every tick — H-009, H-010, … — as results come in. This table is the seed, not the ceiling.)

## 7. What needs Kaggle keys (Wave 2 — train→submit)
Once `KAGGLE_USERNAME`/`KAGGLE_KEY` are in `.env`: wire `kaggle_gpu` to push the training kernel (TASK-R10 output) → poll → pull adapter → CV → gated submit; pull public notebooks via `tools/pull_notebooks.py`. The 40 GB box plugs in as `local_40g` when configured.

## 8. "Start" checklist (what your "go" triggers — still not done here)
1. Implement the hypotheses/experiments ledgers in `state.py` + `tools` (small).
2. Seed Wave-1 deep task files (this plan's table) into `tasks/todo/`.
3. Set throughput config: `CONCURRENCY_CAP=12`, daily budget 60.
4. Start the operator `/loop` in this session (or run ticks manually) → it dispatches the first ~12 deep Jules sessions, then continuously reviews/merges/▶generates.
5. (When keys arrive) flip on Wave 2 (GPU train→submit).

## 9. Risks / guards
- Daily Jules cap 100 / Agent-SDK credit → 60/day budget + the operator tracks usage in `state.json`.
- Independence errors → per-area locks; "if unsure, don't parallelize."
- Deep tasks stalling → client-side timeout + `:sendMessage` nudge, then re-dispatch (resume cursor).
- One-account rule → never spin alt accounts (locked). Submissions gated. Prize-eligibility writeup tracked from day one (H-008).

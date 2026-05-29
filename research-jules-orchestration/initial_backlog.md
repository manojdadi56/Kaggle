# Initial Backlog — Nemotron (draft, planning only)

Drafted 2026-05-30. These become `competitions/nvidia-nemotron-model-reasoning-challenge/{user-stories,tasks/todo}/*.md` when the build session scaffolds the repo. **No task here has been dispatched.**

Actor legend: **[OP]** = operator (Claude Code, has web/git/kaggle). **[JULES]** = worker (analyzes/authors in-repo, no GPU, no creds). **[GPU]** = executor backend.

---

## US-1 — Analyze existing solutions  *(the initial story; foundation for everything)*
> As the system, I want a structured understanding of the best existing Nemotron solutions and the competition's data/scoring, so that training tasks start from proven techniques instead of from scratch.

**Why first:** the open-source progress-prize winner (`tonghuikang/nemotron`) + community repos + the official starter already encode what works. Mining them is the highest-leverage, lowest-cost first move (no GPU needed → perfect for Jules).

**Reachability decision:** references are **vendored into the repo by the operator** (see TASK-1.0); Jules analyzes in-repo. A separate Phase-0 probe (TASK-0.P) tests whether Jules can clone public repos itself.

### Tasks
- **TASK-1.0 [OP] — Vendor reference solutions into `references/`** *(prerequisite; not a Jules task)*
  - Goal: clone/copy into `competitions/<slug>/references/`: `tonghuikang/nemotron` (winner), `yunior123/nvidia-nemotron-reasoning`, `SebAustin/NVIDIA-Nemotron-Model-Reasoning-Challenge`, the official starter notebook (ryanholbrook), and 2–3 top public Kaggle notebooks for the comp. Also drop in the competition `train.csv`/`test.csv` schema and the base-model card.
  - Allowed area: `competitions/<slug>/references/**`, `competitions/<slug>/data/**`.
  - DoD: references present + a `references/INDEX.md` listing each with source URL + license.
- **TASK-1.1 [JULES] — Analyze the winning solution** *(parallel-eligible)*
  - Goal: read `references/tonghuikang-nemotron/**`; produce `references/analysis-winner.md` capturing: data strategy, LoRA config (rank, target modules, hyperparams), training recipe, decoding/prompt tricks, and what made it score. Flag the LoRA rank vs the ≤32 cap and any compute assumptions.
  - Allowed area: `references/analysis-winner.md` (write), `references/**` (read).
  - Acceptance: every claim cites a file/line in the reference; ends with a ranked "techniques to adopt for our compute (40 GB 2-GPU / 2×T4)".
- **TASK-1.2 [JULES] — Analyze community repos + official starter** *(parallel-eligible; disjoint output)*
  - Goal: `references/analysis-community.md` — compare the 2 competitor repos + starter; extract the common pipeline (load base → QLoRA → package `submission.zip`), divergences, and the canonical packaging/validation steps (rank ≤ 32, `adapter_config.json`).
  - Allowed area: `references/analysis-community.md` (write), `references/**` (read).
- **TASK-1.3 [JULES] — Analyze data schema + scoring harness** *(parallel-eligible; disjoint output)*
  - Goal: `references/analysis-data-and-scoring.md` — document `train.csv`/`test.csv` columns, the `\boxed{}` answer format, the fixed host vLLM params (temp 0, max_lora_rank 32, …), and the implied eval harness we should replicate locally for CV.
  - Allowed area: `references/analysis-data-and-scoring.md` (write), `references/**`,`data/**` (read).
- **TASK-1.4 [OP] — Synthesize into the plan**
  - Goal: fold the three analyses into `plan.md` (chosen baseline approach + ranked technique backlog) and open the follow-on training/data tasks. Depends on 1.1–1.3.

**Parallelism:** 1.1 ∥ 1.2 ∥ 1.3 are independent (disjoint output files, read-only on shared refs) → dispatch as concurrent Jules sessions (≤3 free-tier cap). 1.0 precedes all; 1.4 follows all.

---

## US-2 — Analysis validation  *(gate before spending GPU)*
> As the system, I want the analysis conclusions validated as reproducible, so we don't build training on a misread.

- **TASK-2.1 [JULES] — Build a local CV eval harness** that mirrors host scoring (`\boxed{}` extraction, exact/numeric match) and runs on a tiny sample → `eval/`.
- **TASK-2.2 [JULES/dev_local] — Smoke-test the packaging path**: produce a dummy rank-≤32 adapter + `adapter_config.json`, run the validator, confirm a well-formed `submission.zip`. (Runs on `dev_local` 4 GB — tiny model, no real training.)
- **TASK-2.3 [OP] — Validate** that the winner's recipe actually runs end-to-end on a toy model before committing GPU hours. Depends on US-1.

---

## US-3 — Synthetic data generation  *(parallel with early training)*
> As the system, I want curated + synthetic reasoning data, so the adapter generalizes to the hidden test set.
- **TASK-3.x [JULES]** — data-gen scripts (generate reasoning problems with `\boxed{}` solutions), filtering/dedup, difficulty balancing → `data/synthetic/`. CPU/no-GPU → Jules-friendly. Can run ∥ with US-2.

---

## US-4 — Training tasks  *(needs US-1 synthesis + a script + GPU)*
> As the system, I want to train and CV LoRA adapters, picking the best for submission.
- **TASK-4.0 [JULES]** — author the training script + config (QLoRA, rank ≤ 32, multi-GPU aware for `local_40g`).
- **TASK-4.x [GPU]** — operator dispatches training runs on `kaggle_gpu` / `local_40g`; writes `experiments/<id>/cv_score.json`. Multiple variants can train in parallel across backends.

---

## US-5 — Debug root cause & improvement stories  *(reactive, continuous)*
> As the system, when a run underperforms or fails, I want a root-cause task that proposes a concrete fix.
- **TASK-5.x [JULES]** — created by the operator from a failed/weak `experiments/<id>` or from user feedback; each is a scoped "diagnose X → propose/implement fix" story. Naturally serial per issue, but independent issues run ∥.

---

## Dependency / parallelism map
```
TASK-0.P (probe Jules internet) ─┐  (Phase 0, optional)
TASK-1.0 [OP vendor refs] ───────┴──▶ 1.1 ∥ 1.2 ∥ 1.3 [JULES] ──▶ 1.4 [OP synth] ──▶ plan.md
                                                                      │
                          US-3 synthetic data [JULES] ──────────────┐ │
                          US-2 validation (harness+packaging) ──────┤ ├──▶ US-4 training [GPU] ──▶ submit gate
                                                                      │ │           │
                                                                      └─┴──▶ US-5 debug/improve (reactive) ◀┘
```
- **Serial spine:** 1.0 → analysis → 1.4 → training → submit.
- **Parallel within a phase:** the three analysis tasks; multiple synthetic-data tasks; multiple training variants across backends; independent debug stories.
- **Gate:** US-2 validation must pass before US-4 burns real GPU hours; submit gate (beats-best-CV + ≤cap/day) before any Kaggle submission.

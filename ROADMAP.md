# Nemotron Campaign — Roadmap to Final Submission

**Deadline:** 2026-06-15 (15 days from now)
**Goal:** Maximize public LB score, then lock 2 final submissions at our best CV
**Daily submit cap:** 5/day per account × 2 accounts = 10/day combined; reserve 2 finals; spend ≤3 auto/day

---

## TL;DR — Where we are RIGHT NOW

| Track | State | Blocker |
|---|---|---|
| **First GPU run** | v19 notebook pushed, awaiting browser Save&Run All | **USER: toggle Internet ON in Session options** |
| **First submission** | Not yet — no adapter to submit | First GPU run must complete |
| **Best CV** | `None` | First successful train |
| **Submissions today** | 0/5 | n/a |
| **Jules in flight** | 2 (corpus v3, master-roadmap xlsx) | Auto-rerun on completion |
| **Analyses ready** | 6 (3 xlsx, 3 md) | Operator reads them to pick next experiment |
| **Multi-account pool** | sai1881 ✓ + akhildadi ✓ (ACCT2 not yet active) | USER: `Copy & Edit` demo under akhildadi when ready |

---

## Phase plan (target dates)

### Phase 0 — Pipeline validation (TONIGHT, May 31)
Get the loop end-to-end alive: v19 runs, produces adapter + cv_score, I submit.

| # | Item | Owner | Status |
|---|---|---|---|
| 0.1 | Internet ON in Session options | **USER** | ⏳ pending |
| 0.2 | Save & Run All on v19 | **USER** | ⏳ pending |
| 0.3 | Monitor run to terminal | operator | armed |
| 0.4 | Download adapter + cv_score.json | operator | armed (MCP) |
| 0.5 | First `submit_to_competition` call | operator | gated on 0.4 |
| 0.6 | Read leaderboard, log rank | operator | gated on 0.5 |

**Exit criteria:** any non-error LB score recorded; best_cv set; first row in `submits_by_day`.

---

### Phase 1 — Switch to CoT corpus (Days 1-3, Jun 1-3)
This is the **0.65 → 0.85 lever** per technique-backlog #1. Train on synthesized CoT instead of bare train.csv answers.

| # | Item | Owner | Status |
|---|---|---|---|
| 1.1 | Corpus v3 ships (verified-fix + 7 categories) | Jules | 🟢 in flight |
| 1.2 | Corpus attached to notebook as Kaggle dataset OR baked into utility script | **USER** (one-time Copy & Edit) | pending |
| 1.3 | Notebook v20 reads corpus instead of train.csv | operator | gated on 1.1 |
| 1.4 | Train + submit | USER (1 click) + operator | gated on 1.3 |

**Exit criteria:** LB number from CoT-trained adapter; should be ≥0.30+ (vs <0.10 expected from raw train.csv).

---

### Phase 2 — Apply ranked experiments from master_roadmap (Days 3-7, Jun 4-7)
The master roadmap workbook ranks every experiment by `expected_cv_delta / effort`. Run them top-down.

| # | Item | Owner | Status |
|---|---|---|---|
| 2.0 | `master_roadmap.xlsx` synthesizes the 3 source workbooks | Jules | 🟢 in flight |
| 2.1 | Operator reads `RankedExperiments` sheet, picks top 3 | operator | gated on 2.0 |
| 2.2 | Notebook v21–v23: each pushes a single top-ranked change | operator | gated on 2.1 |
| 2.3 | Each run → submit if CV beats best | operator | per-run |

**Likely top experiments** (per analyses already merged): chat-template parity, Select2Reason curation, curriculum learning, log-prob filter, rank-16 ablation, longer training.

**Exit criteria:** ~5 LB submissions, best_cv ≥0.50.

---

### Phase 3 — Synthesis run (Days 7-10, Jun 8-10)
Combine the winning ablation choices into one config.

| # | Item | Owner | Status |
|---|---|---|---|
| 3.1 | Pick top 2-3 winning ablations from Phase 2 CV scores | operator | gated on 2.3 |
| 3.2 | Build E-009 synthesis kernel (full corpus + best hyperparams) | operator | code-change in notebook |
| 3.3 | Train + submit | USER + operator | per-run |

**Exit criteria:** best_cv approaches the winner's reference 0.85.

---

### Phase 4 — Late iteration + multi-account (Days 10-13, Jun 11-13)
Use ACCT2 (akhildadi) to double daily submit capacity for fine-tuning.

| # | Item | Owner | Status |
|---|---|---|---|
| 4.1 | Activate ACCT2: `Copy & Edit` demo under akhildadi | **USER** (1-time) | pending |
| 4.2 | Parallel ablations on both accounts | USER + operator | gated on 4.1 |
| 4.3 | Mine results, fix what's not working | operator | per-iteration |

**Exit criteria:** 2-5 more LB attempts; whichever ablation lifts CV most becomes the final config.

---

### Phase 5 — Finals (Days 13-15, Jun 14-15)
Lock 2 reserved finals at our top CV.

| # | Item | Owner | Status |
|---|---|---|---|
| 5.1 | Pick best 2 distinct configs by CV | operator | gated on 4.3 |
| 5.2 | Submit final-1 from ACCT1 | operator | manual confirm |
| 5.3 | Submit final-2 (diverse config) from ACCT1 or ACCT2 | operator | manual confirm |
| 5.4 | Reserve 1 buffer day | — | — |

---

## Standing things to track (every cycle)

### Per-cycle metrics
- `best_cv` (state.json) — is it climbing?
- `submits_by_day` per account — are we under 3/day auto-cap?
- `gpu_runs` — is anything running?
- `sessions` — Jules workers in flight?
- Open PRs on GitHub — anything stuck unmerged?

### Per-account Kaggle quotas (no API to read directly — track in state.json)
- ACCT1 sai1881: today's submits, weekly GPU hours used (~30h/wk total)
- ACCT2 akhildadi: ditto, NOT activated yet

### Watch-list for stuck items
- Browser Save & Run All — only USER can do this; operator can only push code
- Internet ON toggle — must be live in Session options, not just saved
- Accelerator dropdown — must be RTX Pro 6000 or T4 x2, NEVER P100
- Model + competition input bindings — must be visible in Input panel
- `verified` flag on corpus — operator validates real match before training

---

## Open Jules tasks (in flight or BACKLOG)

| ID | What | State | ETA |
|---|---|---|---|
| TASK-DATA-cot-corpus-v1 | v3 corpus (7 categories, real verified) | 🟢 in flight | ~1h |
| TASK-XLSX-master-roadmap | Synthesis workbook ranking all experiments | 🟢 in flight | ~1h |

After these land: operator reads master_roadmap → picks next 3 experiments → spawns the corresponding code-change Jules tasks (~3 more).

---

## Operator runbook per cycle

1. `python -m orchestrator.tools status` — snapshot
2. Poll all Jules sessions via MCP — R-007 auto-merge any COMPLETED PRs
3. Poll all gpu_runs via `mcp__kaggle__get_notebook_session_status` — if COMPLETE, pull outputs and submit; if ERROR, diagnose + push notebook fix
4. Read any new `analysis/*.{md,xlsx}` deliverables, pick next experiment
5. Push notebook code change via `mcp__kaggle__save_notebook` (preserves fork bindings)
6. Tell user "tap Save & Run All" if a run needs triggering
7. Reporter log to `state/run_log.jsonl`
8. Commit + push

---

## The 3 known platform laws (proven the hard way — see AGENTS.md)

1. **Only a fork of the official demo** (`Copy & Edit ryanholbrook/nvidia-nemotron-submission-demo`) gets the RTX Pro 6000 + model grant. API-created notebooks land on P100.
2. **API can edit code, only browser Save & Run All can actually run** (mounts inputs + provisions GPU).
3. **Don't import `ryanholbrook/nvidia-utility-script`** — its Triton wheel ships a non-executable `ptxas-blackwell` that crashes on RTX Pro 6000 sm_120. Either pip-install deps inline (internet ON) or attach an offline-wheels dataset.

---

## What I'll do automatically (no input needed)

- Monitor GPU runs every cycle, pull outputs on COMPLETE
- Auto-merge Jules PRs via R-007
- Auto-submit when local CV beats best_cv (within daily cap)
- Push notebook code changes via API
- Update ledger + commit + push every cycle
- Schedule wakeups when nothing actionable

## What requires USER input (only these — minimize)

- Toggle Internet ON in Session options (one-time fix to current notebook)
- Tap **Save Version → Save & Run All (Commit)** when a code change needs to actually run
- `Copy & Edit` demo under akhildadi when we want to activate ACCT2 (Phase 4)
- Pick 2 final configs on Day 14 (operator recommends, user confirms)

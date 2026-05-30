# Experimentation plan — Nemotron Reasoning Challenge

Grounded in: the cloned winner repo (`references/winner-*`), 217 scraped discussions, and the merged Jules deliverables on `main` (analysis-discussions-do-avoid.md, analysis-discussions-deltas.md, analysis-winner-training-internals.md, taxonomy.md+classify.py, writeup/SOLUTION.md, eval/{cv,score}.py, kernels/{train,train-rank16}/, data/curation/curriculum.py).

## TL;DR — the strategy in one paragraph
**Replicate the winner's deterministic-CoT + 1-epoch LoRA-SFT recipe**, then run **6 ablations** that each test one specific hypothesis our loop discovered (esp. **cryptarithm_guess — winner skipped it**, **Mamba-mixer LoRA targeting — avoids MoE hang**, **Select2Reason data curation**, **rank-16 vs rank-32**, **curriculum ordering**, **log-prob anti-forgetting filter**). Each experiment is gated: only candidates whose **local CV beats current best** + **submission cap headroom** is positive are sent up. Final submit slots (2 max) reserved for the best ablation + the synthesis run.

## Hard invariants (locked, do not violate)
- Base model **fixed**: `Nemotron-3-Nano-30B-A3B-BF16`. LoRA only, **rank ≤ 32**.
- Answer extraction: `\boxed{...}`. Host vLLM params fixed (temp 0.0, top_p 1.0, max_tokens 7680, max_model_len 8192, max_lora_rank 32, gpu_memory_utilization 0.85, max_num_seqs 64).
- Submissions: **5/day cap, 2 finals total** (locked from `tab-rules.md`). Operator gate = beats-best-CV + ≤3 auto/day.
- One-account-only rule. No cred on Jules VM beyond Kaggle MCP via env-var injection per `JULES_SETUP.md`.
- Mamba-mixer LoRA targeting **required** (`mixer.in_proj`, `mixer.out_proj`); naïve `peft` targeting hangs scanning ~5980 MoE experts (Jules H4, multiple discussion threads).
- Loss objective follows winner: maximize **min log-prob** over the boxed-answer span.

## Phase A — Foundation (status check)
| Deliverable | Status | Source |
|---|---|---|
| Eval CV harness (`eval/cv.py`, `eval/score.py`, tests) | ✅ on main | R8 PR #merged |
| Category taxonomy + rule classifier | ✅ on main | R1a + R1b merged |
| Training kernel (rank-32) + smoke | ✅ on main | R10a + R10b merged |
| Rank-16 ablation kernel | ✅ on main | R24 PR #19 |
| Curriculum-shuffle config | ✅ on main | R23 PR #20 |
| Verified `\boxed{}` CoT generator | ✅ on main | R7 PR #13 |
| Corpus curation | ✅ on main | R9 PR #merged |
| Writeup + public-notebook skeleton | ✅ on main | R12 PR merged |
| Discussion do/avoid + deltas digests | ✅ on main | R11a + R11b merged |
| Winner training-internals (LR + loss + masking) digest | ✅ on main | R13 PR #7 |
| Per-category solvers — bit / cipher / equation | 🟡 in flight | Wave-3 R20/R21/R22 |
| Per-category solvers — gravity / numeral / unit_conv / cryptarithm | 🟡 in flight | Wave-4 R25/R26/R27/R28 |
| Eval per-category breakdown + stratified split | 🟡 in flight | Wave-4 R29 |
| Kaggle access smoke (Jules VM) | 🟡 in flight | K0 — needs env vars set on jules.google |
| Mamba-mixer LoRA target config validated | ❌ not yet | new E-PRECOND (added below) |

## Phase B — Data Engine v1 (E-001)
**Goal:** turn the landed solvers into one canonical `corpus.jsonl` (winner format), stratified train/dev split.
- **Inputs:** all 7 per-category solver outputs + winner-derived CoT generator, mask only the reasoning+answer span (winner's `build_datum` convention from R13).
- **Output:** `competitions/<slug>/data/corpus/v1/corpus.jsonl` + `dev_split.jsonl` (stratified by category to preserve frequency mix).
- **Dispatch:** Jules deep task `TASK-E001-corpus-v1` (~1h) after all Wave-3+4 solvers land.

## Phase C — Baseline Training (E-002)
**Goal:** replicate the winner's recipe end-to-end → first real LB score.
- Backend: `kaggle_gpu` (KGAT bearer; 2×T4 first run; bump to `local_40g` once configured).
- Config (winner-faithful): LoRA rank=32 / alpha=64, 1 epoch, `LinearDecayLRSchedule` 2e-5→1e-5, **Mamba mixer targets** (`mixer.in_proj`, `mixer.out_proj`) + attention `[q,k,v,o_proj]`, AdamW, weight decay 0.01, mixed precision BF16, grad-accum to a sane micro-batch on 2×T4.
- Eval: run the local CV harness; record per-category accuracy.
- **Gate:** only submit if local CV > 0 (first submission allowed to set the floor). One submission used.

## Phase D — Ablations (E-003 … E-008)
Each ablation = a single-variable change vs E-002. Each gated through the submit policy (only submit if it beats current best).
| ID | Tests hypothesis | Single change vs E-002 | Predicted effect |
|---|---|---|---|
| E-003 | H-RANK16 | LoRA rank 32 → 16, alpha 32 | ~equal LB, 2× cheaper |
| E-004 | H-1EPOCH | 1 epoch → 2 epochs | small + or − on LB (refutation test) |
| E-005 | H-CURRICULUM | random order → difficulty-ascending (R23 config) | +0.01–0.03 LB |
| E-006 | H-SELECT2REASON | full corpus → top-utility filtered (~30% size) | ≥ baseline at half cost |
| E-007 | **H-CRYPTARITHM-GUESS** | corpus + cryptarithm_guess solver added (winner skipped) | **direct +0.01–0.03 LB** (164 rows ungrabbed) |
| E-008 | H-LOGPROB-FILTER | drop examples where base-model min-logprob > −0.05 | + on bit_manipulation / cipher harder rules |

Ablation execution rule: run E-003..E-008 sequentially, **at most one Kaggle submission used per ablation**, only if the variant beats local CV. Save submission budget for the final 2-of-2 finals slot.

## Phase E — Synthesis (E-009)
Combine the winning-direction ablation choices into one final run. Train; submit if CV beats best.

## Phase F — Submit & finalize
- Public LB is exposed; we use it as a noisy signal but **trust local CV**.
- Two "final submission" slots are reserved at competition close — pick the best two by **local CV** with disagreement diversity (don't pick two near-identical runs).
- Update `writeup/SOLUTION.md` with final config + reproducibility (prize-eligibility requirement).

## Compute & budget
- **Jules** worker pool: 2 accounts × 15 concurrent / 100 day = 30 / 200 effective. Used for solvers, corpus curation, eval tooling, analysis. **Not training** (no GPU).
- **GPU executor:** `kaggle_gpu` via KGAT (push kernel → poll → pull adapter + cv_score). User's local 40 GB 2-GPU box can be wired as `local_40g` when ready.
- **Submission budget:** 5/day Kaggle cap; operator gate = ≤3 auto/day, only on beats-best-CV. 2 final slots reserved.

## Dependency graph
```
Wave-3/4 solvers (R20..R22, R25..R28) ──┐
                                        ├──► E-001 corpus-v1 ──► E-002 baseline ──┬──► E-003 rank16
                                        │                                          ├──► E-004 2-epoch
Mamba-target validation (E-PRECOND) ────┘                                          ├──► E-005 curriculum
                                                                                   ├──► E-006 select2reason
                                                                                   ├──► E-007 cryptarithm_guess★
                                                                                   └──► E-008 logprob-filter
                                                                                                │
                                                                                                ▼
                                                                                          E-009 synthesis
                                                                                                │
                                                                                                ▼
                                                                                          Finalize (2 picks)
```
★ E-007 is the highest-confidence direct-LB experiment (winner literally skipped this category).

## Open risks
1. Mamba-mixer LoRA targeting must work on 2×T4 in 4-bit. If it doesn't, E-002 cannot run on free GPU — escalate to paid cloud or wait for `local_40g`.
2. Submission cap is 5/day; aggressive ablation pace can use it up. Strictly gate.
3. Public-LB is noisy; if we over-fit to LB we burn final-submission picks.
4. Hypothesis effect-size estimates are pre-registration guesses; the true distribution lives behind `\boxed{}` host scoring.

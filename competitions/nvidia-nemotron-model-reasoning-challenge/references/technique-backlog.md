# Technique backlog — ranked experiments (from community mining)

Reproducible-on-free-GPU first. Promote items into `tasks/todo/` as the operator schedules them.

## 1. Port the winner's CPU-only data engine: per-category deterministic solvers + verified-CoT generation + the 5 rule-based augmenters (reasoning.py/augmentation.py/corpus.py from tonghuikang/nemotron)
- **effort:** L  |  **expected_gain:** Very high (+0.15–0.20 LB vs naive SFT). Largest single lever in the corpus.
- **rationale:** This is THE proven win lever — LB 0.65 (no synthetic) vs 0.85 (this corpus). Pure Python, no GPU, no LLM/API calls, runs anywhere including a laptop; reproduces the single most impactful component. Ideal Jules (no-GPU) task. Output is a verified ~40 MB JSONL corpus that downstream SFT consumes.

## 2. Build a local vLLM CV/eval harness mirroring exact host params (temp 0.0, top_p 1.0, max_tokens 7680, max_model_len 8192, max_lora_rank 32) with \boxed{} extraction + exact/±1e-2 scoring, plus an adapter-validation pre-submit gate
- **effort:** M  |  **expected_gain:** High (enables all iteration; prevents wasted submits).
- **rationale:** Lets us measure CV before spending GPU and before burning the daily submit cap; mirrors winner's dashboards. Inference-only, runs on free 2×T4. Required to make 'submit only beats-best-CV' policy real. De-risks 'adapter doesn't load / wrong format / scores 0'.

## 3. 2×T4 QLoRA SFT smoke test: 4-bit base, explicit Mamba-mixer LoRA targets (mixer.in_proj/out_proj) via peft.get_peft_model(), max_memory sharding (13/13 GiB + CPU/disk offload), transformers>=4.45,<5, mamba-ssm+causal-conv1d, ~10 samples / 1 step
- **effort:** M  |  **expected_gain:** Medium (unblocks all on-Kaggle training; high failure-avoidance value).
- **rationale:** Validates the free-Kaggle training path end-to-end and pre-empts the two known killers: the MoE-expert-scan hang (avoid FastLanguageModel/regex targeting) and the LoRA-merge layer-name mismatch. Cheap, fast, surfaces env/arch issues before a full run.

## 4. First real LoRA SFT on the ported corpus using winner hyperparams adapted for T4: rank 32 (MLP+attn+unembed if it fits, else attention-only), LR 2e-4 step-linear-decay, 1 epoch, micro-batch 16 w/ grad-accum to batch 64, max_seq 2048 (cap 8192 if memory allows), label-masked loss
- **effort:** L  |  **expected_gain:** High (first real LB number; target well above the 0.65 no-synthetic floor).
- **rationale:** Direct reproduction of the 0.85 recipe on reproducible compute. Produces our first real leaderboard score and the baseline every later experiment is measured against (D-2 baseline-first).

## 5. CoT data-selection / curation pass (konbu17 Select2Reason-style): keep only boxed-correct traces, drop repetitive/low-quality, prioritize by difficulty + trace length; mix reasoning-on + reasoning-off samples
- **effort:** S  |  **expected_gain:** Medium (+small LB, plus faster/cheaper training).
- **rationale:** Quality-over-quantity is repeatedly confirmed (CoT-100 viable). Cheap CPU filter on top of the data engine; reduces token volume (cheaper SFT) while often improving accuracy.

## 6. Tune max_seq_length upward (2048→4096→8192) and LoRA target breadth (attention-only → +MLP → +unembed) as memory budget allows on the 40 GB box, A/B against CV
- **effort:** M  |  **expected_gain:** Medium (recovers T4-induced gap toward 0.85).
- **rationale:** Winner used full MLP+attn+unembed at seq 8192; T4 forces 2048/attention-only. Closing this gap on the 40 GB executor likely recovers part of the score lost to T4 constraints. Pure config sweep once harness exists.

## 7. Stratified batching across the 9 categories (even category spread per batch), per winner config
- **effort:** S  |  **expected_gain:** Low–medium (stability; small accuracy gain).
- **rationale:** Cheap config change matching the verbatim winning recipe; stabilizes training across heterogeneous puzzle types and is a documented part of the 0.85 run.

## 8. Cover the categories the winner left weak: add a dedicated solver for cryptarithm_guess (skipped in winner reasoning) and audit any rule_unknown categories
- **effort:** M  |  **expected_gain:** Medium (targets the specific gap to >0.85).
- **rationale:** Winner explicitly skipped cryptarithm_guess and tagged some problems rule_unknown — these are the residual headroom above 0.85. CPU-only Jules work; directly targets the unsolved slice.

## 9. (Deferred) GRPO/RL stage on top of merged SFT adapter, on the 40 GB box or paid cloud (NOT free 2×T4)
- **effort:** L  |  **expected_gain:** Uncertain (no public evidence it beat SFT here; high cost).
- **rationale:** Winner's run was SFT-only; RL losses exist in the repo but were unused. Needs 2×A100 80 GB-class compute and online vLLM serving — out of free-tier reach and unproven for this comp. Only attempt after SFT plateaus and bigger compute is configured.


# Community Knowledge Digest — Nemotron Model Reasoning Challenge

Synthesized from 22 read items (Progress-Prize winner repo + blog, official starter, and ~12 community notebooks/repos). Sourcing caveat: nearly all Kaggle pages are JS/login-gated — concrete configs were recovered from the open-source winner repo `github.com/tonghuikang/nemotron` and corroborating mirrors, not always from the gated notebook cells.

## TL;DR — the winning lever
The benchmark is **procedurally generated puzzles in ~9 categories**, not open-ended math. The Progress-Prize winner (huikang / tonghuikang, **LB 0.85**) did NOT use RL or LLM distillation. He **reverse-engineered each category's deterministic rule, wrote a Python solver per category, emitted verified chain-of-thought traces, and did a single-epoch LoRA SFT** on those traces. Accuracy comes from the **data engine**, not compute. This is the dominant, repeatedly-confirmed pattern across the corpus.

Public LB ladder observed: **0.85** (winner, hand-engineered corpus) > **0.83** (fork, "sft final") > **0.82** (fork, generic CSV CoT) > **0.65** (no-frills SFT, no synthetic data). The gap between 0.65 and 0.85 is almost entirely **data quality**, not hyperparameters.

---

## 1. Data / Synthetic generation (highest leverage)
- **9 categories** (winner): `bit_manipulation, cipher, cryptarithm_deduce, cryptarithm_guess, equation_numeric_deduce, equation_numeric_guess, gravity, numeral, unit_conversion`. [tonghuikang/nemotron]
- **Per-category deterministic solvers** (`reasoning.py`, GENERATORS dict): solve the problem programmatically, then emit a clean CoT trace that mirrors the solver. Tag each problem `rule_found` / `hypothesis_formed` / `rule_unknown`; **only verified `rule_found` traces enter the corpus**. `cryptarithm_guess` was skipped from reasoning. [tonghuikang/nemotron, blog.huikang.dev]
- **Verification gate** `compare_answer()`: extract `\boxed{...}`; binary strings strict; numbers `rel_tol=1e-2 / abs_tol=1e-5`; else case-insensitive string. Mirrors host scoring. [blog.huikang.dev, tonghuikang/nemotron]
- **5 rule-based augmenters** (`augmentation.py`, all deterministic, no LLM/API calls): `Spelling, Concatenation, Splitting, Matching, Lstrip` — multiply each solved problem into many prompt/completion pairs. [tonghuikang/nemotron]
- **Corpus**: `corpus.py` assembles ~40 MB JSONL; tracks masked (prompt) vs unmasked (completion) tokens. Completion format: `(reasoning)</think>\boxed{(answer)}<|im_end|>`. [tonghuikang/nemotron]
- **Pipeline order**: `reasoning.py → augmentation.py → corpus.py → train_sft.py → upload_adapter.py`. [tonghuikang/nemotron]
- **Community data-selection variant** (konbu17): curate CoT down to higher-utility traces — keep only traces whose boxed answer matches ground truth, drop repetitive/low-quality traces, prioritize by difficulty + trace length (Select2Reason-style). Mix "reasoning on" (full CoT) + "reasoning off" (direct answer) samples. [kaggle/konbu17]
- **CoT-100**: adapters trained on ~100 curated CoT examples are viable — structure/format matters more than volume. [kaggle/khursani8, kaggle/kienngx-cot-labels]
- Generic API-distilled CoT (Anthropic/OpenAI) is the weaker community path (SebAustin, samuelabatnehendalie `--cot-backend`; `--skip-cot` gives a synthetic-only baseline). Forks that swapped the hand-engineered corpus for generic CSV CoT scored **lower** (0.82 vs 0.85). [kaggle/tahaalam2009, github/SebAustin]

## 2. Training recipe / LoRA (verbatim from winner `train_sft.py`)
- Base: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` (30B MoE / ~3B active, hybrid Mamba-Transformer). Fixed by rules.
- **LoRA rank 32** (competition cap); train **MLP + attention + unembedding** (`train_mlp/train_attn/train_unembed = True`).
- **LR 2e-4** with `StepLinearDecayLRSchedule` (lr·(1−step/total_steps)).
- **batch 64, micro-batch 16, 1 epoch, max_length 8192, BF16, no quantization** (winner ran on cloud).
- Adam: `beta1=0.9, beta2=0.95, eps=1e-8, weight_decay=0.0, grad_clip_norm=1e9`.
- **Stratified batching**: categories spread evenly across batches.
- **Loss = plain cross_entropy.** Repo *implements* RL/weighted losses (importance_sampling, PPO clip 0.2, CISPO clip 0.8/1.2, DRO beta 0.05, branch/cutoff-weighted CE) with KL/clip-fraction diagnostics — **but the winning run is SFT-only.** [tonghuikang/nemotron, train_sft.py]
- **Token masking**: mask system+user prefix to `-100`, compute loss only on completion/answer span. [kaggle/kienngx]
- Community LoRA defaults differ for T4: `LORA_R=16`, `lora_alpha=16`, `max_seq_length=2048`. [SebAustin, samuelabatnehendalie, kienngx]
- **Architecture gotcha (critical)**: attach LoRA via `peft.get_peft_model()` with an **explicit module list** targeting the ~46 Mamba mixer layers (`mixer.in_proj` / `mixer.out_proj`). `FastLanguageModel.get_peft_model()` and regex targeting **hang** scanning ~5980 MoE experts. The LoRA→base **merge** step fails on this hybrid MoE arch with layer-name mismatches; one fix is restricting target_modules to attention only `[q,k,v,o_proj]`. [kaggle/kienngx, unsloth#3810]
- Community SFT-loss outcome: ~45 → ~17 → **0.99** after label masking. [kaggle/kienngx]

## 3. Prompting / answer format
- Final answer MUST be in `\boxed{...}`; last non-empty match is parsed. [all sources]
- CoT wrapped in `<think></think>`; `enable_thinking=True` in `apply_chat_template`. [kaggle/kienngx]
- Reasoning-trace-then-boxed-answer chat template. [winner, community]

## 4. Eval / scoring harness (host-side, fixed)
- vLLM, **temperature 0.0, top_p 1.0, max_tokens 7680, max_model_len 8192, gpu_memory_utilization 0.85, max_lora_rank 32**. [yunior123, ryanholbrook starter, multiple]
- Metric: exact string match **OR ±1e-2 numeric tolerance** on `\boxed{}` content. [all]
- Submission = `submission.zip` (adapter + `adapter_config.json`); scored offline, not in-notebook.
- **Build a local vLLM eval harness that mirrors these exact params** before spending GPU. The winner shipped per-problem dashboards (Base/Synthetic/Corpus/Training/Metrics) at nemotron.huikang.dev; an **adapter-validation notebook** is the cheap pre-submission gate (confirm adapter loads under vLLM, valid rank/format, parseable answers) — runs on free 2×T4. [kaggle/huikang adapter-validation]

## 5. Reproducibility on free Kaggle 2×T4 (our `kaggle_gpu` executor)
- **Winner's exact stack: NOT reproducible.** BF16 30B on Tinker/Modal cloud; ~60 GB weights exceed 32 GB total T4 VRAM even for inference. [tonghuikang/nemotron, blog]
- **CPU-side data engine: fully reproducible anywhere** (pure Python, no GPU, no LLM calls). This is the transferable, high-value half.
- **SFT on 2×T4 IS feasible** with 4-bit QLoRA + multi-GPU sharding: `max_memory` caps (~7 GiB GPU0 / ~9 GiB GPU1, or 13/13), CPU cap (`NEMOTRON_MAX_MEMORY_CPU`), disk `offload_folder` for MoE spillage; `max_seq_length≈2048`; pin `transformers>=4.45,<5` (v5 OOMs at 16 GB); install `mamba-ssm` + `causal-conv1d`. A single 15 GB T4 is NOT enough. Expect long runtimes near the 9–12 h session limit. [SebAustin, kienngx, samuelabatnehendalie, konbu17]
- **Inference / adapter-validation: comfortably on 2×T4** (4-bit, short eval batches). [khursani8, huikang adapter-validation]
- GRPO/RL stage needs 2×A100 80 GB — out of free-tier reach. [kienngx]
- A clean no-synthetic SFT on RTX Pro 6000 (~96 GB) ran in ~46 min and scored **0.65** — useful lower-bound reference. [kaggle/emanuellcs]

## Source map (per-item files)
- Winner discussion (gated): references/discussions/689915-winner-writeup.md → https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689915
- Winner blog: https://blog.huikang.dev/2026/05/02/nemotron-progress-prize.html
- **Winner repo (primary source of truth)**: https://github.com/tonghuikang/nemotron
- Winner notebook LB 0.85 (gated): https://www.kaggle.com/code/huikang/end-to-end-finetuning-for-lb-0-85
- Adapter validation: https://www.kaggle.com/code/huikang/adapter-validation-notebook
- Official starter: https://www.kaggle.com/code/ryanholbrook/nvidia-nemotron-submission-demo
- 2×T4 SFT scaffolds: github.com/SebAustin/NVIDIA-Nemotron-Model-Reasoning-Challenge ; kaggle kienngx (copy-run / cot-labels) ; samuelabatnehendalie/notebook-lora-training
- CoT data-selection: kaggle/konbu17/nemotron-sft-lora-with-cot-selected-data
- CoT-100 inference: kaggle/khursani8/nvidia-nemotron-inference-with-cot-100-adapter
- LB 0.82 / 0.83 forks: kaggle/tahaalam2009
- No-synthetic 0.65 baseline: kaggle/emanuellcs/nvidia-nemotron-sft
- Unsloth merge gotcha: github.com/unslothai/unsloth/discussions/3810
- Empty scaffold (low value): github.com/yunior123/nvidia-nemotron-reasoning

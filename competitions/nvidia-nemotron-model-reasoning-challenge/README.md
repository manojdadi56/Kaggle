# NVIDIA Nemotron Model Reasoning Challenge

Self-contained workspace for this competition. The orchestrator's `active_competition` points here.

## Facts (see research-jules-orchestration for sources)
- **Task:** train a **LoRA adapter (rank ≤ 32)** on the fixed base **Nemotron-3-Nano-30B-A3B-BF16** to maximize accuracy on logical-reasoning puzzles.
- **Submission:** `submission.zip` = adapter weights + `adapter_config.json`. Scored **host-side via vLLM** on a hidden test set. NOT a predictions CSV.
- **Metric:** accuracy; final answer must be in `\boxed{...}` (exact / ±1e-2 numeric match). Fixed host params (temp 0, max_lora_rank 32, max_model_len 8192).
- **Compute:** Jules has no GPU → training runs on the GPU executor (Kaggle free 2×T4 now; user's 40 GB 2-GPU box once configured; paid cloud as upgrade).
- **Deadline:** final 2026-06-15; entry/merge 2026-06-08.
- **Baseline to fork:** `tonghuikang/nemotron` (open-sourced progress-prize winner) + official starter (ryanholbrook).

## Hard invariants
LoRA rank ≤ 32 · base model fixed · answers in `\boxed{}` · submit only beats-best-CV + within live daily cap.

## Folders
`plan.md` · `tasks/{todo,in-progress,done}` · `user-stories/` · `decisions/` · `experiments/` · `kernels/` · `submissions/{pending,submitted}` · `references/` · `data/`

## OPEN (confirm before live submits)
- Exact daily submission cap + final-selection count (login-gated) — read live, never hard-code.
- That scripted submission is permitted by the rules.

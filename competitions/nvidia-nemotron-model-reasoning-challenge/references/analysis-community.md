# Community Pipeline Analysis: NVIDIA Nemotron Model Reasoning Challenge

This document analyzes two starter/community repositories for the NVIDIA Nemotron Reasoning Challenge, extracting common pipelines, divergences, and canonical packaging requirements.

## Analyzed Repositories
1. **yunior123** (`https://github.com/yunior123/nvidia-nemotron-reasoning`)
2. **SebAustin** (`https://github.com/SebAustin/NVIDIA-Nemotron-Model-Reasoning-Challenge`)

## Common Pipeline: The "Golden Path"

Both repositories follow a highly constrained common path, dictated by the competition invariants:

1. **Base Model:** Both standardize on `nvidia/Nemotron-3-Nano-30B-A3B-BF16`. This is a hard requirement for the competition.
2. **Training (QLoRA):** Both pipelines fine-tune the model using LoRA adapters, focusing heavily on parameter-efficient techniques (PEFT) because full fine-tuning of 30B parameters is computationally prohibitive.
   - They load the base model in 4-bit quantization (QLoRA) for memory efficiency.
   - *Citations:* `train.py` in yunior123's repo (via comments), `scripts/03_train_lora.py` in SebAustin's repo.
3. **Packaging (`submission.zip`):** Both package the fine-tuned LoRA adapters (and crucially, *only* the adapters) into a `submission.zip` archive.
   - *Citations:* `src/submit.py` in yunior123's repo, `scripts/05_package_submission.py` in SebAustin's repo.

## Canonical Validation & Packaging Steps

To pass Kaggle's automated verification, the `submission.zip` must adhere to strict structural constraints:

1. **LoRA Rank (r):** The `adapter_config.json` file must explicitly specify a LoRA rank (`r`) of 32 or lower. Adapters with `r > 32` will fail evaluation.
   - Both `src/submit.py` (yunior123) and `scripts/05_package_submission.py` (SebAustin) explicitly enforce this check or document it. SebAustin's script parses the JSON and throws a `SystemExit` if `r > 32`.
2. **File Structure:** The zip file must contain the contents of the adapter directory at the root of the archive (e.g., `adapter_config.json` and the `.safetensors` or `.bin` weights).
3. **Expected Format:** The model must be fine-tuned to produce the final answer inside `\boxed{}` tags for accurate extraction by the Kaggle host scoring metric.
   - *Citations:* `src/evaluate.py` and `src/data.py` in yunior123's repo extract from `\boxed{}` and format prompts to require it.

## Divergences & Tooling Choices

While the core pipeline is identical, the repositories diverge significantly in structure, tooling, and execution environment:

1. **Framework & Modularity:**
   - **SebAustin:** Offers a highly structured, 5-phase pipeline (`01_eda.py` through `05_package_submission.py`) orchestrated by a `run_all.py` script. It features robust error handling, hardware fallback options (Unsloth vs. HF PEFT), and local vLLM evaluation (`04_evaluate.py`). It deeply considers memory limits on smaller GPUs (e.g., T4), offloading behavior, and handles Mamba/MoE requirements gracefully.
   - **yunior123:** A much lighter, script-based layout (`src/` and `scripts/`). The training script is currently a placeholder indicating that training should occur on Kaggle notebooks using powerful hardware (RTX PRO 6000), rather than providing local execution code. It relies on standard `zipfile` modules and a bash script (`scripts/submit.sh`) hitting the Kaggle API for submission.

2. **Training Libraries:**
   - **SebAustin:** Uses `trl` (`SFTTrainer`) and attempts to load models via `unsloth` first for speed, falling back to standard `peft` if Unsloth is unavailable.
   - **yunior123:** Recommends Unsloth, Axolotl, or TRL, but defers the actual implementation to external notebooks.

3. **Evaluation Metrics:**
   - Both align on extracting the `\boxed{}` answer.
   - **yunior123:** Implements local evaluation logic (`src/evaluate.py`) that falls back to numeric tolerance (`1e-2`) if exact string matching fails.

## Conclusion

The core logic to implement for an autonomous worker is clear: Load the specific Nemotron-3 base model, train a LoRA adapter with `r <= 32`, and zip the `adapter_config.json` and weights together without base model files. The automated packaging tool *must* parse `adapter_config.json` prior to zipping to prevent invalid ranks from wasting a submission slot.
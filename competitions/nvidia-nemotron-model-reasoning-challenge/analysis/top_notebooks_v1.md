# Top 5 Public NVIDIA Nemotron Notebooks Analysis

This document provides a side-by-side analysis of the top 5 most upvoted public notebooks for the NVIDIA Nemotron Model Reasoning Challenge, mapping out their hyper-parameters, data processing steps, and specific competition tricks.

## Notebook Comparison Table

| Notebook | Data Prep & Corpus | Model Load | LoRA Config | Training Loop | Inference / Tricks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ryanholbrook/nvidia-nemotron-submission-demo`** | N/A (Demo) | Loads `AutoModelForCausalLM` bf16 `device_map="auto"`. | Rank 32. | N/A | Submission packaging script using `zip -m submission.zip *`. |
| **`asalhi/tinker-adapter-to-ready-to-submit-adapter`** | N/A (Adapter Conversion) | `weights.build_lora_adapter` for 30B model. | **SVD Compression:** Converts large adapter pairs to forced fused Rank 32. | N/A | `tinker_cookbook` patch `_compress_lora_pair_to_rank` using SVD Frobenius norm approximation. |
| **`dennisfong/nvidia-nemotron-sfttrainer-training`** | `pl.read_csv`, subsamples 600, `Dataset.map` to User/Assistant template. Removes original columns. | `AutoModelForCausalLM` bf16 `device_map="auto"`, `is_fast_path_available=False` patch. | `r=32`, `alpha=16`, `target_modules="all-linear"`, `dropout=0.05` | `SFTTrainer`, `max_seq_len=1024`, `epochs=1`, `batch=1`, `grad_accum=4`, `lr=2e-4`. | **Triton patch:** bypasses Triton rmsnorm `_pure_rmsnorm_fn` and sets `TRITON_PTXAS_BLACKWELL_PATH` to local binary. |
| **`kienngx/nvidia-nemotron-training-cot-labels`** | `pl.read_csv` from `kienngx/nemotron-30b-competition-trainingdata-cot-labels`. Injects `generated_cot` into text prefixing `\boxed{answer}`. | `device_map={"": 0}`, `bfloat16`, `gradient_checkpointing_enable()`. | `r=32`, `alpha=32`, `target_modules="all-linear"`, `dropout=0.05` | `SFTTrainer`, **`max_seq_len=2048`**, `epochs=2`, `batch=1`, `grad_accum=4`, `lr=5e-5`. | Triton rmsnorm patch applied. `datasets.map` to ChatTemplate dropping id/prompt/answer. |
| **`kienngx/nvidia-nemotron-trained-models-submission`** | Lists runs ranging from 600 to 9500 samples. Focus on CoT datasets. | `vLLM` used in evaluation / offline processing. | Tested memory-efficient targets `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` | Listed hyperparameters show experiments with `lr=1e-5` to `1e-4`, `epochs=1` to `2`, `batch=1` to `2`, `grad_accum` up to 16. | Shows success applying `tinker-adapter` for merging and submission of massive runs. |

## Top 5 Missing Techniques in `notebook_fork_working.ipynb`

Comparing the top notebooks above to our baseline implementation in `notebook_fork_working.ipynb`, the following 5 high-impact techniques are notably missing:

1. **Chain-of-Thought (CoT) Prompt Injection**
   - **Source:** `kienngx/nvidia-nemotron-training-cot-labels` (Line 1051)
   - **Description:** Instead of predicting the final `\boxed{answer}` directly, the training data is augmented with reasoning trajectories. The prompt maps to an assistant response formatted as `{generated_cot}\n\n\boxed{{{answer}}}`. The baseline merely tokenizes prompt and completion.

2. **Rank SVD Compression via `tinker_cookbook`**
   - **Source:** `asalhi/tinker-adapter-to-ready-to-submit-adapter` (Line 2930)
   - **Description:** Allows training adapters with `r > 32` (or dense fine-tuning) which are later compressed back to `r=32` via Singular Value Decomposition (SVD) best-fit approximation, legally bypassing competition upload constraints on LoRA rank.

3. **`SFTTrainer` with HuggingFace `datasets` API**
   - **Source:** `dennisfong/nvidia-nemotron-sfttrainer-training` (Line 2111)
   - **Description:** The baseline manually iterates over batches using a raw PyTorch training loop and custom `datum` tokenization. Migrating to `SFTTrainer` and `Dataset.map` provides native gradient checkpointing, built-in Cosine learning rate scheduling, and automated packing (if desired).

4. **Triton RMSNorm / PTXAS Environment Fixes**
   - **Source:** `dennisfong/nvidia-nemotron-sfttrainer-training` (Line 1239) & `kienngx/nvidia-nemotron-training-cot-labels` (Line 1485)
   - **Description:** When training on Kaggle kernels, the default `ptxas-blackwell` permissions and Triton kernels fail. Overriding `rmsnorm_fn` to a pure PyTorch float implementation (`_pure_rmsnorm_fn`) and pointing `TRITON_PTXAS_BLACKWELL_PATH` to a local `chmod`ed binary resolves internal gradient checkpointing CUDA crashes.

5. **`target_modules="all-linear"` (or Expanded Projection Targets)**
   - **Source:** `dennisfong/nvidia-nemotron-sfttrainer-training` (Line 770)
   - **Description:** The baseline limits LoRA target modules to `.*\.(in_proj|out_proj|up_proj|down_proj)$`. Top notebooks specify `"all-linear"` or explicitly include attention components (`q_proj`, `k_proj`, `v_proj`, `gate_proj`), which allows more comprehensive reasoning adaptation.

# Training Kernel for Nemotron Model Reasoning Challenge (Synthesis E-009)

This directory contains the Kaggle kernel script (`train.py`) and its metadata (`kernel-metadata.json`) used to fine-tune the `Nemotron-3-Nano-30B-A3B-BF16` base model.

The training script generates a LoRA adapter (rank <= 32) on a Kaggle GPU instance.

This kernel is the **Synthesis (E-009)** kernel, designed to combine winning ablation choices whose CV beat E-002. Since no ablation choices (E-003 through E-008) have recorded CV scores beating E-002 in the orchestrator state, this synthesis kernel defaults to the E-002 baseline configuration.

## Combined Choices
- E-002 Baseline configuration (no ablations beat E-002).

## Workflow (kaggle_gpu backend)

To execute this kernel on Kaggle and fetch its output, follow the push -> poll -> pull workflow using the provided `tools/kaggle_lite.py` script.

### 1. Push the Kernel
Push the code and metadata to Kaggle. This creates/updates the Kaggle kernel and starts execution.

```bash
python tools/kaggle_lite.py kernel-push -p competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-synthesis-e009/
```

### 2. Poll for Completion
Check the status of the kernel run. Replace `[owner]/[slug]` with the `id` defined in `kernel-metadata.json` (e.g., `username/nemotron-model-reasoning-train-synthesis`). Wait until the status changes to `complete`.

```bash
python tools/kaggle_lite.py kernel-status [owner]/[slug]
```

### 3. Pull Outputs
Once completed, download the resulting adapter and `cv_score.json` from the finished run into your local experiments folder.

```bash
python tools/kaggle_lite.py kernel-output [owner]/[slug] -d competitions/nvidia-nemotron-model-reasoning-challenge/experiments/[slug]/
```

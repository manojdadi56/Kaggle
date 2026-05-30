# Training Kernel for Nemotron Model Reasoning Challenge

This directory contains the Kaggle kernel script (`train.py`) and its metadata (`kernel-metadata.json`) used to fine-tune the `Nemotron-3-Nano-30B-A3B-BF16` base model.

The training script generates a LoRA adapter (rank <= 32) on a Kaggle GPU instance.

## Workflow (kaggle_gpu backend)

To execute this kernel on Kaggle and fetch its output, follow the push -> poll -> pull workflow using the provided `tools/kaggle_lite.py` script.

### 1. Push the Kernel
Push the code and metadata to Kaggle. This creates/updates the Kaggle kernel and starts execution.

```bash
python tools/kaggle_lite.py kernel-push -p competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train/
```

### 2. Poll for Completion
Check the status of the kernel run. Replace `[owner]/[slug]` with the `id` defined in `kernel-metadata.json` (e.g., `username/nemotron-model-reasoning-train`). Wait until the status changes to `complete`.

```bash
python tools/kaggle_lite.py kernel-status [owner]/[slug]
```

### 3. Pull Outputs
Once completed, download the resulting adapter and `cv_score.json` from the finished run into your local experiments folder.

```bash
python tools/kaggle_lite.py kernel-output [owner]/[slug] -d competitions/nvidia-nemotron-model-reasoning-challenge/experiments/[slug]/
```

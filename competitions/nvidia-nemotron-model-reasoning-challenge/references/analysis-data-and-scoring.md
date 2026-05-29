# Data Schema and Scoring Harness Analysis
## NVIDIA Nemotron Model Reasoning Challenge

This document outlines the exact data schema and host scoring parameters for the Nemotron Reasoning Challenge, derived from our findings (F-021..F-023) and architecture specifications.

## 1. Data Schema & Extraction Format

Based on finding F-023:
- **Data Columns**: The competition data relies on a `train.csv` and a hidden `test.csv`. The columns are `id` and `prompt`. In the hidden test set, these columns are swapped out for the private data.
- **Answer Extraction**: The final answer MUST be formatted and emitted inside `\boxed{...}` tags. The host evaluation extracts the value directly from this box.

## 2. Host Scoring Parameters (vLLM)

The competition does NOT use a notebook inference submission for final scoring. Instead, you submit a LoRA adapter (`submission.zip` with `adapter_config.json`, max rank ≤ 32) which the host loads into the fixed `Nemotron-3-Nano-30B-A3B-BF16` base model.

The host runs inference via vLLM with the following **fixed configuration**:
- `temperature`: 0.0
- `top_p`: 1.0
- `max_tokens`: 7680
- `max_model_len`: 8192
- `max_lora_rank`: 32
- `gpu_memory_utilization`: 0.85
- `max_num_seqs`: 64

## 3. Local CV Evaluation Harness Spec

To accurately mirror the host scoring offline without burning submit quota, our local Cross-Validation (CV) harness must be implemented exactly as follows:

1.  **Inference Engine**: Use `vLLM` locally (if GPU supports it) or another compatible engine, but you MUST match the fixed generation parameters above (`temperature=0.0`, `max_tokens=7680`).
2.  **Extraction Logic**:
    -   Parse the model output string to locate the last instance of `\boxed{`.
    -   Extract the inner text until the matching closing brace `}`.
3.  **Matching Logic**:
    -   **Exact String Match**: Compare the extracted string directly to the ground truth.
    -   **Numeric Match**: If the ground truth and extracted prediction are numbers, compare them with a tolerance of ±1e-2 (`abs(predicted - actual) <= 1e-2`).
4.  **Rank Validation (Pre-flight check)**:
    -   The harness MUST parse `adapter_config.json` in the generated output to assert `r <= 32`. If rank is >32, the harness should immediately fail the CV run before inference, as this would be instantly rejected by the Kaggle host.

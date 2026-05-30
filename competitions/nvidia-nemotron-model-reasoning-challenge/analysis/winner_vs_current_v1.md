# Gap Analysis: Winner Solution vs. Our Current Baseline

This document compares the progress-prize-winning solution from Tong Hui Kang with our current baseline implementation (`kernels/train-baseline-e002/train.py` and `writeup/public_notebook.ipynb`), detailing the gaps, required code changes, and recommending next experiments.

## 1. Side-by-Side Comparison

| Feature/Decision | Winner (`tonghuikang/nemotron`) | Our Current Baseline (`train.py` / `public_notebook.ipynb`) |
| :--- | :--- | :--- |
| **Data Generation** | Programmatic, synthetic deterministic reasoning chains via python scripts (`reasoners/`). | Raw `train.csv` / `test.csv` without programmatic CoT mapping. |
| **Data Augmentation** | Extensive text augmentation (`augmenters/` for brackets, spelling, concatenation). | No data augmentation applied. |
| **LoRA Target Modules** | `train_mlp=True`, `train_attn=True`, `train_unembed=True` | Standard projection layers (`q_proj/v_proj` or `in/out/up/down`). No unembed. |
| **LoRA Rank Limit** | Strictly exactly `32`. | Default `32` via argparse, but arbitrary. |
| **Batching Strategy** | Stratified sampling by category (`_stratified_batches` function). | Naive sequential iteration over dataset list. |
| **Loss Function** | Custom configs e.g. `CrossEntropyWithWeightingLossConfig` with branch weighting. | Standard cross-entropy loss over unmasked tokens. |
| **LR Schedule** | Precise `LinearDecayLRSchedule` / `StepLinearDecayLRSchedule`. | Rudimentary `LinearDecayLRSchedule`. |
| **Masking/Formatting** | Uses explicit `<think>` and `</think>` tags; `mask=1` only on completion/CoT. | Implicit masking (`mask=1` on answer tokens), no explicit reasoning tags. |
| **Sequence Length** | Example truncation strictly caps at `TOKEN_LIMIT` of 8192. | `max_length` hardcoded to 8192 during datum build, but no dataset-wide strict filter. |
| **Evaluation/Metrics** | Global metrics tracking like KL-divergence per token and importance sampling ratios. | Simple exact match / numeric match accuracy tracking. |
| **Optimizer** | AdamW with custom `AdamConfig` handled internally by `tinker`. | Standard PyTorch AdamW with `weight_decay=0.01`. |
| **Inference Loop** | Generates completions expecting exact formatting immediately after prompt's `<think>\n`. | Generates via vLLM natively with `temperature=0.0`, manually parses `\boxed{}`. |
| **Submission Format** | Standard adapter submission via `upload_adapter.py`. | Standard adapter submission manually saved to `adapter/`. |

## 2. Top 10 Ranked GAPs and Code Changes

Below are the top 10 ranked gaps between the winner's solution and ours, prioritized by estimated impact on CV, along with the required code changes for our `train.py`.

### Gap 1: Lack of Synthetic Deterministic Reasoning (CoT)
*   **Description**: The winner achieved their score primarily by generating programmatic, step-by-step logic traces (CoT) instead of relying on the base model's heuristics.
*   **Expected CV Delta**: High (+0.10 to +0.20)
*   **Code Change** (requires upstream data processing, but impacts `train.py` data loading):
```python
# Before (train.py)
train_data.append({"prompt": row.get('prompt', row.get('question', '')), "completion": row.get('completion', row.get('answer', ''))})

# After (train.py - assuming synthetic data is provided in a new format)
train_data.append({"prompt": row['prompt'], "completion": row['synthetic_reasoning'] + "\n\\boxed{" + row['answer'] + "}"})
```

### Gap 2: Missing `<think>` Tags in Prompt Formatting
*   **Description**: The winner explicitly formats completions with `<think>...</think>\boxed{...}` to guide the model's reasoning process.
*   **Expected CV Delta**: Medium-High (+0.05 to +0.10)
*   **Code Change**:
```python
# Before (train.py)
prompt_text = data["prompt"]
answer_text = data["completion"]

# After (train.py)
prompt_text = data["prompt"] + "\n<think>\n"
answer_text = data["reasoning"] + "</think>\n\\boxed{" + data["answer"] + "}"
```

### Gap 3: Missing Stratified Batching
*   **Description**: The winner distributes problem categories evenly within batches to prevent catastrophic forgetting of specific logic rules.
*   **Expected CV Delta**: Medium (+0.03 to +0.06)
*   **Code Change**:
```python
# Before (train.py)
for data in train_data:
    # simple sequential batching

# After (train.py)
def _stratified_batches(examples, batch_size, rng):
    # (Implementation grouping by category and yielding mixed batches)
    pass
# In training loop:
batches = _stratified_batches(train_data, micro_batch_size * gradient_accumulation_steps, random.Random(epoch))
for batch in batches:
    # process batch
```

### Gap 4: LoRA `train_unembed` Not Targeted
*   **Description**: The winner targets unembedding layers (`train_unembed=True`), which is crucial for fine-tuning exact token outputs for symbolic logic.
*   **Expected CV Delta**: Medium (+0.02 to +0.05)
*   **Code Change**:
```python
# Before (train.py)
target_modules = [".*\.(in_proj|out_proj|up_proj|down_proj)$"]

# After (train.py)
# Must add lm_head/unembed layers while respecting rank 32 constraints
target_modules = [".*\.(in_proj|out_proj|up_proj|down_proj|lm_head)$"]
```

### Gap 5: No Textual Augmentation on Symbols
*   **Description**: The winner uses augmentations (splitting/merging brackets, spelling) to prevent overfitting to superficial formatting.
*   **Expected CV Delta**: Medium (+0.02 to +0.04)
*   **Code Change**:
```python
# Before (train.py)
# No augmentation

# After (train.py - applied dynamically or pre-processed)
import random
def apply_bracket_augmentation(text):
    if random.random() < 0.5:
        text = text.replace("[", "【").replace("]", "】")
    return text
prompt_text = apply_bracket_augmentation(prompt_text)
```

### Gap 6: Basic Loss vs. Weighted Cross-Entropy
*   **Description**: The winner uses `CrossEntropyWithWeightingLossConfig` to scale advantages based on initial confidence, preventing over-optimization.
*   **Expected CV Delta**: Low-Medium (+0.01 to +0.03)
*   **Code Change**:
```python
# Before (train.py)
loss = compute_loss(logits, input_ids, mask)

# After (train.py)
# Implement confidence-based weighting
def compute_weighted_loss(logits, ref_logits, input_ids, mask):
    # calculate diff in logprobs, apply min(1.0, abs(prev)/branch) weighting
    pass
```

### Gap 7: Strict Mathematical `LinearDecayLRSchedule` Alignment
*   **Description**: While baseline has a linear decay, it must exactly match the winner's step-based or epoch-based multiplier `mult = min(1.0, max(0.0, 1.0 - epoch / (1 + total_epochs)))`.
*   **Expected CV Delta**: Low (+0.01)
*   **Code Change**:
```python
# Before (train.py)
# Baseline implementation of get_lr

# After (train.py)
def get_lr(self, step: int, total_steps: int, epoch: int, total_epochs: int) -> float:
    mult = min(1.0, max(0.0, 1.0 - epoch / (1 + total_epochs)))
    return self.final_learning_rate + (self.learning_rate - self.final_learning_rate) * mult
```

### Gap 8: Missing Global Metrics Tracking
*   **Description**: The winner tracks KL divergence per token to monitor policy drift. Baseline only logs loss.
*   **Expected CV Delta**: +0.00 (Observability improvement)
*   **Code Change**:
```python
# Before (train.py)
print(f"Step {step} Loss: {loss.item()}")

# After (train.py)
kl_div = (final_logprobs - ref_logprobs).mean().item()
print(f"Step {step} Loss: {loss.item()} KL: {kl_div}")
```

### Gap 9: Precise Target Masking Alignment
*   **Description**: Ensure `build_datum` strictly shifts targets/weights (`tokens[:-1]` vs `tokens[1:]`) exactly as `tinker.Datum` does in the winner's code.
*   **Expected CV Delta**: Low (+0.01 if currently misaligned)
*   **Code Change**:
```python
# Before (train.py)
# mask = [0]*len(prompt_tokens) + [1]*len(answer_tokens)

# After (train.py)
# Explicitly shift for standard Causal LM loss inside compute_loss
shift_logits = logits[..., :-1, :].contiguous()
shift_labels = input_ids[..., 1:].contiguous()
shift_mask = mask[..., 1:].contiguous()
```

### Gap 10: Strict Sequence Length Truncation
*   **Description**: The winner strictly enforces `TOKEN_LIMIT` of 8192 across all examples during data prep, not just dynamically.
*   **Expected CV Delta**: +0.00 (Stability improvement)
*   **Code Change**:
```python
# Before (train.py)
if len(tokens) > max_length: tokens = tokens[:max_length]

# After (train.py)
# Filter dataset beforehand
train_data = [d for d in train_data if len(tokenizer(d['prompt'] + d['completion'])['input_ids']) <= 8192]
```

## 3. Recommended Next 3 Experiments (Prioritized)

1.  **Experiment 1: Synthetic Deterministic Reasoning Pipeline**
    *   **Hypothesis**: By porting the winner's Python-based logical solvers (`reasoners/*.py`) to generate deterministic CoT paths for our training dataset, the model will learn explicit algorithmic steps rather than guessing, yielding the largest accuracy increase.
2.  **Experiment 2: Stratified Batching by Category**
    *   **Hypothesis**: Modifying the DataLoader in `train.py` to use `_stratified_batches` ensures the model sees a balanced mix of Math, Logic, and Code problems in every step, preventing catastrophic forgetting of earlier logic rules during single-epoch fine-tuning.
3.  **Experiment 3: LoRA Unembed Layer Targeting**
    *   **Hypothesis**: Including the `lm_head` (unembedding layer) in the `LORA_TARGET_MODULES` (while strictly keeping Rank <= 32) will significantly improve the model's ability to precisely generate specific formatting tokens (like brackets and math symbols) that were augmented in the dataset.

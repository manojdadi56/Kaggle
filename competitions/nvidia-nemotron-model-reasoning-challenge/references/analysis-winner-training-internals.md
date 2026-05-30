# Winner Solution Digest: Training Internals

This document analyzes the learning rate schedule, loss/regularization configurations, and shared training utilities from the winning solution (`tonghuikang/nemotron`).

## 1. Learning Rate Schedule (`lr_schedule.py`)

The winner utilizes two simple learning rate decay schedules, defined in `references/winner-lr_schedule.py.md`:

*   **`LinearDecayLRSchedule`** (Line 28): Decays the learning rate linearly from an initial `learning_rate` (default `2e-5`) to a `final_learning_rate` (default `1e-5`) over the total number of epochs.
    *   Multiplier calculation: `mult = min(1.0, max(0.0, 1.0 - epoch / (1 + total_epochs)))`
    *   Implementation: `final_learning_rate + (learning_rate - final_learning_rate) * mult`
*   **`StepLinearDecayLRSchedule`** (Line 42): Decays linearly based on the global step count rather than epochs, reaching 0 at `total_steps`.
    *   Implementation: `learning_rate * (1 - step / total_steps)`

### Replication in TASK-R10a
For our training replication in TASK-R10a, adopting the `LinearDecayLRSchedule` will allow us to gradually reduce the step size as training progresses, a standard practice for fine-tuning. We can implement a similar learning rate scheduler hook or parameterize our optimizer to follow this decay.

## 2. Loss and Regularization Configurations (`loss_config.py`)

The `references/winner-loss_config.py.md` file defines an abstract `LossConfig` class and several concrete implementations to experiment with different loss functions, regularization techniques, and detailed metric tracking for log-probabilities.

*   **`CrossEntropyWithWeightingLossConfig`** (Line 106): An extension of `CrossEntropyLossConfig`, this class introduces mechanisms similar to GRPO advantage scaling:
    *   **Branch weighting**: Scales advantages based on initial confidence: `min(1.0, abs(prev_logprob) / branch_logprob)`. This reduces the weight of updates on tokens where the model is already extremely confident.
    *   **First epoch cutoff**: Includes a `first_cutoff_weight` to apply lower weights during the first epoch (`epoch == 0`), aiming to prevent destructive over-optimization early in training.
    *   **Global metrics**: Computes weighted percentiles (`weighted_diff_pXX`) of log-probability changes across all tokens.
*   **`ImportanceSamplingLossConfig`** (Line 266): Calculates and logs the KL divergence per token (`final_logprobs[i] - ref_logprobs[i]`) and the mean importance ratio between the final and reference policies (`math.exp(min(lr, 20))`).
*   **`ClipLossConfig` (PPO / CISPO)** (Lines 295, 340, 347): Defines clipping thresholds to bound the likelihood ratio (importance ratio), preventing large catastrophic policy updates.
    *   **PPO** (Line 340): Uses symmetric bounds, e.g., `clip_low=0.2, clip_high=0.2` (`PPOLossConfig`).
    *   **CISPO** (Line 347): Uses broader, asymmetric bounds, e.g., `clip_low=0.8, clip_high=1.2` (`CISPOLossConfig`).
*   **`DROLossConfig`** (Line 354): Implements Distributionally Robust Optimization by applying a penalty proportional to the squared differences in log-probabilities from the reference model (`beta * 0.5 * sum(sq_diffs) / n`).

### Replication in TASK-R10a
For TASK-R10a, tracking metrics similarly to the winner (such as KL per token, distribution of log-prob changes) is crucial. We should consider implementing the `CrossEntropyWithWeightingLossConfig` style branch weighting or PPO-style clipping bounds directly in our custom loss function to stabilize fine-tuning, keep the model close to the reference behavior, and prevent forgetting.

## 3. Shared Training Utilities (`train_common.py`)

The `references/winner-train_common.py.md` script handles data preparation for the training framework (`tinker`).

*   **Corpus Definition**: Training data is tracked via a `corpus.jsonl` index, detailing problem ID, segment, category, and token counts.
*   **`TrainingExample`** (Line 70): Loads pre-tokenized segments and their corresponding masks.
    *   `mask=1`: Unmasked token (loss will be calculated on this token).
    *   `mask=0`: Masked token (loss is ignored).
*   **`build_datum`** (Line 109): This function transforms the tokens and mask into a `tinker.Datum`. Crucially, it shifts the targets and weights relative to the input:
    *   `model_input`: `tokens[:-1]`
    *   `target_tokens`: `tokens[1:]`
    *   `weights`: `mask[1:]`
    This accurately reflects causal language modeling, where the loss for predicting token `i` is determined by the mask value at token `i`.

### Replication in TASK-R10a
When formatting fine-tuning data in TASK-R10a, we must strictly follow this masking strategy. We should only set `weights=1` for the reasoning steps and final answer portions we want to train on, while masking out the prompt. The `build_datum` structure provides a concrete template for aligning inputs, targets, and masks correctly.

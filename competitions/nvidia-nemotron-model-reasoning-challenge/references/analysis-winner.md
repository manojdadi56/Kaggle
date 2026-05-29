# Analysis of Winning Solution: Tong Hui Kang

This document analyzes the open-source progress-prize-winning solution from Tong Hui Kang for the NVIDIA Nemotron Model Reasoning Challenge. The analysis is based on the [GitHub repository](https://github.com/tonghuikang/nemotron) and the corresponding [blog post](https://blog.huikang.dev/2026/05/02/nemotron-progress-prize.html).

## Data Strategy
The author heavily relied on synthesizing high-quality, step-by-step reasoning paths and augmenting the dataset to cover common patterns.
- **Rule-based Reasoning Generation**: Synthetic deterministic reasoning chains are generated using Python scripts representing the logic for different categories of problems. These scripts (e.g., `reasoners/bit_manipulation.py`, `reasoners/cipher.py`, `reasoners/gravity.py`, etc.) are coordinated by `reasoning.py` (Lines 1-50) to output exact reasoning traces matching the problem-solving steps.
- **Data Augmentation**: To improve robust generation across edge-case character formatting, specific text augmentations are produced via `augmentation.py` (Lines 1-40). The techniques involve individual modules in the `augmenters/` directory:
  - `spelling.py` breaks words down into separated, hyphenated characters (e.g., `–s–e–x–v–e–x–`).
  - `concatenation.py` merges distinct bracketed characters into one bracket (e.g., `【]】【}】 -> 【]}】`).
  - `splitting.py` splits one bracketed set of symbols into individually bracketed characters.
  - `matching.py` and `lstrip.py` provide additional structural augmentations.
- **Corpus Construction**: These augmented strings and the synthesized reasoning logic are compiled into `corpus.jsonl` using `corpus.py` (Lines 90-180), correctly appending standard reasoning tags. Only tokens belonging to the completion (the target answers and reasoning logic) are assigned a mask weight of `1` (for computing loss), whereas prompt tokens receive `0` (Lines 140-150 in `corpus.py`).

## LoRA Configuration
The LoRA tuning configuration focuses directly on maximizing expressiveness within the competition limits.
- **Rank Limit**: The LoRA rank is set exactly to the maximum allowed limit `32` (`train_sft.py`, Line 26). This is an explicit compliance factor for the competition's strict `≤32` cap for adapter size.
- **Target Modules**: The LoRA adaptation targets multiple components across the network. Specifically, `train_mlp = True`, `train_attn = True`, and `train_unembed = True` (`train_sft.py`, Lines 28-30). This extensive module selection ensures the adapter impacts a broader set of weights, particularly the unembedding layers which might be critical for generating specific mathematical or structural tokens.

## Training Recipe
The fine-tuning uses Supervised Fine-Tuning (SFT) over the constructed synthetic data.
- **Compute and Epochs**: The model is trained for just **1 epoch** (`train_sft.py`, Line 25).
- **Batching**: The global batch size is set to `64` (`train_sft.py`, Line 24) with a micro-batch size of `16` (`train_sft.py`, Line 33). Stratified sampling distributes problem categories evenly across batches (`train_sft.py`, `_stratified_batches` function).
- **Learning Rate**: A Step Linear Decay Learning Rate schedule is utilized, starting with a peak learning rate of `2e-4` (`train_sft.py`, Line 20).
- **Sequence Length limit**: Example truncation strictly caps all input tokens to a `TOKEN_LIMIT` of `8192` (`corpus.py`, Line 39).
- **Loss Functions**: A Cross-Entropy loss is defined natively by the `LossConfig` (`train_sft.py`, Line 18). Only unmasked target tokens are used to calculate the loss (`train_common.py`, Lines 73-95).

## Decoding / Prompt Tricks
- **Prompt Structure**: The prompts rely on the standard chat format for Nemotron, adding a fixed suffix asking for the final boxed answer (`corpus.py`, Lines 33-36).
- **Generation Logic**: The expected target model completion immediately continues the reasoning output started by the prompt's `<think>\n` tag, outputting the reasoning, concluding with `</think>`, then appending `\boxed{answer}` and ending with the `<|im_end|>` tag (`corpus.py`, Lines 134-138).

## What Drove the Score
The critical component driving the score was the comprehensive, programmatic generation of perfect "chain-of-thought" synthetic data. Instead of relying purely on the base model to learn mapping heuristics, the author mapped problem inputs deterministically to complete step-by-step reasoning pipelines (`reasoning.py`). Then, SFT trained the LoRA adapter simply to replicate these deterministic algorithmic steps inside the `<think>` block, drastically increasing accuracy. Augmentations helped the model adapt to out-of-distribution formatting quirks seen in the competition test set.

## Techniques to Adopt for Our Compute (40GB 2-GPU / 2x T4)
Given the constraints of our 2x 40GB or 2x 16GB (T4) setup, we should prioritize the following techniques ranked by cost/benefit ratio:

1. **Synthetic Deterministic Reasoning**: Generating high-quality, step-by-step logic traces programmatically rather than relying on LLM self-play or generation. This creates exceptionally dense training signals and costs zero GPU compute to create.
2. **Stratified Batching**: Distributing problem classes equally within each batch (`train_sft.py`'s `_stratified_batches`) prevents the model from forgetting earlier logic rules.
3. **Data Augmentation on Symbols**: Augmentations like bracket-splitting/merging (`augmenters/*.py`) prevent the model from overfitting to superficial text characteristics.
4. **LoRA Unembed Targeting**: Setting `train_unembed=True` may be crucial for fine-tuning exact token outputs necessary for symbolic logic manipulation.
5. **Exact Rank 32 Usage**: We must continue to enforce the rank=32 ceiling to maximize expressivity without failing competition validation. We must verify our T4 memory handles Rank 32 across all Attention/MLP/Unembed modules with a reasonable micro-batch size.

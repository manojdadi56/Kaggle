# Deltas vs. Winner & Hypothesis Ledger

This document outlines the key differences (deltas) between the Tong Hui Kang winning solution and alternative community approaches, followed by 5+ concrete hypotheses for the competition ledger.

## Deltas vs. Winner

The winner's solution (`tonghuikang/nemotron`) heavily relied on a custom procedural data engine, creating exact Chain-of-Thought (CoT) traces for 8 out of 9 puzzle categories and fine-tuning an adapter with rank=32 over MLP+Attention+Unembed layers for a single epoch. While this established the winning standard (LB ~0.85), community discussions and alternative implementations highlighted several crucial gaps and variations:

1. **Missing Coverage**: The winner explicitly skipped generating reasoning for the `cryptarithm_guess` category. This represents the most immediate, un-captured headroom for improving the baseline score.
2. **Quality over Quantity (Data Curation)**: The winner's approach trained on all correct synthetic generations. The community (e.g., `konbu17` Select2Reason-style) demonstrated that aggressively filtering down to only the highest-quality traces—prioritizing trace length, difficulty, and dropping repetitive samples—can yield similar or better accuracy while significantly reducing training costs. Mixing "reasoning on" and "reasoning off" (direct answer) samples also appeared in community forks.
3. **Fallback Logic**: For equation puzzles where a rule could not be confidently identified, community members found success implementing deterministic fallbacks (e.g., assuming absolute difference `|a-b|` if the operator wasn't found). The winner's approach simply defaulted to `rule_unknown` and skipped these.
4. **Target Modules & Architecture Compatibility**: The community heavily documented the dangers of `peft` regex module targeting on this specific architecture (Nemotron-3-Nano-30B is a hybrid Mamba-Transformer MoE). Attempting standard target selections caused hangs when scanning ~5980 MoE experts. The community delta was to explicitly target `mixer.in_proj`/`mixer.out_proj` (the ~46 Mamba mixer layers), or restrict targets to attention only `[q,k,v,o_proj]` to prevent LoRA-merge failures. The winner bypassed some of this by relying on managed services.
5. **Loss Weighting Strategies**: Community discussions (and un-activated code in the winner's repo) suggested that filtering out training problems where the min log-prob is already close to zero, or applying dynamic branch weighting (similar to PPO/GRPO), could prevent over-tuning on easy examples and forgetting harder rules. The winner ultimately just ran standard cross-entropy.

---

## Hypothesis Ledger

### Hypothesis 1: `cryptarithm_guess` Solver Implementation
- **Statement**: Adding a dedicated deterministic Python solver to generate correct CoT traces for the skipped `cryptarithm_guess` category will increase the public leaderboard score.
- **Expected effect**: A direct gain in LB score (targeting the gap between 0.85 and 1.0) because the model will learn to reason through a problem category it previously failed on.
- **How to test**: Implement the `cryptarithm_guess` logic in `reasoning.py`. Run the data engine, train a single-epoch LoRA adapter (using the winner's baseline hyperparams), and evaluate against the local CV harness. Compare the aggregate accuracy and per-category accuracy against the baseline 0.85 run.

### Hypothesis 2: Select2Reason Data Curation
- **Statement**: Filtering the synthetic corpus to remove repetitive, low-difficulty CoT traces (keeping only the highest-utility traces per category) will match or exceed the baseline accuracy while significantly reducing training token volume (and cost).
- **Expected effect**: Lower training time and cost without a drop in LB score. May slightly improve generalization by preventing the model from over-indexing on easy, repetitive deterministic patterns.
- **How to test**: Apply a curation filter to `corpus.jsonl` (e.g., grouping by template similarity and down-sampling, prioritizing longer traces). Run the standard SFT training on the curated subset and compare CV scores against the full-corpus baseline.

### Hypothesis 3: Equation Fallback Heuristic
- **Statement**: Defaulting to the absolute difference operator `|a-b|` for equation puzzles where no specific rule is found (instead of emitting nothing) will capture edge cases and improve category accuracy.
- **Expected effect**: A marginal but consistent accuracy gain in the `equation_numeric` and potentially `cipher` categories where rule deduction fails but simple numeric relationships dominate.
- **How to test**: Modify `reasoning.py` for the relevant categories. If the deterministic solver fails to find a rule, append a fallback trace assuming `|a-b|` and emit the corresponding answer. Train on this dataset and check the per-category CV metrics for equation problems.

### Hypothesis 4: Explicit Mamba-Mixer LoRA Targeting
- **Statement**: Explicitly targeting the Mamba mixer layers (`mixer.in_proj`, `mixer.out_proj`) during QLoRA training on 2xT4 GPUs avoids MoE scanning hangs and merge mismatches while preserving the expressivity needed to reach the ~0.85 baseline.
- **Expected effect**: Enables stable, successful local training runs on free compute architectures without encountering `AcceleratorError` or infinite hangs during the `peft.get_peft_model()` call.
- **How to test**: Create a smoke-test training script using 4-bit quantization on 2xT4. Pass a strict list of Mamba target modules. Verify that the model compiles, begins training steps immediately without hanging, and successfully merges the adapter back to the base model.

### Hypothesis 5: Log-Prob Filtered Curriculum (Anti-Forgetting)
- **Statement**: Filtering out training problems where the model's minimum log-probability is already near zero (meaning the model already perfectly predicts it) will prevent over-tuning on easy examples and improve performance on harder rules.
- **Expected effect**: Higher accuracy on complex problems (e.g., `bit_manipulation`) that often suffer from catastrophic forgetting when flooded with easy, deterministic training examples.
- **How to test**: Run an initial inference pass of the base model over the training set to record log-probs. Filter the dataset to exclude examples where the minimum token log-prob > -0.05. Train the SFT model on this filtered dataset and evaluate against the CV harness, checking specifically for degradation in easy categories vs. gains in hard categories.

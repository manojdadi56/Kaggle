# Host Template Specification

This document details the exact system prompt, chat template, and generation hyperparameters used by the host evaluation server for the NVIDIA Nemotron Model Reasoning Challenge, as extracted from `competitions/nvidia-nemotron-model-reasoning-challenge/references/winner-notebook_tinker.py.md`.

## System Prompt

The specific system header text used to enable reasoning behavior is:
```text
reasoning_on
```
It is applied via the `system` role in the chat template.

## Chat Template Output

When the `NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` tokenizer processes a chat containing the system prompt and a user prompt with the competition suffix (`"\nPlease put your final answer inside \`\\boxed{}\`. For example: \`\\boxed{your answer}\`"`), with `add_generation_prompt=True` and `enable_thinking=True`, the exact rendered text is:

```
<|im_start|>system
reasoning_on<|im_end|>
<|im_start|>user
{user_prompt}
Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`<|im_end|>
<|im_start|>assistant
<think>
```

The underlying Jinja template processes `reasoning_content` and handles `<think>` formatting for chain-of-thought outputs, specifically emitting `<think>\n` after `<|im_start|>assistant\n` when `enable_thinking=True`.

## Generation Hyperparameters

The default sampling and generation parameters evaluated on the vLLM server (from `notebook_tinker.py` defaults):
- `max_tokens`: 3584
- `temperature`: 1.0
- `top_p`: 1.0
- `max_model_len`: 4096

*Note: While some code cells in the notebook override these for certain runs (e.g., `temperature=0.0`, `max_tokens=7680`), the exact default parameters defined in the `evaluate` function interface are specified above.*

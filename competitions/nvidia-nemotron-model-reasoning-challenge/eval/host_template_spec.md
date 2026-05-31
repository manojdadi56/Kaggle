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

**AUTHORITATIVE host scoring config** — from the official competition **Evaluation page**
(https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/overview/evaluation),
verified 2026-05-31. The host loads base model + our LoRA adapter under **vLLM** and scores with:

| Parameter | Value |
| :--- | :--- |
| `max_lora_rank` | 32 |
| `max_tokens` | **7680** |
| `temperature` | **0.0** (greedy/deterministic) |
| `top_p` | 1.0 |
| `max_num_seqs` | 64 |
| `gpu_memory_utilization` | 0.85 |
| `max_model_len` | **8192** |

Scoring: extract the final answer (prioritize `\boxed{}`, fall back to other heuristics / last numeric
value); correct if it matches ground truth exactly as a string OR within relative tolerance 1e-2.

⚠️ CONTRADICTION RESOLVED (C-GENPARAMS, 2026-05-31): an earlier version of this spec listed
`max_tokens=3584, temperature=1.0, max_model_len=4096`. Those were the `evaluate()` *defaults* in
`winner-notebook_tinker.py.md`, NOT the competition's actual scoring config — the official Evaluation
page is authoritative. Our local-CV notebook (cell 2/3) was updated to match (temp=0.0,
max_new_tokens=7680, max_model_len=8192) in notebook **v45** so CV faithfully predicts the LB. The KEY
difference is **temperature 1.0 → 0.0**: the host decodes greedily, so any CV measured with sampling
(temp=1.0) is non-faithful and overstates noise.

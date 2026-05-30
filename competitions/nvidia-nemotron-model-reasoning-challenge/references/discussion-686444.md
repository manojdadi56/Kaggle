# Nemotron Inference Improvement Plan

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686444
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 10476

---

Datasets
Models
Code
format_list_bulleted
Discussions
Learn
Kaggle Rankings
Progression
Documentation
Blog
Host a Competition
Research Grants
Educator Resources
Support/Contact
Community Guidelines
Team
Terms
Privacy
note_alt
NVIDIA Nemotron Model Reasoning Challenge
There are still many missing pieces of the puzzle: equation and cryptarithm.
AcceleratorError: no kernel image available on RTX PRO 6000
Temp Blackwell Workaround
What should be included in submission.zip?
Edited
Save order db V1
Kitesdata
History inferencing V3
History inferencing
Fork of inferencing
ARC Prize 2024
LMSYS - Chatbot Arena Human Preference Predictions
notebookc7a610ad46
train Swin_T[pytorch lightning]
Viral Pneumonia Classification | GoogLeNet
1
search
Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.
NVIDIA · FEATURED PREDICTION COMPETITION · 17 DAYS TO GO
Submit Prediction
more_horiz
NVIDIA Nemotron Model Reasoning Challenge
Advance reasoning techniques using NVIDIA Nemotron open models on a novel benchmark
Overview
Data
Code
Models
Discussion
Leaderboard
Rules
Team
Submissions
WILLTLING · 1262ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
4
arrow_drop_down
more_vert
It seems the KV cache is not enabled during RL training
I encountered the following issue:
transformers_modules.nemotron_model.modeling_nemotron_h|WARNING] NemotronH requires an initialized `NemotronHHybridDynamicCache` to return a cache. None was provided, so no cache will be returned
When I was conducting GRPO training, the training speed was very slow. I suspect this might be related to the issue mentioned above. I noticed that a similar problem was also mentioned in this discussion, but I'm not sure if it has been fixed. Additionally, I also tried using vLLM, but the GPU memory was completely insufficient.
add_reaction
React
4 Comments
Hotness
undo
redo
format_size
format_bold
format_italic
format_strikethrough
insert_link
format_quote
format_list_numbered
format_list_bulleted
table_chart
insert_photo
smart_display
insert_emoticon
This comment will be made public once posted.
attach_file
Post Comment
Mark Susol
Posted a month ago
· 3011th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I also tried using vLLM, but the GPU memory was completely insufficient.
Mind sharing your efforts? I am running on DGX Spark so GPU/RAM should be sufficient.
Loading tokenizer: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 Loading base model: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 Loading checkpoint shards: 0%| | 0/13 [00:00<?, ?it Loading checkpoint shards: 100%|██████████| 13/13 [06:13<00:00, 28.70s/it] Loading adapter: /workspace/output/adapter_20260503_203554 Inference: 0%| | 0/950 [00:00<?, ?it/s]This model does not supportCacheinstances.cache_implementation(set to hybrid) will be ignored. NemotronH requires an initializedNemotronHHybridDynamicCacheto return a cache. None was provided, so no cache will be returned.Inference: 10%|█ | 99/950 [30:40<5:58:22, 25.27s/it]
Below is my verbose research thread (perplexity) where I am planning an improvement. How will Kaggle deal with the l;ong inference times?
`
Nemotron Inference Improvement Plan
Objective
Improve inference throughput for the LoRA-adapted Nemotron-3-Nano-30B-A3B model by moving performance-critical runs away from raw Hugging Face model.generate() and toward a cache-aware serving path suitable for Kaggle time limits.[1][2]
Current State
The current inference script uses plain transformers generation with a PEFT adapter attached to the base model.[1] This path is functionally correct for validation, but the current Hugging Face NemotronH integration has a known cache-plumbing issue: generate() follows the standard past_key_values protocol, while the model expects its hybrid cache under cache_params, so KV or hybrid cache is not actually used during decoding.[3][2]
Problem Summary
Because the hybrid cache is not threaded through correctly, generation repeatedly recomputes context instead of benefiting from incremental cached decoding.[3][2] NVIDIA’s own guidance says Hugging Face is mainly for prototyping here and points users to optimized inference engines such as vLLM, TRT-LLM, SGLang, and llama.cpp for KV-cache-aware deployment.[2][1]
Target Architecture
The preferred production path is:
Load the fine-tuned PEFT or LoRA adapter onto the Nemotron base model.
Merge the adapter into the base weights with merge_and_unload().
Save the merged checkpoint as a standalone model artifact.
Run inference through vLLM using the merged model.
Keep the existing Hugging Face script only for smoke tests and small validation runs.[4][5][2]
Why vLLM
vLLM has a documented deployment path for NVIDIA Nemotron-3-Nano-30B-A3B and is part of NVIDIA’s recommended inference stack for this model family.[4][5][1] This avoids the current Hugging Face cache mismatch and gives a better chance of meeting Kaggle runtime limits.[2]
Implementation Steps
1. Freeze the baseline
Keep the current scripts/infer_lora.py path unchanged for reproducibility and baseline comparison.[1]
Record current runtime metrics: prompt length, max_new_tokens, tokens per second, total job duration, and hardware profile.
2. Add a merge script
Create a script such as scripts/merge_lora.py.
Load base model + tokenizer + adapter.
Call merge_and_unload() on the PEFT model.
Save merged model and tokenizer to a new output directory such as output/merged_nemotron_model/.
Validate that the merged checkpoint loads without PEFT dependencies in the inference environment.
3. Validate output parity
Run a small fixed eval set through both paths: current HF+adapter flow and merged-model flow.
Compare decoded outputs, task metrics, and any competition-specific scoring proxies.
Accept minor formatting drift, but investigate large semantic divergence.
4. Stand up vLLM inference
Start with NVIDIA’s documented vLLM recipe for Nemotron-3-Nano-30B-A3B, including --trust-remote-code and model-specific parser flags where needed.[4][1]
Point vLLM at the merged model directory instead of the base-plus-adapter pair.
Build a thin client script that submits prompts and writes predictions in the format required by the competition.
5. Benchmark on target hardware
Measure end-to-end throughput on the same class of hardware expected for Kaggle submission or local dry runs.
Benchmark several realistic settings: short prompts, long prompts, and the competition’s typical max_new_tokens budget.
Record tokens per second, total runtime, memory footprint, and failure modes.[4]
6. Integrate into submission flow
Add a clear switch in the pipeline such as --backend hf vs --backend vllm.
Default local validation to Hugging Face only if simplicity matters more than speed.
Default submission generation to vLLM once parity and stability are confirmed.
Fallback Option
If vLLM integration becomes blocked, the secondary path is a custom generation loop that calls model.forward() directly and passes the initialized Nemotron hybrid cache through cache_params on every step.[3][6] This should restore cache-aware decoding in principle, but it is more brittle and requires maintaining custom decoding logic, stopping criteria, and sampling behavior.[3]
Non-Goals
Do not refactor the existing baseline path until the merged-model path is validated.
Do not rely on raw Hugging Face model.generate() performance improvements landing in time for the current competition run.[2]
Do not introduce multiple inference backends at once beyond a simple baseline-versus-vLLM split.
Risks
Risk Impact Mitigation
Merged model outputs differ from adapter-attached outputs Medium Run parity tests on a fixed sample set before switching default inference
vLLM environment differs from Kaggle runtime High Dry-run on the closest available hardware and container stack before final submission
Nemotron-specific flags or parser settings are incomplete Medium Start from NVIDIA and vLLM published examples rather than a generic vLLM command.[4][1]
Time spent on custom HF patching delays delivery Medium Treat HF monkey-patching as a last resort, not the main path.[2]
Recommended Deliverables
scripts/merge_lora.py
scripts/serve_vllm.sh
scripts/infer_vllm.py
docs/nemotron_inference_notes.md
output/merged_nemotron_model/ directory contract
Acceptance Criteria
The migration is successful when all of the following are true:
The merged checkpoint loads cleanly in vLLM.[4][5]
Output quality is materially unchanged on a representative validation slice.
End-to-end inference runtime is significantly lower than the current raw Hugging Face path.
The submission pipeline can run without manual intervention.
The old Hugging Face path remains available for debugging and quick validation.
Suggested Sequence
Benchmark the current script.
Implement and test adapter merge.
Validate output parity.
Bring up vLLM with the merged model.
Benchmark throughput.
Switch submission inference to vLLM.
Keep custom HF cache work only as an optional experimental branch.[4][2]
References
[1] nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 - Hugging Face
[2] nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 · doesn't do kv cache when using Transformers · Discussion #14 - Hugging Face
[3] nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16 · Bug Report: model.generate() does not use cache_params · Discussion #2 - Hugging Face
[4] NVIDIA Nemotron-3-Nano-30B-A3B User Guide - vLLM Recipes
[5] Deploying NVIDIA Nemotron-3-Nano with vLLM - GitHub
[6] NemotronH - Hugging Face Transformers Documentation
`
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Supposedly transformers GRPO trainer lets you share model memory b/w training and VLLM inference so you dont have to load the model twice - although I haven't tried this (I also had problems even loading LORA in vllm - so I'm curious if you managed to solve this) - Also helpful to let you compute KL-div against base model by swapping LORA in and out to save memory
Additionally - you could try loading the model in 4bit quantization
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Quantization make training terribly long
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
yes need to fix this problem
reply
Reply
add_reaction
React

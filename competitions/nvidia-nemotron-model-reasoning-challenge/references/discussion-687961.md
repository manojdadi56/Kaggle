# LoRA parameters

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687961
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 9749

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
Save order db V1
Let's learn from Google Tunix Hack for Nemotron
Metric Update
How to Get Started + Nemotron Model Reasoning Challenge Resources
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
TONG HUI KANG · 1173RD IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
33
arrow_drop_down
more_vert
Training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences
I want to understand the theoretical limitations when training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences.
I have not proven that any of the configurations listed here works in practice. I am making my own training implementation, and I want to understand whether my inefficiencies are avoidable with better implementation. Please help me check if I have missed any theoretical limits, thanks!
This table calculates how much memory is needed to train Nemotron-3-Nano-30B-A3B-BF16 with different microbatch sizes (μ). Larger microbatch sizes can improve hardware utilization and speed up training, but only if they fit in memory [1].
Component Formula μ=1 μ=4 μ=16 μ=64
Base model weights (BF16) W × 2 63.6 GB 63.6 GB 63.6 GB 63.6 GB
LoRA adapter weights (FP32) P × 4 3.5 GB 3.5 GB 3.5 GB 3.5 GB
LoRA gradients (FP32) P × 4 3.5 GB 3.5 GB 3.5 GB 3.5 GB
Optimizer m + v (FP32) P × 8 7.1 GB 7.1 GB 7.1 GB 7.1 GB
CUDA context & buffers ~3 GB 3.0 GB 3.0 GB 3.0 GB 3.0 GB
Checkpointed layer inputs L × μ × S × H × 2 2.3 GB 9.2 GB 36.6 GB 146.6 GB
Peak intra-layer intermediates μ × S × D × 2 331 MB 1.3 GB 5.3 GB 21.2 GB
Backward intra-layer gradient μ × S × H × 2 44 MB 176 MB 704 MB 2.8 GB
Logits — unchunked μ × S × V × 2 2.1 GB 8.6 GB 34.4 GB 137.4 GB
TOTAL (unchunked logits) 85.6 GB 100.1 GB 157.8 GB 388.8 GB
Logits — fused CE μ × S × 4 32 KB 128 KB 512 KB 2 MB
TOTAL (fused CE) 83.5 GB 91.5 GB 123.5 GB 251.4 GB
LoRA parameters
Layer type Weight name Shape per adapter × count typical possible
Attention q_proj [2688, 4096] 217,088 × 6 1.30M 1.30M
k_proj [2688, 256] 94,208 × 6 565,248 565,248
v_proj [2688, 256] 94,208 × 6 565,248 565,248
o_proj [4096, 2688] 217,088 × 6 1.30M 1.30M
SUBTOTAL 3.74M 3.74M
Mamba-2 in_proj [2688, 12864] 497,664 × 23 11.45M 11.45M
out_proj [5376, 2688] 258,048 × 23 5.94M 5.94M
conv1d [5376, 1, 4] — × 23 — —
dt_bias [64] — × 23 — —
A_log [64] — × 23 — —
D [64] — × 23 — —
SUBTOTAL 17.38M 17.38M
MoE routed experts.{j}.fc1 [2688, 1856] 145,408 × 2944 428.08M 428.08M
experts.{j}.fc2 [1856, 2688] 145,408 × 2944 428.08M 428.08M
SUBTOTAL 856.16M 856.16M
MoE shared shared_experts.fc1 * [2688, 3712] 204,800 × 23 — 4.71M
shared_experts.fc2 * [3712, 2688] 204,800 × 23 — 4.71M
SUBTOTAL — 9.42M
MoE router gate [2688, 128] 90,112 × 23 — 2.07M
Output lm_head [2688, 131072] 4,280,320 × 1 — 4.28M
Embedding embed_tokens [131072, 2688] 4,280,320 × 1 — 4.28M
All layers norm (RMSNorm) [2688] — × 104 — —
TOTAL 877.28M 897.33M
FP32 size 3.51 GB 3.59 GB
Training throughput
The forward pass is 3.5B active parameters × 8192 sequence length × 2 = 57 TFLOP. With gradient checkpointing, the backward pass is 3× the forward (recompute forward, compute activation gradients, compute weight gradients) = 171 TFLOP [5]. Each forward-backward pass requires 228 TFLOP per sample.
GPU BF16 TFLOPS HBM bandwidth Critical arithmetic intensity (FLOPs/byte)
H200 990 4.8 TB/s 206
RTX Pro 6000 252 1.15 TB/s 219
If training achieves 100% compute efficiency, it will be able to process one sequence in 228 / 990 = 0.23 seconds on a H200 or 228 / 252 0.90 seconds on a RTX Pro 6000.
However, you do not get 100% compute efficiency. I am still understanding why. Papers usually report a MFU of 30% - 40%.
Glossary
Symbol Meaning Value
μ microbatch size samples per forward/backward; B = μ × grad accumulation steps
S sequence length 8,192 tokens per sample
V vocabulary size 131,072 possible output tokens
H hidden dimension 2,688
L number of layers 52 (23 Mamba-2 + 23 MoE + 6 GQA attention)
R LoRA rank 32
B global batch size 64
W base model params 31.8B
P LoRA trainable params 886.7M
D MoE intra-layer width 20,224 = 6 (active experts per token) × 1856 (expert FFN intermediate) + 3712 (shared expert intermediate) + 2×2688
Observations
Notebooks on Kaggle has access to GPU RTX Pro 6000, which has 96GB VRAM. Apparently it can barely fit a microbatch size of 1 or 4 [2].
unsloth uses fused cross entropy to avoid the memory requirement for storing the logits for the microbatch [3].
Adapter weights are FP32 (3GB), even as the model is in BF16
Nemotron supports Flash Attention, which means it does not require quadratic memory for the attention mechanism [4].
References
[1] https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide#effective-batch-size
[2] https://unsloth.ai/docs/models/nemotron-3#fine-tuning-nemotron-3-and-rl
[3] https://unsloth.ai/docs/blog/500k-context-length-fine-tuning#unsloth-loss-refactoring-chunk-and-fuse
[4] https://github.com/huggingface/transformers/pull/44390/changes
[5] https://jax-ml.github.io/scaling-book/transformers/ — training FLOPs: 6N without checkpointing, 8N with; arithmetic intensity and roofline model
[6] Gu & Dao, "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" (2023), https://arxiv.org/abs/2312.00752 — "most operations (except matrix multiplication) are bounded by memory bandwidth"; hardware-aware scan fuses in SRAM
[7] Gale et al., "MegaBlocks: Efficient Sparse Training with Mixture-of-Experts" (2022), https://arxiv.org/abs/2211.15841 — Megatron-LM sustains 21–48% of peak; MoE padding overhead forces 2×–8× smaller microbatches
[8] https://github.com/stas00/ml-engineering/blob/master/training/performance/README.md — individual matmul kernels achieve 72–77% of peak; end-to-end single-GPU training achieves 8–20% MFU due to non-matmul overhead between kernels
3
add_reaction
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
Nguyen
Posted 2 months ago
· 2110th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I can only train with a μ=1 and a length of 16384 in 1XH200, each step taking ~22s with a gradient cumulative with B=16. Are you using packing?
cc: @huikang
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1173rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
There is no point training with a length of 16384 since the limit is 8192.
If you limit to 8192, you should be able to train with μ=2 I guess?
reply
Reply
add_reaction
React
Nguyen
Posted 2 months ago
· 2110th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Ah, I mean is packing with a length of 16k, it equivalent to a mini-batch of 2 x 8192 if your data only contains data with a max length of 8192. What I want to mention is that the mini batch size you mentioned in Training throughput, for example 4x or 16x8192, seems to result in OOM (no offload weight or activation), as far as I understand.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
rin2401
Posted a month ago
· 452nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Does the Nemotron model support flash attention 2? I'm using unsloth/trl for training, but I'm get an unsupported error
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted a month ago
· 1173rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Good question. The Github PR I cited has strings like _supports_flash_attn_2 = True.
When I run the training script on Kaggle, it has logs with FA2 = False
==((====))==  Unsloth 2026.3.17: Fast Nemotron_H patching. Transformers: 4.57.6.
\\   /|    NVIDIA RTX PRO 6000 Blackwell Server Edition. Num GPUs = 1. Max memory: 94.971 GB. Platform: Linux.
O^O/ \_/ \    Torch: 2.10.0+cu128. CUDA: 12.0. CUDA Toolkit: 12.8. Triton: 3.6.0
\        /    Bfloat16 = TRUE. FA [Xformers = 0.0.35. FA2 = False]
"-____-"     Free license: http://github.com/unslothai/unsloth
In summary, I am not sure.
reply
Reply
add_reaction
React
Benni
Posted a month ago
· 1870th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
It actually does support flash attention 2. For some reason the native modeling_nemotron_h.py (used when setting trust_remote_code=True) in the model directory does not set that flag as opposed to the transformers implementation (used when setting trust_remote_code=False).
Since the native implementation has cache issues with transformersv5 anyways and does not use the performance optimizations from the new packed experts implementation (which greatly speeds up training & inference) it makes no sense to use transformersv4 or the implementation that does not have fa2 support enabled anyways.
reply
Reply
add_reaction
React

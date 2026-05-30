# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686865
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5954

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
Compute Access
CUDA Error: no kernel image available for execution on the device
Kaggle Environment Fixes for Nemotron-3-Nano (March 2026
Is RLVR worth it? or should I work on SFT only?
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
HAOKWOK · 2671ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
3
arrow_drop_down
more_vert
Has anyone successfully run NVIDIA Nemotron using DeepSpeed ZeRO-3?
Hi everyone,
I am seeking advice on a persistent issue when transitioning from DeepSpeed ZeRO-2 to ZeRO-3 for fine-tuning Nemotron-30B on a local setup with 2x NVIDIA A100 (80GB).
Current Context & Motivation Previously, I was using ZeRO-2, which works but is pushed to the absolute physical limit. With per_device_train_batch_size=2 and max_seq_len=3072, my VRAM usage sits at 79.5GB / 80GB. To gain more headroom for larger batches or longer sequences, I am trying to move to ZeRO-3.
The Problem When I switch to ZeRO-3, the following sequence occurs:
Initial Load: The model initially fills about 62GB on each GPU.
Sharding: The ZeRO-3 sharding kicks in successfully, and the VRAM footprint drops to exactly 35,482MB on both cards.
The Deadlock: Right at the transition to the training phase (or just before the first forward pass), both GPUs spike to 100% utilization, yet the VRAM remains frozen at 35,482MB.
No Progress: There is zero sign of data exchange (NIC/NVLink activity is idle) and no training logs are produced. The process remains in this state indefinitely with no NCCL timeout errors.
Questions Has anyone successfully run Nemotron-30B with ZeRO-3? Are there specific transformer_layer_cls or zero_leaf_modules that need to be explicitly defined in the ds_config?
Could this be related to the way the model's custom kernels or attention mechanisms are initialized under the ZeRO-3 wrapper?
Are there any known compatibility issues between accelerate and the Nemotron weight-loading logic when sharding is enabled?
I would appreciate any insights or sample ds_config files that have worked for this model. Thanks!
add_reaction
React
3 Comments
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
lkevincc
Posted a month ago
· 974th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The issue with multi-GPU training is that if we do not fine-tune the "*.experts" layers, the model runs well across multiple GPUs. However, this approach results in a significant loss of trainable parameters during fine-tuning. On the other hand, including the expert layers leads to deadlocks due to rank mismatches in the multi-GPU setup. Therefore, I ultimately abandoned the multi-GPU approach and switched to using a single H200 for fine-tuning.
reply
Reply
add_reaction
React
LX
Posted a month ago
· 31st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The same problem with me.I encountered the following training deadlock issue:
Train:   0%|          | 0/176 [00:00<?, ?it/s][INFO:swift] use_logits_to_keep: False
It seems to be stuck at:
modeling_nemotron_h.py:772
hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
The training deadlock is caused by incompatible interaction between the Nemotron model and DeepSpeed ZeRO-3. Accessing norm.weight.dtype in the forward stage triggers unintended all-gather of sharded parameters, leading to cross-rank CUDA synchronization hang.
reply
Reply
add_reaction
React
HaoKwok
TOPIC AUTHOR
Posted 2 months ago
· 2671st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Implementation Details: ds_config_path = os.path.join(config_dir, "ds_config_stage_3.json") device_map = None
with deepspeed.zero.Init(enabled=False): model = AutoModelForCausalLM.from_pretrained( MODEL_PATH, low_cpu_mem_usage=False, device_map=DEVICE_MAP, trust_remote_code=True, dtype=torch.bfloat16, )
training_args = SFTConfig( output_dir=OUTPUT_DIR, deepspeed=DS_CONFIG_PATH, per_device_train_batch_size=PER_DEVICE_BATCH_SIZE, gradient_accumulation_steps=GRAD_ACCUM, num_train_epochs=NUM_EPOCHS, dataloader_num_workers=8, dataloader_pin_memory=True, …
)
trainer = SFTTrainer( model=model, train_dataset=train_dataset, processing_class=tokenizer, args=training_args )
{ "fp16": { "enabled": false }, "bf16": { "enabled": true },
"zero_optimization": { "stage": 3, "offload_optimizer": { "device": "none" }, "offload_param": { "device": "none" }, "overlap_comm": true, "contiguous_gradients": true, "sub_group_size": 1e9, "reduce_bucket_size": "auto", "stage3_prefetch_bucket_size": "auto", "stage3_param_persistence_threshold": "auto", "stage3_max_live_parameters": 1e9, "stage3_max_reuse_distance": 1e9, "gather_16bit_weights_on_model_save": true },
"gradient_accumulation_steps": "auto", "gradient_clipping": "auto", "steps_per_print": 10, "train_batch_size": "auto", "train_micro_batch_size_per_gpu": "auto", "wall_clock_breakdown": false }
reply
Reply
add_reaction
React

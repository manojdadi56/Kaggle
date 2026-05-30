# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698277
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2733

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
From 8% → 71% on Cryptarithm Tasks, But Score Still Stuck at 0.86
Nemotron ATLAS: Architecture-Targeting LoRA with Augmented Solvers
Synthetic data generation allowed
How are GPU hours calculated?
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
HARDIK YERNE · POSTED 21 DAYS AGO
arrow_drop_up
-5
arrow_drop_down
more_vert
DeepSeek Math 7B LoRA fine-tuning — dependency issues on Kaggle environment
Hi everyone,
I'm fine-tuning DeepSeek Math 7B with LoRA for this competition and running into package compatibility issues on Kaggle's environment.
My setup:
Model: deepseek-math-7b-instruct (4-bit NF4 quantization)
LoRA: r=8, target q_proj + v_proj
Training: 600 steps, cosine LR, batch=1, grad_accum=8
Val loss reached 0.6889 at step 600
Issues faced:
trl/transformers/bitsandbytes version conflicts
tokenizer path validation errors with local Kaggle model paths
numpy binary incompatibility after force reinstalls
Questions:
What trl + transformers + bitsandbytes versions work cleanly on Kaggle GPU T4?
How are others loading local Kaggle model datasets with from_pretrained?
Any tips for the Save & Run All full run succeeding?
Happy to share my notebook if it helps others. Thanks!
add_reaction
React
1 Comment
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
a14iiiii
Posted 21 days ago
· 80th in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
This competition does not include traing ds model, you are supposed to train lora adapter for NVIDIA Nemotron-3-Nano-30B. For dependencies, it is better to install libraries via 'uv pip install' to automatically find the best versions for you.
reply
Reply
add_reaction
React

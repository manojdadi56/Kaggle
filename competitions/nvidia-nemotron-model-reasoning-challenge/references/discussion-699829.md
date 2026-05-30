# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/699829
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2766

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
Does the official answer parser support literal { or } inside \boxed{...}?
Does the final evaluation dataset necessarily exclude test questions from the training set?
[Bug or Expected?] Issue in Eval code
GRPO Traning guide needed
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
WKDRBWND1 · 1760TH IN THIS COMPETITION · POSTED 15 DAYS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Is ~2 tokens/sec normal for Nemotron-30B on Kaggle?
Model:
Nemotron-3-Nano-30B-A3B (Hybrid Mamba-Transformer)
Setup:
Quantization: 4-bit (via Unsloth / bitsandbytes)
GPU: NVIDIA RTX 6000 Ada (or Blackwell, based on Kaggle instance)
Framework: Unsloth + Transformers
Method: Manual Inference Loop using model.forward() with cache_params (to avoid MoE-related index_add_ type mismatch errors in model.generate())
Issue: I am currently getting around ~2 tokens/sec generation speed. Given the 30B parameter size and the manual loop overhead, I am wondering if this is the expected performance on Kaggle for this specific model architecture.
If this is slower than normal, what should I check first?
Is there a significant overhead when using a manual for loop instead of model.generate() for Nemotron's hybrid architecture?
Are there specific optimizations for cache_params (the hybrid equivalent of KV Cache) that I might be missing?
Would torch.compile() be recommended for this hybrid MoE structure, or is it likely to cause kernel conflicts?
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
m4nocha
Posted 14 days ago
· 1961st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
useing vLLM I am getting 3000 Token/s
reply
Reply
add_reaction
React

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703214
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3095

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
Is DoRA allowed does it actually improve LB scores?
Kaggle CLI Can’t Set GPU Type? Tired of Manually Switching to RTX 6000 Every Time 😩
Why are we seeing 0.84 – 0.86 score variance with the 0.85 winning zip?
corrupted or puzzel (numeric equations)
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
YANGLE MA · 1276TH IN THIS COMPETITION · POSTED 18 HOURS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Struggling with Nemotron training stability in local H20 (Loss stagnation & exploding grad_norm）
Hi everyone,
I’m working on the Nemotron-3-Nano-30B-A3B pipeline (based on the popular notebook from huikang https://www.kaggle.com/code/huikang/end-to-end-finetuning-for-lb-0-85 ) but I’m running into significant stability issues when running it on my local H20 cluster.
I’ve tested this on both single-GPU and multi-GPU setups, but the behavior is consistent:
Loss stagnation: The loss just doesn't drop as expected.
Exploding gradients: The grad_norm is consistently massive compared to typical fine-tuning runs.
Currently, I’ve been using a gradient sanitization hook to clamp/filter out large/invalid gradients just to keep the training from crashing (the 59392/59392 issue). However, I’m fully aware that this is a "band-aid" fix—it effectively kills the training and prevents any real learning from happening.
Is there anyone else who has managed to train this specific model architecture locally? I suspect it might be related to:
Precision/Precision-handling: Maybe the way MoE or LoRA params are cast to fp32 is interacting poorly with the local environment (unlike the official Kaggle kernel).
Gradient scaling: Are there specific hyper-parameters or grad_clip values that make this model "behave"?
I’m a bit stuck on whether this is a hardware-specific nuance or if I’m missing something in the Unsloth/Mamba integration. Any advice or pointers on how you guys are keeping this stable would be amazing. Thanks!
add_reaction
React
0 Comments
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

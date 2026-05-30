# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698649
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2972

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
Compute partner needed - deterministic solvers for all puzzle categories built, budget-constrained
leaderboard score barrier of 0.87
Issue running NVIDIA Nemotron model on Kaggle (mamba_ssm import error)
Nemotron only for submission ?
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
ANJANA MOHAN · 2514TH IN THIS COMPETITION · POSTED 19 DAYS AGO
arrow_drop_up
-6
arrow_drop_down
more_vert
Stuck at 0.56 — Need advice on improving SFT approach
Hi everyone! 👋 I’ve been working on this competition and hitting a wall at 0.56. Would love advice from those scoring higher. My current approach: • Training on 4 deterministic puzzle types: gravity, numeral, unit_conversion, cipher + bit_manipulation • Programmatic CoT traces with tags • 7,219 correctly solved training examples from train.csv • LoRA rank 16, lr=2e-4, 3 epochs, bf16 What I’ve tried: • Short CoT (~234 tokens) → 0.56 ✅ best • Longer CoT (~340 tokens) → 0.50 ❌ • Rank 32, lr=5e-5 → 0.50 ❌ • No system prompt, correct prompt suffix → 0.56 My questions: 1. What CoT length works best for you? 2. Should I mask the prompt tokens during training (only train on completion)? 3. Is there something specific about how tags should be formatted? 4. Any advice on improving bit manipulation accuracy beyond 54%? @huikang @donaldgalliano — would really appreciate your insights! 🙏 Thank you! 🙏
add_reaction
React
2 Comments
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
FO-SHIZZLE
Posted 10 days ago
· 139th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Your max_seq_length is likely too short. You need to increase it to at least 4096. It seems rediculous but that's what's working. You only need to train for 1 epoch.
reply
Reply
add_reaction
React
So_Good_Person
Posted 10 days ago
· 2307th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
rank: 32, lr: 2e-4
reply
Reply
add_reaction
React

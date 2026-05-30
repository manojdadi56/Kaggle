# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685710
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3804

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
leaderboard score barrier of 0.87
Issue running NVIDIA Nemotron model on Kaggle (mamba_ssm import error)
Nemotron only for submission ?
DeepSeek Math 7B LoRA fine-tuning — dependency issues on Kaggle environment
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
DONALD GALLIANO III · 2831ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
-6
arrow_drop_down
more_vert
Compute partner needed - deterministic solvers for all puzzle categories built, budget-constrained
I've spent the last two weeks reverse-engineering all 8 puzzle categories in this benchmark.
I have:
Working factories that generate unlimited verified training samples for every category Structured reasoning traces (not naive SFT) with Python-verified ground truth Full understanding of the binary boolean decomposition, cipher substitutions, symbol transforms, digit pairings, gravity/roman/unitconv formulas A 50k sample synthetic dataset ready to train on Correct chat template, sensitive layer targeting, and training pipeline ready to execute
I haven't been able to run a clean training job yet. The Kaggle RTX 6000 environment has been broken for the entirety of this competition, and I don't have the budget for cloud GPUs to iterate.
What I need: a partner with GPU access willing to run training jobs. The data pipeline, problem analysis, and training scripts are complete.
DM me if interested. Targeting April 9 midpoint.
add_reaction
React
5 Comments
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
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
What the hell, you have so many public notebooks, that show u how to do sft. Environment isnt really broken just fork a notebook.
reply
Reply
add_reaction
React
Donald Galliano III
TOPIC AUTHOR
Posted 2 months ago
· 2831st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I’ve forked and run multiple notebooks. The environment issues with mamba_ssm, causal_conv1d, and ptxas on the RTX 6000 are well-documented across several threads here, including my own post from 9 days ago that got staff acknowledgment. The recent Docker update helped but didn’t fully resolve things (cutlass still missing, mamba_ssm still needs workarounds). My constraint is compute budget, not knowledge. Looking for a partner, not a tutorial.
reply
Reply
add_reaction
React
This comment has been deleted.
Donald Galliano III
TOPIC AUTHOR
Posted 2 months ago
· 2831st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yes, I have all categories covered including transformations (100% solved). Happy to share details in DM when I get off work tonight!
reply
Reply
add_reaction
React
This comment has been deleted.

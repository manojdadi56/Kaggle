# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/700197
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3312

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
Official Scoring Metric Code were not set to be Deterministic
ImportError: mamba-ssm is required by the Mamba model but cannot be imported
ModuleNotFound Error for mamba-ssm
RL/GRPO difficulty
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
KAICHENGYU517517 · 1873RD IN THIS COMPETITION · POSTED 13 DAYS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
Question about training data selection
Hi, trying to replicate Tong's winning approach and have a question about training data selection.
I can reach 0.81 training on all 9500 examples where the deterministic solver produce a reasoning trace (correct or not) for each problem. The winning run (04-08-16-14) used 7,830 examples —after digging into the artifacts I found this breaks down as 6,171 distinct competition problems + 1,659 exact duplicates (with -d/-p suffixes) to up-weight harder examples.
My questions:
How were the 6,171 distinct problems selected? Was it simply all rule_found at that time?
What determined which problems to duplicate and how many times? min_logprob from a prior run? Category balance?
Trying to understand the gap between 0.81 and 0.85 — any insight appreciated.
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
Tong Hui Kang
Posted 13 days ago
· 1173rd in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
How were the 6,171 distinct problems selected?
This means that I do not use all solvable problems in training. The idea is that I do not want to train on sequences that would have been already well-trained if I train on other sequences.
By well-trained I mean the min-logprob is close to zero. This means that the model with the trained adapter is already capable of generating the whole sequence verbatim even without training on that sequence in particular.
What determined which problems to duplicate and how many times?
If the min logprob has not apporach zero by the end of training I would increase the number of times I repeat the problem category.
However, I do not repeat all problems in the category, only the more difficult sequences. The more difficult sequences are sequences where the min logprob is not close to zero by the end of the training.
reply
Reply
2
add_reaction

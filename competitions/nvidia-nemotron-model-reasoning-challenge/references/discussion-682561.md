# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682561
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2215

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
When should winners publish their public notebook and writeup?
How to break 0.86 ceiling
The Rise of "Brain Rot" Submissions in Nemotron Challenge (Updated Daily)
causal_conv1d_cuda not compiled for Blackwell SM120 - training impossible
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
MD MUSHFIRAT MOHAIMIN · 2475TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
7
arrow_drop_down
more_vert
Inconsistency in Evaluation metric
In the Evaluation section of overview page, the parameters mentioned are:
max_tokens = 7680
max_num_seqs = 64
max_model_len = 8192
But, in the evaluation metric notebook (https://www.kaggle.com/code/metric/nvidia-nemotron-metric), the score function is defined with the following default parameters:
max_tokens = 3584
max_num_seqs = 128
max_model_len = 4096
So, which one is actually being used during evaluation?
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
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
3
arrow_drop_down
more_vert
The parameters on the Evaluation page override the default parameters.
reply
Reply
add_reaction
React

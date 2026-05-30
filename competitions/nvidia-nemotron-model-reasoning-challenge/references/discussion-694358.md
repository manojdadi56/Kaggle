# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694358
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2738

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
About Evaluation metric raised an unexpected error
Cloud Server Environment Setup Issues
Clarification on using Synthetic CoT from proprietary Teacher Models (e.g., GPT-5 family) for distillation
Is ~2 tokens/sec normal for Nemotron-30B on Kaggle?
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
BORIS POLISHCHUK · 2544TH IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Cannot install unsloth on the GPU RTX Pro 6000 notebook
Hello!
I cannot install unsloth when running new Kaggle notebook GPU RTX Pro 6000. It looks like internet is off, but in fact it's on. When I set accelerator to None in Session options, everything is fine, pip install works.
Do anybody has a chance to run RL training with the one of NVIDIA frameworks like Unsloth in the Kaggle notebook with GPU? Could you please share your settings?
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
dz
Posted a month ago
· 109th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
This is due to the limitations of the Kaggle GPU environment for this competition. In a GPU session, external network access, such as pip install, is disabled, so dependencies cannot be installed online.
Therefore, the dependencies need to be installed offline, for example by uploading the required packages to a Kaggle Dataset.
You can refer to my notebook, where I used Unsloth to complete SFT training.
reply
Reply
add_reaction
React
Boris Polishchuk
TOPIC AUTHOR
Posted a month ago
· 2544th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks a lot! That's what I need.
reply
Reply
add_reaction
React

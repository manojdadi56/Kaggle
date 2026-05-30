# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/702473
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2939

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
PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell'
How to successfully submit file for competition without error?
Struggling with Nemotron training stability in local H20 (Loss stagnation & exploding grad_norm）
Is DoRA allowed does it actually improve LB scores?
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
FYRIAN_MIGU · 332ND IN THIS COMPETITION · POSTED 6 DAYS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Clarification on Final Evaluation Settings
Hi, I noticed that the validation settings shown in the challenge overview seem to differ from the settings used in the evaluation metric notebook.
In the challenge overview, the validation description lists the following settings:
Parameter Value
max_lora_rank 32
max_tokens 7680
top_p 1.0
temperature 0.0
max_num_seqs 64
gpu_memory_utilization 0.85
max_model_len 8192
However, in the evaluation metric notebook, the settings appear to be:
Parameter Value
max_lora_rank 32
max_tokens 3584
top_p 1.0
temperature 1.0
max_num_seqs 128
gpu_memory_utilization 0.85
max_model_len 4096
Which of these two configurations is used for the final evaluation?
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
Tong Hui Kang
Posted 6 days ago
· 1173rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
This is why, in internal code reviews, if a parameter is effectively always passed the same value, I ask colleagues to either drop the default value or remove the parameter altogether.
reply
Reply
add_reaction
React
Manish Swami
Posted 6 days ago
· 146th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
check out
https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687798
reply
Reply
add_reaction
React

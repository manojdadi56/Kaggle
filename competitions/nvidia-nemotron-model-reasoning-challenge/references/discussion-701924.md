# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/701924
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3116

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
GRPO Traning guide needed
Just one Question on reasoning
0.60 using only SFT on Bit manipulation question.
Clarification on Final Evaluation Settings
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
SAMEER164 · 2125TH IN THIS COMPETITION · POSTED 10 DAYS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
[Bug or Expected?] Issue in Eval code
Hi, say for a gravity problem, the answer is 10, but the model outputs 10.00, this will be wrongfully categorized as a False output. If the intention was to allow answer within 10^-2 accuracy this shouldnt happen ?
Can someone answer if this is expected and if so why?
I would say this is a bug because this behavior is asymmetric, if the answer was 10.00 but the model outputs 10, it is categorized as True.
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
JK-Piece
Posted 9 days ago
· 8th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I expect the metric to work for the two cases (when ground truth is 10.00, 10 should be accepted, and when ground truth is 10, 10.00 should be accepted). Did you notice that it does not work with the current evaluation metric?
reply
Reply
add_reaction
React
Tong Hui Kang
Posted 9 days ago
· 1173rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I thought the ground truth for these problems would have the decimals, for example https://nemotron.huikang.dev/synthetic.html?problem=778ea123
reply
Reply
add_reaction
React
Sameer164
TOPIC AUTHOR
Posted 9 days ago
· 2125th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
In the training examples , for example the training row id: 0bcffccd, the answer is 10, so if my trace returned 10.00, running the nvidia metric code would classify that as incorrect.
But if the real eval sets will have 10.00 as gt then its not a problem.
The metric code checks if the answer has only 1 and 0, and if so falls to string matching whic causes this problem when using a portion of train set as validation
reply
Reply
add_reaction
React

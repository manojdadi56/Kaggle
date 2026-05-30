# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686419
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4258

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
Submission re-runs give different scores
Are all symbolic puzzles guaranteed to be uniquely solvable? Some seem to lack enough information
ModuleNotFoundError: No module named 'cutlass'
Unlock 15 or 30 extra GPU hours per week (connect Colab Pro)
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
FORCEWITHME · 1ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
10
arrow_drop_down
more_vert
Train locally and get lower scores.
I trained models with all 9500 samples with/without cot on my local machine. Upload the lora weight to kagge dataset, and submit with the following code:
import os
os.chdir('kaggle_lora_path')
!zip -r /kaggle/working/submission.zip ./*
No mater with/without cot, no matter how many iterations, the score is always lower than 0.6. I noticed that public notebook easily score 0.6x with 600 samples. My score doesn't make any sense! Has anyone faced the same issues and know the reason?
I just joined this competition two days before, don't downvote me!🤣
add_reaction
React
6 Comments
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
datnt114
Posted 2 months ago
· 94th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
same for me, I rent GPU in vast.ai and train 12h for 4 submit best submit 0.63 :( I think I should double-check the data and use Kaggle's GPU to save money.
reply
Reply
add_reaction
React
ForcewithMe
TOPIC AUTHOR
Posted 2 months ago
· 1st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
What is the score if yo use kaggle gpu to train?
reply
Reply
add_reaction
React
ForcewithMe
TOPIC AUTHOR
Posted 2 months ago
· 1st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
It's terrible… Sampling 600 data is much better than 9500 data.
reply
Reply
add_reaction
React
QianYuu
Posted 2 months ago
· 605th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
I encountered the same problem: 0.62 for 9500 data points, 0.67 for 600 data points, and 0.66 for 1200 data points.🥹
reply
Reply
1
add_reaction
MD Mushfirat Mohaimin
Posted 2 months ago
· 2475th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
maybe the distribution of those 600 samples was somehow close to the distribution of the LB test data?
Did you try a different random seed for selecting those 600 samples?
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
Noizersam
Posted 2 months ago
· 355th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Based on my own experience, a larger sample size is not necessarily better, nor is a longer CoT. I am currently still experimenting to determine which specific settings yield the best results. My hypothesis is that this is due to significant distributional shifts between the training and test sets, as well as the presence of noisy data—such as problems that have no valid solution😅
reply
Reply
add_reaction
React
HaoKwok
Posted 2 months ago
· 2671st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Yes, fine-tuning for 1 epoch with my own dataset of ~4,800 CoT samples resulted in a score of 0.26, whereas using ~3,500 CoT samples for ~0.60 epochs yielded a score of 0.52.
reply
Reply
add_reaction
React

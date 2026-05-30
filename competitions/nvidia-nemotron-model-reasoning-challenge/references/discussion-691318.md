# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/691318
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3878

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
corrupted or puzzel (numeric equations)
2 interpretations of the bit manipulation problem
Google Colab Pro not available in my country
Submission taking too long?
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
SVANIK KOLLI · 141ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Why are we seeing 0.84 – 0.86 score variance with the 0.85 winning zip?
I’ve noticed that when running Tong Hui Kang’s winning 0.85 submission zip, different people are reporting scores ranging from 0.84 to 0.86. Since the solution uses a temperature of 0.0 and a deterministic chain-of-thought, shouldn't the results be identical?
I’m curious if anyone has identified the cause of this drift. Is it due to:
Hardware differences (T4x2 vs Geforce RTX 6000 Pro) affecting floating-point operations?
Discrepancies in vLLM versions or library environments?
Slight misalignments between the original Tinker training and the Kaggle inference setup?
Has anyone managed to consistently hit the 0.86 mark, and if so, did you make any environment tweaks to get there?
add_reaction
React
4 Comments
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
hongan
Posted 2 months ago
· 55th in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
LLM inference are not deterministic even if temp = 0
reply
Reply
add_reaction
React
Chan Kha Vu
Posted a month ago
· 692nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
As someone mentioned earlier, LLM inference is NOT deterministic, even with temp=0.0, hence the difference. Relevant blogs:
Defeating Nondeterminism in LLM Inference: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
SGLang supports deterministic inference: https://www.lmsys.org/blog/2025-09-22-sglang-deterministic/
@ryanholbrook any chance the competition metric can be made deterministic?
reply
Reply
1
add_reaction
Ogurtsov
Posted 2 months ago
· 730th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Since the solution uses a temperature of 0.0
https://www.kaggle.com/code/metric/nvidia-nemotron-metric temperature: float = 1.0,
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
That is the default value, not the value the metric actually uses. See the Evaluation page for the actual values.
reply
Reply
add_reaction
React
Ogurtsov
Posted 2 months ago
· 730th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yes, I got it, but did you double-check actual evaluation value? Temperature erroneously set to 1 could be very likely explanation of the run-to-run LB score variability. Otherwise we have a bad news if result is non-deterministic to such extent.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687740
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3544

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
ImportError: mamba-ssm is required by the Mamba model but cannot be imported
ModuleNotFound Error for mamba-ssm
RL/GRPO difficulty
Queued for hours for the first time!
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
CHEW KOK WAH · 82ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
Official Scoring Metric Code were not set to be Deterministic
I check the scoring Metric and found that there is no per request seed and Batch Invariance setting for VLLM, this make the scoring metric non-deterministic, please @ryanholbrook @cpmpml make it more deterministic before the rescore.
The above setting had been experimentally proven to 100% guarantee deterministic output.
If it is too expensive to rescore, can you enable the setting after the 9 April Midpoint award date? By then, all participants score will be very near, a non-deterministic score will make this Competition into a LOTTERY game.
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
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
Hi @chewkokwahibrainai,
We have investigated the possibility of deterministic scoring in vLLM. Unfortunately, it appears that this will lead to a significant throughput drop on the order of 35% to 55%. With our current stock of GPUs, this would lead to significant queueing. As such, we will not be changing the metric.
Also, it's worth noting that determinism in vLLM doesn't solve the problem of order variance in the questions. Scores on the private test set are still subject to order variance, it's just that the order is the same for all submissions. You still have no way of knowing which submission was "lucky" and got a higher score on the private lb by chance.
reply
Reply
add_reaction
React
Ertuğrul Demir
Posted 2 months ago
· 32nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for clarifying. Could you share the rough magnitude of the score variance you’ve seen from order effects in practice? It would help us understand how noisy the scores may be.
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
@datafan07 I'm afraid I don't have a good estimate. I've seen some discussion about it though, and just observing your own submission variance on train CV or the public LB could be informative too, of course.
reply
Reply
add_reaction
React

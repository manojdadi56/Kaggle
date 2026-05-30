# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685920
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5380

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
RTX PRO 6000 Blackwell — CUDA kernel incompatibility status + GPU time spent debugging
Edge case in metric: \boxed{} cannot contain }
Competition Metric Bug: verify method fails for Binary String Problem (?)
Pip install with internet disabled: install dependencies feature
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
JK-PIECE · 8TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
17
arrow_drop_down
more_vert
Something wrong -- My notebook of 0.80+ now scores 0.77
Did anyone else notice a decrease in their score?
My previous notebook with score 0.80+ now scores 0.77
Can the hosts provide any insights here?
add_reaction
React
8 Comments
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
7
arrow_drop_down
more_vert
Thanks, @jeannkouagou. I am looking into a rescore. Since this requires the RTX GPUs, I need to ensure we still have availability for ordinary scoring.
reply
Reply
add_reaction
React
MD Mushfirat Mohaimin
Posted 2 months ago
· 2475th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
From my observation, I believe the evaluation is not running with temperature=0
Can you please update the default parameter of temperature to 0 in the evaluation notebook? Right now, it is set to 1.0
Each submission is currently returning different scores. Because of this, we have to submit our solution multiple times just to get back the maximum score.
reply
Reply
add_reaction
React
JK-Piece
TOPIC AUTHOR
Posted 2 months ago
· 8th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Yes, this is true. The temperature value is now 1.0 instead of the initial 0.0 . @ryanholbrook could you please also fix this?
reply
Reply
add_reaction
React
14 more replies
arrow_drop_down
+5
Chew Kok Wah
Posted 2 months ago
· 82nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
In your scoring Metric code there is no per request seed set, this make the score non-deterministic and keep on changing even with no code change. Can you set the seed to make the score more deterministic? @ryanholbrook
reply
Reply
add_reaction
React
bliao
Posted 2 months ago
· 2142nd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
The verify function (https://www.kaggle.com/code/metric/nvidia-nemotron-metric) is changed. See discussion at https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683853
reply
Reply
add_reaction
React
Tong Hui Kang
Posted 2 months ago
· 1173rd in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
I note that this part was added
# If the answer is a binary string, compare strictly as strings
if re.fullmatch(r"[01]+", stored_answer):
return predicted.lower() == stored_answer.lower()
If this is indeed the case, I think we should rescore (just rescore, not rerun) the leaderboard
reply
Reply
add_reaction
React
bliao
Posted 2 months ago
· 2142nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
agree to rescore the LB, since the metric is different. In addition, the same notebook gets different scores, although temp=0. There might be some issues about deterministic.
reply
Reply
add_reaction
React
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
I dont think its needed, since scores will improve and rescoring will be naturally done. I doubt top scores will stay this low. Iam about to publish comprahensivve dataset for bit problems, with very good traces.
Iam currently running vllm inference with gpt oss 120B, so I hope to share my dataset today. Lets see what others think.
reply
Reply
add_reaction
React
pranavpoduval
Posted 2 months ago
· 1925th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Yah everyones score fell by 0.03-0.04 approx. likely due to the evaluation change
reply
Reply
add_reaction
React
muyouqian4
Posted 2 months ago
· 1862nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Wow, thanks! I resubmit my best submission.csv, 0.82 -> 0.8
reply
Reply
add_reaction
React
datnt114
Posted 2 months ago
· 94th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I also tried resubmitting the best model in kernel public, but it only achieved 0.64.
reply
Reply
add_reaction
React

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/699811
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4202

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
Unable to load Nemotron-3-Nano-30B-A3B-BF16 due to mamba_ssm dependency (No Internet Environment)
Is ~0.86 a current ceiling for most approaches?
How is leaderboard rank decided on same score
Midpoint Leaderboard Clarification + Open Contribution Award Question
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
PENGUIN · 74TH IN THIS COMPETITION · POSTED 15 DAYS AGO
arrow_drop_up
3
arrow_drop_down
more_vert
Is the model not good at mathematics at all, is the model dumb or am i missing something?
Check these reasoning traces out:
Here the correct ans was just 9
d = 4.591 * 1.96:
4.591 * 0.06 = 0.27546
4.591 * 0.90 = 4.13190
4.591 * 1.00 = 4.59100
0.27546 + 4.13190 = 4.40736
4.40736 + 4.59100 = 9. --------------------------------------------------------------------- 9.99836
= 9.998
I will now return the answer in \boxed{}
The answer in \boxed{–} is \boxed{9.998}
\boxed{9.998}",9.998,False
Here the correct ans was 138.45
d = 9.34 * 14.8225:
9.34 * 0.0005 = 0.004670
9.34 * 0.0020 = 0.018680
9.34 * 0.0200 = 0.186800
9.34 * 0.8000 = 7.472000
9.34 * 4.0000 = 37.360000
9.34 * 10.0000 = 93.400000
0.004670 + 0.018680 = 0.023350
0.023350 + 0.186800 = 0.210150
0.210150 + 7.472000 = 7.682150
7.682150 + 37.360000 = 45.042150
45.042150 + 93.400000 = 148.442150
= 148.442
I will now return the answer in \boxed{} The answer in \boxed{–} is \boxed{148.442}
\boxed{148.442}",148.442,False
Could have gotten both of them correct, if the model knew basic maths ig? Or maybe my 1 epoch of training made the model forget how to do basic maths
add_reaction
React
3 Comments
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
Posted 14 days ago
· 1173rd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
You can see from the highly negative logprob tokens on where the mistakes are happening - https://nemotron.huikang.dev/training.html?logpath=04-10-04-33&category=gravity&problem=e32c84ec
One thing I tried to get the model to break down the addition further, instead of doing addition all at once, do addition digit by digit and note all the carryovers. For some reason, it did not improve performance.
A way to remedy this, which I have not tried, is to train the model to recover from mistakes.
reply
Reply
add_reaction
React
Penguin
TOPIC AUTHOR
Posted 14 days ago
· 74th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
What about these types of questions:
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
46%21 = 67
44%79 = 123
96(33 = 3169
75(40 = 3001
Now, determine the result for: 70/51
Answer: /19
How should the model know that it should put a '/' before 19?
Are these intended?
reply
Reply
add_reaction
React
jane96
Posted 16 hours ago
· 1157th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@huikang Could you please advise: Is it possible that the model is getting confused due to too many CoT examples? If I use fewer examples to solve for gravity—for instance, just one example, since gravity should be consistent—would that help avoid this issue?
reply
Reply
add_reaction
React

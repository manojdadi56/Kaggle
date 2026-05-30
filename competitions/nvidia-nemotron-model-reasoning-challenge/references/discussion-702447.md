# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/702447
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4138

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
The Rise of "Brain Rot" Submissions in Nemotron Challenge (Updated Daily)
causal_conv1d_cuda not compiled for Blackwell SM120 - training impossible
[BUG] Utility script permission error
Fix ModuleNotFoundError for cutlass
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
BOBBER CHENG · 159TH IN THIS COMPETITION · POSTED 6 DAYS AGO
arrow_drop_up
7
arrow_drop_down
more_vert
How to break 0.86 ceiling
Hi guys, in last week I tried to scale up my best 0.86 solution by following:
use 20K+ synthetic binary puzzles and other categories, still 0.86.
grpo from SFT, still 0.86, no increase no decrease.
different CoT format than Huikang's one. decrease or no increase. The 0.86 model now does very good job for memory but still has lots of improvement space for unseen held data. I also found if you made multiple submissions with the same lora in same time, you may get different LB score but 0.86 is the ceiling.
I'm very curious why more synthetic data and grpo cannot improve accuracy for held data. What are possible traps here? I'm happy to share my receipts here as same 0.86 for 6 submissions with different experiences means I'm wrong with something for sure.
BTW, I use tinker cloud for both SFT and grpo as kaggle notebook cannot handle large training data, but I use Kaggle notebook for full eval(2 hours each eval).
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
Bobber Cheng
TOPIC AUTHOR
Posted 6 days ago
· 159th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Here is my Kaggle notebook of my 0.86 tinker replicate, https://www.kaggle.com/code/bobber/vex506-reinst-kaggle-replica?scriptVersionId=320585244
reply
Reply
add_reaction
React
jane96
Posted 15 hours ago
· 1157th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
could you make your data construction method public?
reply
Reply
add_reaction
React
Manoj Mangam
Posted 6 days ago
· 1295th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The evals on 9500 questions take me around 5 hours using RTX pro 6000. How come 2 hours ?
reply
Reply
add_reaction
React
Bobber Cheng
TOPIC AUTHOR
Posted 6 days ago
· 159th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Here is my Kaggle eval notebook, https://www.kaggle.com/code/bobber/vex-eval-vex506-reinst
reply
Reply
add_reaction
React
Manoj Mangam
Posted 4 days ago
· 1295th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thanks Bobber! The notebook isn't opening.
reply
Reply
add_reaction
React
Gaofeng Huang
Posted 6 days ago
· 2552nd in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
Maybe the hard problems exist beyond Alice’s Wonderland…
reply
Reply
add_reaction
React
Rustam Bazarbayev
Posted 5 days ago
· 1393rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
How did you generate binary puzzles or synthetic data? Maybe Duplicate / generic CoT traces – the model saw identical reasoning for different questions, so it learned to ignore the reasoning and guess
reply
Reply
add_reaction
React

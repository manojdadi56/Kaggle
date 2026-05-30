# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683401
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4181

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
Использовать определенный accelerate через kaggle api
Why people downvote?
Is it difficult to improve your score in this competition?
Just noticed I'm in the golden zone — and I know almost nothing about this competition
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
LUCIAN KUCERA · 2171ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
-17
arrow_drop_down
more_vert
Ground Breaking Discovery regarding SFT[MUST WATCH]
I created this notebook, that shows few example of outputs after applying Naive SFT. It absolutelly kills models reasoning and makes it dumb as rocks. notebook
Please don't give me dislikes, if u do please share your reason, beacause disliking without reasoning is not constructive.
Iam getting review bombed for telling the truth pls give me upvote, so we can counter reviewbombing.
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
ImperfectKitto
Posted 2 months ago
· 608th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Don't know about others, but I gave you dislike just for the clickbaity title
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1451st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I am just starting the competition so I am not familiar with the data yet. But, SFT as I know definitely can hurt if not configured properly. It is better suited for tasks that does not require unpredictable steps, and hence not reasoning task at least. It can suite the objectives like aligning a LLM to be nice, or tuning its output for a certain style for example. Reasoning can take very different turns at each step, so RL works better because it cares about the outputs and not the path. SFT still might work if one takes a huge model, like opus, and save its reasoning, and then train this smaller model to do reasoning like it. But simply applying it on dataset provided, can hence kill the performance. I am quite sure top rankers that are already way beyond the reach of highest scoring public notebook are definitely using RL methods like GRPO. Please let me know if you think my reasoning is right.
reply
Reply
add_reaction
React
NNMax
Posted 2 months ago
· 1184th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
after applying Naive SFT
The reason's in your post itself. For this kind of reasoning task, naive SFT barely works and there's a lot of methods out there for LoRA SFT itself. Have you experimented with adjusting hyperparameters first?
I'm seeing a massive difference in tuning the hyperparameters itself and there's still a lot of other things to explore like finetuning methods, two-stage approaches, LoRA rank vs alpha tradeoff tuning and much more.
reply
Reply
add_reaction
React
lucian kucera
TOPIC AUTHOR
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Bro most people are trying naive SFT, so iam trying to help them to stop. Since it is a dead end. Look at most notebooks, with lot of upvotes, all of them use naive SFT. My message is to stop doing it.
reply
Reply
add_reaction
React

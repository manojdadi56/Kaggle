# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/692950
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5120

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
How is leaderboard rank decided on same score
Midpoint Leaderboard Clarification + Open Contribution Award Question
BlackWell Kaggle Internet Issue
How do you get the GPU resources for this Competition?
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
emoji_people
TAHA · 421ST IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
3
arrow_drop_down
more_vert
Is ~0.86 a current ceiling for most approaches?
I’ve been experimenting quite a bit with the Nemotron reasoning setup over the past few days, and I’m starting to feel like many of us might be hitting a similar ceiling around ~0.86.
From what I can tell, a lot of current approaches seem to fall into two buckets:
building directly on top of strong public notebooks (which already reach ~0.86), or
trying to reproduce / adapt methods like Tong Hui Kang’s pipeline
I’ve personally tried a mix of things on top of that:
different LoRA variants (including DoRA)
some knowledge distillation setups
hybrid synthetic + distilled data
prompt / formatting tweaks
But so far, nothing has meaningfully pushed me past that same range.
Right now I even have a long run going (~14 hours in), trying a slightly different data pipeline, but I’m not super confident it’ll break through.
So I wanted to ask: Do you think this plateau is mostly coming from model capacity (LoRA rank limits), data quality, or something else entirely?
Also curious if anyone has seen actual gains from:
distillation-heavy approaches
more structured synthetic CoT pipelines
or anything outside the usual playbook
If I do manage to get something working beyond this range, I’ll update this thread with details.
Would be great to hear what others are seeing as well.
It feels like people have stopped being creative after Tong Hui Kang’s discussion most are either reproducing it or fixing small issues, and nothing really new is emerging. I do agree that his method is key, and I’m grateful for the breakthrough.
Also, Kaggle’s 30-hour quota seems to be another limiting factor for experimentation. I’ve personally been working around this using Tinker and Modal.
Just to be clear, no criticism intended toward anyone this is just an observation based on what I’ve been seeing.
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
MAJ0RT0M
Posted a month ago
· 1779th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
I think Tong laid out a few areas for improvement w/ his method
e2e fine tuning to recover mamba weights dropped by SVD when converting from tinker (or training w/o using tinker at all)
training on tokens to avoid tokenization issues
producing an algorithm for cryptarithm that fits w/in COT budget
generating problems to then produce synthetic COT and train on those
Ive seen some public notebooks doing (1) - which I guess probably makes up the bulk of people currently scoring 0.86
But I haven't see anyone publicly doing any of (2),(3),(4)
My opinion is that Tong has the right idea - training the model to replicate optimal COTs that fit w/in the token budget is better than using distilled data or RL - so that what I've been focusing on
If someone could solve a single substitution cipher w/in the token budget they could achieve 15-20% on cryptarithm problems - which is 2-3% and would get them to 0.87-8.89 depending on their starting score. If you see people starting to hit those scores thats my guess on what they are doing
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted a month ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
i have been doing all of them you mentioned
reply
Reply
add_reaction
React
MAJ0RT0M
Posted a month ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Were you able to benchmark these methods against eachother?
I'm surprised you haven't seen good results producing a COT for cryptarithm
How does training on tokens compare to e2e fine tuning?
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
This comment has been deleted.

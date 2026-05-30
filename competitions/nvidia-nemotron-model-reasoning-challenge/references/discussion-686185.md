# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686185
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4169

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
Submission Type and Time
Score 0.87 started queuing at the top of leaderboard
infra speed
Is the model not good at mathematics at all, is the model dumb or am i missing something?
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
CS MAJOR · 2044TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
2
arrow_drop_down
more_vert
Seemingly Impossible Questions in Dataset?
Was looking through some of the questions where my CoT generating code failed (mostly in the symbolic algebra question types) and I noticed a few questions such as the following:
"In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples: 34/44 = 1 41/32 = 9 34|25 = 69 87\64 = 8853 Now, determine the result for: 69/52" and the solution is "17/"
and
"In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples: 45^08 = 0234 37}95 = 131 99^88 = 2178 Now, determine the result for: 52}51" and the solution is "93"
Is this just a dataset quality issue or am I missing something? I got a higher score (0.7) leaving these unsolved examples in compared to excluding them (0.63) so I'm not too sure honestly.
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
Kh0a
Posted 2 months ago
· 5th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
the puzzles are very rule-consistent. "/" appeared since is it defined as negative sign.
69/52 = rev(rev(52) - rev(69)) = rev(25 - 96) = rev(-71) = 17- => 17/
52}51 = rev(rev(52) + rev(51) - 1) = rev(25 + 15 -1) = rev(39) = 93
reply
Reply
add_reaction
React
KG
Posted 10 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
may i ask what approach did u follow to generate CoT for ur dataset? and is there any CoT that contains guesses? like mine contains "Guessing the answer would be 17/ and not 17"
reply
Reply
add_reaction
React
CS Major
TOPIC AUTHOR
Posted 2 months ago
· 2044th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
If it helps, this is the log for success/failure
bit_manipulation: 842 success, 760 failed (52.6% success)
gravity_physics: 1590 success, 7 failed (99.6% success)
numeral_conversion: 1576 success, 0 failed (100.0% success)
symbolic_algebra: 1004 success, 551 failed (64.6% success)
text_encryption: 1576 success, 0 failed (100.0% success)
unit_conversion: 1593 success, 1 failed (99.9% success)
reply
Reply
add_reaction
React
akshit manocha
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
this is for the brute force? or was your fine tuned model able to solve this?
reply
Reply
add_reaction
React
CS Major
TOPIC AUTHOR
Posted 2 months ago
· 2044th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
This was produced by my deterministic CoT generating code. I haven’t actually tested my model against a validation set yet (probably not best practice) but once my solver is strong enough I’m planning on using that to produce synthetic example’s following the same logic in the provided set and train + validate on that.
reply
Reply
add_reaction
React

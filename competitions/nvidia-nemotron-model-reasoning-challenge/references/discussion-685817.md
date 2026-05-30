# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685817
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3175

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
Are all symbolic puzzles guaranteed to be uniquely solvable? Some seem to lack enough information
ModuleNotFoundError: No module named 'cutlass'
Unlock 15 or 30 extra GPU hours per week (connect Colab Pro)
Runtime Limits During Evaluation? (CPU/GPU Constraints)
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
MD MUSHFIRAT MOHAIMIN · 2475TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
11
arrow_drop_down
more_vert
Submission re-runs give different scores
I submitted the same submission.zip multiple times, and got different scores.
As per comments in other threads, many other participants can also observe this.
This is only possible if the temperature parameter during evaluation is something other than 0. In the evaluation section of the competition overview, it's written that temparature is supposed to be 0. Perhaps, there's a mistake in the evaluation code? It's possible because the default value of temparature is set to 1.0 in the evaluation metric notebook.
@ryanholbrook can you please look into this? Can you please make sure that the evaluation code is correctly overriding the function's default temperature parameter?
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
MD Mushfirat Mohaimin
TOPIC AUTHOR
Posted 2 months ago
· 2475th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I used the code from the evaluation metric notebook, and tried to do inference using temperature=1.0 and temperature=0
Using temperature=1.0 gives much lower accuracy compared to temparature=0
And the accuracy spread with temperature=1.0 is comparable to what's happening with the public LB
I'm getting more confident that evaluation runs are using temperature=1.0 instead of 0
@ryanholbrook plz investigate
reply
Reply
add_reaction
React
This comment has been deleted.
MD Mushfirat Mohaimin
TOPIC AUTHOR
Posted 2 months ago
· 2475th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
are you sure? can you plz let me know the source behind that info?
reply
Reply
add_reaction
React
This comment has been deleted.

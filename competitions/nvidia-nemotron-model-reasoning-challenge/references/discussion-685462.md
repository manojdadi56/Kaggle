# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685462
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2003

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
Eligibility for participants under 18
Hallucination in equation problems?
How many examples are there in the public leaderboard?
Does increasing token limit actually help? [SPOILER=IT DOESN'T] How do we solve this?[SPOILER=SFT and RL]
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
ASKDKJANFKQF · 2372ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
4
arrow_drop_down
more_vert
Default parameters mismatch
In the NVIDIA Nemotron Metric notebook, the scoring function is defined to be:
def score( ... max_tokens: int = 3584, top_p: float = 1.0, temperature: float = 1.0, max_num_seqs: int = 128, ... ) -> float:
Just want to make sure, are we using the parameters in the overview? This is the metric in the overview section which I believe makes more sense:
max_tokens= 7680, temperature = 0.0,max_num_seqs: int = 64
add_reaction
React
0 Comments
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

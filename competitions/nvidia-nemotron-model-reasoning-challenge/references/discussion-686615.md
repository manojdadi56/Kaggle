# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686615
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2715

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
Equation Symbolic has anyone figured out the pattern?
[Potential problem] Eval regex cannot parse answers starting with character"}"
sharing high quality synthetic data generation prompt
Unit testing model on simple bit transformations
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
ASHUTOSH KUMAR · 1901ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
8
arrow_drop_down
more_vert
BUG in Nemotron Model file://Models/modeling_nemotron_h.py
There's the bug in the model itself! Look at line 1659: "past_key_values": past_key_values,
But the .forward() method (line 1695) expects cache_params, NOT past_key_values: def forward(self, …, cache_params=None, …)
The prepare_inputs_for_generation returns {"past_key_values": cache} but forward() receives it as **kwargs — it gets lost! The cache is created but never used.
However, this is the model code on the HF Hub — it works in the competition evaluation because vLLM handles caching differently. The model file on the training server might be different.
The forward() has cache_params in its signature but prepare_inputs_for_generation passes past_key_values. Since forward() has args, the past_key_values goes into kwargs and is silently ignored. cache_params stays None.
This is a bug in NVIDIA's model code. The fix: patch forward() to extract past_key_values from kwargs and use it as cache_params
add_reaction
React
1 Comment
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
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
5
arrow_drop_down
more_vert
This bug is fixed in transformers library for versions 5.3.0+.
reply
Reply
4
3
1
add_reaction

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686794
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3813

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
Queued for hours for the first time!
Permission denied error for ptxas-blackwell
Fixed: Any fix for trl installation?
Exactly same "types" of the prompts?
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
DARREN AMADEUS MARTIN · 1882ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
RL/GRPO difficulty
Has anybody tried using RL techniques such as GRPO ? Since on RL, we basically need to hold 2 copies of the model, training in bf16 is absolutely impossible and training with quantized model can lower performance. I tried using unsloth where it said that you don't need 2 copies of the model to be loaded at the gpu at the same time but the debugging is super hard and is very prone to errors. Has anybody managed to do RL and if you had done it, how slow was it ?
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
vLLM + sleep mode worked for me
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
curious how were able to load your LORA adaptor in VLLM - getting this error: AssertionError: Module model.layers.0.mixer.conv1d must be a BaseLayerWithLoRA instance
reply
Reply
add_reaction
React
Darren Amadeus Martin
TOPIC AUTHOR
Posted 2 months ago
· 1882nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Would you mind explaining what sleep mode is ?
reply
Reply
add_reaction
React
5 more replies
arrow_drop_down
WillTLing
Posted 2 months ago
· 1262nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
unsloth not support fast_inference for Mamba hybrid models (https://github.com/unslothai/unsloth/issues/4073), so vLLM won’t work in unsloth. Also, since this model seem is no KV cache implemented under the transformers inference engine, the inference speed is painfully slow.
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Have you tried huggingface GRPO trainer? it supports the same VLLM + pytorch RAM sharing as unsloth (supposedly - haven't got it to work)
reply
Reply
add_reaction
React
Darren Amadeus Martin
TOPIC AUTHOR
Posted 2 months ago
· 1882nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Wait, huggingface GRPO trainer also support ram sharing like unsloth? I thought only unsloth does that
reply
Reply
add_reaction
React
This comment has been deleted.
MAJ0RT0M
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Ah no - I was mistaken - it doesnt
reply
Reply
add_reaction
React

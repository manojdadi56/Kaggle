# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/688120
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4467

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
Is anyone able to get inference/generation speeds >2 tokens/sec?
Large submission.zip can't be downloaded and Commit fails due to insufficient GPU memory
how to train unsloth multi gpu??
Kaggle Scoring
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
SAHIL PATIL · 3022ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Calling experienced fine-tuners: share LoRA / PEFT resources for newcomers in this challenge
Hi everyone,
A lot of participants here are new to LoRA/PEFT and training adapters. This comp’s setup-Nemotron base + LoRA zip submission + exact-match puzzle eval-is a concrete goal, but the learning curve is still steep without a good reading order and a few battle-tested patterns.
If you’ve fine-tuned LLMs before (especially LoRA on HF stacks, Kaggle GPUs, or similar reasoning/supervised setups), it would help a lot if you could pay it forward in this thread:
One or two resources you’d actually assign to a colleague (docs, posts, notebooks-not necessarily Nemotron-specific). Practical gotchas for this kind of task (OOM, LR, eval splits, answer formatting for strict match, exporting a clean adapter). Optional: a minimal “do this first, then this” path in a few bullets. If you’re newer, reply with where you’re stuck or your background-short answers from people who’ve done this before often save days of thrashing.
Let’s make this a curated resource pile for anyone who wants to learn fine-tuning through this competition. Thanks for sharing.
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
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
I can share few tips:
For example bit problems aren't determinsitc, I have prooven that such problems have infinite wrong solution. So you need to teach model test distribution of data. Which might be impossible task.
Generate high quality chain of thought data: You don't need 100k data, but high quality traces. For example model strugles with concept of Majority/Choice. It doesn't know they can be used to emulate NOR and NAND. So you prepare high quality data that aligns model, with knowladge of Choice making it possible to emulate NOR/NAND.
Equations are very difficult, but my guess is they are more deterministic, tho there is blatantly wrong data in train set. So maybe filtering could help.
Other problems seem to be easily trained.
So I would probably focus on equation problems.
For finuting best is to isolate tasks and try to improve model on one task. Use part of the training set for eval. Lets say u try to improve equations. U create lora only trained on COT data for equation and than use vllm for evaulation. If beats baseline ur data was good, otherwise your data sucks and u need reevaluate it.
Another use Muon optimizer: Its better for optimizing LORA, there are several papers on it.
Dont quantize weights.
Use unsloth, tho gains here are minimal, since both transformers and unsloth use mamba_ssm kernels
Use RLVR after sfting model over baseline. I saw huge boosts on bit problemss after 3 epochs of rlvr.
Dont waster ur time tuning hyperparametrs, untill u find good data. Rank=32 and all linear layers is good default.
Sfting over pair of values is trash: since it destroys model reasoning. So use coherent COT for training.
reply
Reply
7
add_reaction

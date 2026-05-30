# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/696993
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2730

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
Bit problems question for competion hosts.[COMPETITION HOST]
WHY is internet access banned if free GPU provided by competition is used?
RL and SFT Training Questions
Calling experienced fine-tuners: share LoRA / PEFT resources for newcomers in this challenge
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
ANJANA MOHAN · 2514TH IN THIS COMPETITION · POSTED 25 DAYS AGO
arrow_drop_up
-1
arrow_drop_down
more_vert
Feedback Needed: SFT on Deterministic Puzzles Dropping Score Below Baseline
Hi everyone, I’ve been working on fine-tuning Nemotron-3-Nano-30B with LoRA on the 4 deterministic puzzle types (gravity, numeral, unit_conversion, cipher) and experiencing score drops below baseline. My setup: • Base model score: 0.51 • Training data: 6,343 real train.csv examples with programmatically generated CoT traces • 100% solver accuracy on all 4 types locally • LoRA rank 16, 3 epochs, lr=2e-4 • Prompt format includes the competition suffix: Please put your final answer inside \boxed{} Results: • Attempt 1 (synthetic data, no suffix): 0.50 • Attempt 2 (real data + system prompt): 0.44 • Attempt 3 (real data + correct suffix, no system prompt): 0.31 My questions: 1. Is the reasoning trace format critical? Mine is very short (~234 tokens mean). Should it be longer? 2. Should the tags be included in the assistant response during training? 3. Is enable_thinking=True needed in the chat template? 4. Any advice on why training on correct examples causes score to drop? Thanks in advance! 🙏
@huikang and @donaldgalliano
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
This comment has been deleted.

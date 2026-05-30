# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682167
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3716

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
Why a "Better" Dataset Scored Worse: Lessons on Logprobs, Gradient Saturation, and SFT Bugs
Per-Category Error Analysis After SFT (0.63 LB) — Where the Real Bottlenecks Are
Zero shot predictions
Something wrong -- My notebook of 0.80+ now scores 0.77
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
C-NUMBER · POSTED 2 MONTHS AGO
arrow_drop_up
16
arrow_drop_down
more_vert
What is the minimum VRAM for training?
I tried training with unsloth using my RTX 5090, but failed due to OOM. Has anyone been able to train locally?
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
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
7
arrow_drop_down
more_vert
Bruh u have RTX PRO 6000 on kaggle, there is no point in using 5090. Kaggle GPU has 3 times the vram.
Model is in BF16 and has 30B params so simple math u need 60GB vram to load model. Than ofc when u train lora u add additional params + activations. Optimizer has copy of each trainable param so u double the params for lora.
IF u used 4bit precison for entire model u would need 15GB vram + vram for aditional params.
Also if u check Unsloth mentions requriements for qlora on their website. requirements
For 32B model it says for qlora u need 26GB vram, which should fit into 5090. So i guess u can use 4Bit qlora.
But i would strongly advise u agianst using qlora, u dont stand a chance in this competition if u lower precision.
In reasoning precision is exteremly important, low precision llm thinks like unwell person. Hope it helps. For ur own sake just use nvdia provided GPU.
You could try CPU offloading, sadly as fair as i know Unsloth doesn't support offloading natively, u would have to write code for it yourself or try to use Claude to write the code for it. Tho i expect it to be quite difficult task, if u decide to extend hugginface trainer, because of monkeypatching done by unsloth. Maybe writing ur own custom trainer would be the wisest choice in this case.(this is my guesscpu offloading issue)
reply
Reply
4
1
add_reaction
c-number
TOPIC AUTHOR
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
Thanks! I couldn't get QLoRA work, but maybe I did something wrong. It's always good if you can train every day, so I think I'll use QLoRA locally while training using bf16 on kaggle.
reply
Reply
add_reaction
React
Victor Merckle
Posted 2 months ago
· 1192nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The Lora adapter trained on a quantized model will have reduced performance or terrible performance when used on the BF16 model.
reply
Reply
add_reaction
React

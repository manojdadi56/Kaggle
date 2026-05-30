# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682877
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3274

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
Clarification needed: Experimenting with prompting strategies vs. strict sequence length constraints?
What is the minimum VRAM for training?
Why a "Better" Dataset Scored Worse: Lessons on Logprobs, Gradient Saturation, and SFT Bugs
Per-Category Error Analysis After SFT (0.63 LB) — Where the Real Bottlenecks Are
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
ANTON KRATZ · 3141ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
13
arrow_drop_down
more_vert
AcceleratorError: CUDA error: no kernel image is available for execution on the device; causal_conv1d; mamba_ssm
On Kaggle notebook runtime GPU RTX Pro 6000, fine-tuning metric/nemotron-3-nano-30b-a3b-bf16/transformers/default fails at trainer.train() with:
AcceleratorError: CUDA error: no kernel image is available for execution on the device
The actual failing call in the traceback is:
causal_conv1d_cuda.causal_conv1d_fwd(…)
from Kaggle’s preinstalled causal_conv1d / mamba_ssm path.
This looks like the CUDA extension was built without support for the assigned GPU architecture. Model load works; the crash starts on the first training forward pass.
I have made a public notebook documenting this: https://www.kaggle.com/code/antonkratz/nvidia-nemotron-finetune-ipynb
I already spent over 10 GPU hours on this issue.
Can you confirm whether the GPU RTX Pro 6000 runtime image is missing a compatible build of causal_conv1d / mamba_ssm for this competition?
Tricks like turning internet off/on and then trying to install did not work for me. This issue should be fixed in the base environment I think.
add_reaction
React
2 Comments
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
aemad
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
check this notebook> it applies a Triton ptxas fix https://www.kaggle.com/code/kienngx/nvidia-nemotron-training-copy-run-instantly
reply
Reply
add_reaction
React
Ashish Kumar Jha
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
I'm also facing the same issue and the fix for this issue is inprogress refer: https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683067, Thanks
reply
Reply
add_reaction
React

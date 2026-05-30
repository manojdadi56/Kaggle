# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682355
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4121

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
What is the minimum VRAM for training?
Why a "Better" Dataset Scored Worse: Lessons on Logprobs, Gradient Saturation, and SFT Bugs
Per-Category Error Analysis After SFT (0.63 LB) — Where the Real Bottlenecks Are
Zero shot predictions
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
KAMAL RAJ KANAKARAJAN · POSTED 2 MONTHS AGO
arrow_drop_up
14
arrow_drop_down
more_vert
Clarification needed: Experimenting with prompting strategies vs. strict sequence length constraints?
Hi,
I have a question regarding how we can experiment with prompting strategies given the fixed evaluation pipeline and some strict constraints on sequence length.
Model Sequence Length Constraints
Based on the submission demo and competition overview, we are working with very specific length limits:
Prompt Limit: The input prompt length is strictly capped at <512 tokens.
Total Max Length: The model's max_length is fixed at 8192.
Reasoning Overhead: This means the model's entire reasoning process, plus the final answer, must fit within the remaining token limit without us having the option to adjust the max_length.
The Evaluation Pipeline & Submission Format
Additionally, the inference pipeline is locked down:
The following string is automatically appended to all evaluation prompts: '\nPlease put your final answer inside \\boxed{}. For example: \\boxed{your answer}'
We are only submitting the LoRA adapter weights (adapter_config.json and adapter_model.safetensors).
My Question
Given that the inference/evaluation pipeline is locked and we are only submitting the adapters, what exactly is meant by "experimenting with prompting strategies"?
Since we cannot modify the prompt template used during the hidden test set evaluation (and have a strict 512-token budget for the input), does this refer strictly to how we format our prompts during the training phase so that the adapter learns a specific reasoning behavior? Or is there a way to inject inference-time prompting strategies that I am missing?
Any clarification would be greatly appreciated. Thanks!
6
add_reaction
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
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
You are right that the prompt used in the evaluation is fixed. You can't experiment with it.
We did not disclose the prompt used in the evaluation to limit reverse engineering. We expected some reverse engineering on the problem structures, and it already happened. It is why we wanted to coerce people into training the model instead of implementing a specific problem solver.
Does this mean that no prompt experimentation is doable during training? Maybe. Maybe not. You tell us.
reply
Reply
add_reaction
React
Stefano Viel
Posted 2 months ago
· 3546th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
A follow-up question on this is if we can have the prompt that will be used in evaluation (so that we can replicate the same settings locally).
reply
Reply
add_reaction
React
This comment has been deleted.

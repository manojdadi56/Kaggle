# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/697746
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3165

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
Error: Internet cannot be enabled for this competition with the current accelerator.
Anyone tried loading on macOS Apple Silicon?
label learning
Chat template during inference
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
HARSHITA KUMARI · 607TH IN THIS COMPETITION · POSTED 23 DAYS AGO
arrow_drop_up
2
arrow_drop_down
more_vert
SCORE NOT IMPROVING EVEN WITH REASONING+ANSWER FINETUNING
I have tried cot finetuning, generated custom reasoning from deepseek/qwen-30b model for bit manipulation and other complex tasks it generated reasoning but it was not complete but still i collected all of them and finetuned but the score is .52 which is very low
https://www.kaggle.com/code/harshitakumari256/notebook633554d240
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
Manish Swami
Posted 21 days ago
· 146th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
target_modules = [ 'out_proj', 'v_proj', 'q_proj', 'down_proj', 'embed_tokens', 'k_proj', 'in_proj', 'up_proj', 'o_proj', 'lm_head', 'gate_proj' ] remove embed_tokens , gate_proj and lm_head and then try again
reply
Reply
add_reaction
React
Harshita Kumari
TOPIC AUTHOR
Posted 21 days ago
· 607th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
still the same score
reply
Reply
add_reaction
React
Manish Swami
Posted 20 days ago
· 146th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Then its is CoT improve it
reply
Reply
add_reaction
React
KG
Posted 15 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
mine too: https://www.kaggle.com/code/krishnagupta02468/tinker-submission-notebook
i dont have tinker credits, so i found this guy's raw weights from tinker: https://www.kaggle.com/datasets/penguin069/nemotron-adapter-run
but i am not getting good results, even in the validation notebook
reply
Reply
add_reaction
React
SHUBHAM KUMAR
Posted 18 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
check you token length for input if its too low the cot will get cut off before reaching the boxed answer!!
reply
Reply
add_reaction
React

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686431
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2908

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
Permission error
What is the setting of the enable_thinking in the chat_template during testing?
Seemingly Impossible Questions in Dataset?
Submission Type and Time
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
NOIZERSAM · 355TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
2
arrow_drop_down
more_vert
QLoRA Fine-tuning Bug
I am attempting to fine-tune a model using QLoRA, but I am encountering the following error when training on a model that has been quantized using bitsandbytes: RuntimeError: mat1 and mat2 shapes cannot be multiplied (302x4096 and 1x2752512) Has anyone else encountered this same error, or does anyone have a solution?
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
MAJ0RT0M
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Need to patch in pytorch code - otherwise the model doesnt support quantized layers
# Force the slow (pure PyTorch) code path for Nemotron-H layers
# The fast CUDA kernels may not work on all container versions
for name, mod in sys.modules.items():
if 'modeling_nemotron_h' in name and hasattr(mod, 'is_fast_path_available'):
mod.is_fast_path_available = False
print(f'Patched {name}: using slow path')
The reasoning starter notebook has a snippet for this (where I got the code from above)
reply
Reply
add_reaction
React
The Swimmer
Posted 20 days ago
· 1202nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
interesting, but where exactly would this code be put in the whole process?
edit: I tried this code right before the line where I call trainer.train() and it seems to have fixed the dimension error, but i now get an error called "RuntimeError: index_add_(): self (Half) and source (Float) must have the same scalar type"
reply
Reply
add_reaction
React

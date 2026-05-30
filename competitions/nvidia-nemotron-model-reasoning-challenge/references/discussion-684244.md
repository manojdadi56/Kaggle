# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684244
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 2658

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
RL/GRPO difficulty
Queued for hours for the first time!
Permission denied error for ptxas-blackwell
Fixed: Any fix for trl installation?
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
SAI SRIKANTH · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
ModuleNotFound Error for mamba-ssm
Hello, I am facing the below import error while loading and running the Nemotron Nano model. ImportError: mamba-ssm is required by the Mamba model but cannot be imported
Can anyone help me with this, I am using RTX6000 GPU and the below code.
import torch import torch.nn.functional as F import kagglehub from datasets import Dataset from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments from peft import LoraConfig, get_peft_model, TaskType from trl import SFTTrainer, SFTConfig
MODEL_PATH = kagglehub.model_download("metric/nemotron-3-nano-30b-a3b-bf16/transformers/default")
model = AutoModelForCausalLM.from_pretrained( MODEL_PATH, device_map="auto", trust_remote_code=True, dtype=torch.bfloat16, use_mamba = False )
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
tiffanyseah
Posted 2 months ago
· 2876th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
you have to include the utility scripts in your inputs (see the image below)
check this "https://www.kaggle.com/code/ryanholbrook/nvidia-utility-script"
reply
Reply
add_reaction
React
Sai Srikanth
TOPIC AUTHOR
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Yeah checked it, It is working.
reply
Reply
add_reaction
React

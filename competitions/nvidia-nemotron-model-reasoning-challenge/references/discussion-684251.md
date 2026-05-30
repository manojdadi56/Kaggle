# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684251
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3503

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
Question about minor participation
SCORE NOT IMPROVING EVEN WITH REASONING+ANSWER FINETUNING
Error: Internet cannot be enabled for this competition with the current accelerator.
Anyone tried loading on macOS Apple Silicon?
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
DAOHE LIU · 444TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
1
arrow_drop_down
more_vert
The fit of unsloth to the Nemotron model
Unsloth's official documentation has added an adapter for Nemotron, but Kaggle shows that the trainable parameters seem to differ from the official documentation. Has anyone encountered this issue? The official documents are as follows：
model = FastLanguageModel.get_peft_model(
model,
r = 8, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
"gate_proj", "up_proj", "down_proj",
"in_proj", "out_proj",],
lora_alpha = 16,
lora_dropout = 0, # Supports any, but = 0 is optimized
bias = "none",    # Supports any, but = "none" is optimized
# [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
random_state = 3407,
use_rslora = False,  # We support rank stabilized LoRA
loftq_config = None, # And LoftQ
)
However, the results show: Unsloth: Detected MoE model with num_experts = 128 and target_modules = ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj', 'in_proj', 'out_proj']. Enabling LoRA on MoE parameters: ['mlp.experts.gate_up_proj', 'mlp.experts.down_proj']
Is this normal? Unsloth only performed LoRa on a small number of layers instead of the layers we specified, resulting in very few trainable parameters.
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
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@DaoHe Liu Not sure, that iam using the newest version of unsloth, but to me it seems lora adapters are applied. Would be nice if u show screenshot of notebook output after applying peft config. With layers with no lora adapters. If there are some layers without adapters, that would be concerning.
reply
Reply
add_reaction
React
DaoHe Liu
TOPIC AUTHOR
Posted 2 months ago
· 444th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I think I roughly know what to do.
reply
Reply
add_reaction
React

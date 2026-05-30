# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684654
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4814

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
Exactly same "types" of the prompts?
[Discussion] Concerns about copied notebooks and misleading submissions in the Notebooks section , Heavy Plagiarism
How can I use vLLM to speed up test.csv inference on Kaggle?
Observations on high-visibility notebooks with minimal model contribution in the Nemotron Reasoning Challenge
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
PRADEEP BOOPATHY · 411TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
Fixed: Any fix for trl installation?
Add this in the first cell also add dataset: /kaggle/input/datasets/pradeepboopathy/nvidia-nemotron-offline-package in the dataset panel
import subprocess, sys, os
from pathlib import Path
def resolve_python_path(target_dir):
for pth_file in Path(target_dir).glob("*.pth"):
with pth_file.open() as fp:
relpath = fp.read()
rel_pack_path = (pth_file.parent/relpath)
if rel_pack_path.exists():
print(f"append {rel_pack_path}")
sys.path.append(str(rel_pack_path))
offline_dir = "/kaggle/input/datasets/pradeepboopathy/nvidia-nemotron-offline-package/extra_packages"
target_dir = "/kaggle/working/packages"
os.makedirs(target_dir, exist_ok=True)
resolve_python_path("/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/")
if os.path.exists(offline_dir):
subprocess.check_call([
sys.executable, "-m", "pip", "install", "-q",
"--no-index",
"--find-links", offline_dir,
"--target", target_dir,
"datasets", "trl"
])
print("Installed from offline packages")
# Add to Python path
sys.path.append(target_dir)
resolve_python_path(target_dir)
import datasets, cutlass
add_reaction
React
6 Comments
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
Yann
Posted 2 months ago
· 1053rd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
For the TRL import, I was using https://www.kaggle.com/datasets/dennisfong/nvidia-nemotron-offline-packages , but the new version no longer includes TRL.
reply
Reply
1
add_reaction
Yann
Posted 2 months ago
· 1053rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I'm using https://www.kaggle.com/datasets/mayukh18/nemotron-packages now. The following code should be in top cell:
import os, sys
os.environ["WANDB_DISABLED"] = "true"
os.environ["WANDB_MODE"] = "disabled"
!pip install -q --no-index --find-links /kaggle/input/datasets/mayukh18/nemotron-packages/packages \
--ignore-installed \
unsloth trl peft transformers datasets accelerate bitsandbytes
!pip install -q /kaggle/input/datasets/mayukh18/nemotron-packages/causal_conv1d-1.6.1+cu12torch2.10cxx11abiTRUE-cp312-cp312-linux_x86_64.whl
!pip install -q /kaggle/input/datasets/mayukh18/nemotron-packages/mamba_ssm-2.3.1+cu12torch2.10cxx11abiTRUE-cp312-cp312-linux_x86_64.whl
from trl import SFTTrainer
You may need to uninstall wandb juste before with: !pip uninstall -y wandb
reply
Reply
add_reaction
React
Ralph Neumann
Posted 2 months ago
· 416th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I am facing the same problem.
reply
Reply
add_reaction
React
Pradeep Boopathy
TOPIC AUTHOR
Posted 2 months ago
· 411th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Fixed. Please add the above code.
reply
Reply
add_reaction
React
Ralph Neumann
Posted 2 months ago
· 416th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Which above code? Thanks for your reply
reply
Reply
add_reaction
React
Noizersam
Posted 2 months ago
· 355th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I've encountered the same problem. Have you solved it?
reply
Reply
add_reaction
React
Pradeep Boopathy
TOPIC AUTHOR
Posted 2 months ago
· 411th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Fixed. Check above
reply
Reply
add_reaction
React

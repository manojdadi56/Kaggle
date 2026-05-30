# Step 1:

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/702267
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5030

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
How to successfully submit file for competition without error?
Struggling with Nemotron training stability in local H20 (Loss stagnation & exploding grad_norm）
Is DoRA allowed does it actually improve LB scores?
Kaggle CLI Can’t Set GPU Type? Tired of Manually Switching to RTX 6000 Every Time 😩
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
NITIN S · 1575TH IN THIS COMPETITION · POSTED 8 DAYS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell'
PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell' get this while trying to train. Please help me as I am just starting to learn.
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
AMITH NAIR
Posted 4 days ago
· 1595th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Follow these steps exactly:
Step 1:
Before any cell, add this code block
import os import shutil import stat import glob
candidates = glob.glob("/kaggle/usr/lib/notebooks//nvidiautility*script/triton/backends/nvidia/bin/ptxas-blackwell")
if not candidates: raise FileNotFoundError("ptxas-blackwell not found")
src = candidates[0]
dst_dir = "/tmp/triton-bin" os.makedirs(dst_dir, exist_ok=True)
dst = f"{dst_dir}/ptxas-blackwell"
shutil.copy2(src, dst)
os.chmod(dst,os.stat(dst).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.environ["PATH"] = f"{dst_dir}:" + os.environ["PATH"]
os.environ["TRITON_PTXAS_PATH"] = dst os.environ["TRITON_PTXAS_BLACKWELL_PATH"] = dst
os.environ["CUDA_MODULE_LOADING"] = "LAZY" os.environ["TRITON_DISABLE_AUTOTUNE"] = "1" os.environ["USE_TRITON"] = "0"
os.environ["PTXAS_PATH"] = dst
print("PTXAS override:", dst)
Step 2:
After importing modules, add this code block
print("TRITON_PTXAS_PATH =", os.environ.get("TRITON_PTXAS_PATH")) print("TRITON_PTXAS_BLACKWELL_PATH =", os.environ.get("TRITON_PTXAS_BLACKWELL_PATH")) print("PTXAS_PATH =", os.environ.get("PTXAS_PATH"))`
It should output:
TRITON_PTXAS_PATH = /tmp/triton-bin/ptxas-blackwell TRITON_PTXAS_BLACKWELL_PATH = /tmp/triton-bin/ptxas-blackwell PTXAS_PATH = /tmp/triton-bin/ptxas-blackwell
Step 3:
Right before your training code, add this code block
import subprocess
subprocess.check_output([os.environ["TRITON_PTXAS_BLACKWELL_PATH"], "--version"]).decode()`
It should output:
'ptxas-blackwell: NVIDIA (R) Ptx optimizing assembler\nCopyright (c) 2005-2025 NVIDIA Corporation\nBuilt on Tue_May_27_02:18:05_PDT_2025\nCuda compilation tools, release 12.9, V12.9.86\nBuild cuda_12.9.r12.9/compiler.36037853_0\n'
reply
Reply
add_reaction
React
Manish Swami
Posted 8 days ago
· 146th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
import subprocess, sys, os
from pathlib import Path
def resolve_python_path(target_dir):
for pth_file in Path(target_dir).glob("*.pth"):
with pth_file.open() as fp:
relpath = fp.read().strip()
rel_pack_path = pth_file.parent / relpath
if rel_pack_path.exists():
sys.path.append(str(rel_pack_path))
offline_dir = "/kaggle/input/datasets/dennisfong/nvidia-nemotron-offline-packages/offline_packages"
target_dir  = "/kaggle/working/packages"
os.makedirs(target_dir, exist_ok=True)
resolve_python_path("/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/")
if os.path.exists(offline_dir):
subprocess.check_call([
sys.executable, "-m", "pip", "install", "-q",
"--no-index", "--find-links", offline_dir,
"--target", target_dir,
"datasets", "trl", "peft"
])
print("Offline packages installed.")
sys.path.append(target_dir)
resolve_python_path(target_dir)
try out this
reply
Reply
add_reaction
React
Nitin S
TOPIC AUTHOR
Posted 7 days ago
· 1575th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
didn't work
reply
Reply
add_reaction
React
This comment has been deleted.

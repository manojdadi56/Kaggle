# Step 1:

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683711
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5385

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
Fix ModuleNotFoundError for cutlass
Bit manipulation puzzles: are transformations uniquely determined?
FIX: ModuleNotFoundError: No module named 'cutlass'
Training error: CUDA error: no kernel image is available for execution on the device
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
IOANNIS M · 1944TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
8
arrow_drop_down
more_vert
[BUG] Utility script permission error
any ideas how this can be solved? I think until yesterday was fine
PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell'
Thanks in advance
add_reaction
React
7 Comments
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
Ioannis M
TOPIC AUTHOR
Posted 2 months ago
· 1944th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
@ryanholbrook or someone from kaggle mods - please let us know if you have any updates or plan any fixes on this issue with ptxas and permission error?
It is been hours of failed trials and gpu hours without any result and people continue struggling. Thanks for the support
reply
Reply
add_reaction
React
omkar_pavale
Posted 2 months ago
· 2251st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Did you get any solution for this?
reply
Reply
add_reaction
React
Ioannis M
TOPIC AUTHOR
Posted 2 months ago
· 1944th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
not yet actually. sometimes works, most not. Not sure how to debug this.
reply
Reply
add_reaction
React
AMITH NAIR
Posted 6 days ago
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
Nitin S
Posted 8 days ago
· 1575th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Did anyone find a solution for it?
reply
Reply
add_reaction
React
ulasdesouza
Posted 2 months ago
· 1465th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
replace with _ for - nvidia-utility-script part
reply
Reply
3
add_reaction
Ievgenii Krevenets
Posted 2 months ago
· 3393rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
hm, when I did these changes I got:
ModuleNotFoundError: No module named 'cutlass'
reply
Reply
add_reaction
React
omkar_pavale
Posted 2 months ago
· 2251st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
add this to resolve that issue.
import site
cutlass_pkg_path = "/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/"
site.addsitedir(cutlass_pkg_path)
reply
Reply
add_reaction
React

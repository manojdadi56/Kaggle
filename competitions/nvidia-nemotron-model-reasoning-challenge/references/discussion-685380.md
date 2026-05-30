# Step 1:

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685380
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 11709

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
Fixed: Any fix for trl installation?
Exactly same "types" of the prompts?
[Discussion] Concerns about copied notebooks and misleading submissions in the Notebooks section , Heavy Plagiarism
How can I use vLLM to speed up test.csv inference on Kaggle?
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
VAIDEHIPANDEY · 3074TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
Permission denied error for ptxas-blackwell
I am getting this error when I try to train my lora adapter:
PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/triton/backends/nvidia/bin/ptxas-blackwell'
add_reaction
React
9 Comments
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
Posted 2 months ago
· 1944th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
try to change - with _ in the utility script path
"/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/"
reply
Reply
add_reaction
React
Ievgenii Krevenets
Posted 2 months ago
· 3393rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
hm, but there is no: /kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/ at the environment.
e.g.:
!ls /kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/
ls: cannot access '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/': No such file or directory
reply
Reply
add_reaction
React
Ievgenii Krevenets
Posted 2 months ago
· 3393rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
also script fails now with error:
ModuleNotFoundError: No module named 'cutlass'
reply
Reply
add_reaction
React
Ioannis M
Posted 2 months ago
· 1944th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
actually make sure that you run this "fix" before anytorch, transformers, or model import otherwise is not working.
hm, but there is no: /kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/ at the environment.
depends on which version you use, e.g. select a file and copy path (with right click) to check it.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
AMITH NAIR
Posted 7 days ago
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
Mark Cooper
Posted a month ago
· 50th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The rename trick only works if your notebook actually has nvidia_utility_script with underscores — some versions have dashes (nvidia-utility-script). Either way, Errno 13 Permission denied is a filesystem permission issue on a read-only mount, not a path issue.
Robust fix that works for either path variant — find your actual ptxas-blackwell location,
then:
```python import shutil, os, stat, glob
candidates = glob.glob('/kaggle/usr/lib/notebooks///triton/backends/nvidia/bin/ptxas-blackwell') if not candidates: raise FileNotFoundError('ptxas-blackwell not found — check your notebook utility script
path') src = candidates[0] dst = '/tmp/ptxas-blackwell' shutil.copy2(src, dst) os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH) os.environ['TRITON_PTXAS_PATH'] = dst print(f'TRITON_PTXAS_PATH = {dst} (copied from {src})')
Critical: run this cell BEFORE any import torch, import transformers, import peft etc. Triton
binds to ptxas at import time, so setting the env var later has no effect.
For the separate ModuleNotFoundError: cutlass — install cutlass via !pip install -q nvidia-cutlass-dsl or pull it from the utility script's dataset. That's a different issue.
reply
Reply
2
add_reaction
harsha7754
Posted a month ago
· 2348th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I am still getting the error
This is my code
src = "/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/"
ptx_src = "/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell"
CUTLASS_PKG_PATH = Path(src) if not CUTLASS_PKG_PATH.exists(): raise RuntimeError( "Missing NVIDIA utility script path. In Kaggle, add the notebook data source " "'ryanholbrook/nvidia-utility-script' before running this notebook." ) sys.path.insert(0, str(CUTLASS_PKG_PATH))
import kagglehub import mamba_ssm
import os, shutil, stat
dst = "/tmp/ptxas-blackwell"
if os.path.exists(src): shutil.copy2(ptx_src, dst) os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) os.environ["TRITON_PTXAS_PATH"] = dst
import torch from torch.utils.data import Dataset from peft import LoraConfig, TaskType, get_peft_model
from transformers import ( AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, default_data_collator, )
reply
Reply
add_reaction
React
Mark Cooper
Posted a month ago
· 50th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Your import order is the bug. import mamba_ssm (and import kagglehub potentially) pulls in CUDA/Triton, which binds to ptxas at that moment — before your os.environ["TRITON_PTXAS_PATH"] line runs. Setting the env var after that point has no effect.
Move the ptxas setup to the very top of the notebook, before any other import that could touch CUDA / Triton / torch. Like this:
Cell 1 — ptxas setup MUST be first, before ANY other import
import os,
shutil, stat, glob, sys                                                                                                                                                                                                                                                                               from pathlib import Path
candidates = glob.glob('/kaggle/usr/lib/notebooks/*/nvidia*utility*script/triton/backends/nvidia/bin/ptxas-blackwell')
if not candidates:
raise FileNotFoundError('ptxas-blackwell not found')
src_ptx = candidates[0]
dst = '/tmp/ptxas-blackwell'
shutil.copy2(src_ptx, dst)
os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
os.environ['TRITON_PTXAS_PATH'] = dst
print(f'TRITON_PTXAS_PATH set to {dst}')
Cell 2 — cutlass path (still before mamba_ssm)
CUTLASS_PKG_PATH = Path('/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/')
if not CUTLASS_PKG_PATH.exists():
raise RuntimeError("Missing NVIDIA utility script path — add ryanholbrook/nvidia-utility-script as a notebook data source")
sys.path.insert(0, str(CUTLASS_PKG_PATH))
Cell 3 — NOW do the heavy imports (Triton is already pointed at the writable ptxas)
import kagglehub
import mamba_ssm
import torch
from torch.utils.data import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, default_data_collator
Key changes:
- The three lines that matter (os.environ[...], shutil.copy2, os.chmod) go in a cell that runs FIRST, with
nothing above them
- mamba_ssm and torch go AFTER. If you put them before, the env var is a no-op.
If you're already past the env var line at runtime and Triton has already been loaded, restart the kernel and run cells top-to-bottom in the corrected order. A del torch; import torch won't fix it — Triton's state persists.
reply
Reply
add_reaction
React
harsha7754
Posted a month ago
· 2348th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Nope still no luck😪
`import os, shutil, stat, glob, sys from pathlib import Path
candidates = glob.glob('/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell') if not candidates:
raise FileNotFoundError('ptxas-blackwell not found') src_ptx = candidates[0] dst = '/tmp/ptxas-blackwell' shutil.copy2(src_ptx, dst) os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) os.environ['TRITON_PTXAS_PATH'] = dst print(f'TRITON_PTXAS_PATH set to {dst}')`
CUTLASS_PKG_PATH = Path('/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/nvidia_cutlass_dsl/python_packages/') if not CUTLASS_PKG_PATH.exists(): raise RuntimeError("Missing NVIDIA utility script path — add ryanholbrook/nvidia-utility-script as a notebook data source") sys.path.insert(0, str(CUTLASS_PKG_PATH))
import kagglehub import mamba_ssm import torch from torch.utils.data import Dataset from peft import LoraConfig, TaskType, get_peft_model from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, default_data_collator
import random import re import subprocess
Follwed by main logics, prompts and functions
reply
Reply
add_reaction
React
Ievgenii Krevenets
Posted 2 months ago
· 3393rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
got the same error, have you managed to solve it?
reply
Reply
add_reaction
React
This comment has been deleted.
harsha7754
Posted a month ago
· 2348th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
did you resolve the issue?
reply
Reply
add_reaction
React

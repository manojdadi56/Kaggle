# Appreciation (2)

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684385
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3513

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
Bit manipulation puzzles: are transformations uniquely determined?
FIX: ModuleNotFoundError: No module named 'cutlass'
Training error: CUDA error: no kernel image is available for execution on the device
BUG in Nemotron Model file://Models/modeling_nemotron_h.py
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
LEI ALEX · 1885TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
8
arrow_drop_down
more_vert
Fix ModuleNotFoundError for cutlass
The actual cutlass code is hidden inside nvidia_cutlass_dsl/python_packages/. The package uses a .pth file to tell Python where to find it. However, simply adding your target directory to sys.path does not parse .pth files in non-standard directories. Python completely ignores the .pth file and fails to find the hidden folder.
Just replace the first cell in your notebook with this code:
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
offline_dir = "/kaggle/input/nvidia-nemotron-offline-packages/offline_packages"
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
else:
subprocess.check_call([
sys.executable, "-m", "pip", "install", "-q",
"--target", target_dir,
"datasets", "trl"
])
print("Installed from PyPI")
# Add to Python path
sys.path.append(target_dir)
resolve_python_path(target_dir)
import datasets, trl, cutlass
print("datasets:", datasets.__version__, "trl:", trl.__version__, "cutlass:", cutlass.__version__)
add_reaction
React
3 Comments
2 appreciation comments
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
This comment has been deleted.
Appreciation (2)
Arthur Yu
Posted 2 months ago
· 744th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Great thanks👍 fantastic work done！
Javier Hernández
Posted 2 months ago
· 770th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks a lot! it works! 👍

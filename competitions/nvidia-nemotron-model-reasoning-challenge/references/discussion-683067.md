# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683067
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 7133

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
Edge case in metric: \boxed{} cannot contain }
Competition Metric Bug: verify method fails for Binary String Problem (?)
Pip install with internet disabled: install dependencies feature
Fix for “CUDA error: no kernel image is available for execution on the device” on RTX PRO 6000 Blackwell
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
DONALD GALLIANO III · 2831ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
18
arrow_drop_down
more_vert
RTX PRO 6000 Blackwell — CUDA kernel incompatibility status + GPU time spent debugging
The pre-installed mamba_ssm and causal_conv1d packages in the competition environment are compiled for sm_90, but the RTX PRO 6000 Blackwell GPU requires sm_120.
This means:
The demo notebook loads and saves weights fine (no forward pass required) Any actual training or inference immediately crashes with AcceleratorError: CUDA error: no kernel image is available for execution on the device Internet is disabled on the Blackwell accelerator, so we cannot pip install fixed packages The workaround (forcing Mamba's Python slow path + patching Triton's ptxas permissions) works but is extremely slow and incompatible with gradient checkpointing
I've spent hours of GPU time across multiple sessions just debugging environment issues — not training, not experimenting, just trying to get a single forward pass to complete. Based on the other threads here, I'm far from alone.
Two questions for the organizers:
Is there a timeline for updating the base environment with sm_120-compatible builds of mamba_ssm, causal_conv1d, and Triton? This is currently a blocker for every participant attempting to train on the provided hardware. ( i dont have strong enough local hardware for it )
Will GPU hours consumed debugging this infrastructure issue be credited back? The weekly GPU quota is limited, and a significant portion has been spent on an environment problem rather than actual competition work.
For context: I'm not just raising this from the sidelines. I've put significant time into dataset analysis and training data preparation, and I have a working notebook ready to go via slow-path workarounds. I just need the environment to cooperate so I can train at a reasonable speed.
I'm genuinely excited about this competition! The problem design is clever (love ciphers… nah, not those substitution ones) and the reasoning challenges are legitimately hard. Would love to focus that energy on training and iteration rather than fighting CUDA kernels.
Thanks for the op guys!
add_reaction
React
13 Comments
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
Pinned comments
push_pin
Tiffany Xiang
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
4
arrow_drop_down
more_vert
The new Docker image with CUDA 12.8 and updated PyTorch and Triton is rolled out now! Thanks everyone for your patience :)
reply
Reply
1
add_reaction
This comment has been deleted.
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I want to install mamba_ssm. It does not seem to be there post update. I try:
# Fix 1: Add utility script to Python path (provides mamba_ssm, triton, etc.)
sys.path.insert(0, '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script')
Then I get: ModuleNotFoundError: No module named 'cutlass'
reply
Reply
add_reaction
React
9 more replies
arrow_drop_down
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
How can I import vllm into the Kaggle environment? I have the newest script pack, data set and model attached, GTX 6000 selected. It does not find vllm. Inference is extremely slow below 5 tokens/sec.
reply
Reply
add_reaction
React
All other comments
Addison Howard
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
7
arrow_drop_down
more_vert
We're working on upgrading the docker image and getting it released shortly!
reply
Reply
2
add_reaction
Donald Galliano III
TOPIC AUTHOR
Posted 2 months ago
· 2831st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you!
reply
Reply
add_reaction
React
Jaisree D.R.
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
Hello, are there any updates on the docker image yet? Thank you!
reply
Reply
add_reaction
React
Anton Kratz
Posted 2 months ago
· 3141st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Dear @addisonhoward has there been any progress on this issue? I want to participate in this challenge, however I depend on the provided Blackwell GPU. I have spend over 10 GPU hours on this plus more for troubleshooting, documented my work in a public notebook here on Kaggle, could not get it to work. I believe this really needs to be fixed from the Kaggle side, not by the much slower workarounds that the community could develop. I would be excited to implement some of the ideas that I have for increasing the reasoning score, however I feel the "AcceleratorError: CUDA error: no kernel image is available for execution on the device" issue is a real blocker.
reply
Reply
add_reaction
React
This comment has been deleted.
Eidan Rosado
Posted 2 months ago
· 2636th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I ended up burning through a bit of the week's credits debugging, but I made the patches public (without my fine-tuning logic for now): https://www.kaggle.com/code/edyvision/nvidia-nemotron-submission-demo-w-blackwell-patch
Hope this unblocks some folks in the meantime while the official env gets updated! It is indeed exceptionally slow.
reply
Reply
add_reaction
React
This comment has been deleted.
Dustin
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681820#3422400
We're working on getting the default env updated. In the meantime, its probably best to dump the needed deps into a dataset/notebook, and then do an "offline" install of the upgrades on the rtx pro 6000 machine.
reply
Reply
add_reaction
React
This comment has been deleted.

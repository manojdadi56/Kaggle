# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682428
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4743

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
BUG in Nemotron Model file://Models/modeling_nemotron_h.py
Equation Symbolic has anyone figured out the pattern?
[Potential problem] Eval regex cannot parse answers starting with character"}"
sharing high quality synthetic data generation prompt
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
HARSH RAJBHAR · POSTED 2 MONTHS AGO
arrow_drop_up
8
arrow_drop_down
more_vert
Training error: CUDA error: no kernel image is available for execution on the device
How to fix this ?
[ERROR] Training error: CUDA error: no kernel image is available for execution on the device Search for cudaErrorNoKernelImageForDevice' in https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html for more information. CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect. For debugging consider passing CUDA_LAUNCH_BLOCKING=1 Compile withTORCH_USE_CUDA_DSA` to enable device-side assertions.
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
Abhigyan Srivastava
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
The error is still here. Kaggle team says they are working on it. I only hope that they send out a shoutout mail to all of us once it is fixed.
reply
Reply
add_reaction
React
Timmy Juicehouse
Posted 2 months ago
· 172nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
If I'm not mistaken, you plan to train with PyTorch, but the PyTorch version in your environment is incompatible with the CUDA version required for the RTX Pro 6000. When I ran it on my workstation, I had to update the CUDA environment.
reply
Reply
add_reaction
React
Harsh Rajbhar
TOPIC AUTHOR
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Could you plz explain in detail , how you fixed it ? Since , i can't use pip because internet is disabled on GPU RTX Pro 6000 .
reply
Reply
add_reaction
React
Timmy Juicehouse
Posted 2 months ago
· 172nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Are you training in a Kaggle environment? Try downloading the offline PyTorch installation package and then installing it in the online environment.
reply
Reply
add_reaction
React
Harsh Rajbhar
TOPIC AUTHOR
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
I’ve already updated to PyTorch nightly with CUDA 12.8, and torch.cuda.get_arch_list() correctly shows sm_120, so PyTorch itself supports the GPU. However, training still fails with:
CUDA error: no kernel image is available for execution on the device
This seems to come from causal_conv1d, which appears to be compiled for older architectures and not SM120.
Since Kaggle does not allow proper CUDA compilation (nvcc), I’m unable to rebuild causal_conv1d from source inside the environment.
Could you please clarify:
Is there a precompiled version of causal_conv1d that supports SM120?
Should we disable causal_conv1d and use a fallback implementation instead?
If disabling is expected, what is the recommended way/config flag to do so in this competition setup?
reply
Reply
add_reaction
React
Sulavss7
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
i am not able to use p100 gpu . T4 is working fine . what the hell is happening
reply
Reply
add_reaction
React
chenchen2
Posted a month ago
arrow_drop_up
0
arrow_drop_down
more_vert
I also encountered this problem. How did you solve it
reply
Reply
add_reaction
React
xianxu qiu
Posted 2 months ago
· 2574th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I encountered the same problem; without using sm_120, the inference speed was only 1.7 tokens/s.
reply
Reply
add_reaction
React

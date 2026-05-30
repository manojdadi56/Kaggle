# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683820
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5438

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
The fit of unsloth to the Nemotron model
Question about minor participation
SCORE NOT IMPROVING EVEN WITH REASONING+ANSWER FINETUNING
Error: Internet cannot be enabled for this competition with the current accelerator.
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
KO · 2166TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
1
arrow_drop_down
more_vert
CUDA error: no kernel image is available for execution on the device — How to resolve CUDA/GPU architecture mismatch?
Hi everyone, I'm running into the following error when executing my PyTorch code on Kaggle's GPU environment: AcceleratorError: CUDA error: no kernel image is available for execution on the device (cudaErrorNoKernelImageForDevice) What I understand so far: This error typically means the compiled CUDA kernel doesn't support the GPU architecture on the current device. However, I'm not sure what the best fix is in Kaggle's managed environment where I have limited control over the CUDA/driver setup. My environment (as best I can tell):
Runtime: Kaggle Notebook (GPU accelerator enabled) Framework: PyTorch (via torch) (please fill in your torch/CUDA version from torch.version.cuda and torch.cuda.get_device_name(0))
Things I've already tried / considered:
Passing CUDA_LAUNCH_BLOCKING=1 for better stack traces Checking if the issue is package-version related (e.g., a pre-built wheel compiled for an older CUDA compute capability)
My questions:
Is this a known issue with specific GPU types (e.g., T4 vs P100 vs newer GPUs) on Kaggle? Is reinstalling PyTorch with the correct CUDA wheel the right approach, and if so, what version combination works reliably on Kaggle's current environment? Are there any Kaggle-specific workarounds (e.g., pinning package versions in the notebook)?
Any guidance would be greatly appreciated. Thanks!
Error log is below.
AcceleratorError: CUDA error: no kernel image is available for execution on the device
Search for `cudaErrorNoKernelImageForDevice' in https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__TYPES.html for more information.
CUDA kernel errors might be asynchronously reported at some other API call, so the stacktrace below might be incorrect.
For debugging consider passing CUDA_LAUNCH_BLOCKING=1
Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.
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
Tiffany Xiang
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
The new Docker image with CUDA 12.8 and updated PyTorch is rolled out now! Please make sure to select the latest environment in Session options :)
reply
Reply
add_reaction
React
Ko
TOPIC AUTHOR
Posted 2 months ago
· 2166th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for your comment! I still can't figure out why my code doesn't work. Could you take a look at it? https://www.kaggle.com/code/komurase/fork-of-nvidia-nemotron-submission-demo
I tried to install cutlass via pip, but it doesn't work well.
---------------------------------------------------------------------------
ModuleNotFoundError                       Traceback (most recent call last)
/tmp/ipykernel_17/4056115492.py in <cell line: 0>()
2
3 import kagglehub
----> 4 import mamba_ssm
5 import torch
6 from peft import LoraConfig, get_peft_model, get_peft_model_state_dict, TaskType
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/mamba_ssm/__init__.py in <module>
4 from mamba_ssm.modules.mamba_simple import Mamba
5 from mamba_ssm.modules.mamba2 import Mamba2
----> 6 from mamba_ssm.modules.mamba3 import Mamba3
7 from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/mamba_ssm/modules/mamba3.py in <module>
16 from mamba_ssm.ops.triton.mamba3.mamba3_mimo_rotary_step import apply_rotary_qk_inference_fwd
17
---> 18 from mamba_ssm.ops.cute.mamba3.mamba3_step_fn import mamba3_step_fn
19
20 class Mamba3(nn.Module):
/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/mamba_ssm/ops/cute/mamba3/mamba3_step_fn.py in <module>
12 import cuda.bindings.driver as cuda
13
---> 14 import cutlass
15 import cutlass.cute as cute
16 from cutlass import Int32, Float32, Float16, BFloat16, Boolean, const_expr
ModuleNotFoundError: No module named 'cutlass'
reply
Reply
add_reaction
React

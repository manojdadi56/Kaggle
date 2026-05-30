# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682521
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4254

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
Date Conflict: Midpoint Cut-off Date in Prizes vs Timeline section
Default parameters mismatch
Eligibility for participants under 18
Hallucination in equation problems?
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
HARUI-IG · POSTED 2 MONTHS AGO
arrow_drop_up
4
arrow_drop_down
more_vert
Working Dockerfile on RTX5070Ti to fix `CUDA error: no kernel image is available for execution on the device`
I ran into CUDA error: no kernel image is available for execution on the device on an RTX 5070 Ti (sm_120) when testing both causal-conv1d and mamba-ssm. The root cause was that the installed CUDA extensions did not contain sm_120 code. In my case, both causal_conv1d_cuda and selective_scan_cuda were missing sm_120, so the kernels could not launch on Blackwell. What fixed it for me was rebuilding both extensions from source inside the devcontainer with a proper CUDA 12.8 compiler available, and forcing the build to target Blackwell:
install cuda-compiler-12-8 so that /usr/local/cuda-12.8/bin/nvcc exists
set CUDA_HOME=/usr/local/cuda-12.8
set TORCH_CUDA_ARCH_LIST=12.0
set CAUSAL_CONV1D_FORCE_BUILD=TRUE
set MAMBA_FORCE_BUILD=TRUE
install causal-conv1d from source with --no-binary
install mamba-ssm from source from the git repo After that, both extensions were rebuilt with sm_120 included, and my repro script started working correctly. For reference, this was the Dockerfile I used:
```dockerfile
FROM gcr.io/kaggle-gpu-images/python@sha256:9fa0da194fad2241d3f01a80581cbecbd3a258b4d1b695e2cbbbc62a0fd205ac
SHELL ["/bin/bash", "-lc"]
ARG USERNAME=vscode
ARG USER_UID=10000
ARG USER_GID=10000
# Blackwell / RTX 50-series support:
# - force source builds for causal-conv1d and mamba-ssm
# - make sure CUDA 12.8 nvcc is available inside the container
# - explicitly target sm_120
ENV CUDA_HOME=/usr/local/cuda-12.8
ENV PATH=/usr/local/cuda-12.8/bin:${PATH}
ENV TORCH_CUDA_ARCH_LIST=12.0
ENV CAUSAL_CONV1D_FORCE_BUILD=TRUE
ENV MAMBA_FORCE_BUILD=TRUE
RUN if ! getent group "${USERNAME}" >/dev/null; then \
groupadd --gid "${USER_GID}" "${USERNAME}"; \
fi \
&& if ! id -u "${USERNAME}" >/dev/null 2>&1; then \
useradd --uid "${USER_UID}" --gid "${USER_GID}" -m "${USERNAME}"; \
fi
# Install CUDA compiler first, then install the matching PyTorch nightly build.
RUN uv pip uninstall causal-conv1d mamba-ssm torch torchvision torchaudio \
&& apt-get update \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
cuda-compiler-12-8 \
&& rm -rf /var/lib/apt/lists/* \
&& uv pip install --system \
torch==2.12.0.dev20260315+cu128 \
torchvision==0.26.0.dev20260315+cu128 \
torchaudio==2.11.0.dev20260315+cu128 \
--index-url https://download.pytorch.org/whl/nightly/cu128 \
&& /usr/local/cuda-12.8/bin/nvcc -V
# Rebuild causal-conv1d and mamba-ssm from source so sm_120 gets embedded.
RUN uv pip install --system --no-build-isolation --no-binary causal-conv1d \
"causal-conv1d>=1.4.0" \
&& uv pip install --system --no-build-isolation \
"git+https://github.com/state-spaces/mamba.git@175d263c1c0e58b5d5bd2a51eef43c28696396fa"
WORKDIR /workspaces/nemotron
add_reaction
React
0 Comments
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

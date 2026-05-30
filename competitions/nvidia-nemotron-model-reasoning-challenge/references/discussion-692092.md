# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/692092
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 7532

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
How to delete old submission.zip to save space?
Why every bit problem always has INFINITE AMOUNT OF WRONG SOLUTIONS[WHY IT DOESN'T TEST REASONING]
runnung issues
how can I download the model from the /kaggle/working?
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
ZKHDGUOFENG · 3311TH IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Please help me, my predict code as slow as 1 token/second
blow is my predict code, it's too slow that predicting 1token/second. My server is 4 cards of L20(48G GPU):
PyTorch: 2.6.0+cu118
CUDA available: True
CUDA version: 11.8
GPU count: 4
GPU name: NVIDIA L20
nvidia-smi
Thu Apr 16 16:28:16 2026
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.126.20             Driver Version: 580.126.20     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L20                     On  |   00000000:16:00.0 Off |                    0 |
| N/A   46C    P0            114W /  350W |   34651MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA L20                     On  |   00000000:5A:00.0 Off |                    0 |
| N/A   50C    P0            113W /  350W |   18240MiB /  46068MiB |     62%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA L20                     On  |   00000000:98:00.0 Off |                    0 |
| N/A   45C    P0             86W /  350W |   18238MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA L20                     On  |   00000000:C8:00.0 Off |                    0 |
| N/A   47C    P0            111W /  350W |   33598MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
Would you please modify my code blow to be fast to 30 tokens/second running on 4*L20.
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from peft import PeftModel
from threading import Thread
import os
# Set HF mirror endpoint for faster downloads in China
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# 加载模型
base_model = AutoModelForCausalLM.from_pretrained(
"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
torch_dtype=torch.bfloat16,
device_map="auto",
low_cpu_mem_usage=True,
trust_remote_code=True,
)
model = PeftModel.from_pretrained(base_model, "/home/nvidia/gf/tmp/adapter_large")
model.eval()
# Disable torch.compile to avoid Triton kernel autotuner issues
# if(hasattr(model, "compiled")):
#     model = torch.compile(model, mode="reduce-overhead")
tokenizer = AutoTokenizer.from_pretrained(
"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
trust_remote_code=True,
)
if tokenizer.pad_token is None:
tokenizer.pad_token = tokenizer.eos_token
def predict(message, history):
messages = [{"role": "user", "content": message}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
# 使用 TextIteratorStreamer 适合 Gradio
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
generation_kwargs = dict(
**inputs,
max_new_tokens=15120,
use_cache=True,
temperature=0.1,
do_sample=False,
num_beams=1,  # Must be 1 when using streamer
# Remove early_stopping when num_beams=1 to avoid validation errors
pad_token_id=tokenizer.pad_token_id,
streamer=streamer,
)
thread = Thread(target=model.generate, kwargs=generation_kwargs)
thread.start()
accumulated_text = ""
for new_text in streamer:
accumulated_text += new_text
yield accumulated_text
gr.ChatInterface(
predict,
title="Bit Operation Rule Learner",
description="",
).queue().launch(server_name="127.0.0.1", server_port=7860)
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
Mark Cooper
Posted a month ago
· 50th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Your problem is the Nemotron cache bug — modeling_nemotron_h.py has a parameter name mismatch between prepare_inputs_for_generation() (sends past_key_values) and forward() (expects cache_params). The KV cache gets silently ignored, so the model recomputes every token from scratch. That's why you're at 1 tok/s.
Three-step fix:
Upgrade to transformers>=5.3.0 — it has native NemotronH support with the correct parameter mapping
Remove trust_remote_code=True from your from_pretrained calls — this is critical,
otherwise it pulls the old buggy modeling_nemotron_h.py from the HF model cache and overrides the library's fix
Set gradient_checkpointing=False if you use it anywhere — the built-in implementation
throws ValueError on it
On Kaggle (no internet), upload the transformers wheel as a dataset and install with:
```python !pip install -q --no-deps --force-reinstall "/kaggle/input/your-dataset/transformers-5.5.3-py3-none-any.whl"
Expected: 2 tok/s → ~38 tok/s (20× speedup). Komil Parmar's write-up has the full explanation:
https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/690161
For production serving, vLLM with --enable-lora --max-lora-rank 32 is faster still.
reply
Reply
2
1
add_reaction
zkhdGuoFeng
TOPIC AUTHOR
Posted a month ago
· 3311th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you. But what are the transformers and pytorch version? I can't run after Upgrade to transformers>=5.3.0.
reply
Reply
add_reaction
React

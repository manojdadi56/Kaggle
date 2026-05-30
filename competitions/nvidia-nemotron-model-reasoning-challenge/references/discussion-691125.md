# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/691125
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3907

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
CPU instead of GPU is running on NVIDIA RTX PRO 6000 Blackwell
Doubts regarding the competition
Rounding off issues numerical problems
Please help me, my predict code as slow as 1 token/second
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
DEVAL MUKHERJEE1 · 1460TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Is the evaluation deterministic ?
I saw the post from Tong about his attempt and he mentioned that he got a score of .84 twice and .85 once or something like that. If the evaluation is deterministic how does that happen ? am I missing something ?
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
-2
arrow_drop_down
more_vert
Yes, it's non-deterministic in practice even though Kaggle sets temperature=0. You're not missing anything. Sources of variance:
CUDA kernel non-determinism. torch.backends.cudnn.deterministic=False is the default, and several ops (attention, softmax reductions, batched matmul) have tiny float-order differences across runs. At temperature=0 these rarely matter, but over 7680 tokens × 34 puzzles a single
flipped greedy decision cascades into a completely different answer.
Batch composition. If Kaggle batches your 34 puzzles with different padding arrangements or ordering, logits for identical inputs can shift by ~1e-6. Usually harmless, but at exact greedy boundaries it flips the picked token.
GPU hardware drift. Kaggle's grading infrastructure isn't guaranteed to route you to the same physical GPU / driver version between submissions. Different CUDA versions produce subtly different results.
vLLM's prefix caching & scheduling. If prefix caching is enabled server-side, concurrent request arrival order affects KV cache hits.
Practical impact: THK's 0.84/0.84/0.85 pattern suggests ~1 puzzle out of 34 flipping correct/wrong between runs = ~3% score variance. Matches your 0.64→0.66 (≈1 puzzle).
What to do about it:
Kaggle lets you pick 2 submissions for the final private leaderboard. Submit your best adapter 3-5 times, pick the highest-scoring two.
For your own local benchmarking, expect ±1-2% just from this — don't chase changes smaller than that as if they're real.
If you really need determinism, set torch.use_deterministic_algorithms(True) and torch.backends.cudnn.deterministic=True in your training/inference stack — hurts speed but pins outputs.
It's a known feature of large-model inference at exact greedy, not a bug in the competition's grader.
reply
Reply
add_reaction
React
Trishanth Mellimi
Posted 2 months ago
· 1464th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
even i got non deterministic score, 0.64 and 0.66 for the same submission a week back
reply
Reply
add_reaction
React

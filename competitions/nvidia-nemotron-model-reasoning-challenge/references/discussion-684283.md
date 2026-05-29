# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684283#3431423
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 8279

---

menu

Create
explore
Home
emoji_events
Competitions
leaderboard
Benchmarks
smart_toy
Game Arena
code
Data Hub
expand_more
format_list_bulleted
More
expand_more
note_alt
Your Work
expand_less
Viewed
expand_less
NVIDIA Nemotron Model Reasoning Challenge
Kaggle CLI — Develop Locally and Run on RTX Pro 6000 GPU
Strategy to solve 85% of bit manipulation
Visualize the problems and completions from the base model
Answers To Everything Data: Read Me! 100% Solve Rate
Edited
expand_less
Kitesdata
Save order db V1
History inferencing V3
History inferencing
Fork of inferencing
Bookmarks
expand_less
ARC Prize 2024
LMSYS - Chatbot Arena Human Preference Predictions
notebookc7a610ad46
train Swin_T[pytorch lightning]
Viral Pneumonia Classification | GoogLeNet
auto_awesome_motion
1
View Active Events

search
Kaggle uses cookies from Google to deliver and enhance the quality of its services and to analyze traffic.
Learn more
OK, Got it.
NVIDIA · FEATURED PREDICTION COMPETITION · 17 DAYS TO GO
NVIDIA Nemotron Model Reasoning Challenge
Advance reasoning techniques using NVIDIA Nemotron open models on a novel benchmark
NVIDIA Nemotron Model Reasoning Challenge
Submit Prediction
more_horiz
Overview
Data
Code
Models
Discussion
Leaderboard
Rules
Team
Submissions
ZHUANG JIA · 162ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
60
arrow_drop_down
more_vert
Mainstream LLM Performance Comparison：Gemini-3.1-Pro delivers the best performance, while DeepSeek-V3.2 is also highly impressive.
Directly use the zero-shot prompting method to test the performance of mainstream LLMs. The prompt used for the request is consistent with the official testing method:
prompt + '\nPlease put your final answer inside `\\boxed{}`. For example: `\\boxed{your answer}`'
The test results are as follows:
model think max_tokens score
Gemini-3.1-Pro ✅ 32768 0.81
Claude-Opus-4.6 ✅ 32768 0.78
DeepSeek-V3.2 ✅ 32768 0.74
Kimi-K2.5 ✅ 32768 0.72
Qwen3-Max ✅ 32768 0.72
MiniMax-M2.5 ✅ 32768 0.66
Qwen3.5-Plus ✅ 32768 0.64
GLM-5 ✅ 32768 0.52
Claude-Sonnet-4.5 ❌ 32768 0.51
GPT-5.4 ❌ 32768 0.36
For the complete comparison, see here：https://www.kaggle.com/code/jiazhuang/nemotron-mainstream-llm-performance-comparison
5
add_reaction
comment
17 Comments
Hotness
undo
redo
format_size
format_bold
format_italic
format_strikethrough
insert_link
format_quote
code
format_list_numbered
format_list_bulleted
table_chart
insert_photo
smart_display
insert_emoticon
help
 This comment will be made public once posted.
attach_file
Post Comment
James Day
Posted 2 months ago
· 1172nd in this Competition
arrow_drop_up
13
arrow_drop_down
more_vert
Here are similar statistics for some local models with a 16K token reasoning budget & same prompt template as the official metric.
Model Quantization Temperature Accuracy (%) Avg Tokens / Correct
Qwen3.5-27B FP8 1.0 72.3 5851
Qwen3.5-27B AWQ-4bit 1.0 71.2 6264
Qwen3.5-27B FP8 0.6 65.8 6601
nemotron-sft-baseline FP8 1.0 69.2 2446
nemotron-sft-baseline FP8 0.0 68.4 2004
Qwen3-Next-80B-A3B-Instruct AWQ-4bit 1.0 62.2 5246
Nemotron-3-Super-120B-A12B GGUF UD-IQ4_K_XS 1.0 54.9 4111
Nemotron-3-Nano-30B-A3B NVFP4 1.0 54.8 4465
Nemotron-3-Nano-30B-A3B NVFP4 0.7 54.8 3954
gpt-oss-20b MXFP4 0.7 51.5 2435
gpt-oss-20b MXFP4 1.0 51.2 2710
The "nemotron-sft-baseline" LoRA above scored 0.66 LB. The accuracy figures above were measured on 1K questions from outside the training dataset (random partitioning).
One common problem is that models tend to think too long and hit the 8K token limit in the submission environment, thereby crippling accuracy. A histogram illustrating that for the Nemotron foundation model is included below.
reply
Reply
2
add_reaction
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Impressive! You did exactly what I had in mind. Thank you so much.
reply
Reply
add_reaction
React
Serhii Hrynko
Posted 2 months ago
· 1262nd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Where is GPT-OSS-120B (one that crushes AIMO3)?
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I will have a try
reply
Reply
add_reaction
React
Serhii Hrynko
Posted 2 months ago
· 1262nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Also accessing proprietary LLM via API where it is backed by dynamic math specific RAG is not the same as running standalone model without access to any tools or inference time data augmentation.
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Subsequent considerations will include the addition of some locally deployed model evaluations.
reply
Reply
add_reaction
React
HZM
Posted 2 months ago
· 995th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
could you please set max_tokens as 7680, cause our vllm infere max_tokens is that. 32k + is too much
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
if set 7680，most of the requests will fail
reply
Reply
add_reaction
React
lucian kucera
Posted 2 months ago
· 2168th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
But if u dont set it to 7680, then well its not really relevant, since token constrain plays huge role in this competition. But nontheless its interesting, but would be much more interesting with token generation contraint, so its easier to compare with nemeotron directly.
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
You are right. The current testing is still quite rudimentary. Perhaps we could find a way to control the "thinking budget" rather than letting it fail due to exceeding the max_token limit.
reply
Reply
add_reaction
React
datnt114
Posted 2 months ago
· 94th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I think we already have response reasoning, so we can use another LLM to summarize it to fit the 7680 tokens.
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Indeed, that is a direction worth trying.
reply
Reply
add_reaction
React
ImperfectKitto
Posted 2 months ago
· 608th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Interesting to see GPT-5.4 fail so badly
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
The default reasoning effort of GPT-5.4 model is 'none', which means no reasoning. May be it's the reason.
reply
Reply
add_reaction
React
Deval Mukherjee1
Posted 2 months ago
· 1458th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Can I ask how are you testing out these models ? When I tried to do that the safety filter for the API doesn't let me.
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I run the requests on my own computer
reply
Reply
add_reaction
React
DePie
Posted 2 months ago
· 957th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The distribution of the questions you use is unbalanced.
2 types "equations transformation" (prefix: In Alice's Wonderland, a secret set of transformation rules is applied to equations) and "bit manipulation" (prefix: In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers) are easier to get wrong, but there are fewer samples of them (11 and 13 compared to ~20 for the rest)
reply
Reply
add_reaction
React
Zhuang Jia
TOPIC AUTHOR
Posted 2 months ago
· 162nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I haven't had a chance to analyze the data distribution yet; I simply randomly sampled 100 instances from the training set.
reply
Reply
add_reaction
React
This comment has been deleted.
Serhii Hrynko
Posted 2 months ago
· 1262nd in this Competition
arrow_drop_up
7
arrow_drop_down
more_vert
Thank you Claude, we always appreciate your feedback.
reply
Reply
22
1
add_reaction

# SFT vs GRPO: Why One Works Fine and the Other Doesn't

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/690161#3462928
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 10704

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
Mainstream LLM Performance Comparison：Gemini-3.1-Pro delivers the best performance, while DeepSeek-V3.2 is also highly impressive.
Kaggle CLI — Develop Locally and Run on RTX Pro 6000 GPU
Strategy to solve 85% of bit manipulation
Visualize the problems and completions from the base model
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
KOMIL PARMAR · 1449TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
58
arrow_drop_down
more_vert
Why GRPO is Painfully Slow on Nemotron (and the Fix)
If you've tried GRPO fine-tuning on Nemotron-3-Nano-30B and noticed generation crawling at ~2 tokens/sec, you're not alone. I spent a while debugging this, so here's a full breakdown of what's going on, why it happens, and how to fix it.
SFT vs GRPO: Why One Works Fine and the Other Doesn't
SFT is "Open-Book"
Think of SFT (Supervised Fine-Tuning) like a student studying with the answer key right next to them. The model (student) sees the full conversation, i.e. both the question AND the correct answer, all at once. It just does one big forward pass across the entire sequence, compares its predictions to the right answer, and adjusts. Like if you are simply reading the question and the answer and say 'Ah! that's how to solve it. Okay, got it. Let's move on'.
The key thing: SFT never actually generates text. The student never try to answer the question on their own. It hence processes everything in parallel. The model never has to produce one token, then the next, then the next. It's like reading a book versus writing one, reading is fast because you see all the words at once.
GRPO is "Closed-Book Exam"
GRPO (Group Relative Policy Optimization) works completely differently. It gives the model a question and says "write your answer from scratch." The model has to generate a full response one token at a time, token 1, then token 2, then token 3, and so on. Then it does this multiple times (typically 4+ completions per prompt) to compare which attempts were better. So its like the student tried to answer the same question 4+ times, than the teacher reviewed the answer (only the answer, not the whole process or reasoning) and said, whatever you did on your first and forth trial (for example) was correct, so do more like that.
This token-by-token generation is where the speed problem hits.
The Speed Bug: A Simple Name Mismatch
How Autoregressive Generation Should Work
When a model generates text token-by-token, it uses a cache to avoid redundant computation. Imagine you've already generated "The answer is": you don't want to reprocess those 3 tokens from scratch every time you generate the next word. The cache (KV) stores all the internal states so each new token only requires a tiny bit of new computation.
With caching: ~30-50 tokens/sec. Without caching: ~2 tokens/sec.
What Goes Wrong with Nemotron
NVIDIA's modeling_nemotron_h.py has a parameter name mismatch between two functions that need to talk to each other:
prepare_inputs_for_generation() — runs before each token, prepares the inputs. It creates the cache and passes it forward as past_key_values.
forward() — the actual model computation. It expects to receive the cache as cache_params.
See the problem? Function A sends the cache labeled as past_key_values. Function B looks for a parameter called cache_params. Since the names don't match, the cache lands in **kwargs and gets silently ignored. No error, no warning, just the model quietly recomputing everything from scratch on every single token.
This is why SFT works perfectly (no generation, no cache needed) but GRPO grinds to a halt (generation on every step, cache broken).
The Numbers
Without fix: ~2 tokens/sec. A single GRPO step with 4 completions × 2048 max tokens could take minutes.
With fix: ~38 tokens/sec. Nearly 20× faster.
At 2 tok/sec, a 500-step GRPO run would take days. At 38 tok/sec, it fits within a Kaggle session.
The Fix
Thanks to CPMP for confirming this in this discussion here — transformers >= 5.3.0 fixes this bug natively. The library now has built-in NemotronH support with the correct parameter mapping.
What to do:
Step 1: Install transformers >= 5.3.0. On Kaggle (no internet), upload the wheel as a dataset:
!pip install -q --no-deps --force-reinstall "/kaggle/input/your-dataset/transformers-5.5.3-py3-none-any.whl"
The --no-deps flag prevents pip from trying to download dependencies (no internet on Kaggle, if you don't do that, code will try to use internet). The --force-reinstall flag is needed because Kaggle comes with an older transformers pre-installed, and pip will skip the install thinking "it's already satisfied" without this flag.
Step 2: Remove trust_remote_code=True from your model loading:
# BEFORE (uses old buggy modeling_nemotron_h.py from model repo)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, ...)

# AFTER (uses fixed built-in transformers implementation)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, ...)
This is critical — even with transformers 5.5.3 installed, trust_remote_code=True pulls in the OLD modeling_nemotron_h.py from the HuggingFace model cache, which overrides the library's fix entirely. Drop the flag and let the library's native implementation handle it.
Step 3: Also note that with the built-in implementation, gradient_checkpointing=True will throw a ValueError because NemotronHForCausalLM doesn't declare support for it. Set gradient_checkpointing=False in your training config.
TL;DR
SFT GRPO
Generation needed? No (parallel forward pass) Yes (token-by-token)
Cache needed? No Yes
Affected by bug? No Yes — 20× slowdown
Fix: transformers >= 5.3.0 + remove trust_remote_code=True. That's it. Thanks CPMP!
Hope this saves someone a few hours of debugging (took days in mine 🥲)
12
add_reaction
comment
11 Comments
1 appreciation comment
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
PatrickKarle
Posted a month ago
arrow_drop_up
1
arrow_drop_down
more_vert
No matter what gets used, thanks for your great work and sharing.
reply
Reply
1
add_reaction
Durga Kumari
Posted a month ago
arrow_drop_up
0
arrow_drop_down
more_vert
Great catch that silent KV cache miss explains the huge slowdown.
reply
Reply
1
add_reaction
Yang Wei Hao
Posted 2 months ago
· 3100th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
good method, thats very useful.😀
reply
Reply
1
add_reaction
namnamna
Posted 2 months ago
· 359th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
this is great work
reply
Reply
1
add_reaction
Sypher_S
Posted a month ago
· 529th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Hi, I have a question regarding the proper way to handle multi-stage adapters for this challenge. My current pipeline involves an initial SFT phase, followed by GRPO to enhance reasoning. Since the evaluation script loads a single LoRA adapter against the original NVIDIA base model, I am concerned about maintaining the SFT formatting. If I train GRPO on top of a merged SFT checkpoint, should I submit the GRPO adapter directly, or should I re-calculate the total delta (Final Model - Original Base) to ensure the SFT knowledge isn't lost? Thanks!
reply
Reply
add_reaction
React
Giovanny Rodríguez
Posted 2 months ago
· 40th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Did you also try doing it with vllm?
reply
Reply
add_reaction
React
Komil Parmar
TOPIC AUTHOR
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
No I haven't tried it with vllm yet. Will check out. However, I was earlier bounded by the input tokens/s speed rather than the output speed. For pure inference, didn't try for training. Check this: 2752/38000 [45:39<7:09:15,  1.37it/s, est. speed input: 156.72 toks/s, output: 2074.51 toks/s]
reply
Reply
1
add_reaction
Giovanny Rodríguez
Posted 2 months ago
· 40th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
An alternative solution would be to use ORPO.
reply
Reply
add_reaction
React
4 more replies
arrow_drop_down
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
have this fixed your grpo slow generation?
NemotronH requires an initialized `NemotronHHybridDynamicCache` to return a cache. None was provided, so no cache will be returned.
i am getting this and taking for ever to generate token
reply
Reply
add_reaction
React
Komil Parmar
TOPIC AUTHOR
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Yes, follow this 3 steps and that warning will be gone.
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
and speed is increased right? and can you please public transformers-5.5.3-py3-none-any.whl dataset
reply
Reply
add_reaction
React
Komil Parmar
TOPIC AUTHOR
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
In the 'The Numbers' section, I have mentioned the before and after speed.
Earlier it was ~1-2 tokens/s
Now its 38 tokens/s
This won't match the actual inference speed, because here (for GRPO and other training methods) you also have to keep a track of the gradients. It's in training mode, not inference.
reply
Reply
add_reaction
React
This comment has been deleted.
This comment has been deleted.
Appreciation (1)
jane96
Posted 5 days ago
· 1159th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
thanks！It‘s work！

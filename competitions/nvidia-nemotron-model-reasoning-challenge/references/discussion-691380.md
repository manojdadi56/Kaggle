# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/691380
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 6446

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
Synthetic data generation allowed
How are GPU hours calculated?
RL Training
Is 0.86 already the limit?
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
SHEHAB ANWER · 2769TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
-4
arrow_drop_down
more_vert
Nemotron ATLAS: Architecture-Targeting LoRA with Augmented Solvers
Hi Kaggle community & NVIDIA team 👋
I'd like to share ATLAS, my end-to-end pipeline for the NVIDIA Nemotron Reasoning Challenge. NOTEBOOK LINK
ATLAS stands for Architecture-Targeting LoRA with Augmented Solvers. It combines high-quality programmatic reasoning traces with efficient LoRA targeting tailored to Nemotron’s hybrid Mamba-2 + MoE + Attention architecture.
Key Techniques
Solver-Augmented Training (SAT)
Programmatic solvers generated verified Chain-of-Thought traces for all 6 puzzle types. Success rate reached 100% on 5 types and nearly 100% on cipher (using ground-truth disambiguation), resulting in 788 high-quality traces for SFT.
Architecture-Targeting LoRA (ATLAS)
Instead of applying LoRA to all ~5,888 routed MoE experts, I targeted only the always-active modules: shared experts, Mamba-2 in/out projections, and full Attention (Q/K/V/O). This reduced targeted base parameters by ~95% while focusing learning where it matters most.
Critical-Token Weighted SFT + Curriculum Learning
Applied 5× loss weight on tokens inside \boxed{}
Sorted samples by length into easy/medium/hard tiers
Progressive curriculum across 3 epochs: Easy → Easy+Medium → All
Training Summary (proto-run on 0.1 dataset fraction)
788 traces → 710 train / 78 val
Balanced type distribution (all ~20%)
Curriculum tiers: easy=236, medium=237, hard=237
Training curves (rank-32 LoRA, bfloat16):
Epoch 1 (Easy): Train Loss 1.4471 → Val Loss 0.9648 (PPL 2.62)
Epoch 2 (Easy+Medium): Train Loss 0.7172 → Val Loss 0.5321 (PPL 1.70)
Epoch 3 (All): Train Loss 0.3461 → Val Loss 0.2639 (PPL 1.30) ✅
Best checkpoint was restored and exported as the final LoRA adapter (submission.zip).
The full notebook with solvers, ATLAS targeting logic, curriculum implementation, and training logs is linked below. Happy to answer any questions or discuss details!
— Shehab Anwer
Artificial Intelligence
GPU
Python
Research
Science and Technology
add_reaction
React
3 Comments
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
Omar
Posted a month ago
· 1202nd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Your method ⬇️
reply
Reply
1
add_reaction
Shehab Anwer
TOPIC AUTHOR
Posted a month ago
· 2769th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@omarafik thanks for sharing - have you run it on full dataset scale & got this score? Also, there is a bug I am working regarding gravity traces..
reply
Reply
add_reaction
React
Omar
Posted a month ago
· 1202nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I have just submitted the zip file, I also have a question, i noticed that you use the answers to generate CoT traces. How do you ensure that the traces are correct? Sometimes the model cheats or doesn't strictly follow the prompt and ends up giving a method that isn't actually valid.
reply
Reply
add_reaction
React
Shehab Anwer
TOPIC AUTHOR
Posted a month ago
· 2769th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@omarafik Great question and a concern worth clarifying if I get your question correctly: my attempt involves no model in trace generation - only programmatic solvers: regex parsing, arithmetic, boolean function enumeration, and string templates. To my understanding there would not be a "model cheats" failure. IOW: reasoning chain is the computation, not a posthoc explanation by a model to filter: A) Numeral, unit_conversion, gravity, binary, equation_transform) never reference the answer parameter internally. They derive everything from the prompt alone: Roman numeral tables, ratio averaging, d=1/2gt^2, boolean function enumeration over examples, positional mapping from same-operator examples. B) Cipher solver builds the decryption mapping from pairs, then uses check_answer(decrypted, answer) as a rejection gate so that the answer validates the result but never enters the mapping construction.
Again this is a protorun - where I attempt (and working on) the six types pass through a pipeline-level check_answer(computed/ground_truth) filter that rejects any trace when the solver produces a wrong result.
Additionally, binary and equation_transform use internal hold-out cross-validation of last example, solve from N-1, and verify against the held-out before even reaching the pipeline filter. This acts as a second layer of quality control independent of the answer.
So the answer's role is strictly as a post-computation filter to rejects wrong derivations without role in building them.
The tradeoff: If no filtering based on answers, coverage drops for the harder types (cipher, binary, equation_transform) due to ambiguity: cipher x alphabet coverage in cipher, binary x boolean functions , insufficient examples in x equations.
The filter doesn't make wrong reasoning "look right" — it discards ambiguous cases and ensures only unambiguously correct derivations enter the SFT training set.
Happy to dig into any specific solver if you want more detail - Again, this is a protorun and hopefully gets even better soon!
reply
Reply
add_reaction
React

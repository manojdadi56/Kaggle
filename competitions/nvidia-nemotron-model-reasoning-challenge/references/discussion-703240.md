# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/703240
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5671

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
Nemotron ATLAS: Architecture-Targeting LoRA with Augmented Solvers
Synthetic data generation allowed
How are GPU hours calculated?
RL Training
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
emoji_people
TAHA · 421ST IN THIS COMPETITION · POSTED 12 HOURS AGO
arrow_drop_up
-4
arrow_drop_down
more_vert
From 8% → 71% on Cryptarithm Tasks, But Score Still Stuck at 0.86
I managed to achieve near-100% performance on:
cryptarithm_deduce
cryptarithm_guess
equation_numeric_guess
This was done with heavy assistance from Claude Opus 4.8 (max effort), along with reverse engineering the entire dataset generation pipeline and solver logic (XHigh + ultracode).
❯ /usage
Total cost:            $129.79
Total duration (API):  5h 23m 36s
Total duration (wall): 2d 7h 44m
Total code changes:    2156 lines added, 583 lines removed
Usage by model:
claude-opus-4-7:
245.9k input
342.3k output
88.6m cache read
6.4m cache write
($94.27)
claude-opus-4-8:
50.6k input
135.8k output
22.7m cache read
3.3m cache write
3 web searches
($35.52)
(base) rust_solution % cargo run --release -- --solve /WORK/train_classified.csv
Finished `release` profile [optimized] target(s) in 0.11s
Running `target/release/rust_solution --solve /WORK/train_classified.csv`
Reading CSV from: /WORK/train_classified.csv
Total targets to evaluate: 959
[00:00:32] [########################################] 959/959 (100%) | ETA: 0s | Solved: Done!
--- RESULTS ---
Total targets: 959
Solved: 959 (100.00%)
Correct: 959 (100.00%)
Time taken: 32.863204125s
Right now I’m experimenting with fine-tuning on both the solver outputs and a new CoT generator.
Current validation breakdown:
Category Correct Total Weightage Accuracy Contribution
bit_manipulation 142 169 17.8% 84.0% 14.9%
cipher 158 162 17.1% 97.5% 16.6%
cryptarithm_deduce 13 71 7.5% 18.3% 1.4%
cryptarithm_guess 10 14 1.5% 71.4% 1.1%
equation_numeric_deduce 42 48 5.1% 87.5% 4.4%
equation_numeric_guess 3 7 0.7% 42.9% 0.3%
gravity 156 159 16.7% 98.0% 16.4%
numeral 146 149 15.7% 98.0% 15.4%
unit_conversion 168 171 18.0% 98.0% 17.7%
TOTAL 838 950 100.0% 88.2% 88.2%
I’m still following roughly the same category blend as Tong Hui Kang:
bit_manipulation         1,754
cipher                   1,656
unit_conversion          1,070
gravity                  1,055
numeral                    730
equation_numeric_deduce    658
cryptarithm_deduce         627
cryptarithm_guess          154
equation_numeric_guess     126
However, my score still seems stuck around 0.86.
As the cryptarithm categories become stronger, I’m seeing some regression in categories that previously scored nearly 100%, especially:
gravity
numeral
unit_conversion
For comparison, Tong Hui Kang’s results were:
Category Accuracy
bit_manipulation 88.2%
cipher 97.5%
cryptarithm_deduce 8.5%
cryptarithm_guess 21.4%
equation_numeric_deduce 87.5%
equation_numeric_guess 0.0%
gravity 100.0%
numeral 100.0%
unit_conversion 100.0%
Even though I significantly improved the cryptarithm categories, the overall score barely moved because of the regressions elsewhere.
At this point I feel like if I can recover even a small amount of performance in the previously saturated categories while keeping the cryptarithm gains, I should be able to push comfortably beyond 0.86+.
Would love to hear ideas from others who hit similar multi-task balancing issues during fine-tuning.
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
SHUN_04
Posted 6 hours ago
· 1693rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you for the helpful information. I have one question I'd like to ask: did you make any of your own modifications to the baseline published by @huikang ? I am using training data with the same distribution, and I haven't changed the training order or the config, but my LB score is 0.84 and won't reach 0.86. Could my training method be fundamentally flawed? I am running it on tinker. I have invested a considerable amount of time and money into this, and I am feeling rather anxious that I haven't even been able to reach the 0.86 baseline. I apologize for the trouble, but I would greatly appreciate a reply.
reply
Reply
add_reaction
React
Tong Hui Kang
Posted 6 hours ago
· 1173rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I think people has reproduced 0.86 training notebooks on Kaggle end-to-end, I suggest you replicate that first.
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted 12 hours ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
reply
Reply
add_reaction
React

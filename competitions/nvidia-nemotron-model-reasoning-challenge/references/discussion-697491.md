# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/697491
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 10609

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
Per-Category Error Analysis After SFT (0.63 LB) — Where the Real Bottlenecks Are
Zero shot predictions
Something wrong -- My notebook of 0.80+ now scores 0.77
RTX PRO 6000 Blackwell — CUDA kernel incompatibility status + GPU time spent debugging
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
TAHA · 421ST IN THIS COMPETITION · POSTED 24 DAYS AGO
arrow_drop_up
16
arrow_drop_down
more_vert
Why a "Better" Dataset Scored Worse: Lessons on Logprobs, Gradient Saturation, and SFT Bugs
Hey everyone,
Over the last week, I went down a massive rabbit hole trying to improve the synthetic Chain of Thought (CoT) generation for the hard categories in this competition (cryptarithm_deduce, cryptarithm_guess, equation_numeric_guess).
I managed to write a much better deterministic algorithm to solve these, pushing my synthetic dataset accuracy from the baseline 87.7% to 95.8%. I assumed this would guarantee a leaderboard boost. Instead, my first few runs crashed to 0.73, and even my stabilized runs hovered around 0.82–0.84, failing to beat the 0.85 baseline.
I wanted to share exactly why a "better" dataset doesn't automatically equal a better LB score, and the three massive traps I fell into (and how to fix them).
The Data Comparison
Here is the baseline (Tong's) generation vs. my custom generation. Notice the massive jump in the hard categories:
Original Baseline (LB ~0.85):
Category Total Accuracy
bit_manipulation 1602 85.1%
cipher 1576 100.0%
cryptarithm_deduce 659 8.2%
cryptarithm_guess 164 6.7%
equation_numeric_deduce 596 90.6%
equation_numeric_guess 136 15.4%
gravity 1597 100.0%
numeral 1576 100.0%
unit_conversion 1594 100.0%
TOTAL 9500 87.7%
My Custom Generation (LB ~0.82-0.84):
Category Total Accuracy
bit_manipulation 1602 85.1%
cipher 1576 100.0%
cryptarithm_deduce 659 89.8%
cryptarithm_guess 164 85.4%
equation_numeric_deduce 596 90.6%
equation_numeric_guess 136 92.6%
gravity 1597 100.0%
numeral 1576 100.0%
unit_conversion 1594 100.0%
TOTAL 9500 95.8%
Trap 1: Algorithmic Complexity vs. LLM Learnability (The Logprob Test)
Just because a Python script can solve a cryptarithm perfectly using backtracking or constraint solving doesn’t mean a language model can learn to predict those same steps token by token.
I checked this by looking at the base model’s loss (negative log probability) across different datasets:
AVG DIFFERNCE :
cryptarithm_deduce: ~0.4
cryptarithm_guess: ~0.20–0.3
equation_numeric_guess: roughly the same as Tong's
The takeaway is simple but easy to miss. Even though the data was correct, the reasoning paths in the “deduce” set were heavier and harder for the model to follow. Lower logprob data tends to be easier for the model to learn, even if it’s less “clean” from a traditional algorithmic point of view. Refer to LogProb Data Here
Trap 2: Catastrophic Forgetting via Oversampling
Because my hard categories only made up ~10% of the dataset, I initially oversampled them by 14x. This resulted in an LB score of 0.73.
By force-feeding the model massively complex cryptarithm gradients (with a standard learning rate of 2e-4), I triggered gradient saturation. The optimizer prioritized memorizing the hard math, and in doing so, it violently overwrote the base model's knowledge of basic math, gravity, and ciphers.
Fix: Cap oversampling at 3x, lower the learning rate to 5e-5, and increase gradient accumulation to 64 to smooth the updates.
My Notebooks & Datasets
If anyone wants to look at the code, the logprob filter, or the 95% dataset, here they are:
Datasets:
Nemotron-0-90 (The 95.8% Dataset)
Nemotron-Logprob (Pre-computed losses)
Notebooks:
Batched Logprob Filter + Train
End-to-End Finetuning for LB 0.82
Nemotron SFT Final 0.83 LB
TL;DR: To win, you can't just have a 100% accurate synthetic generator. You must merge your hard CoTs with the easy baseline data (to act as an anchor), manage your gradients so you don't overwrite base knowledge, and ensure your token masking is bulletproof.
Happy to hear if anyone else ran into the gradient saturation wall! Any Suggestions? then drop down! ;D
3
1
add_reaction
10 Comments
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
Ogurtsov
Posted 24 days ago
· 730th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
@tahaalam2009 Why do you think this is better CoT and correct solution?
Based on character frequency heuristics, we guess the answer.
output: 【@&】-> 【{@&}】
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted 24 days ago
· 421st in this Competition
arrow_drop_up
-3
arrow_drop_down
more_vert
I haven't evaluated the dataset even once , i get it now its just filled with garbage
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted 24 days ago
· 421st in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
I made a dataset so trash never realized how bad it was 🥀
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted 24 days ago
· 1896th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I think you have to make your algorithm appeal to its priors because you're limited in how much you can move the model from its base. I came up with a very clever and mechanical way to solve bits, but I had to over-engineer it to fit in the 7.8k context (like converting Binary to Hex) -- my average loss was sub 0.01 , but it translated to only about 12% accuracy. Too expensive for me to keep trying that route though (long traces == expensive to train).
Almost all my success has been keeping all traces less than 1300 tokens. (Originally 900).
It feels impossible to iterate over long traces -- as least with what I know. Takes several hours for an eval, and very expensive to train!
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 18 days ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@tahaalam2009 - theres something very fishy about your results
cryptarithm_guess 164 85.4% equation_numeric_deduce 596 90.6% equation_numeric_guess 136 92.6%
how can the guess categories achieve parity w/ the non-guess categories?
even if you SMT solved these problems (which definitely is not a COT compatible algorithm) I dont think these results are possible
Are you sure you aren't passing the golden answer into your solver?
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted 18 days ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yeah, after digging deeper I realized a lot of the dataset I generated was honestly pretty garbage for SFT. My assumption was that forcing the model to “guess” more would improve generalization, but that mostly didn’t translate into better LB performance. BUT it went from 1.5% -> 15.3% That said, the cryptarithm_guess category actually did improve on the validation script, which is why I initially thought the approach was working. I wasn’t passing any golden answers into the solver the issue was more that the generated CoTs were noisy/non-learnable and the model couldn’t effectively absorb them.
So the main lesson for me was that solver correctness != learnable reasoning traces for an LLM.
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 17 days ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I dont think your solver is correct either 1) the cryptarithm problems are inherently ambiguous and can'e be solved w/ the same level of accuracy as equation numeric 2) the guess problems are also inherently ambiguous - i think ub for these problems is not more than 20%
Yet both problem categories achieve comparable accuracy to equation numeric deduce in your solver results
You need to look carefully at what your solver is doing - and what modifications to Tong's codebase you made
Im not really sure what the problem could be - but I think its something along the lines of passing the golden answer into your predictor or producing many answers and checking if any match golden
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted 16 days ago
· 421st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Vibe coding landed me in trouble and the dataset was just "guesswork" , I have rewritten an algorithm in rust and it solves 60% of problems and rest 40% are unsolvable i believe , once i test out ill let you guys know!
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 15 days ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yeah that was about what I observed also
reply
Reply
add_reaction
React
Nic Barthelemy
Posted 23 days ago
· 491st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I went all in initially on strong solvers and arrived at exactly the same conclusion as you. I'm still hunting like most of the field sitting at 0.86LB waiting for that aha that gets at last a 0.01 - 0.02 bump with deterministic scoring.
reply
Reply
add_reaction
React
Giovanny Rodríguez
Posted 23 days ago
· 40th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
You also need to remember the winner model multiplied by 11 in the cry sample, which is more memorization than anything else.
reply
Reply
add_reaction
React
This comment has been deleted.
emoji_people
Taha
TOPIC AUTHOR
Posted 24 days ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I understand that, but I don’t see why a better algorithm wouldn’t improve generalization shouldn’t clearer, more accurate reasoning help the model learn better? and also log probs dont differ much between two
reply
Reply
add_reaction
React

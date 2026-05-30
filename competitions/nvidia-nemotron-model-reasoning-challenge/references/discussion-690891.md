# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/690891
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5545

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
AcceleratorError: no kernel image available on RTX PRO 6000
Temp Blackwell Workaround
What should be included in submission.zip?
90.7% Synthetic CoT Accuracy -> LB Drop: A Warning on Data Generation & Thanks to Donald
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
ZEJUN_ · 473RD IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
4
arrow_drop_down
more_vert
There are still many missing pieces of the puzzle: equation and cryptarithm.
Thank huikang for providing such a powerful new starting point for the latter part of this competition. Congratulations! If you run the longer notebook and look at the report results, you will find that the accuracy rates for the three categories of problems, cryptarithm_deduce, cryptarithm_guess, and equation_numeric_guess, are all very low. These will be the main directions for everyone's efforts after this incredibly powerful baseline.
To solve them, while I tried to solve them independently, I also tried to get the LLM to generate CoT. Unfortunately, neither I nor the LLM could provide reasonable steps for the answers in the CSV file. Does anyone have any experience in solving these complex and difficult mapping problems? If not using human effort but LLMs, what models do you use to generate accurate CoT? I think this is very meaningful for this competition and will enable the top-kagglers to aim for a perfect score.
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
2
arrow_drop_down
more_vert
Two sub-problems worth separating.
Problem one: CAN we solve them algorithmically?
cryptarithm_deduce — yes, with brute force. The operator IS in the examples, just hidden under a substitution cipher. Enumerate cipher permutations times operator primitives and check consistency across examples. Expensive but tractable on GPU. We hit about 95% solver coverage via exhaustive GPU sweeps.
cryptarithm_guess and equation_numeric_guess — genuinely info-theoretic. The unknown operator does not appear anywhere in the examples, so no amount of analysis recovers it. Best you can do is heuristic guesses like absolute difference, concatenation, output-length-based fallback. See my earlier post in this forum.
Problem two: Can we make the model generate those solver CoTs?
This is the real problem, and where almost everyone fails. Two approaches we have seen.
LLM-generated CoTs, which is what Zejun tried. Frontier models like Claude, GPT, DeepSeek hallucinate constantly on cipher-plus-operator puzzles. They get the answer right about 30% of the time but the reasoning is wrong, so training on them teaches the model to guess confidently rather than derive correctly. Not recommended.
Algorithmic CoTs, which is Tong Hui Kang's approach. Write Python that produces the exact derivation as text, mirroring what a solver does step-by-step. This is how THK got bit_manipulation from 21% to 85%. The bit_manipulation playbook is published at discussion 690307.
What we think the cryptarithm equivalent of THK's bit trick looks like:
Enumerate candidate cipher maps in parallel, token-by-token, using an output-length hash analogous to his bitsum to prune.
Show the matching step for each candidate rather than trying to reason the map.
Keep each token derivable from a small fixed context, no global reasoning required.
Nobody has published this for cryptarithm yet. Whoever writes it first is probably in the top 10 at the end.
For the _guess subtypes: accept the 15-20% ceiling and optimise the heuristic pick. Output-length match is the best signal we have found.
reply
Reply
add_reaction
React
FO-SHIZZLE
Posted a month ago
· 139th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
My guess is that this particular dataset was derived from some internal work done at Nvidia. I am almost sure this has very real and practical implications for some sort of translation problem they face internally. It is highly unlikely that the solutions to these problems exist in the open domain. They likely exist internally but they are trying to figure out a way to speed up things without exposing their trade secrets. In short, the cryptic nature of the problems are because they are protecting trade secrets and just need the best model so they can follow the recipe internally and speed up some sort of translation or solve some important task.
reply
Reply
add_reaction
React

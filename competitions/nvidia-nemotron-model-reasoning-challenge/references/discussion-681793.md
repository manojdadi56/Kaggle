# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681793
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5294

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
Training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences
Save order db V1
Let's learn from Google Tunix Hack for Nemotron
Metric Update
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
DEVIN ANZELMO · POSTED 2 MONTHS AGO
arrow_drop_up
29
arrow_drop_down
more_vert
Are problem types the same for train and test?
There appear to be six different problem types in the training set:
numbers are secretly converted into a different numeral system
the gravitational constant has been secretly changed
a secret set of transformation rules is applied to equations
secret encryption rules are used on text
a secret bit manipulation rule transforms 8-bit binary numbers
a secret unit conversion is applied to measurements
Are these the same set of problem types that appear in the test set? The approach to this competition is completely different depending on whether we are looking at all new question types or not so it would be helpful to know the answer to this question.
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
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
11
arrow_drop_down
more_vert
Yes, they are the same. The distribution should be roughly similar as well.
reply
Reply
add_reaction
React
Yuchen20
Posted 2 months ago
· 1904th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
Yes, they are the same. The distribution should be roughly similar as well.
That said, wouldn’t it be possible that we can produce some simple programmatic approach that works for a whole class of similar problems, so the model can read the answer from the function output, instead of actually requiring reasoning?
For example, for a problem like this:
In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:
14.89 m becomes 21.91
9.37 m becomes 13.79
5.73 m becomes 8.43
26.82 m becomes 39.46
Now, convert the following measurement: 23.28 m
one could easily write a script like:
import re
text = """
In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:
14.89 m becomes 21.91
9.37 m becomes 13.79
5.73 m becomes 8.43
26.82 m becomes 39.46
Now, convert the following measurement: 23.28 m
"""
# Extract training pairs like: 14.89 m becomes 21.91
pairs = [(float(a), float(b)) for a, b in re.findall(r'(\d+\.\d+)\s*m\s*becomes\s*(\d+\.\d+)', text)]
# Estimate conversion factor by averaging b/a
factor = sum(b / a for a, b in pairs) / len(pairs)
# Extract the final value to convert
target = float(re.search(r'convert the following measurement:\s*(\d+\.\d+)\s*m', text, re.I).group(1))
# Compute Wonderland value
result = target * factor
print("pairs:", pairs)
print("target:", target)
print("wonderland value:", round(result, 2))
which derives:
pairs: [(14.89, 21.91), (9.37, 13.79), (5.73, 8.43), (26.82, 39.46)]
target: 23.28
wonderland value: 34.25
Then the result could simply be appended to the prompt, given that prompt engineering is allowed.
reply
Reply
add_reaction
React
KCLamm
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
Seems to me that there is a fixed pipeline for the model evaluation, in which the only thing kagglers are supposed to change is the LoRA part. The 'you can experiment with: prompting strategies, …' part in the rules is followed by 'Participants may use any training framework, tooling, or workflow to produce their LoRA adapter,' may be indicating the prompt engineering thing mentioned is about training LoRA only.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
Aditya Todi
Posted 10 days ago
· 1940th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Are the rules for each individual subtypes are consistent as well with training data or should we expect them to deviate and have some new rules which were not seen in the training dataset?
For example, in the subtypes like equation transformation rules, bit manipulation there are roughly 20-25 operations that covers the entire training dataset. Should we expect them to remain locked or does the test data has some rules which were not seen in the training data provided?
Please help if you can. TIA
reply
Reply
add_reaction
React

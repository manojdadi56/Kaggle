# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687063
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4277

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
Train locally and get lower scores.
Submission re-runs give different scores
Are all symbolic puzzles guaranteed to be uniquely solvable? Some seem to lack enough information
ModuleNotFoundError: No module named 'cutlass'
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
KH0A · 5TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
10
arrow_drop_down
more_vert
Inquiry regarding inference non-determinism and Open Progress Prize fairness
Hi Team, @ashleyoldacre, @ryanholbrook
I have a few concerns I'd like to clear up:
Non-deterministic Results: I’ve noticed that identical submissions are yielding different results (e.g., scoring 0.72 yesterday and 0.73 today). Is the inference environment fully deterministic, or is there a known issue?
Leaderboard Equity: Since submissions made before the metric fix seem to hold a scoring advantage, how will this be handled for the Open Progress Prize? I suggest re-running earlier submissions (which may cost a lot) or resetting the prize eligibility to include only those submitted after the fix to ensure fairness.
Thanks for the help!
add_reaction
React
5 Comments
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
5
arrow_drop_down
more_vert
Hi @llkh0a,
We are currently assessing a rescore. Due to limited GPU availability, we need to be thoughtful about how it's done. I will try to post an announcement about how we'll proceed in the next couple days.
reply
Reply
1
add_reaction
Kh0a
TOPIC AUTHOR
Posted 2 months ago
· 5th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thank you for the reply, there are some cases like for id 10ff9431, the groundtruth is 0271, but with the verify function logic as:
def verify(stored_answer: str, predicted: str) -> bool:
"""Verify if the answer matches.
For numerical answers, allow them to be judged as equal within a certain relative tolerance (1e-2);
otherwise, compare strictly as strings (case-insensitive).
"""
# Clean up strings
stored_answer = stored_answer.strip()
predicted = predicted.strip()
try:
# Try to convert the answers to floating point numbers
stored_num = float(stored_answer)
predicted_num = float(predicted)
# Use a small absolute tolerance for numbers near zero
return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
except Exception:
# Fallback to case-insensitive string comparison
return predicted.lower() == stored_answer.lower()
prediction 271 is also accepted; Could you clarify if this work as intended?
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
LLM inference is non deterministic. Even with temp=0.
reply
Reply
1
add_reaction
Chew Kok Wah
Posted 2 months ago
· 82nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The scoring Metric code is one of the problem, there is no per request seed set for vLLM.
reply
Reply
add_reaction
React
Donald Galliano III
Posted 2 months ago
· 2831st in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
i support bullet point 2. But i know we gonna see higher scores than current before April 9th.
reply
Reply
add_reaction
React

# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/699812
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4432

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
Does the final evaluation dataset necessarily exclude test questions from the training set?
[Bug or Expected?] Issue in Eval code
GRPO Traning guide needed
Just one Question on reasoning
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
WEIHAO HUANG2004 · 205TH IN THIS COMPETITION · POSTED 15 DAYS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Does the official answer parser support literal { or } inside \boxed{...}?
I ran into a potential edge case while preparing training/evaluation data for this competition.
Some official answers appear to contain literal brace characters, such as { or }. Normally, final answers are expected in a boxed format like:
\boxed{ANSWER}
However, if the answer itself contains a literal right brace, for example:
^}
then the natural boxed form would be:
\boxed{^}}
This seems ambiguous for the official parser.
From inspecting the verifier logic in nemo_rl.environments.dapo_math_verifier, the boxed-answer extraction appears to use raw character-level brace counting:
def last_boxed_only_string(string: str):
idx = string.rfind("\\boxed{")
if idx < 0:
return None
i = idx
right_brace_idx = None
num_left_braces_open = 0
while i < len(string):
if string[i] == "{":
num_left_braces_open += 1
if string[i] == "}":
num_left_braces_open -= 1
if num_left_braces_open == 0:
right_brace_idx = i
break
i += 1
return string[idx: right_brace_idx + 1] if right_brace_idx is not None else None
This means escaped braces such as:
\boxed{^\}}
do not seem to be handled as literal braces, because the parser still counts the } character inside \} as a closing brace.
So my understanding is:
\boxed{^\}}
would likely be parsed as containing ^\ rather than ^}.
Similarly:
\boxed{\{17}
may not reliably represent the literal answer {17.
My questions are:
Is this understanding correct?
If an official answer literally contains { or }, what is the expected submission format?
Should such answers be represented without \boxed{...}, or is there another accepted canonical form?
Does the official evaluator normalize LaTeX commands like \rbrace, \lbrace, \{, or \} before comparison?
This matters because a small number of examples may have official answers containing literal braces, especially in symbolic / cryptarithm-style tasks. If escaped braces are not supported, then training models to output \boxed{\}}-style answers may actually teach an invalid final-answer format.
Any clarification from organizers or others who have tested this would be very helpful.
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
Tong Hui Kang
Posted 14 days ago
· 1173rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I ran extract_final_answer from Version 15 of the metric notebook
answer = "\\boxed{^}}"
print("#", answer, extract_final_answer(answer))
# \boxed{^}} ^}
answer = "\\boxed{^\\}}"
print("#", answer, extract_final_answer(answer))
# \boxed{^\}} ^\}
answer = "\\boxed{\\{17}"
print("#", answer, extract_final_answer(answer))
# \boxed{\{17} \{17
answer = "\\boxed{\}}"
print("#", answer, extract_final_answer(answer))
# \boxed{\}} \}
The result seems to be correct?
reply
Reply
add_reaction
React
weihao huang2004
TOPIC AUTHOR
Posted 14 days ago
· 205th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks, this is very helpful！
reply
Reply
add_reaction
React

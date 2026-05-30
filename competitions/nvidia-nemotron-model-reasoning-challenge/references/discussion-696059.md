# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/696059
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 6448

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
[RESOLVED] How to use RTX Pro 6000 instead of P100 with the Kaggle API?
Midpoint Cut-off Date and the Open Progress Prize
Is it possible to win this competition using only Kaggle-provided machine resources?
How to Cut Nemotron Training from 11 Hours to 5h 40m (And Fix the "Loss Illusion")
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
BIRTLEY DORU · 137TH IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
11
arrow_drop_down
more_vert
What if the answer contains square brackets?
fa5dfa46,"In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples: $<&@ = &$@\ }->@ = -!$ }>+@< = !}} \@@@ = &<>$ Now, determine the result for: }^-`}",-^}
What if the answer contains square brackets? Can putting a box over a character correctly identify whether it's right or wrong?
add_reaction
React
8 Comments
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
Shivam Shinde
Posted a month ago
· 16th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
I had posted about this a month ago as well:
https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689284
Still no response from the hosts.
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
4
arrow_drop_down
more_vert
We missed it obviously.
We'll look into that.
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted a month ago
· 1896th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Another quick question: Because our eval/submission path loads the adapter through vLLM LoRA, the final submitted adapter cannot rely on lm_head or embedding LoRA tensors --- was that intended?
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
0
arrow_drop_down
more_vert
Yes, we aimed for simplicity.
reply
Reply
3
add_reaction
Ryan Holbrook
KAGGLE STAFF
Posted a month ago
arrow_drop_up
2
arrow_drop_down
more_vert
Thanks for flagging, and apologies for missing this the first time. I will look into it.
reply
Reply
add_reaction
React
Shivam Shinde
Posted 23 days ago
· 16th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@cpmpml @ryanholbrook I have a suggestion to fix this :https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689284#3454216
reply
Reply
add_reaction
React
Ogurtsov
Posted 24 days ago
· 730th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
@ryanholbrook If we have any chance to get fixed train dataset, please also inspect such cases (task 00d8b3db):
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
34/44 = 1
41/32 = 9
34|25 = 69
87\64 = 8853
Now, determine the result for: 69/52
It assumes answer 17/ but where does the symbol / come from? Another example (task 0c8a8a16): answer {17 contains redundant {. One more example is reported here https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/697333
reply
Reply
add_reaction
React
Kh0a
Posted 23 days ago
· 5th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I have explained it in this discussion: https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686185#3432076
reply
Reply
add_reaction
React
daulettoibazar
Posted 23 days ago
· 6th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Assuming model encounters this sample in inference time, applying abs(rev(a) - rev(b)) = output:
abs(rev(34) - rev(44)) = 1 correct 🟩 abs(rev(41) - rev(32)) = 9 correct 🟩
which leads to abs(rev(69) - rev(52)) = 71 incorrect 🟥
This indicates that the issue is not a case of multiple valid solution paths converging on the same final answer. Instead, different solution approaches can lead to different answers, which makes the problem insufficiently represented in the dataset. The only way to reliably obtain the specific ground-truth answer provided here would be to train directly on this formulation and effectively overfit to it.
reply
Reply
add_reaction
React
Ogurtsov
Posted 22 days ago
· 730th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Different meanings of the same symbol in different parts of an equation is very counterintuitive. It even violates the entire definition of equation.
reply
Reply
add_reaction
React
Giovanny Rodríguez
Posted a month ago
· 40th in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
def _extract_last_boxed(text: str) -> str | None:
if not starts:
return None
start = starts[-1]
depth = 1
i = start
while i < len(text):
c = text[i]
if c == "{":
depth += 1
elif c == "}":
depth -= 1
if depth == 0:
if text[i + 1 :].strip():
return None
return text[start:i]
i += 1
return None
Hi @ryanholbrook, the metric regex \boxed{([^}]*)(?:}|$) stops at the first }. In cryptarithm puzzles { and } can be valid answer characters — about 20% of cryptarithm puzzles in train.csv (169/823) have such answers and can never be marked correct.
reply
Reply
add_reaction
React
faizan
Posted 17 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
Not really — the box itself doesn't do anything, it's just a visual thing. What actually tells you if a character is right or wrong is the logic running behind it. The box is just how that result gets shown to you.
reply
Reply
add_reaction
React

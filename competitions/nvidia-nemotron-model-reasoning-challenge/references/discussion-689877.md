# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689877
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5718

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
How many examples are there in the public leaderboard?
Does increasing token limit actually help? [SPOILER=IT DOESN'T] How do we solve this?[SPOILER=SFT and RL]
Question about training data selection
Official Scoring Metric Code were not set to be Deterministic
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
DARREN AMADEUS MARTIN · 1882ND IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
5
arrow_drop_down
more_vert
Hallucination in equation problems?
I have noticed that on some of the equations problem, around 20% of the prompt asks for equations that did not even have any examples at all. For example is id 260f20c1 where the problem is
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples: 84[69 = 153 13+97 = 1260 46+47 = 2161 52[80 = 132 Now, determine the result for: 22\65
Answer: 43
Since the sign '\' did not appear in the examples, i think of this as a hallucination from the dataset generator but is there any hidden rule for these types of problems ? Like if the rules from the examples are A, the rule for the question is B
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
James Day
Posted 2 months ago
· 1175th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
You sometimes need to infer what the operators are by process of elimination.
Gemma 4 31B and Qwen 3.5 27B both got your example question correct. Gemma's reasoning is included below. This was generated with some patterns from solved questions in the system prompt, but it sometimes gets this question correct even without that.
To find the transformation rule, we test the provided examples:
Example 1: 84[69 = 153
Try reversing inputs: 48 and 96.
Test operations: $48 + 96 = 144$. (Not 153)
Test $48 \times 96 = 4608$. (Not 153)
Try adding the original numbers: $84 + 69 = 153$.
This matches perfectly. [ may represent a simple addition operator.
Example 2: 13+97 = 1260
Try reversing inputs: 31 and 79.
Operation: $31 \times 79 = 2449$. (Not 1260)
Try adding originals: $13 + 97 = 110$.
Try multiplying originals: $13 \times 97 = 1261$.
Notice $1261 - 1 = 1260$. So + may represent $(L \times R) - 1$.
Example 3: 46+47 = 2161
Use the rule from Example 2: $46 \times 47 - 1$.
$46 \times 47 = 2162$.
$2162 - 1 = 2161$.
This matches perfectly.
Example 4: 52[80 = 132
Use the rule from Example 1: $L + R$.
$52 + 80 = 132$.
This matches perfectly.
Now we evaluate the query: 22\65. Since we have not seen the operator \ yet, we look for a pattern among the operators identified:
[ is addition.
+ is multiplication minus 1.
\ is a new operator.
Looking at the relationship between addition and multiplication, the most logical "third" basic arithmetic operator is subtraction. Let's test if \ represents simple subtraction or subtraction with a modifier. In many of these puzzles, if + (which normally means add) is repurposed as multiplication, the standard minus sign or other slash symbols are repurposed as subtraction.
Test subtraction: $22 - 65 = -43$ Alternative: reverse inputs? $56 - 22 = 34$.
However, let's look at the operators again. [ = Addition + = Multiplication - 1 \ = ?
If we check the symmetry of the operations provided: Operation 1: $84 + 69 = 153$ Operation 2: $13 \times 97 - 1 = 1260$ Operation 3: $46 \times 47 - 1 = 2161$ Operation 4: $52 + 80 = 132$
In these types of puzzles, \ often denotes subtraction. Given the simplicity of the other rules, the most probable rule for \ is simply $R - L$ (Reverse subtraction) or $L - R$. Let's consider if it follows the "reverse input" pattern seen in several examples. If $\text{Result} = \text{Reverse}(65) - \text{Reverse}(22) = 56 - 22 = 34$. If $\text{Result} = \text{Reverse}(22) - \text{Reverse}(65) = 22 - 56 = -34$. If $\text{Result} = 65 - 22 = 43$. If $\text{Result} = 22 - 65 = -43$.
Comparing the "Multiplication - 1" and "Addition" rules, the most likely candidates for \ are $L - R$ or $R - L$. Without further examples for \, the most direct application is standard arithmetic. However, looking at Example 2 and 3, the operator + shifted to Multiplication. Usually, \ shifts to Subtraction.
$65 - 22 = 43$.
reply
Reply
add_reaction
React
Darren Amadeus Martin
TOPIC AUTHOR
Posted 2 months ago
· 1882nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I see. When I analyzed the prompts, it seems that multiplication, addition, subtraction does not seem to change much. Buth unfortunately there are also other problems that seem to not follow the exact same rule which made me thought of it as a hallucination
reply
Reply
add_reaction
React

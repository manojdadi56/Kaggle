# Wonderland Math Puzzle Solution

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684192#3436420
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 10937

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
Why GRPO is Painfully Slow on Nemotron (and the Fix)
Mainstream LLM Performance Comparison：Gemini-3.1-Pro delivers the best performance, while DeepSeek-V3.2 is also highly impressive.
Kaggle CLI — Develop Locally and Run on RTX Pro 6000 GPU
Strategy to solve 85% of bit manipulation
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
DENNIS · 2354TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
53
arrow_drop_down
more_vert
[Dataset Hallucination?] How did you resolve these problems by human?
eeae398e
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
63]67 = 4
18]81 = 9
72-22 = 95
64]48 = 16
65]15 = 5
Now, determine the result for: 65/58
When we look at the above question, slash has never appeared in the example. How can we deduce the solution? We know that ] is max(A, B) % min(A, B). No example is given for /
e7cf0394
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
88\87 = 7656
30]47 = 3047
52*15 = *37
Now, determine the result for: 97]83
If the symbol works across the "Alice Wonderland", here 30] 47 should not use concat.
It seems that the training dataset has hallucination?
One more thing, 7993452d
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
`!-`/ = -[]
[/-:( = -](
^`*<! = :%[!
%/-<< = -/(
!<+^^ = %((
Now, determine the result for: :<-]!
Would anyone share how to reason this kind of problem? I have asked some LLM, they spent many tokens but unable to find the solution. I have also tried to deduce it but in vain.
It seems the data is unbalanced and there are some hallucinations (I think it is severe) in the dataset.
2
add_reaction
comment
14 Comments
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
Yuchen20
Posted 2 months ago
· 1902nd in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
This one is not even solvable, id : 4e840a1a
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
58*93 = 152
26*21 = 48
56*65 = 122
Now, determine the result for: 15+53
the + is not even in the multi-shot example
reply
Reply
10
add_reaction
Donald Galliano III
Posted 2 months ago
· 2827th in this Competition
arrow_drop_up
-6
arrow_drop_down
more_vert
Solved here : https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/688461
reply
Reply
add_reaction
React
Durga Kumari
Posted 2 months ago
arrow_drop_up
-3
arrow_drop_down
more_vert
Nice Dataset
reply
Reply
add_reaction
React
Navneet
Posted 2 months ago
arrow_drop_up
-4
arrow_drop_down
more_vert
Cool Dataset @dennisfong
reply
Reply
add_reaction
React
Ashutosh Kumar
Posted 2 months ago
· 1899th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Exactly, for bit_manipulation and equation_transformation, despite so many rotations and handlings model hallucinates and its not fit for arithmetic operations
Bit manipulation (46% per-bit, 100% rotation):
Rotation: 9/9 = 100% — model recognizes rotation patterns perfectly Per-bit: 42/91 = 46% — model writes correct format but derives WRONG boolean rules Failed predictions heavily use complex ops (xnor: 80, or_not: 42, and_not: 33) Correct predictions dominated by simple ops (COPY: 290, AND: 90) The model can't actually compute boolean operations — this is a 3B model capability limit Equation transformation (54% numeric, 4% symbolic):
28/100 equations have numeric answers, 72/100 have symbolic Numeric: 15/28 correct (54%) — model gets arithmetic wrong in 13 cases Symbolic: 3/72 correct (4%) — arbitrary character substitutions are fundamentally impossible Common failure: model claims "a+b+1: 26,93→120? no → MATCH" — hallucinates verification
reply
Reply
add_reaction
React
Asadullah Baig
Posted 2 months ago
· 3003rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
In short training on this dataset is not recommended. Either correct it and then train on a different set?
reply
Reply
add_reaction
React
ImperfectKitto
Posted 2 months ago
· 608th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
What about the hidden testing dataset?
reply
Reply
add_reaction
React
George
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Who can solve this puzzle? * not present in the examples at all
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
81+79 = 511
19-41 = 7
58-87 = 7
Now, determine the result for: 07*79
reply
Reply
add_reaction
React
zoey
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Impossible, my opus-4.6 failed
reply
Reply
add_reaction
React
Đăng Nguyễn Hồng
Posted 2 months ago
· 1940th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I found the provided dataset is quite consistent in rule, but some questions indeed unsolvable in mathematical term (such as a query operator is unseen in example equations-there are many cases, but not sure if there are hidden rules to find it out, but until now it seems random to me). By this nature, think about it as a puzzle intead of mathematic :D
reply
Reply
add_reaction
React
Dennis
TOPIC AUTHOR
Posted 2 months ago
· 2354th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@dangnh0611 , can you give some hints on solving this?
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
`!-`/ = -[]
[/-:( = -](
^`*<! = :%[!
%/-<< = -/(
!<+^^ = %((
Now, determine the result for: :<-]!
reply
Reply
add_reaction
React
Đăng Nguyễn Hồng
Posted 2 months ago
· 1940th in this Competition
arrow_drop_up
15
arrow_drop_down
more_vert
This result obtained from a LLM by provide a detailed prompt/instructions about how to solve this kind of puzzle. Share you my obtained response, with long-CoT-thinking prunned, strip to the final result:
Digits mapping:
[ = 0, ( = 1
< = 2
/ = 3
] = 4
% = 5
: = 6
! = 7
^ = 8
` = 9
Operators:
+ = standard addition
* = multiplication
- = negative absolute difference (neg_abs_diff)
We can substitute the assigned digits into the equations to verify:
Eq 1: 97 - 93 = -04 → -|79 - 39| = -40 → reverses to -04. (Matches -[])
Eq 2: 03 - 61 = -41 → -|30 - 16| = -14 → reverses to -41. (Matches -]()
Eq 3: 89 * 27 = 6507 → 98 * 72 = 7056 → reverses to 6507. (Matches :%[!)
Eq 4: 53 - 22 = -31 → -|35 - 22| = -13 → reverses to -31. (Matches -/()
Eq 5: 72 + 88 = 511 → 27 + 88 = 115 → reverses to 511. (Matches %(()
PHASE 3: COMPUTE ANSWER We need to determine the result for the query: :< - ]!
Translate the operands: : = 6, < = 2 → 62 ] = 4, ! = 7 → 47
Apply reverse mode (reverse operands): A' = 26 B' = 74
Apply the operator - (neg_abs_diff): -|26 - 74| = -|-48| = -48
Reverse the magnitude for the final result: 48 reversed is 84. Sign is preserved as -84.
Re-encode into symbols: 8 = ^ 4 = ] Result = -^]
reply
Reply
add_reaction
React
This comment has been deleted.
Dennis
TOPIC AUTHOR
Posted 2 months ago
· 2354th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@dangnh0611 . Thanks for sharing. It inspired me how to teach my model to fine tune.
reply
Reply
add_reaction
React
yash bhaskar
Posted 2 months ago
· 166th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@dangnh0611 Whats the logic here?
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
#[!}} = >#
]]-?< = >"]
]](>> = <<
>#-<} = <#>}
Now, determine the result for: >}-<"
reply
Reply
add_reaction
React
Kh0a
Posted 2 months ago
· 6th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I asked gemini
Wonderland Math Puzzle Solution
Digits mapping: " = 0, < = 1 ] = 2 # = 3 ? = 4 } = 5 [ = 8 > = 9
Operators: ! = standard addition - = multiplication ( = Greatest Common Divisor (GCD)
We can substitute the assigned digits into the equations to verify:
Eq 1: 38 + 55 = 93 (Matches >#)
Eq 2: 22 * 41 = 902 (Matches >"])
Eq 3: GCD(22, 99) = 11 (Matches <<)
Eq 4: 93 * 15 = 1395 (Matches <#>})
PHASE 3: COMPUTE ANSWER
We need to determine the result for the query: >}-<"
Translate the operands: > = 9, } = 5 → 95 | < = 1, " = 0 → 10
Apply the operator - (multiplication): 95 * 10 = 950
Re-encode into symbols: 9 = >, 5 = }, 0 = " → Result = >}"
reply
Reply
4
add_reaction
MD Mushfirat Mohaimin
Posted 2 months ago
· 2472nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I found another example.
026106f5
In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
52{43 = 9
31*15 = 46
37{26 = 11
17{92 = 24
Now, determine the result for: 75*97
Here, we can observe that { acts like a minus for two examples, but for the last example the mapping is NOT a minus.
We can also observe that * seems to act like a plus from the only one example where this operator is used.
So, the answer to 75*97 would be the sum of 75 and 97, which is 172, right?
But, in the dataset, the answer to this prompt is 631
What's the logic behind it?
reply
Reply
add_reaction
React
Dennis
TOPIC AUTHOR
Posted 2 months ago
· 2354th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I tried to solve it by hand.
31*15=46 seems like 3+1 =4 , 1+5 = 6 , and then concat = 46
@ryanholbrook , could you please provide some insights ? Thanks in advance.
reply
Reply
add_reaction
React
Đăng Nguyễn Hồng
Posted 2 months ago
· 1940th in this Competition
arrow_drop_up
9
arrow_drop_down
more_vert
About this example:
{ means digit-reverse then take abs(B-A) -> reverse: 9=34-25; 11=abs(62-73), 42=abs(29-71)
* means reverse -> add -> reverse: 64=51+13; 136=79+57
reply
Reply
4
add_reaction

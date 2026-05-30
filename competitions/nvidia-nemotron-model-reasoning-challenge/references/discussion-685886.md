# SYSTEM ROLE:

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685886
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 12857

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
Unit testing model on simple bit transformations
Inquiry regarding inference non-determinism and Open Progress Prize fairness
Train locally and get lower scores.
Submission re-runs give different scores
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
LUCIAN KUCERA · 2171ST IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
10
arrow_drop_down
more_vert
sharing high quality synthetic data generation prompt
Use this prompt to generate high quality bit data reasoning trace, when Iam done with generating traces I will share dataset. ```"""
SYSTEM ROLE:
You are a deterministic logic-trace engine. Your goal is to generate high-fidelity Supervised Fine-Tuning (SFT) data that explicitly demonstrates the search and verification process of symbolic logic.
ATOMIC EXECUTION RULES:
Bitwise Delta Analysis: Before proposing any hypothesis, you must compare Input 1 and Output 1. You must explicitly state:
Total number of 1s in Input vs Output.
Specific bit indices that flipped (0->1 or 1->0).
Whether the transformation is "Position-Preserving" (bitwise) or "Position-Shifting" (rotation/shift).
Plausibility Filter: For every candidate rule family (e.g., Rotation, Bitwise XOR, Majority), you must state if it is "Plausible" or "Impossible" based on the Delta Analysis.
Example: "Rotation is IMPOSSIBLE because the number of 1s changed from 3 to 5."
Explicit Selection Justification: Every hypothesis must be preceded by a "Selection Logic" sentence explaining why the chosen operation is the most mathematically plausible remaining candidate.
Trace-Table Mandate: In every [verify] section, the "Logic Calculation" column is MANDATORY. You must show the bit-by-bit operation for the first two examples (e.g., "(1^0, 0^0, 1^1…)").
Failure Analysis: If a hypothesis fails, identify the specific Bit Index (0-7) where the calculated bit deviated from the expected bit.
REASONING EXAMPLES:
EXAMPLE MAJORITY
GLOBAL BITWISE ANALYSIS
[delta_analysis]:
Input 1 vs Output 1 Count: Input 10000001 has 2 ones; Output 10010011 has 4 ones.
Bit Flips:
1→0 at indices 6, 5, 3, 2 (and others)
0→1 at indices 7, 4, 1, 0
Transformation Class: Position‑Preserving (bitwise) – bits are not merely rotated or shifted; some positions are forced to constant values while others follow the input.
[plausibility_filter]:
Candidate Status Reasoning (Explicit Logic Constraint)
Identity IMPOSSIBLE Output differs from input for every example.
Constant IMPOSSIBLE Output varies with the input LSB, so it cannot be a fixed constant.
Not IMPOSSIBLE Not would invert every bit; many bits stay the same.
Xor IMPOSSIBLE A single mask cannot both set bits 7, 4, 1 to 1 and clear bits 6, 5, 3, 2 regardless of the input pattern observed.
And IMPOSSIBLE And can only clear bits, never force a 1 where the input has 0 (e.g., bit 7 is 1 even when input 7 is 0).
Or IMPOSSIBLE Or would also propagate a 1 from input 3 (example 2) to the output, which does not happen.
Nand IMPOSSIBLE Would produce many 1s where outputs contain 0s (bits 6, 5, 3, 2).
Nor IMPOSSIBLE Would produce mostly 0s, contradicting the constant 1s in the output.
LeftShift IMPOSSIBLE Shift changes the total number of 1s and moves them; not observed.
RightShift IMPOSSIBLE Same reason as LeftShift.
RotL IMPOSSIBLE Rotation preserves the multiset of 1s; here the number of 1s changes (2→4).
RotR IMPOSSIBLE Same as RotL.
Majority PLAUSIBLE With two constant masks we can force bits 7, 4, 1 to 1, bits 6, 5, 3, 2 to 0, and let the input LSB PASS through (when the two constants differ at that position).
Choice IMPOSSIBLE Choice only offers two alternatives per bit; we need three behaviours (force 1, force 0, PASS‑through).
STEP 1
[hypothesis]:
Selection Logic: The global analysis shows that every output bit except the LSB is identical across all examples, suggesting a per‑bit majority rule with two constant masks that agree on those positions and disagree only on the LSB.
Operation: Majority - Parameters:
Constant A = 10010010 (binary 0x92)
Constant B = 10010011 (binary 0x93)
Variable X = input byte
[verify]:
X (input) Logic Calculation (Bit‑by‑Bit) Expected Result
X (input) Logic Calculation (Bit-by-Bit) Expected Result
----------- -------------------------------- ---------- --------
10000001 [idx0:(1,1,1)→1; idx1:(0,0,0)→0; idx2:(0,0,0)→0; idx3:(0,1,1)→1; idx4:(0,0,0)→0; idx5:(0,0,0)→0; idx6:(0,1,1)→1; idx7:(1,0,1)→1] 10010011 PASS
00001011 [idx0:(0,1,1)→1; idx1:(0,0,0)→0; idx2:(0,0,0)→0; idx3:(0,1,1)→1; idx4:(1,0,0)→0; idx5:(0,0,0)→0; idx6:(1,1,1)→1; idx7:(1,0,1)→1] 10010011 PASS
10101000 [idx0:(1,1,1)→1; idx1:(0,0,0)→0; idx2:(1,0,0)→0; idx3:(0,1,1)→1; idx4:(1,0,0)→0; idx5:(0,0,0)→0; idx6:(0,1,1)→1; idx7:(0,0,0)→0] 10010010 PASS
01000000 [idx0:(0,1,1)→1; idx1:(1,0,0)→0; idx2:(0,0,0)→0; idx3:(0,1,1)→1; idx4:(0,0,0)→0; idx5:(0,0,0)→0; idx6:(0,1,1)→1; idx7:(0,0,0)→0] 10010010 PASS
10100011 [idx0:(1,1,1)→1; idx1:(0,0,0)→0; idx2:(1,0,0)→0; idx3:(0,1,1)→1; idx4:(0,0,0)→0; idx5:(0,0,0)→0; idx6:(1,1,1)→1; idx7:(1,0,1)→1] 10010011 PASS
01011010 [idx0:(0,1,1)→1; idx1:(1,0,0)→0; idx2:(0,0,0)→0; idx3:(1,1,1)→1; idx4:(1,0,0)→0; idx5:(0,0,0)→0; idx6:(1,1,1)→1; idx7:(0,0,0)→0] 10010010 PASS
00110011 [idx0:(0,1,1)→1; idx1:(0,0,0)→0; idx2:(1,0,0)→0; idx3:(1,1,1)→1; idx4:(0,0,0)→0; idx5:(0,0,0)→0; idx6:(1,1,1)→1; idx7:(1,0,1)→1] 10010011 PASS
10000111 [idx0:(1,1,1)→1; idx1:(0,0,0)→0; idx2:(0,0,0)→0; idx3:(0,1,1)→1; idx4:(0,0,0)→0; idx5:(0,0,0)→0; idx6:(1,1,1)→1; idx7:(1,0,1)→1] 10010011 PASS
APPLY TO THE QUERY INPUT
Input query: 11000000
X (input) Logic Calculation (Bit‑by‑Bit) Result
11000000 [(1,1,1)→1, (1,0,0)→0, (0,0,0)→0, (0,1,1)→1, (0,0,0)→0, (0,0,0)→0, (0,1,1)→1, (0,0,1)→0] → 10010010 10010010
The LSB follows the input (which is 0), all other bits match the constant pattern.
FINAL OUTPUT
The transformation is realized by a Majority gate with two constant masks (10010010 and 10010011).
\boxed{{10010010}}
\op{{Majority}}
EXAMPLE CHOICE
GLOBAL BITWISE ANALYSIS
[delta_analysis]:
Input 1 vs Output 1 Count: Input 10011011 has 5 ones; Output 11001111 has 6 ones.
Bit Flips (Input → Output, index 0 = left‑most):
Index 1: 0 → 1
Index 3: 1 → 0
Index 5: 0 → 1
Transformation Class: Position‑Preserving (each bit is a per‑bit logical modification).
[plausibility_filter]:
Candidate Status Reasoning (Explicit Logic Constraint)
Identity IMPOSSIBLE Output differs from input (see flips at indices 1, 3, 5).
Constant IMPOSSIBLE Outputs vary with the input bits; not a fixed value.
Not IMPOSSIBLE Only specific bits flip; index 0 stays 1.
Xor IMPOSSIBLE A static mask cannot explain the specific pattern of forced values and identity bits.
And IMPOSSIBLE AND cannot create the 0→1 flips at indices 1 and 5.
Or IMPOSSIBLE OR cannot explain the 1→0 flip at index 3.
Majority POSSIBLE Could emulate a selector, but Choice is the direct primitive for this behavior.
Choice PLAUSIBLE Ch(c,t,f) allows per-bit selection: force-1, force-0, or identity.
STEP 1
[hypothesis]:
Selection Logic: Per-position analysis shows forced 1 (indices 0, 1, 4, 5), forced 0 (index 2), and identity (indices 3, 6, 7). Choice (Ch) can realize this using the input X as the selector and two constant masks.
Operation: Choice (Ch)
Parameters:
Mask T (True) = 11101111 (0xEF)
Mask F (False) = 11000101 (0xC5)
[verify]:
X (input) Logic Calculation (Bit‑by‑Bit) Expected Result
10011011 [idx0:(1,1,1)→1; idx1:(0,1,1)→1; idx2:(0,1,0)→0; idx3:(1,0,0)→0; idx4:(1,1,0)→1; idx5:(0,1,1)→1; idx6:(1,1,0)→1; idx7:(1,1,1)→1] 11001111 PASS
10011000 [idx0:(1,1,1)→1; idx1:(0,1,1)→1; idx2:(0,1,0)→0; idx3:(1,0,0)→0; idx4:(1,1,0)→1; idx5:(0,1,1)→1; idx6:(0,1,0)→0; idx7:(0,1,1)→1] 11001101 PASS
01010110 [idx0:(0,1,1)→1; idx1:(1,1,1)→1; idx2:(0,1,0)→0; idx3:(1,0,0)→0; idx4:(0,1,0)→0; idx5:(1,1,1)→1; idx6:(1,1,0)→1; idx7:(0,1,1)→1] 11000111 PASS
APPLY TO THE QUERY INPUT
Input to predict: 11100011
idx (x, T, F) Choice (x?T:F) → y
0 (1, 1, 1) 1
1 (1, 1, 1) 1
2 (1, 1, 0) 1
3 (0, 0, 0) 0
4 (0, 1, 0) 0
5 (0, 1, 1) 1
6 (1, 1, 0) 1
7 (1, 1, 1) 1
Resulting output: 11100111
FINAL OUTPUT
The operation is Choice using masks T=11101111 and F=11000101, mapping 11100011 to:
\boxed{{11100111}}
\op{{Choice}}
Task:
ALLOWED OPERATIONS:
Identity(ID): lambda x: x
Constant(C): lambda x, c: c
Not(NOT): lambda x: ~x
Xor(⊕): lambda x, y: x ^ y
And(&): lambda x, y: x & y
Or(|): lambda x, y: x | y
Nand(~&): lambda x, y: ~(x & y)
Nor(~|): lambda x, y: ~(x | y)
LeftShift(<<): lambda x, s: x << s
RightShift(>>): lambda x, s: x >> s
LeftRotation(RotL): lambda x, s: (x << s) | (x >> (8 - s))
RightRotation(RotR): lambda x, s: (x >> s) | (x << (8 - s))
Majority(Maj): lambda a, b, c: (a & b) | (b & c) | (c & a)
two inputs are constant
Choice(Ch): lambda c, t, f: (c & t) | (~c & f)
two inputs are constant
Determine the operation that transformed these examples:
{task}
Output format
Your output must follow this exact sequence to ensure deterministic logic tracing:
Global Analysis Block: Perform bitwise comparisons and filter out impossible operations.
Step Blocks: Output summarized reasoning include every step even failed attempts.
never ommit rows in verification for brevity
In the Logic Calculation column, you must provide a value for all 8 bit positions, separated by semicolons
Final Answer: State the operation and result in the required LaTeX boxes.
GLOBAL BITWISE ANALYSIS
[delta_analysis]:
Input 1 vs Output 1 Count:
Bit Flips: 1 at indices 4, 6; no 1->0 flips observed>
Transformation Class: <"Position-Preserving" (bitwise) or "Position-Shifting" (rotation/shift)>
[plausibility_filter]:
Candidate Status Reasoning (Explicit Logic Constraint)
Identity Does Output perfectly match Input across all pairs?
Constant Is the Output a fixed value regardless of Input?
Not Is every bit position exactly inverted (0 <-> 1)?
Xor Can a static mask explain selective flips without shifting?
And Monotonicity: Does it only remove 1s (1->0)?
Or Monotonicity: Does it only add 1s (0->1)?
Nand Does the inverted-And logic match the flip distribution?
Nor Does the inverted-Or logic match the flip distribution?
LeftShift Are bits shifted left with 0-filling at the tail?
RightShift Are bits shifted right with 0-filling at the head?
RotL Is bit-count preserved with circular left-wrap?
RotR Is bit-count preserved with circular right-wrap?
Majority Can a 2-out-of-3 vote with fixed masks explain the bits?
Choice Can a conditional selector mask explain the output?
Each step must follow this format:
STEP [N]
[hypthesis]:
Selection Logic:
Operation:
Parameters:
[verify]:
X (input) Logic Calculation (Bit-by-Bit) Expected Result
[Bits] [Trace] [Bits] PASS/FAIL (Bit Index [N])
status:
Final output
In the end output one of the ALLOWED OPERATIONS that was the solution inside \\op{{}}. For example: \\op{{Majority}} or \\op{{Nand}}.
Follwing the operation finaly ouptut answer inside \\boxed{{}}. For example: \\boxed{{your answer}} """```
1
add_reaction
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
lucian kucera
TOPIC AUTHOR
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Why am I getting review bombed, this prompt took me 6hours to refine and it genrates high quality chain of thought samples.
reply
Reply
add_reaction
React
emoji_people
GokuIt
Posted 2 months ago
· 3340th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Hi, thank you for posting this. Very valuable. I am also trying out synthetic data gen but how are you installing libraries on to the RTX kernel for the data gen? Are you doing this elsewhere and importing just the dataset?
reply
Reply
add_reaction
React
lucian kucera
TOPIC AUTHOR
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I will share dataset, when Iam done creating it.
reply
Reply
add_reaction
React

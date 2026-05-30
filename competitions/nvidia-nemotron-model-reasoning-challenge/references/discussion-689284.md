# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689284
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4079

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
Competition Metric Bug: verify method fails for Binary String Problem (?)
Pip install with internet disabled: install dependencies feature
Fix for “CUDA error: no kernel image is available for execution on the device” on RTX PRO 6000 Blackwell
symbol_transformation class problem can have multiple valid candidate answer
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
SHIVAM SHINDE · 16TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
19
arrow_drop_down
more_vert
Edge case in metric: \boxed{} cannot contain }
While going through the dataset I noticed a few rows where the answer itself contains }.
The metric prioritizes answers inside \boxed{} using the regex:
\boxed{([^}]*)}
Since the capture stops at the first }, the extractor cannot include } inside the boxed content.
However some dataset answers contain } as part of the final string. Example:
65}27 = }38 11}59 = }48 46}23 = }23
Now determine: 28}58 Answer: }30
If a model tries to output:
\boxed{}30}
the regex extracts an empty string instead of }30.
If the metric then falls back to other heuristic patterns or the last numeric value, the extracted answer becomes something like 30 (or 30}), while the ground truth is }30, so it would still be marked incorrect.
add_reaction
React
1 Comment
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
TOPIC AUTHOR
Posted 23 days ago
· 16th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I wanted to suggest a fix for the metric. The root cause is that the current regex [^}]* stops at the first }, so any answer containing } (like }30, `}:}, //:}, etc.) gets incorrectly extracted. Since \boxed{} is always the last thing in the model output (no text follows it), the fix is:
Find the last \boxed{ in the output
Take everything after it
Find the last } in the output
Everything between them is the answer
def extract_final_answer(text: str) -> str:
if text is None:
return 'NOT_FOUND'
last_boxed_idx = text.rfind(r'\boxed{')
if last_boxed_idx != -1:
after_open = text[last_boxed_idx + len(r'\boxed{'):]
last_brace = after_open.rfind('}')
if last_brace != -1:
return after_open[:last_brace]
return after_open.strip()  # unclosed box fallback
# existing heuristic fallbacks...
This correctly handles all edge cases:
\boxed{}30} → }30
\boxed{`}:}} → `}:}
\boxed{//:}} → //:}
\boxed{42} → 42 Important caveat: This approach relies on the assumption that the model outputs nothing after \boxed{}. If the model adds any trailing text containing } such as \boxed{42} therefore the set is {1, 2, 3} the rfind would incorrectly grab the last } from that trailing text, capturing 42} therefore the set is {1, 2, 3 instead of just 42. So this fix is valid as long as the prompt instruction and sampling are set up such that the model stops immediately after closing the box which appears to be the case here based on the current prompt template. If that assumption ever changes, a more robust approach would be needed.
reply
Reply
add_reaction
React

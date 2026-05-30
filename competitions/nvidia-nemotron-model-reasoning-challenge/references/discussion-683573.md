# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683573
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5121

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
[Discussion] Concerns about copied notebooks and misleading submissions in the Notebooks section , Heavy Plagiarism
How can I use vLLM to speed up test.csv inference on Kaggle?
Observations on high-visibility notebooks with minimal model contribution in the Nemotron Reasoning Challenge
MAMBA 2.3.1 from 2.2.2 lowering performance and cutlass mock
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
DENNIS · 2357TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
6
arrow_drop_down
more_vert
Exactly same "types" of the prompts?
(1) In Alice's Wonderland, a secret unit conversion is applied to measurements. For example: 22.27 m becomes 16.31
1a) can I expect "In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:" must appear in all public and private datasets for the same type of unit conversion question?
1b) can I expect the example will have varied "unit", or the unit is the same (must be "m") in all public and private datasets for the same type of unit conversion question something like 22.27 m becomes 16.31 22.27 km becomes 163.1
============
(2) In Alice's Wonderland, the gravitational constant has been secretly changed. Here are some example observations: For t = 1.58s, distance = 8.84 m
2a)can I expect "In Alice's Wonderland, the gravitational constant has been secretly changed. Here are some example observations:" must appear in all public and private datasets for the same type of gravitational constant question?
2b) can I expect "d = 0.5gt^2" must appear in all public and private datasets for the same type of gravitational constant question?
2c) apart from gravitational constant , will other constant (Kinematic Regression) be examined in all public and private datasets for the same type?
2d) the obeservations in the training dataset is like For t = 1.37s, distance = 14.92 m For t = 4.27s, distance = 144.96 m Can I expect the t is always in s, and the distance is always m? There will be no Alice Wonderland's special unit like t = 1.37l or t = 1.37t ? distance = 14.92 km , distance = 14.92 p?
============
(3) In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers. The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, and possibly majority or choice functions.
3a) Can I expect there is no other bit's binary numbers apart from 8-bit?
3b) Can I expect there is no other numbers apart from binary? Will there be 8-bit Hex?
3c) "The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, and possibly majority or choice functions. " will there be more operations apart from those named?
============ (4) In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples: !*[{ = '""[
4a) Can I expect the examples won't have double (or more) equal sign like !*[{ == '""[' !*[{ === '""[''
============ (5) One general question:
Will "Alice's Wonderland" appear in all prompts? Will there something like no wonderland, Dennis Wonderland, … ?
This may be a silly question since Nvidia may not want us to overfit the model. However, this is a competition with limited competition time. I want to create a better dataset for the competition.
Thanks for answering, host 😀
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
emoji_people
Ravi Ramakrishnan
Posted 2 months ago
· 14th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
What if one removes these words - do they add value to the problem at hand @dennisfong? I think it does not matter if the wonderland belongs to a name / PII.
reply
Reply
add_reaction
React
Dennis
TOPIC AUTHOR
Posted 2 months ago
· 2357th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
@ravi20076
I am thinking template overfit.
In addition, if the wonderland is something like "when you see plus sign just concat wonderland" but the examples are really addition. Do we need to handle those extreme cases?
reply
Reply
add_reaction
React

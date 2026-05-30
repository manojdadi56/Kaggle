# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694446
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 3277

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
QLoRA Fine-tuning Bug
Permission error
What is the setting of the enable_thinking in the chat_template during testing?
Seemingly Impossible Questions in Dataset?
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
GHAZI BOUMEDIENE GHAOUTI · POSTED A MONTH AGO
arrow_drop_up
2
arrow_drop_down
more_vert
Is it possible to use my own new training data?
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
AMITH NAIR
Posted 20 days ago
· 1595th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Your question is a bit vague regarding what you mean by "my own training data."
If you are asking whether you can perform feature engineering on the provided competition dataset (train.csv), then yes absolutely. In fact, that is essentially the core objective of the competition and one of the main ways to improve performance.
However, if you are asking whether you can create an entirely new training dataset with your own custom questions and answers, then the answer is generally no.
The reason is that the provided competition dataset is carefully engineered around specific underlying patterns and relationships between the questions and their corresponding answers. The hidden evaluation data used for testing submissions follows those same underlying patterns. If you generate completely unrelated training examples, you risk teaching the model incorrect or inconsistent logic that does not align with the competition’s actual task distribution.
The only realistic way to safely create additional data would be to first build reliable task-specific solvers for the existing dataset patterns, and then use those solvers to generate new synthetic examples that preserve the same logical structure and answer-generation rules as the original dataset. Without that, newly generated data would likely introduce noise and harm model performance rather than improve it when being evaluated.
reply
Reply
add_reaction
React
TwangyGarlic449
Posted a month ago
· 2219th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yes, if you find a good way to generate problems, I don't see why you wouldn't be allowed to.
reply
Reply
add_reaction
React

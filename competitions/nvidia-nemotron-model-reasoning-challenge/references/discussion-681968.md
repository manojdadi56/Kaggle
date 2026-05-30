# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681968
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 4029

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
Is ~0.86 a current ceiling for most approaches?
How is leaderboard rank decided on same score
Midpoint Leaderboard Clarification + Open Contribution Award Question
BlackWell Kaggle Internet Issue
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
MINDSET324 · 1634TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
3
arrow_drop_down
more_vert
Unable to load Nemotron-3-Nano-30B-A3B-BF16 due to mamba_ssm dependency (No Internet Environment)
I’m facing an issue while trying to load the Nemotron-3-Nano-30B-A3B-BF16 model.
From what I understand, this model relies on Mamba SSM components, which require the mamba_ssm library. Since the Kaggle GPU RTX PRO 6000 environment has internet access disabled, I’m unable to install this dependency using pip, which prevents the model from loading successfully.
Issue:
Model: Nemotron-3-Nano-30B-A3B-BF16
Error: Missing mamba_ssm dependency
Constraint: No internet access → cannot install required package
What I’ve tried:
Attempted standard pip install mamba-ssm (fails due to no internet)
Checked for preinstalled packages (not available)
Questions:
Is there a preinstalled or offline-compatible version of mamba_ssm available in this environment?
Are we expected to vendor the dependency manually (e.g., upload wheels or source code as a dataset)?
Is there an alternative way to run Nemotron-3 models in this setup (e.g., prebuilt runtime, container, or supported inference framework)?
Has anyone successfully run this model in the competition environment?
Any guidance from organizers or participants would be really helpful.
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
Kh0a
Posted 2 months ago
· 5th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
You can add this utility script to your notebook https://www.kaggle.com/code/ryanholbrook/nvidia-utility-script
reply
Reply
add_reaction
React
HADY
Posted 2 months ago
· 3530th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
it didn't work for me
Screenshot 2026-03-18 181504.png
reply
Reply
add_reaction
React
water joe
Posted 2 months ago
· 1005th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Use the official script directly, do not create your own.
reply
Reply
add_reaction
React
badwolfe
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
so can we not use unsloth?
reply
Reply
add_reaction
React
Fusion Flux
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
It is not working for me; please suggest any other method
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1451st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
There are lots and lots of Amazing Public notebooks that people have shared. Use one of them for reference, or make a replica and then update it to do your experiments. In the practice, You will notice how to set up the environment properly.
reply
Reply
add_reaction
React

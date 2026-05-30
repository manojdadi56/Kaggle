# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687142
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 5193

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
Fix for “CUDA error: no kernel image is available for execution on the device” on RTX PRO 6000 Blackwell
symbol_transformation class problem can have multiple valid candidate answer
[update] Read CPMP's reply. [original] Do not distill models that do not allow distillation (e.g. gemini, gpt5)
[Fake Notebook Alert] Watch out for fake laptops that copy and upload other people's submission.
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
CPMP · POSTED 2 MONTHS AGO
·
COMPETITION HOST
arrow_drop_up
22
arrow_drop_down
more_vert
Pip install with internet disabled: install dependencies feature
I responded to a comment but this maybe worth sharing as a topic. There is a little known or not visible enough feature that allows for pip installs without the need to create additional notebooks with downloaded wheels.
When running notebooks before submitting you can allow internet access, and have your pip installs in the notebook.
When you submit, or save for submission, with internet access disabled, then you can just move your pip installs as indicated in this screenshot. Just click on the dots at the right of the submit button, click on "install dependencies", and put all your pip install commands there. More info: https://www.kaggle.com/docs/notebooks#modifying-a-notebook-specific-environment
2
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
Darren Amadeus Martin
Posted 2 months ago
· 1882nd in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Thank you for replying to my comment in another discussion forum. This is a feature that I did not even know existed. So with this feature, basically for submission or saving version that must not use internet, pips can be installed with relative ease. Youu mentioned that internet access are allowed before submitting while running notebooks. However, the issue is, everytime I try to put internet on with the gpu rtx pro 6000, it gave me an error of "internet not allowed with this accelerator" hence even for debugging or trial and error while editting the notebook (not using save version), it requires me to download the wheels on a different notebook. Moreover, if the pip requires to be compiled in the same environment, I have to run it twice, one notebook without accelerator to pip download and one notebook with accelerator for installation and compile process. Morever, latelt notebooks with rtx pro 6000 prevents me from adding new datasets/models/notebook outputs with the same "internet not allowed with this accelerator" error unless I deattach the competition data and add the datas I need before attaching the competition data again. So 2 things I'd like to note is
Turning internet on while editting with rtx pro 6000 on gave an error
Notebook with rtx pro 6000 can't add another dataset
I hope that competition host and kaggle staff can look at this matter
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
-3
arrow_drop_down
more_vert
Sorry, I did not know internet access was disabled for this accelerator, my bad.
I get that for interactive use this is a bit painful.
reply
Reply
add_reaction
React
Darren Amadeus Martin
Posted 2 months ago
· 1882nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I think that's what everybody concerns about. I know that disabling internet is to prevent GPU exploitation but having internet access on the notebook would really help with debuggings and pip installations. So it would be rewlly helpful if competition hosts and kaggle staffs take a look and reconsideration
reply
Reply
add_reaction
React
matmul_in_W_plus_b
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
It's really hard to run code on a offline environment. Please consider enabling internet.
reply
Reply
add_reaction
React
HZM
Posted 2 months ago
· 993rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
i am using https://github.com/NVIDIA-NeMo/RL/tree/main to sft the model, but do you need how to covnert the dist torch model weight to hf format, it brothes me a lot
reply
Reply
add_reaction
React

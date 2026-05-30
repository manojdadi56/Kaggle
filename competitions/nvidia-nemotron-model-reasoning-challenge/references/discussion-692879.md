# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/692879
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 6288

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
Kaggle CLI Can’t Set GPU Type? Tired of Manually Switching to RTX 6000 Every Time 😩
Why are we seeing 0.84 – 0.86 score variance with the 0.85 winning zip?
corrupted or puzzel (numeric equations)
2 interpretations of the bit manipulation problem
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
emoji_people
TAHA · 421ST IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
1
arrow_drop_down
more_vert
Is DoRA allowed does it actually improve LB scores?
Hey everyone,
I’m currently prepping a final training run and wanted to get the community's thoughts on using DoRA (Weight-Decomposed Low-Rank Adaptation) instead of standard LoRA for this specific reasoning challenge.
I’ve managed to hit a solid baseline (around 0.84 - 0.85) using standard SFT with a carefully balanced data mix and a cosine scheduler. However, I'm looking for that last 1-2% push to handle the harder algorithmic categories (like cryptarithms).
Theoretically, DoRA should be perfect here. By separating the weight updates into magnitude and direction, it usually performs much closer to full fine-tuning, which seems critical for rigid mathematical reasoning tasks where standard LoRA tends to plateau , the extra VRAM overhead from tracking the magnitude vectors isn't a bottleneck for me.
My main hesitation is Kaggle's submission evaluator. As we know, Kaggle spins up a vanilla vLLM instance and injects our adapter_model.safetensors. Unsloth/PEFT handles DoRA beautifully during training, and it should mathematically fold the magnitude and direction back into standard $A$ and $B$ matrices when calling save_pretrained().
But Kaggle's backend can be notoriously finicky. I've had issues in the past with adapters throwing errors or scoring abysmally low because of slight formatting or merging quirks.
Has anyone here successfully submitted a DoRA-trained adapter to the leaderboard?
Did it load correctly in the hidden vLLM environment, or did it trigger an evaluation error / 0.0 score?
If it worked, did you actually see a tangible LB boost over standard LoRA (assuming the same rank/alpha)?
I only have enough compute budget for a couple more serious runs, so I’m trying to decide if flipping use_dora=True is a smart calculated bet or a technical trap.
Any insights would be hugely appreciated!
add_reaction
React
7 Comments
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
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
4
arrow_drop_down
more_vert
It is allowed provided you can use the submission format.
On a personal note, I tried DORA in a previous competition, and the extra training time did not translate into better LB score. It would be nice to see if you get a positive outcome.
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted a month ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for the real-world experience! Even if DoRA saves correctly to standard LoRA format via Unsloth/PEFT, vLLM's config detection likely kills it anyway no confirmed successful Kaggle LBs with DoRA yet. Your note on no LB boost despite extra time seals it for me; with limited compute, I'll skip use_dora=True and optimize standard LoRA (higher rank/alpha, data tweaks) for cryptarithms instead. Appreciate the heads-up
reply
Reply
add_reaction
React
NNMax
Posted a month ago
· 1184th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Doesn't current versions of vllm do not support native DoRA?
I think the possible ways are either mimicking DoRA finetuning but by using LoRA alone or some really complex engineering?
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted a month ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yes, you're spot on current standard vLLM versions (including Kaggle's vanilla setup) don't natively support DoRA. The PEFT helper explicitly errors with "vLLM does not yet support DoRA" when it detects DoRA configs. PR #14389 for DoRA support is still open with merge conflicts, no merge by April 2026, and recent issues show inference failures for DoRA models.
Mimicking DoRA with plain LoRA misses the core benefit (separate magnitude training), so gains would be suboptimal. Complex forks like vllm-dora work locally but won't fly in Kaggle's locked env. Best bet: stick to standard LoRA for safe LB submits. I Did a bit of research and got to know that While vLLM does not yet natively support DoRA (Weight-Decomposed Low-Rank Adaptation) adapters for dynamic serving as of early 2026
reply
Reply
add_reaction
React
Noizersam
Posted a month ago
· 355th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Have you tested how many epochs of training yield the best results?
reply
Reply
add_reaction
React
emoji_people
Taha
TOPIC AUTHOR
Posted a month ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
i dont have heavy compute , i just have modal and few dollars in tinker , so i havent tested yet
reply
Reply
add_reaction
React
Giovanny Rodríguez
Posted a month ago
· 40th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I'll try to make them a couple of weeks ago, Pissa and Dora LB: 0
reply
Reply
add_reaction
React

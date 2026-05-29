# Appreciation (2)

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684212#3446363
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 8546

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
Answers To Everything Data: Read Me! 100% Solve Rate
[Open Progress Prize Publication] SFT to maximize minimum logprob
How to get started + Competition's Official Discord
Rescore After Metric Update
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
TONG HUI KANG · 1170TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
140
arrow_drop_down
more_vert
Visualize the problems and completions from the base model
I ran the base model (yes, the base model) over all the 9500 problems at least once. These are the results.
https://nemotron.huikang.dev/base
You can see the model generation as well.
The code is here. This is derived from my work in AIMO 3 and ARC-AGI-2.
26
add_reaction
comment
19 Comments
2 appreciation comments
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
emoji_people
Kishan Vavdara
Posted 2 months ago
· 14th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
@huikang I took the liberty and published the dataset here
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
Thanks! I uploaded my copy as well https://www.kaggle.com/datasets/huikang/nemotron-base-model-generation
reply
Reply
3
add_reaction
Anton Kratz
Posted 2 months ago
· 3135th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Excellent work @huikang ! How long did it take to run all 9500 problems at least once? I am woking on something similar, using Blackwell here on Kaggle, I need about 4 minutes per problem. This seems… slow?!?
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
If I only consider the latest run for each of the 9500 problems, apparently there are 48,217,898 tokens generated.
At 2.5k tokens per second it is 5.35 hours, which is about right.
reply
Reply
3
add_reaction
Ra'uf Fauzan Rambe
Posted a month ago
· 112th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Wow, that's nearly 50 million. At our current speed of 2.5k tokens per second, it should wrap up in about 5 hours, right?
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
FAQ
Is this the base model? It is the base model.
Why are the partially solved problems in the middle? Most of the questions are ran only once, except some at the start and some in the middle. I ran the inference script in alphabetical and reverse alphabetical order and went for a nap. When I woke up, each script is slightly more than half done and I terminated it.
Where is the prompt from? It is from the official metric notebook.
How much money did it cost? On Modal I ran on an RTX PRO 6000 which is $3.03 per hour. I think I ran this for five hours. The throughput was 2.5k tokens per second.
Comments
You see that the solve rate is almost 50%, which aligns with the demo submission from the organizer.
For many entries of equation numeric, and almost all entries in equation symbolic, I could not figure the pattern. This is reported in other threads.
reply
Reply
2
add_reaction
Darshan Makwana
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
Hey @huikang thanks for sharing this, it's really helpful to understand the model's current behaviour around these puzzles. I have one doubt regarding the partial problems, as you said problems where attempted more than twice due to the way you ran two separate scripts, but in the inference metrics the temperature is set to 0.0 so this still shouldn't happen and every inference run should give me the same thinking and answer chain, or maybe I misunderstood something
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Great question, the temperature was 1.0.
Otherwise everything will be logprob zero (need to confirm). I want to see which tokens are super likely and which tokens are unlikely.
reply
Reply
add_reaction
React
Ankith Savio
Posted 2 months ago
· 895th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
What was the batch size here? I am trying to understand how we can achieve that throughput.
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
For vLLM inference, we do not think in terms of batch size but in terms of concurrency --max-num-seqs.
I remember having a concurrency of 256. I do not think I needed that high, I remember achieving the same 2.5k token throughput with a concurrency of 128.
reply
Reply
1
add_reaction
Ankith Savio
Posted 2 months ago
· 895th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I remember having a concurrency of 256. I do not think I needed that high, I remember achieving the same 2.5k token throughput with a concurrency of 128.
I am only able to achieve half of this. Any tips? Are you utilizing quantized model?
reply
Reply
add_reaction
React
Tito_42
Posted 2 months ago
· 565th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Hi Tong Hui Kang, thank you for sharing ;) I rent a GPU RTX Pro 6000 at $0.90 per hour on Google Cloud (Spot option).
reply
Reply
add_reaction
React
HZM
Posted 2 months ago
· 995th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
may i ask where the problem type comes from? I am a liitle bit late to join this competation
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
Oh, that is extracted from the problem. If you see, the problems categorizes nicely into 6 (or 7) formats.
reply
Reply
2
add_reaction
emoji_people
shitmaster
Posted 2 months ago
· 422nd in this Competition
arrow_drop_up
-3
arrow_drop_down
more_vert
你好，请教一下是否需要自己在官方给的9500条训练数据以外再加一些训练数据以达到更高分数。 谢谢！！
reply
Reply
add_reaction
React
Ashutosh Kumar
Posted 2 months ago
· 1898th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Very true! It's the worst model I have ever seen.
reply
Reply
add_reaction
React
Bisnu sarkar
Posted 2 months ago
· 2181st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you for the amazing work @huikang . It becomes a useful tool for exploring the dataset.
reply
Reply
add_reaction
React
emoji_people
Aurora Rabbit
Posted 2 months ago
· 294th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@huikang Great job! This seems to work really well. The results are also quite consistent with my own evaluation.
reply
Reply
2
add_reaction
This comment has been deleted.
This comment has been deleted.
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
lol I somewhat gave up on AIMO 3, I want to prove that I can finetune models here, then I go back to AIMO 3
Also I am waiting for the Tinker credits for use in AIMO 3
reply
Reply
add_reaction
React
This comment has been deleted.
Appreciation (2)
Navneet
Posted 2 months ago
arrow_drop_up
-4
arrow_drop_down
more_vert
Thank you for the base model @huikang
DaoHe Liu
Posted 2 months ago
· 444th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Great work！

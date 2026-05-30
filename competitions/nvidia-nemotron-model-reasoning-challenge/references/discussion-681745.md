# Information for First-Timers

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681745
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 16197

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
expand_less
Datasets
Models
Code
format_list_bulleted
More
expand_less
comment
Discussions
school
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
Your Work
expand_more
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
JAMIL C SEMAAN · POSTED 2 MONTHS AGO
·
COMPETITION HOST
arrow_drop_up
58
arrow_drop_down
more_vert
How to Get Started + Nemotron Model Reasoning Challenge Resources
Information for First-Timers
New to NVIDIA Nemotron open model family and its NeMo open libraries? If you’re just starting to explore these models, tools, or docs, feel free to start a new thread in this channel, or drop any first-timer questions here and folks can help you get unblocked. If you’re new to Nemotron and NeMo, skim the official Nemotron model pages, NeMo docs, and the resources listed below, then come back with specific questions about setup, fine-tuning, RL, or evaluation. Happy reasoning with Nemotron, and good luck climbing the leaderboard!
1. Core Nemotron model family (models & baselines)
Nemotron overview (model family, capabilities, benchmarks)
Nemotron GitHub(main repo and examples)
Nemotron 3 Nano technical blog (architecture, efficiency, training details)
Nemotron v3 collection on Hugging Face (ready-to-use checkpoints)
2. Nemotron open libraries for data & RL
Synthetic data generation NeMo Data Designer (generate domain/task-specific synthetic data):
GitHub: https://github.com/NVIDIA-NeMo/DataDesigner
Docs: https://nvidia-nemo.github.io/DataDesigner/latest/
Recipes: https://nvidia-nemo.github.io/DataDesigner/latest/recipes/cards/
Data filtering and curation NeMo Curator (multi‑modal data curation: text, images, video, audio):
GitHub: https://github.com/NVIDIA-NeMo/Curator
Docs: https://docs.nvidia.com/nemo/curator/latest/
RL & Gym (reasoning, behavior, agents) NeMo RL (RL training at scale with SOTA algorithms):
GitHub: https://github.com/NVIDIA-NeMo/RL
NeMo Gym (build/manage RL environments)
GitHub: https://github.com/NVIDIA-NeMo/gym
Available environments: https://github.com/NVIDIA-NeMo/Gym?tab=readme-ov-file#-available-environments
Guides & tutorials Nemotron 3 Super – multi‑stage RLVR & RLHF recipe with NeMo RL:
Guide: https://github.com/NVIDIA-NeMo/RL/blob/super-v3/docs/guides/nemotron-3-super.md
GRPO RLVR Jupyter notebook: https://github.com/NVIDIA-NeMo/Nemotron/tree/main/usage-cookbook/Nemotron-3-Super/grpo-dapo
Nemotron 3 Nano RL guide https://docs.nvidia.com/nemo/rl/nightly/guides/nemotron-3-nano.html
3. Nemotron open datasets (instruction-following & reasoning)
Pre‑training datasets collection: Link
Post‑training datasets: Link
RL instruction‑following dataset: Link
Agentic dataset:Link
RAG dataset: Link
Personas collection: Link
More NVIDIA datasets: Link
4. Cookbooks, recipes, and evaluation
Nemotron main repo (cookbooks, training recipes, deployment examples): https://github.com/NVIDIA-NeMo/Nemotron
Nemotron 3 Nano reproducibility / eval guide with NeMo Evaluator: https://github.com/NVIDIA-NeMo/Evaluator/blob/main/packages/nemo-evaluator-launcher/examples/nemotron/nano-v3-reproducibility.md
5. Community & learning paths
If you get stuck, want feedback on an idea, or just want to see how others are approaching the challenge, these are great next stops:
Nemotron / NVIDIA Developer Discord (join + Nemotron channel): Join: https://discord.com/invite/nvidiadeveloper
Nemotron Reasoning Challenge Discord channel: https://discord.gg/udbkJyWk
NVIDIA community email (questions, feedback, sharing work): community@nvidia.com
Learning paths
Build an AI agent (guide + code): https://developer.nvidia.com/topics/ai/how-to-build-an-ai-agent
GitHub: https://github.com/NVIDIA-NeMo
Build a RAG agent (guide + code): https://developer.nvidia.com/topics/ai/how-to-build-agentic-ai-rag
GitHub: https://github.com/NVIDIA-NeMo
Launchable environment for Nemotron (pre‑configured cloud env): https://brev.nvidia.com/launchable/deploy?launchableID=env-32kC34ErT9wsqTcJyaKMxBEuhr2
GitHub: https://github.com/NVIDIA-NeMo
Nemotron Labs livestreams playlist (deep dives, demos, Q&A): https://youtube.com/playlist?list=PL5B692fm6--vEL0FwctKghCpyEnBGAQJA&si=jhVNZVfdj_91hpEJ
21
18
add_reaction
comment
23 Comments
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
Ashutosh Kumar
Posted 2 months ago
· 1901st in this Competition
arrow_drop_up
9
arrow_drop_down
more_vert
Hi Jamil,
There appears to be some trainining data bug which I identified lately, as the model was being trained on buggy data and gave wrong answer.
Below are the areas critical:
Bit manipulation: 50.5% of training traces are WRONG (764/1513 mismatches between computed Result and answer)
Equation transformation: 49% have I/O length mismatches making char_map fundamentally broken, 44% have unknown chars
Bit Manipulation:
1988 total training examples 1513 have a Result line 764 have MISMATCHES between computed Result and \boxed{} answer 50.5% mismatch rate - HALF the training data teaches WRONG reasoning! 344 examples have f() unknowns (where we couldn't determine the rule) Equation Transformation:
3157 total training examples
1555 (49%) have input/output lengths that differ - char_map approach is fundamentally wrong for these
Another 1382 (44%) have unknown '?' characters when applying the char_map to the query
77 (2%) the char_map fails to even predict any of the given examples
The pattern is unmistakable: bit_manipulation is poisoning the model with wrong answers in half its examples, and equation_transformation's char_map strategy simply doesn't work for nearly half the data due to length mismatches and missing characters.
Was this left on purpose ?
Is there any plan to fix these bugs or we don't intend to fix ?
I used this script to find the issues and bugs in training data.
check_bugs.py
reply
Reply
add_reaction
React
NoorMazhar
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
I am getting started with learning nemo libs.
when I launch the brev/lab environment (https://brev.nvidia.com/launchable/deploy?launchableID=env-32kC34ErT9wsqTcJyaKMxBEuhr2)….It is asking me to buy credits.
Is that the only way to use the lab is buying credits or for this competition is there a free lab environment?
reply
Reply
add_reaction
React
Ievgenii Krevenets
Posted 2 months ago
· 3391st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Nemotron Reasoning Challenge Discord channel: https://discord.gg/kRwhDfTW NVIDIA community email (questions, feedback, sharing work): community@nvidia.com
Screenshot 2026-03-31 at 19.17.07.png
reply
Reply
add_reaction
React
cg
Posted 2 months ago
· 2519th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Hi, I submitted the same output twice and got different results. Is this expected?
reply
Reply
add_reaction
React
MD Mushfirat Mohaimin
Posted 2 months ago
· 2474th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
That's strange.
Are you sure you submitted the EXACT same submission.zip file twice?
Or did you run a notebook twice, and then submitted the output file of both versions twice? If this is the case, then the submission.zip file may not be the exactly the same due to randomness in the notebook.
reply
Reply
add_reaction
React
cg
Posted 2 months ago
· 2519th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I submitted the ouput of the same version of my notebook 4 times. I got 0.66,0.67,0.66,0.62 score. It is the publically available notebook by Dennis. I just modified max seq len to 640.
reply
Reply
add_reaction
React
emoji_people
Nabid Nur
Posted 2 months ago
· 344th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
why might that be due to selection of random 600 samples?
reply
Reply
add_reaction
React
NoorMazhar
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
may I ask if the notebooks can be run locally? Or I have to buy brev credits to run?
reply
Reply
add_reaction
React
Asadullah Baig
Posted 2 months ago
· 3005th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The notebooks cant be run locally And you dont have to buy credits. each week you get 30 hrs for the 4 different GPUs.
reply
Reply
add_reaction
React
jerryv69
Posted 2 months ago
· 2588th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
locally ij a mac mini?
reply
Reply
add_reaction
React
Hide replies
arrow_drop_up
Asadullah Baig
Posted 2 months ago
· 3005th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
If my solution isnt able to run on the RTX Pro 6000 is that a me problem?
reply
Reply
add_reaction
React
Muhammad
Posted 2 months ago
· 3456th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
NVIDIA Nemotron Submission Demo page is not working
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Fixed! Thank you.
reply
Reply
add_reaction
React
Muhammad
Posted 2 months ago
· 3456th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
despite updating the utility Script,"""ModuleNotFoundError: No module named 'cutlass'"""
reply
Reply
add_reaction
React
xianxu qiu
Posted 2 months ago
· 2572nd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The official mirror cannot use sm_120, and the inference token speed is only 1.7/s. Can the mirror be updated?
reply
Reply
add_reaction
React
Muhammad
Posted 2 months ago
· 3456th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The max input tokens for the eval model is 128k. In the main page, inference parameters setting is showing with max_model_len = 8192 while in the metric code, it is 4096. Similarly, for other parameters as well. Please tell me which settings will be used to evaluate the final results, except for LORA.
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
The parameters on the Evaluation page are what the metric is currently running with. They override the default values in the code.
reply
Reply
add_reaction
React
Marília Prata
Posted 2 months ago
arrow_drop_up
-1
arrow_drop_down
more_vert
Hi Seeman,
unfortunately, many (almost all) NVidia GitHub pages that I tried to open, resulted in: Error Loading Page
reply
Reply
add_reaction
React
Marcelo
Posted 2 months ago
· 2152nd in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Hi Seeman,
unfortunately, many (almost all) NVidia GitHub pages that I tried to open, resulted in: Error Loading Page
The "Error loading page" message on GitHub often stems from browser cache issues, network problems, or extensions blocking content. (https://www.perplexity.ai/search/when-accessing-a-page-on-githu-HCOLk.MqRKyHUFYvIszm9g)
reply
Reply
1
add_reaction
Jamil C Semaan
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
1
arrow_drop_down
more_vert
Hi Marilia - can you confirm if you're still experiencing this issue? I just clicked through the links and they seem to be working correctly, but happy to help investigate further if needed.
reply
Reply
add_reaction
React
Marília Prata
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you Jamil. Every link is working now. No issue at all.
reply
Reply
1
add_reaction
Gerves François Baniakina
Posted 25 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
Hello there! I am having this issue Requirement already satisfied: transformers in /usr/local/lib/python3.12/dist-packages (5.0.0) Collecting transformers Downloading transformers-5.7.0-py3-none-any.whl.metadata (33 kB) Collecting mamba-ssm Downloading mamba_ssm-2.3.1.tar.gz (121 kB) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 121.7/121.7 kB 4.6 MB/s eta 0:00:00 Installing build dependencies … done error: subprocess-exited-with-error
× Getting requirements to build wheel did not run successfully. │ exit code: 1 ╰─> See above for output.
note: This error originates from a subprocess, and is likely not a problem with pip. Getting requirements to build wheel … error error: subprocess-exited-with-error
× Getting requirements to build wheel did not run successfully. │ exit code: 1 ╰─> See above for output.
note: This error originates from a subprocess, and is likely not a problem with pip.. Can anybody to help?
reply
Reply
add_reaction
React
UoM23MLMSc239362l
Posted 25 days ago
· 3560th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Rookie Getting started
Hello I am it new to this. I have been trainning & fine tuning LLMs. But here with this I am bit confused with the tasks. I have below questions. Kindly please give me some answers for them to start the competition. 😇
Do I have to train the any LLM with give dataset ?
Or I have to use Nemo-tron model train and evaluate with metric/nemotron-3-nano-30b-a3b-bf16
reply
Reply
add_reaction
React
Steve Roberts
Posted a month ago
· 563rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Neither of the workshops appear to work - both the "Build an AI agent" and "Build a RAG agent" just get stuck on a loading page.
reply
Reply
add_reaction
React
Alpaca
Posted 2 months ago
· 3196th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
discord link for the competition seems to be broken
reply
Reply
add_reaction
React
NoorMazhar
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
same for me too, getting invalid discord link.
was there a resolution for this?
reply
Reply
add_reaction
React
Jamil C Semaan
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Hi @aggshourya @noorneo - please use this link to Discord channel and let us know if issue persists https://discord.gg/udbkJyWk
reply
Reply
add_reaction
React
Ra'uf Fauzan Rambe
Posted 2 months ago
· 112th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Hello everyone, my name is Ra'uf. I need some help regarding my submission for the NVIDIA Nemotron Model Reasoning Challenge.
Although my code runs successfully and performs well in my local environment, the submission keeps failing or isn't ranking as expected. Does anyone have advice on how to optimize my code for a successful submission or how to improve my ranking in this specific challenge?
Thank you very much!
reply
Reply
add_reaction
React
Asadullah Baig
Posted 2 months ago
· 3005th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
For each test case, the model is prompted to generate a response and instructed to place its final answer within a \boxed{} LaTeX command. The metric extracts the final answer from the generated text, prioritizing content within the boxed format while falling back to other heuristic patterns or the last numeric value found.
reply
Reply
add_reaction
React
Ra'uf Fauzan Rambe
Posted a month ago
· 112th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks sir
reply
Reply
add_reaction
React
Liangjie Zhao
Posted 2 months ago
· 3494th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Evaluation metric raised an unexpected error. I submitted submission.zip, but it showed an error both times. What could be the reason?
reply
Reply
add_reaction
React
This comment has been deleted.
HADY
Posted 2 months ago
· 3528th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
go to code section in the competition, and make a new notebook you will find it
reply
Reply
add_reaction
React

# Quick links

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689915#3447796
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 39429

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
How to get started + Competition's Official Discord
Rescore After Metric Update
Metric Update
How to Get Started + Nemotron Model Reasoning Challenge Resources
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
223
arrow_drop_down
more_vert
[Open Progress Prize Publication] SFT to maximize minimum logprob
I would like to thank the competition hosts and Kaggle for organizing this competition. I did manage to find something interesting to bet on, and I am happy to see my gamble paying off.
You might have made some predictions that I have asked for. These are the answers.
The score I was aiming for - 0.877
How many tokens are used to train - 27,850,703 tokens for the winning solution, 598,958,637 in total
How much money I have spent - $212.48 in Tinker credits, approximately $60 in Modal credits, $10 for Kaggle / Colab subscription.
What do you think is the secret - bit manipulation, you only need SFT, deterministic chain-of-thought design, use of min logprob as objective, use of Tinker for training
Quick links
Original notebook
Validation notebook
Training metrics and logs for winning submission
Github containing the relevant code
What was I betting on
This is what I am betting on
Nemotron can act as a simple computer after LoRA training.
These are the assumptions in my bet
I can craft the chain-of-thought better than my competitors. I think this turned out to be true. The main differentiator was the bit manipulation problem where I managed to figure out a chain of thought that has solved many more problems.
I can finetune LoRA correctly and efficiently. I think I got this almost correct. KhoA managed to get perfect scores on numeral, gravity and unit_conversion whereas my winning model still sometimes fails in these categories.
What am I betting against
Reinforcement learning. I already have the optimal policy for solvable problems. I already know the best next token for the LLM to make (assuming they have been making all the correct moves). The only job of the LLM is to follow the policy.
Distilling larger models. The optimal policy should be directly generated with code.
Chain-of-thought design principles
As mentioned, I believe I can craft the chain-of-thought better than the other competitors.
This is how I designed my chain-of-thought
Design objectives
Deterministic. The temperature in the leaderboard evaluation metric is 0.0. This means I just need to get the most likely token correct. My training objective is to maximize the minimum logprob for the traces I am training on.
Simple. Each token should be derived from as few sources as possible, and as easy to compute as possible. For example, division should be broken down into subtraction and addition. Instead of choosing from 77 wonderland words to match, I should iterate through 77 wonderland words and classify whether the words match.
Coverage. I want rare operations to be well-trained. For example, when I am matching the wonderland words, I do not stop on the first word, I continue on with the rest of the Wonderland words so that I get the model to all the words it needs to match.
Within length limit. The full chain-of-thought has to be under 7680 tokens, as required by the competition.
Tokenization awareness. Letters and symbols can be tokenized with other tokens. I should write chain-of-thought that avoids dealing with the model weaknesses in handling tokenization.
Generalizable. Apart from certain information (Wonderland words for Cipher), I should not be training the model to memorize answers. I should be aware of signs where the model is merely memorizing answers in the training set.
Non-goals
Diversity. Frontier models are supposed to be able to generate a diverse set of completions with the best rewards. I do not need diversity here, as long as the answer is correct, it does not matter if all the solutions look the same. This is also possible because the leaderboard scores submissions with temperature zero.
Conciseness. I do not need the chain-of-thought to be concise. However, the longer the chain-of-thought, the more it costs to train the model.
Verification. For now, I assume the model generates every token correctly. With this assumption, I do not need to run verification or recovery from errors.
The chain of thought should also be very easy to iterate on. It should be easy to track, modify, train, and debug the chain of thought.
Solution approach
There are seven categories of problems. I describe my approach to solving these problems, in increasing order of difficulty.
Numeral
This task asks to convert a Roman numeral into an integer.
I am aiming for a 100% (1576/1576) solve rate.
All Roman numerals in the training set are between 1 and 100.
I enumerated all the numerals. I also have a step-by-step process of solving the numeral.
The code to generate the chain of thought is available here and an example output is available here.
Unit conversion / Gravity
This task asks to figure out a scalar value, and multiplication to apply the scalar value on the question input. I am aiming for a 100% (1594/1594) solve rate on unit conversion and a 100% (1597/1597) solve rate on gravity.
The multiplication and division are split into multiple steps, so that it is easier to train the model to not make mistakes.
The code to generate the chain of thought is available here for unit conversion and here for gravity. An example output is available here for unit conversion and here for gravity.
Cipher
This task asks to decrypt a substitution cipher. Given several example encryptions of Wonderland-themed sentences, the model must deduce the character-level mapping and apply it to decrypt a new sentence.
I am aiming for a 100% (1576/1576) solve rate.
The solution is straightforward
Compute the current character mapping
Collate the unmapped characters
Assign the unmapped characters
The code to generate the chain of thought is available here and an example output is available here.
Apparently, Nemotron is quite bad at spelling. I think perfect performance at this subtask is a baseline expectation to medal in the final leaderboard.
Bit manipulation
This task asks to discover a per-bit transformation rule from input-output examples of 8-bit binary numbers.
I am aiming for an 85.1% (1364/1602) solve rate.
Please refer to the full-length post on how I approach the bit manipulation problem.
Equation
This task asks to discover the arithmetic rule applied to two-number equations. Given examples like 64-65 = 201, the model must figure out what operator maps the two operands to the result.
I am aiming for a 76.6% (561/732) solve rate.
There are four transformations for (AB, CD) -> XY
Reversed operands, reversed result (BA, DC) -> YX
Reversed operands only (BA, DC) -> XY
Reversed result only (AB, CD) -> YX
No transformation (AB, CD) -> XY
There are 32 operators. I have separated them into two groups of operators, so that I match the more popular set of 8 operators first before matching the rarer set of 24 operators.
The code to generate the chain of thought is available here and an example output is available here.
There are operators that are not found in the examples. I assume that they are absolute difference. This increases my target solve rate by 21 / 9500 = 0.2%.
Cryptarithm
There are some discussions on how this is a verbal arithmetic problem.
I did manage to decode some operations if I assume that the operators involve multiplication, division and absolute difference. However, I was not able to craft the chain-of-thought that guides the model to produce the answer.
I reduced the problems to identifying whether the question operator is concatenation or reverse concatenation. If the question operator is not found in the examples, I assume the question operator is concatenation. This helped me to increase my target solve rate by (54 + 11) / 9500 = 0.6%.
The code to generate the chain of thought is available here and an example output is available here.
I am aiming for a 7.9% (65/823) solve rate overall — 8.2% (54/659) on cryptarithm_deduce and 6.7% (11/164) on cryptarithm_guess.
Apparently, Nemotron is also quite bad at splitting and concatenating symbols. I also think perfect performance at this subtask is a baseline expectation to medal in the final leaderboard.
Target solve rate
Overall, I am aiming for an 87.7% (8333/9500) solve rate.
================================================================
Category                      Found  Total   Accuracy     Avg ms
----------------------------------------------------------------
bit_manipulation               1364   1602      85.1%        0.8
cipher                         1576   1576     100.0%        0.1
cryptarithm_deduce               54    659       8.2%        0.0
cryptarithm_guess                11    164       6.7%        0.0
equation_numeric_deduce         540    596      90.6%        0.6
equation_numeric_guess           21    136      15.4%        0.6
gravity                        1597   1597     100.0%        0.1
numeral                        1576   1576     100.0%        0.0
unit_conversion                1594   1594     100.0%        0.1
----------------------------------------------------------------
TOTAL                          8333   9500      87.7%        0.2
================================================================
If the chain-of-thought is achievable and I train the model correctly, I should be able to achieve an 87% or 88% solve rate on the leaderboard. I achieved an 85% solve rate.
I think that any higher solve rate will require new insights on how to even solve the problems programmatically.
Training
The training runs for the winning submission were done on Tinker.
However, the adapter Tinker produces cannot be immediately submitted to the competition.
There are these differences
The key prefix uses model instead of backbone.
Tinker trains with fused expert weights (experts.w1, experts.w2) while the submission format needs per-expert weights (experts.{i}.up_proj, experts.{i}.down_proj).
Tinker trains separate gate_proj and x_proj for Mamba layers, while the submission format needs a single in_proj.
Tinker trains LoRA for lm_head, which is not present in the reference adapter.
I need to implement these changes
Unfuse experts.w1 into per-expert up_proj and experts.w2 into per-expert down_proj, by broadcasting the shared LoRA dimension across 128 experts.
Singular Value Decomposition (SVD) to merge gate_proj + x_proj into in_proj (rank 64 to rank 32).
Rename key prefix from base_model.model.model to base_model.model.backbone.
Keep the LoRA for the lm_head weights.
However, the SVD transformation is lossy, only 75% of singular mass values are captured. There is this training-serving misalignment. These are some behaviors I observed
Not being able to write \boxed
Generating degenerate responses by repeating previous tokens
Not following the template exactly and missing out words
There are multiple remedies for this, which I have yet to apply on my winning submission
Tune on Tinker with rank 16, and losslessly upscale the LoRA to rank 32. However this means that I am not fully using all the ranks. I did manage to score 0.82 with the approach, but apparently it is still making low-level mistakes that are not present in training.
Implementing the finetuning script end-to-end. I needed to research the compute and memory requirements. I did manage to implement something that scores 0.81. However, instead of 8 seconds per step, training is now 50 seconds per step. The cost is around the same anyway, so I continue finetuning on Tinker instead which allows me to iterate much faster.
Post-finetune to align the weights. I have not tried this. The idea is to recapture the loss introduced by SVD on tokens that have their loss increased due to SVD.
End-to-end processes
This is how I iterate on my training
1) I write or update the code that generates the completion traces. This involves the use of AI coding tools. I usually point out the chain-of-thought that I dislike, and what I prefer instead, and I get Claude Code to fix the code. I do not read all the code Claude Code is writing, but if I find Claude Code writing code in a hacky way I will ask it to fix. I inspect the result to check that Claude Code is actually doing what I want.
2) I run the script (reasoning.py) that generates the completion traces. I compare the difference in the output before the edit and after the edit.
3) I send the completion traces (train_sft.py) for finetuning on Tinker. This is the step that is costing money.
4) I inspect the minimum logprob of individual traces. As mentioned, my objective is to maximize the minimum logprob. I find out which traces have a minimum logprob of less than 0.69, which means it is possible that the similar tokens will not be generated in submission.
5) I inspect the tokens with a huge loss. If I see tokens with a logprob more than 0.69, it is likely that similar tokens will not be generated in similar context. I will need to think of how to modify the chain of thought to address the issue.
6) I upload the adapter to Kaggle upload_adapter.py.
7) I run the notebook on Kaggle to convert the Tinker adapter to a submission-compatible adapter and the evaluation. From this I discover that there is some training-serving misalignment. There are easy problems that the model is doing well in training but failed to be correct at validation.
8) Submit the notebook for the public leaderboard score.
These are the training metrics for the winning submission.
Performance
This was computed in a manner similar to the validation notebook.
Version v20 Target
Training tokens 27,850,703 -
Link to training metrics 04-08-16-14 -
Total solve rate on training set 87.8% (8340) 87.7% (8333/9500)
Leaderboard performance 0.85 three times, 0.84 five times -
numeral 100.0% (1576) 100.0% (1576/1576)
unit_conversion 99.7% (1590) 100.0% (1594/1594)
gravity 99.6% (1591) 100.0% (1597/1597)
cipher 99.3% (1565) 100.0% (1576/1576)
bit_manipulation 87.2% (1397) 85.1% (1364/1602)
equation_numeric_deduce 90.8% (541) 90.6% (540/596)
equation_numeric_guess 16.2% (22) 15.4% (21/136)
cryptarithm_deduce 7.1% (47) 8.2% (54/659)
cryptarithm_guess 6.7% (11) 6.7% (11/164)
Note that
I am testing on what the model has trained on. This explains why the training set solve rate is higher than my leaderboard submission.
cryptarithm_deduce / cryptarithm_guess metrics are misleading. This is because cryptarithm_deduce and cryptarithm_guess are trained on multiple epochs. Their minlogprob approached zero, but it was misleading because they have memorized the training set.
Reflections
This is my analysis of why I think I won.
I actually spent quite a lot of time on this. I was on leave since March 31 in Singapore. I initially intended to spend my time on AIMO 3. However, I could not prove that my approach to AIMO 3 works in a small scale, so I invested my time in this Nemotron competition instead.
Things I think I did well
LeetCode. I still do LeetCode for fun. This gave me an advantage in solving bit manipulation better than the competitors. Even though AI can greatly outperform me at LeetCode (which I now feel quite sad about), my competitive programming background gave me the insight on how to reduce the "time and space complexity" of the problem. In hindsight, this contributed more than half the difference between my notebook and Kh0A's notebook.
I looked at the data. I did not merely look at the loss curve - even as the loss curve goes to zero, the loss curve for each category can be very different. I did not merely look at the loss curve per category - even as the loss curve for the category goes to zero, there are still tokens with a huge loss. I looked at the minlogprob. I looked at which tokens the logprob is the lowest. If you only look at the number, you only get a scalar reward. If you look at the data, you get a richer reward signal that informs where you should make your changes.
I know what I do not need to try. There was a discussion on model distillation, but I do not need to do that. I know reinforcement learning approaches are not necessary when you know what the optimal policy should be.
Building a product for myself. The finetuning dashboard was made for myself. It is worth it to just make a finetuning interface just for me to use. I hope this interface can serve as inspiration for building your own tooling.
Using Tinker. Tinker allowed me to iterate much faster. Instead of waiting 4 hours to train on the data, it took me 20 minutes instead. I do not regret spending time to set up training as I learnt about memory and compute requirements. Setting up the training pipeline gave me more respect for the Tinker product.
Writing code locally. This allows me to use Claude Code to write and test procedures. My notebooks are written locally, linted and typechecked before uploading to Kaggle.
Things that could be done better
Writing the validation notebook. As you see, my winning submission failed at some simple tasks like numeral. I am aware of this, but I do not know the scale of how often this is happening.
Investing in a held out validation set. This allows me to predict the public leaderboard score before submitting it. I think it would have been worth it to craft a function that generates valid problems, and train on those problems instead so that the training set can be used for validation, uncontaminated.
Using AI coding tools more effectively. I think I used an appropriate amount of AI in my development. I cannot really use AI fully autonomously because the step involving training with Tinker costs $10 to $20 per iteration. I think it still needs good human judgment to ensure that each Tinker finetuning run is worth it. However, there are some processes where I should have used more AI. One place is the investigation of the tokens with highly negative logprobs. I needed to search for these highly negative logprobs manually. There should be a script that AI can use to write and document these so that we can work on the chain of thought.
Improvements that you can make to score 0.877
Fixing the training-serving misalignment. Currently the SVD decomposition is lossy. I have observed that the model fails at inference at places it did not fail in training. Maybe you could try post-finetuning my model to make sure it scores 100% on the easy tasks.
Work with tokens instead of text. Currently I am working with text. My code produces text, and the text gets tokenized for training. I propose that my code should produce the tokens directly, instead. The true training data should be stored in tokens, not text. I will still render the tokens with text to sanity check the completion traces. This should make half of the token-related task unnecessary (concatenation for example).
Fix Nemotron's ability to convert text to characters. Even as I work with tokens, I do not control the tokenizer in submissions. The base Nemotron is quite bad at converting text to characters, and converting symbol groups to individual characters.
Scaling training. Currently I do not create synthetic problems to train the model. This would require a function that produces problem statements on demand. With this, we can use a part of the training set as validation set.
Predictions
These are my predictions for the final state of the competition
Guaranteeing a score of 0.877 is the baseline to even medal. I think it is possible to train such a model end-to-end in the 30 hour weekly allowance of Kaggle notebooks. There will be people sharing this notebook.
Top solutions will need to maximize their score on bit manipulation. Currently my solution does not solve operations like (ROT(2) XOR NOT SHL(3)) OR SHR(1) because I will run out of tokens. This may involve representing bits with fewer tokens (in base 64 for example).
Top solutions will need to make significant progress on cryptarithm. I think this requires training the model to make guesses. This may mean that I cannot merely continue with my approach of crafting the deterministic chain-of-thought and apply my logprob-zero objective at the sections where guessing needs to happen.
We will be clearer on which problems are actually not possible to solve. For example, for equation and cryptarithm, there are problems where the question operator does not even appear in the problem text. There might be other problems that are indeed proven unsolvable without hurting performance in other problems. This allows us to focus on the problems that we actually can solve.
I hope the competition gets more interesting from now. There is plenty of work to do!
20
29
29
10
add_reaction
comment
38 Comments
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
Tong Hui Kang
TOPIC AUTHOR
Posted a month ago
· 1170th in this Competition
arrow_drop_up
14
arrow_drop_down
more_vert
I have received the DGX Spark!
reply
Reply
31
6
add_reaction
Brandonioti
Posted a month ago
· 81st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Well done, well deserved, really awesome work.
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
14
arrow_drop_down
more_vert
I have published my work, all the best for the remainder of the competition!
Please reach out here if I am missing anything!
reply
Reply
6
add_reaction
MAJ0RT0M
Posted 2 months ago
· 1777th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Hey! - not sure if this is intentional - but the repo seems to be missing at least the following modules/files: trainer,loss_config,lr_schedule,train_common
From train_sft:
from trainer.client import ServiceClient

from loss_config import (
    CrossEntropyLossConfig,
    CrossEntropyWithWeightingLossConfig,
    LossConfig,
)
from lr_schedule import LRSchedule, StepLinearDecayLRSchedule
from train_common import TrainingExample, load_corpus_entries
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
Thanks for pointing out!
These commands should work now
uv run python3 reasoning.py
uv run python3 augmentation.py
uv run python3 corpus.py
These commands should work when you have your environment and API keys set up
uv run python3 train_sft.py
uv run modal run upload_adapter.py
reply
Reply
add_reaction
React
MAJ0RT0M
Posted 2 months ago
· 1777th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thanks for updating! But - just a heads up - I think you may have included some additional work unintentionally
There looks to be some additional utils used to create synthetic data/rebalance the train set/and augment some data rows
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Great observations!
The winning submission included some rebalancing data so that traces with persistently low minlogprob will get another pass at training.
The winning submission did not include synthetic problems. I left the synthetic problems in the release to show that Nemotron is bad at spelling, concatenation and splitting.
reply
Reply
add_reaction
React
Ali
Posted a month ago
· 19th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
Hi, Great write-up 🙂
I started to train on Tinker from the beginning. My best was 0.74 with no CoT traces at all (it scores in like 35 to 40 mins on LB) I trained with around 64K of training data (the original data and auto-generated data based on a solver I wrote, with 82% pass rate on the training data).
So it was easy to hook your work in, I was able to score 0.86 twice and many 0.85 using your nicely fitting data and approach. It seems the 0.86 will be a bottleneck and hard to break without a breakthrough in cryptarithm.
I tried different ways to convert training-serving misalignment. Two approaches work slightly better than your current (my best 0.86 is a direct reason for that).
Thanks for your great contributions.
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted a month ago
· 1170th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for trying out my code and data!
I am curious how did you even get to submit the Tinker adapter even for the 0.74 submission. It was really not easy for me to figure out.
The idea of doing SVD was from Claude Code, I wonder if you did something similar.
My view is that 0.87 is achievable without the breakthrough in cryptarithm.
My bit manipulation chain of thought design is actually not that easy for LLMs to figure out the pattern. It seems that it is still quite hard to get the LLM to decide whether to produce a whitespace (it means there is a match in the correct position) or produce a y (there is a match, but at the wrong position).
reply
Reply
add_reaction
React
Ali
Posted a month ago
· 19th in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
I will publish a notebook that uses one successful approach to convert a tinker adapter to a "ready to submit" adapter. I am not sure if I can score it (since it uses internet - CPU), but I think in the end we are submitting a file, not a notebook. If it didn't submit, I will share it directly; if it did, I will wait for the score. So within an hour :-)
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
Chan Kha Vu
Posted 2 months ago
· 692nd in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
Congrats! You've been one of the most helpful contributor in most of the competitions I've seen you participating (AIMO 1 and 2, this one as well). You completely deserve a DGX station to yourself, even without the progress prize in this competition :)
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thanks for the kind words!
reply
Reply
add_reaction
React
James Day
Posted 2 months ago
· 1172nd in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
Congrats!
I feel like I'll probably be wrong if I try to speculate, but to take a crack at your questions:
"The score I was aiming for" - I'd guess ~90%. That's the best I've gotten an ensemble to score locally, so I suspect it is ~the ceiling of what can realistically be achieved.
"How many tokens are used to train (for the winning submission, and in total)" - More than the top public notebooks 😂. I'd guess you either found a way to get brute-force SFT scaling to work or had a small high-quality SFT dataset followed by RL. You'd be using more tokens than the public notebooks in either case. I'd be a bit surprised if you got 0.85 simply by training on a small super-duper-high-quality dataset (because I've been trying to do that without much success).
"How much money I have spent" - Maybe ~1k? I recall seeing in your post history that you were renting a Pro 6000 for $3/hr. 50% uptime for 24 days would cost a little under $1k. I'd be a bit surprised if you used less than that, but not surprised if you used more.
"What do you think is the secret" - Oh man. You're miles ahead of me and I'm relatively new to LLM finetuning, so your post will likely be a goldmine of multiple secrets I'm eager to read. IDK what you view as the secret sauce, but I'm most curious to read about your data generation strategy and the degree to which you relied on SFT vs RL.
reply
Reply
add_reaction
React
lucian kucera
Posted 2 months ago
· 2167th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
90% makes sens, since about 10% samples will likely be faulty.
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
5
arrow_drop_down
more_vert
Congrats!
Looking for your current solution.
I hope the rest of the competition won't just be knob tuning on your code. We'll see.
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
it will be ofcourse 🙃
reply
Reply
7
add_reaction
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
People have started forking and submitted your model as you haven't published base work most will stay on focked score as getting over need more computation then rtx 6000 pro and a pro plan as of my experience 0.79 score on rtx 6000 pro is achievable but above it without any more computation is mostly impossible I can be wrong also but I think releasing model invited people with no work and no brain tosted to get good score and people could only improve from this score by a highly efficient plan with a large computation that is not possible on rtx 6000 Pro I may be wrong but as of my experience till now competition is increased in unfair way
I will get down vote from all of them😉
reply
Reply
add_reaction
React
Barno Barno
Posted 2 months ago
· 3592nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Have you tried retraining his adapter further ? (also pls use some punctuation )
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I used to bunk grammar classes and ultimately failed 😁😁 and I have tried everything and will try till end
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
This is another plus point of Open Progress Prize. You can use the rank 1 adapters, most of the compute-heavy pretraining is already done and only some relatively cheaper refinement is needed to improve it.
reply
Reply
add_reaction
React
Adarsh Kumar
Posted 2 months ago
· 762nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Yes in frustration I forgot that 🙃 thanks for the idea
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
The guidelines mention that the external data we use (assuming this already trained lora adapters falls in it) shall be publicly available to everyone equally and be of 'minimal cost'. Since he has made the solution public, I think we can use it, don't know about the latter condition though. lol
reply
Reply
1
add_reaction
Svanik Kolli
Posted 2 months ago
· 141st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Congrats on the incredible performance, Tong!
Cracking 0.85 when the field was clustering at 0.84 is a massive achievement. Here are my specs on your questions:
Target Score: You were definitely hunting for that 0.85+. It’s the safety zone that separates a lucky run from a dominant model, and hitting it right at the deadline shows how much you pushed the 30B architecture.
Tokens: I’m guessing the winning run was surprisingly efficient maybe 200M to 500M high-quality tokens. Given your focus on visualizing the problems, it feels like you prioritized high-signal reasoning traces over raw volume.
Spend: Since you’re a master of optimization (using Unsloth and 96GB VRAM setups), I’d bet you kept it lean somewhere between $300 and $500 USD by leveraging spot instances and Kaggle’s internal resources.
Secret: I suspect the secret is Rejection Sampling with a Verifiable Reward (RLVR). Since you mentioned your AIMO work, you likely built a pipeline that forces the model to generate specific reasoning thought blocks that must lead to a correct symbolic answer before they are added to the training set.
Can’t wait to see the interface and notebooks on Sunday!
Best, Svanik Kolli
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted 2 months ago
· 1893rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
94%, 5k, $100, I don't understand "secret" here.
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted 2 months ago
· 1893rd in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
But I think the "secret" should be how to make steps tractable and in the correct order if you're doing SFT. RLHF lets the model figure that out.
reply
Reply
add_reaction
React
Nguyen
Posted 2 months ago
· 2107th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Congratulations! Base on your submit freq, I guess 5h h200 is enough.
reply
Reply
add_reaction
React
toxu
Posted 2 months ago
· 20th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
congratulations! Really looking forward to reading your write-up and learning from your methods.
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
Thanks!
It seems that you only made 4 submissions on April 9 the final day. I was waiting for your 43rd submission before I submit mine, but I was too tired and gave up at 6:30am, made my final submissions, and went to sleep.
reply
Reply
1
add_reaction
einherjer
Posted 2 months ago
· 2617th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
The temperature in the leaderboard evaluation metric is 0.0.
@huikang the competition metric notebook shows temperature as 1.0. Not 0.0. Is that just a typo?
def score(
    ...
    temperature: float = 1.0,
    ...
) -> float:
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
The defaults are defaults and were being overridden
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Many congratulations @huikang! I think now you can use the DGX Spark immediately for the rest of the experiments in this competition 😅. About the guesses, I think you would have spent <$50 on data. Because I think the secret ingredient (if any) would be the data, or the teacher model. I estimated the cost of using a big deepseek model (haven't spent yet worrying about the what cost is considered 'minimal' as per the rules) and it was coming out to be $25 in api. However, from some of your discussions I realize you have also experimented a lot. So in compute I highly believe it would be something close to $100.
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1449th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Hi @huikang, just wanted an update. Is the solution delayed or uploaded somewhere else maybe? I was checking since morning as you mentioned 12th April but didn't get yet. Please update the estimated date for everyone to refer easily. Thankyou
reply
Reply
add_reaction
React
Durga Kumari
Posted a month ago
arrow_drop_up
-1
arrow_drop_down
more_vert
Really impressive breakdown Especially the focus on deterministic chain-of-thought and min logprob optimization
reply
Reply
add_reaction
React
emoji_people
Adithya Hegde Kota
Posted 2 months ago
· 2073rd in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
firstly orz @huikang , great work we'll meet on leaderboard hopefully!
reply
Reply
add_reaction
React
Bhawesh Sinha 07
Posted 2 months ago
arrow_drop_up
-1
arrow_drop_down
more_vert
Congratulations on this! Keep it up
reply
Reply
add_reaction
React
Ogurtsov
Posted 2 months ago
· 730th in this Competition
arrow_drop_up
-11
arrow_drop_down
more_vert
The prize for best intermediate solution is good, but publishing it now is worst innovation ever.
reply
Reply
add_reaction
React
Yurnero
Posted 2 months ago
· 3rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
worst innovation ever
reason?
reply
Reply
add_reaction
React
Ogurtsov
Posted 2 months ago
· 730th in this Competition
arrow_drop_up
-5
arrow_drop_down
more_vert
Because it's like publishing top score notebook near the competition end. Yes, we are just on 1/3 of timeline, but best public solution is much stronger than ordinary top score notebook.
reply
Reply
add_reaction
React
3 more replies
arrow_drop_down
Murugesan Narayanaswamy
Posted a month ago
· 1662nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I am new to this competition - I am wondering without using GRPO and solving the challenge that are mostly programmatically solvable using SFT based on CoT traces (an AI agent would do it with the same python scripts), are you not simply overfitting the adapter for the training dataset? Especially since you are getting same score with the test dataset (which seems to have exact same distribution of problems), are you not overfitting a model for a problem that can be much more efficiently solved through simple python program? Why you need a costly Nemotron inference for a problem that can be solved by a simple python script?
On the other hand, if the trained adapter could solve any such problem, then it is worth the training as it would mean that it has learnt some reasoning circuits which cannot be programmatically implemented and the problems cannot be solved by other means.
If the above 0.85 score is achieved through pure GRPO training (which I think not feasible without a prior cold start SFT with CoT traces), then we can say Nemotron has acquired reasoning capability to solve these kind of problems like bit manipulation, cypher problems etc.
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
Huge congrats on the win! Your approach to maximizing minimum logprob and the deterministic CoT design is brilliant. Truly well deserved!
reply
Reply
add_reaction
React
Roadie
Posted a month ago
· 343rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Great write-up. Congratulations!
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
How much did a complete training run cost you on Tinker?
reply
Reply
add_reaction
React
Tong Hui Kang
TOPIC AUTHOR
Posted a month ago
· 1170th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Just for the winning submission - 27,850,703 x $0.40 = $11.14
reply
Reply
1
add_reaction
This comment has been deleted.
This comment has been deleted.
This comment has been deleted.

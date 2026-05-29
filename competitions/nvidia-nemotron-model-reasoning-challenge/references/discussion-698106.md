# Appreciation (1)

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/698106#3459134
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 8192

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
How to Get Started + Nemotron Model Reasoning Challenge Resources
Strategy to solve 85% of bit manipulation
Mainstream LLM Performance Comparison：Gemini-3.1-Pro delivers the best performance, while DeepSeek-V3.2 is also highly impressive.
Kaggle CLI — Develop Locally and Run on RTX Pro 6000 GPU
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
RYAN HOLBROOK · POSTED 21 DAYS AGO
·
KAGGLE STAFF
arrow_drop_up
22
arrow_drop_down
more_vert
Metric Update
Hi everyone,
I just deployed a fix to the metric that should address the issue of answers with the '}' character not being correctly extracted. I've tested it against a variety of inputs, and I believe it should be robust. If it seems like it's not working though, please let me know.
Also, since this fix should only improve scores, I won't be doing a rescore. Instead, just resubmit anything you want scored again.
Please let me know if you have any questions or concerns.
add_reaction
React
comment
15 Comments
1 appreciation comment
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
Ogurtsov
Posted 13 days ago
· 730th in this Competition
arrow_drop_up
5
arrow_drop_down
more_vert
I suppose rescoring is needed at least for private test calculation with updated metric. Otherwise private scores would be computed with different metrics for early and later submits. @ryanholbrook please confirm how this issue will be resolved.
reply
Reply
add_reaction
React
RB
Posted 14 days ago
· 1171st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
We resubmitted 3 models - none of them improved either.
reply
Reply
add_reaction
React
emoji_people
Kishan Vavdara
Posted 14 days ago
· 14th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Similar results for us too. Instead of improving, score reduced by third decimal. In selecting the final submission this will be problematic. @ryanholbrook if there will be no rescoring with new metric how will the final submission score finalized. Suppose our best sub is on older metric and we select that, will you rescore it with new metric after competition end?
reply
Reply
add_reaction
React
emoji_people
Ravi Ramakrishnan
Posted 14 days ago
· 14th in this Competition
arrow_drop_up
-4
arrow_drop_down
more_vert
@kishanvavdara fair point.
Also there should be a policy that such material changes should be ensued in the first week/ 2 weeks of the competition. Adjusting such a core element after the half way point of the competition and after handing over a prize for early success is not optional at all.
I have raised this issue earlier as well. Competitions lately are witnessing a lot of such material changes during the training period. Perhaps better governance is the need of the hour..
reply
Reply
1
1
add_reaction
3 more replies
arrow_drop_down
Ali
Posted 19 days ago
· 19th in this Competition
arrow_drop_up
6
arrow_drop_down
more_vert
I am also seeing some kind of 1% drop in scores.
If my understanding is correct, the update is to fix such cases, right?
True answer: +}
Model output: \boxed{+}}
Old metric extracted: +
New metric extracts: +}
Result: now correct
But if for some reason the model added } at the end of boxed, like this :
True answer: 42
Model output: \boxed{42}}
Old metric extracted: 42
New metric extracts: 42}
Result: wrong
Then our score will go down with the new update.
So maybe this is the case? The public LB does not have problems with "}" in the answer (or our models can't handle it correctly in the first place), but might have some outputs with multiple }} in the boxed output, which causes the wrong answer to other problems.
PS: In my local tests, I see an increase of 2%, but my local validation set outputs do not include a case with }} beside the ones needed fix.
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 18 days ago
arrow_drop_up
6
arrow_drop_down
more_vert
This seems like an ambiguity that doesn't have a clear resolution. I'm still in favor of keeping the fix, though, since it allows a larger subset of problems to be correctly answered which were simply impossible before.
reply
Reply
add_reaction
React
JK-Piece
Posted 20 days ago
· 8th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Thanks for the update. My first feedback is that it has dropped my score by 1%. So from 0.86 to 0.85. But you expected it to increase scores! There is something wrong probably. I will do some tests with the new metric and provide updates here.
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 18 days ago
arrow_drop_up
1
arrow_drop_down
more_vert
If you discover an error, please let me know!
reply
Reply
add_reaction
React
JK-Piece
Posted 18 days ago
· 8th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
My tests did not reveal any issue yet. So I guess the answer extraction script works well.
reply
Reply
add_reaction
React
NoOneAhead
Posted 21 days ago
· 181st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I'm not sure what went wrong; the same file submission is now getting a score 0.02 lower than before.
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 21 days ago
arrow_drop_up
1
arrow_drop_down
more_vert
Maybe try submitting it again? There is some non-determinism inherent in the evaluation. It's possible the metric change didn't affect you much, but you're just seeing variation in vLLM.
reply
Reply
add_reaction
React
Tong Hui Kang
Posted 21 days ago
· 1170th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
PSA that the metric notebook is at https://www.kaggle.com/code/metric/nvidia-nemotron-metric/notebook
reply
Reply
add_reaction
React
Ra'uf Fauzan Rambe
Posted 21 days ago
· 112th in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
Sure I am give a solution in this the problems:
Can have make code into character answer correctly this the import Library this import re to handle the patterns, but I'll make sure my regex is now robust enough to match your fix.
This is mine solutions
reply
Reply
add_reaction
React
Harshit samrat
Posted 21 days ago
· 1987th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Any chance you can allocate more compute for the metric calculation takes 2 hrs to test one adapter ;)
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 21 days ago
arrow_drop_up
3
arrow_drop_down
more_vert
You should rely on local CV to evaluate your adapter. Relying on public leaderboard is a recipe for overfitting.
Remember that what matters is your score on the private test data, not the public test data.
Back to why evaluation takes two hours is because we kept enough samples for the test data to avoid to much instability in scoring. There is still some instability. If we were to modify it then I'd advocate for using more samples in test data, which would mean longer scoring.
reply
Reply
add_reaction
React
This comment has been deleted.
Appreciation (1)
CPMP
COMPETITION HOST
Posted 21 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you Ryan.

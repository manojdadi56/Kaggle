# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694975
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 10658

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
Ground Breaking Discovery regarding SFT[MUST WATCH]
Использовать определенный accelerate через kaggle api
Why people downvote?
Is it difficult to improve your score in this competition?
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
MURUGESAN NARAYANASWAMY · 1665TH IN THIS COMPETITION · POSTED A MONTH AGO
arrow_drop_up
-22
arrow_drop_down
more_vert
GRPO is must for this competition
Congratulations to @huikang for the mid-progress prize! What a tremendous effort he had put and then his kaggle spirit making everything public!
But there is one thing I disagree - his strategy for this competition where he says he bets against reinforcement training ('I already have the optimal policy for solvable problems. I already know the best next token for the LLM to make (assuming they have been making all the correct moves). The only job of the LLM is to follow the policy')
The concept of machine learning is meant for function approximation where no singe programmatic function can be designed to model the system behavior. In the case of Nemotron reasoning challenge, it has been shown most of the problems can be programmatically solved. Why do we then require a machine learning or AI model? Given that the same argument can be applied for LLMs acquiring capabilities for numerical calculations (that calculators can do) and basic programming tasks, we can argue that building such reasoning capabilities as part of the LLM weights can strengthen the reasoning horizon of LLMs like the way coding and math increased the overall reasoning capabilities.
However, if these reasoning capabilities should become core of the AI model, then it cannot overfit the given training samples. If the training samples can be solved upto 87% and the test data would also give a leaderboard score of 0.87, the whole exercise becomes meaningless.
On the other hand, I think it is for these kind of problems, the reinforcement learning is envisaged - the model has to build its own reasoning paths to achieve the specified goals. However, the model has infinite states to explore which makes GRPO quite challenging. The solution is the cold start SFT where the basic paths are built using CoT traces. Once the basic boundary and context is set, then GRPO can explore the various reasoning paths to achieve the goals. This is why DeepSeek-R1 used DeepSeek's CoT traces before GRPO training.
In this competition, this makes GRPO very essential. In fact, the mid-progress prize of 0.86 is literally so - the model trained for 0.86 score should now be trained with GRPO so that it builds generic reasoning circuits that strenthen the core reasoning capabilities of the model.
In fact, I am convinced that the winning pipeline for this competition would be exactly similar to the pipeline used by deepseek for creating a full fledged reasoning model! So, I think GRPO is quite essential part of this competition and I strongly disagree with @huikang and consider without GRPO, the model will not learn a generic policy that would help strengthen its reasoning capabilities.
add_reaction
React
13 Comments
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
Taha
Posted a month ago
· 421st in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
See this amazing GPRO notebook yet it yields same results HERE
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted a month ago
· 1665th in this Competition
arrow_drop_up
-2
arrow_drop_down
more_vert
Thanks, will look into it! Need to see whether he is using DAPO instead of GRPO for efficiency purpose or it serves better for this usecase.
Also, GRPO/DAPO needs to be run for each category of problems separately - if data is not sufficient for individual category of problems, then synthetic data needs to be created with minor variations.
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted 24 days ago
· 1665th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
oh, sorry, running GRPO for each category separately can lead to catastrophic forgetting. Quite a lot of time since I did ML training! But the point that additional set of newly created synthetic data and extra data where required will be necessary if you are going to train again with GRPO is still correct.
reply
Reply
add_reaction
React
FO-SHIZZLE
Posted a month ago
· 139th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
why would anyone give this Discussion a -1?
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
0
arrow_drop_down
more_vert
See https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694975#3450715
reply
Reply
add_reaction
React
Ogurtsov
Posted a month ago
· 730th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
In this competition, this makes GRPO very essential. In fact, the mid-progress prize of 0.86 is literally so - the model trained for 0.86 score should now be trained with GRPO so that it builds generic reasoning circuits that strenthen the core reasoning capabilities of the model.
The only real goal (for participants) of any kaggle competition is to achieve a good score on unseen test dataset. We assume test set, at least public, is very similar to the train one, and we have strong evidence of it. And if train samples are composed this way, we have nothing to do but fine-tune model to solve programmatically solvable tasks.
p.s. I don't see any examples in between programmatically solvable and completely unsolvable ones like inferring the meaning of symbol without training examples.
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted a month ago
· 1665th in this Competition
arrow_drop_up
-2
arrow_drop_down
more_vert
In classical machine learning, we have this concept of splitting the dataset into training and validation / test dataset. However, those datasets cannot be solved programmatically. So, taking a sample of training dataset and keeping it for testing works. But when the training dataset is programmatically solvable, the test dataset should bo beyond the training dataset distribution. If competition organizers did not bother about this and the idea is just to convert the program logic involved in training dataset into LLM weights, then it is fine!
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted a month ago
· 1665th in this Competition
arrow_drop_up
-4
arrow_drop_down
more_vert
I am wondering - are these downvotes due to disagreement with 'content' of this post or 'presentation style' of the post?!😄 It's three years since I participated in any kaggle competition, guess a lot of rules have changed - not sure what downvotes and upvotes serve! If its due to presentation style - ok, whomever downvotes feel so - but if its about content, then there is no freedom of speech! Upvotes should be meant to raise or lower the posts ranking in discussion forum but downvotes should not be used for that purpose
reply
Reply
add_reaction
React
emoji_people
Saicharan Ramineni
Posted a month ago
· 117th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I think some people just downvoted everything.
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
10
arrow_drop_down
more_vert
I'm not sure, but maybe it is this:
You make lots of claims, you criticize the mid point winner strategy, but haven't submitted at all.
Maybe you are right, but the only way to prove it is to submit and get a better score. Kaggle is not a place where opinion matters. Scores matters. It is why Kaggle is valuable: it cuts through the hype and crap that is so pervasive in AI on social media.
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted a month ago
· 1665th in this Competition
arrow_drop_up
-6
arrow_drop_down
more_vert
Sorry, but I am not participating in this competition. All the best!
reply
Reply
add_reaction
React
5 more replies
arrow_drop_down
emoji_people
Saicharan Ramineni
Posted a month ago
· 117th in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
Have you considered why no one else has implemented GRPO yet?
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted a month ago
· 1896th in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
I'm curious; why not?
reply
Reply
add_reaction
React
emoji_people
Taha
Posted a month ago
· 421st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
too slow , but peope did fix and gpro is waste of compute i feel
reply
Reply
1
add_reaction
4 more replies
arrow_drop_down
CPMP
COMPETITION HOST
Posted a month ago
arrow_drop_up
0
arrow_drop_down
more_vert
No one shared a public notebook with GRPO would be more appropriate.
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
TOPIC AUTHOR
Posted a month ago
· 1665th in this Competition
arrow_drop_up
-5
arrow_drop_down
more_vert
It's three years since I have interacted with you! Glad you are now organizing this competition!
I am wondering whether the test dataset can be a split of training dataset when the problems are programmatically solvable, if the objective is to make Nemotron acquire generic reasoning capabilities. May be it has completely different distribution but still SFT with CoT enables a score of 0.86, which would be a tremendous achievement. If this clarity is not there, then any methods to improve the score from 0.86 would be mostly one of overfitting rather than extending the capabilities.
reply
Reply
add_reaction
React
This comment has been deleted.

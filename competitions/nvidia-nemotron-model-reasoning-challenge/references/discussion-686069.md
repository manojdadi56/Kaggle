# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686069
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 6421

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
Zero shot predictions
Something wrong -- My notebook of 0.80+ now scores 0.77
RTX PRO 6000 Blackwell — CUDA kernel incompatibility status + GPU time spent debugging
Edge case in metric: \boxed{} cannot contain }
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
ENDREAM · 2108TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
16
arrow_drop_down
more_vert
Per-Category Error Analysis After SFT (0.63 LB) — Where the Real Bottlenecks Are
I ran error analysis on 300 stratified samples (50 per category) after SFT training (1200 samples, LoRA rank 32, 2 epochs). Here are the per-category accuracy numbers:
Category Accuracy Error Pattern
numeral 100% —
unit_conv 100% —
bit_ops 30% Model guesses plausible but wrong bit patterns
gravity 12% Numerical errors of 10-25%, model doesn't compute g correctly
cipher 0% Outputs random plausible words, no actual decryption
symbol 6% Completely wrong outputs
Key observations:
Format is not the issue. All 176 errors had properly formatted \boxed{} output — the model learned the output format perfectly. The problem is purely about reasoning quality.
cipher at 0% is the most striking. The model outputs grammatically correct phrases with the right number of words (e.g., predicts "the wise mouse draws" when the answer is "the clever turtle sees"), but it's not actually doing any letter-by-letter substitution. It's generating plausible-sounding text.
gravity errors are systematic, not random. The predicted values are always in a reasonable range but off by 10-25%. The model seems to be "estimating" rather than computing g = 2d/t² from the examples.
symbol data quality may be a factor. Consistent with other threads discussing dataset hallucination — many symbol problems may not have uniquely determinable answers from the given examples.
What I'm trying next:
Programmatic CoT for cipher and gravity (writing out the actual computation steps, not just "The answer is X")
Synthetic data generation for gravity/unit_conv/cipher (we can generate unlimited training examples with verified answers)
GRPO with task-specific reward functions (continuous reward for gravity based on numerical error, per-word reward for cipher)
Would be curious if others see similar per-category breakdowns. Is anyone having success with cipher specifically?
add_reaction
React
4 Comments
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
James Day
Posted 2 months ago
· 1175th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
Your SFT results are quite a bit different from mine… I'm having more trouble with the bit manipulation puzzles and less trouble with the cipher & gravity ones.
CV results from my best model (0.68 LB) are included below. These were measured with 1K questions from outside the training dataset.
Category Accuracy with 8K token limit Accuracy with 16K token limit
bit_manipulation 9.9% 18.8%
numeral_system 100.0% 100.0%
physics_gravity 98.8% 98.8%
symbol_transform 17.3% 20.7%
text_cipher 75.5% 76.1%
unit_conversion 100.0% 100.0%
overall 67.1% 69.3%
I suspect my bit manipulation failures largely stem from distilling models which yap too much. Qwen3.5 27B with thinking "disabled" and no special instructions can solve 49% of those problems within 16K tokens, but accuracy drops to 10% at 8K, so I likely have some poisonous examples in my training data 🙃
reply
Reply
add_reaction
React
MD Mushfirat Mohaimin
Posted 2 months ago
· 2475th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@endream is training the model to directly output \boxed{answer}, no thinking.
And you're distilling Qwen3.5 27B
that's causing the difference.
reply
Reply
add_reaction
React
EnDream
TOPIC AUTHOR
Posted 2 months ago
· 2108th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Thanks for sharing your breakdown — this is really valuable! Your gravity at 98.8% vs my 12% confirms the issue is my training approach, not the task itself.
The key difference seems to be CoT quality. I was training with "The answer is X.\boxed{X}" (basically no reasoning), while your distilled CoT likely teaches the model the actual computation steps.
Interesting that your bit_ops drops from 18.8% to 9.9% at 8K tokens — I hadn't considered token truncation as a major factor. Are you doing anything specific to keep outputs concise?
I'm now experimenting with higher-quality CoT data and will report back.
reply
Reply
add_reaction
React
James Day
Posted 2 months ago
· 1175th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Are you doing anything specific to keep outputs concise?
Nothing besides setting thinking to disabled, running it multiple times to cherry pick the shortest correct answer, and switching to Gemma 4.
Populating the system prompt with examples of the patterns that frequently appear in the current type of question generally makes the reasoning traces longer, not shorter. I haven't put much effort into prompt engineering.
reply
Reply
add_reaction
React
EnDream
TOPIC AUTHOR
Posted 2 months ago
· 2108th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Got it, thanks.
reply
Reply
add_reaction
React
lucian kucera
Posted 2 months ago
· 2171st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Interesting, since in zero shot setting it seems to do well on ciphers.
reply
Reply
add_reaction
React

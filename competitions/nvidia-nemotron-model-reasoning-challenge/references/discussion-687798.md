# Match the LAST \boxed{…}, allowing nested braces

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687798#3454461
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 12393

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
Metric Update
How to Get Started + Nemotron Model Reasoning Challenge Resources
Strategy to solve 85% of bit manipulation
Mainstream LLM Performance Comparison：Gemini-3.1-Pro delivers the best performance, while DeepSeek-V3.2 is also highly impressive.
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
RYAN HOLBROOK · POSTED 2 MONTHS AGO
·
KAGGLE STAFF
arrow_drop_up
16
arrow_drop_down
more_vert
Rescore After Metric Update
Hi everyone,
Recently, there was an update to the evaluation metric that fixed a bug that was causing binary answers to match as floats instead of exactly as strings. This update led to a drop of about 0.3-0.4 points on new submissions. (The update is in the verify() function of the linked notebook.)
So that the leaderboard will only reflect submissions using the new metric, I will be initiating a rescore on Monday. This rescore will only evaluate those submissions that both are still present on the Public Leaderboard and that were made on or before March 28th, that is, prior to the metric update. This will affect a little less than 2/3 of the current LB. Other submissions made on or before March 28th, I will invalidate. Submissions made after that time will be preserved.
Why are we not rescoring every submission? Unfortunately, this would amount to over 9000 rescores and would strain our available capacity of the special GPUs used in this competition. We believe the above approach is the best compromise, that both preserves the existing leaderboard and maintains GPU availability for the community going forward.
Please let us know if you have any questions or concerns below.
add_reaction
React
comment
15 Comments
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
Pinned comments
push_pin
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
3
arrow_drop_down
more_vert
The rescore is complete!
reply
Reply
add_reaction
React
push_pin
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
4
arrow_drop_down
more_vert
I am about to begin the rescore process. The leaderboard may be in a strange state for a bit until the rescore completes. Here is what will happen:
DONE I will invalidate submissions not still present on the leaderboard that were made on or before March 28th.
DONE I will initiate a rescore of those submissions still present on the leaderboard that were made on or before March 28th.
The rescore may take awhile to complete. I will keep you updated here.
reply
Reply
2
add_reaction
All other comments
Tong Hui Kang
Posted 2 months ago
· 1170th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
I want to confirm if the stored answer is 0234, is 234 the considered correct?
I remember someone wrote a comment asking this, but I think it has since been deleted.
import re
import math

def verify(stored_answer: str, predicted: str) -> bool:
    # Clean up strings
    stored_answer = stored_answer.strip()
    predicted = predicted.strip()

    # If the answer is a binary string, compare strictly as strings
    if re.fullmatch(r'[01]+', stored_answer):
        return predicted.lower() == stored_answer.lower()

    try:
        # Try to convert the answers to floating point numbers
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        # Use a small absolute tolerance for numbers near zero
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception as e:
        print(e)
        # Fallback to case-insensitive string comparison
        return predicted.lower() == stored_answer.lower()

print(verify("0234", "234"))
Currently this is True.
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
I will look into it. As this would require another update and rerun, perhaps it's better to accept the ambiguity if it doesn't meaningfully affect the scores. Will let you know.
reply
Reply
add_reaction
React
Sangram Patil
Posted 2 months ago
· 356th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
One of the bit manipulation questions is:
In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers. The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, and possibly majority or choice functions.

Here are some examples of input -> output:
01100110 -> 00000001  
01111111 -> 10000001  
11111111 -> 10000011  
00011110 -> 00000000  
11000011 -> 10000011  
00100101 -> 10000000  
11100101 -> 10000011  
11100100 -> 00000011  
01011110 -> 00000001  

Now, determine the output for: 01011000
The given ground truth label is 1 only, but the expected output is 00000001. So I think the labels were created according to this format.
Also, some of the ground truth labels in the bit manipulation tasks are not 8-bit (e.g., 1, 111101, 1000100, 10111111, etc.). Even if we train the model to predict 8-bit outputs, we need the ground truth labels to be in the same format if we want to compute accurate metrics.
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
-1
arrow_drop_down
more_vert
chatGPT, Gemini, Claude? Which one did you use?
reply
Reply
4
add_reaction
Sandy
Posted a month ago
· 1466th in this Competition
arrow_drop_up
-2
arrow_drop_down
more_vert
has the submissions been rescored today too? i am sure i had 5x0.84s and 2x0.85 before
reply
Reply
add_reaction
React
emoji_people
Ravi Ramakrishnan
Posted 2 months ago
· 14th in this Competition
arrow_drop_up
-3
arrow_drop_down
more_vert
@ryanholbrook I wish to purport that a lot of the recently launched competitions are having such operational issues including-
Post launch metric adjustments
Post launch data adjustments
Post launch data + metric adjustments
Ethical issues resulting in pausing the competition after launch
I think some additional operational enhancements with human-driven supervision could be improved to curb such post-launch sub-optimalities.
reply
Reply
2
3
add_reaction
CPMP
COMPETITION HOST
Posted 2 months ago
arrow_drop_up
0
arrow_drop_down
more_vert
Which ethical issues? Which post launch data adjustment?
There has been one metric change so far.
reply
Reply
add_reaction
React
ImperfectKitto
Posted 2 months ago
· 608th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@ravi20076 is most likely talking about overall decline in quality of Kaggle competitions (those are issues other past and current competitions have)
reply
Reply
add_reaction
React
emoji_people
Ravi Ramakrishnan
Posted 2 months ago
· 14th in this Competition
arrow_drop_up
-1
arrow_drop_down
more_vert
@defdet yes, a lot of the recently launched competitions in the last 4-5 months have had these issues. I am unsure if this is due to AI usage / supervision / governance issues.
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
Why use this competition forum for a cross competition discussion?
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
4
arrow_drop_down
more_vert
Hi @ravi20076,
I will bring your concerns up with the team. You might wish to raise them in the Product Feedback forum instead to keep this forum on topic.
reply
Reply
add_reaction
React
Chew Kok Wah
Posted 2 months ago
· 82nd in this Competition
arrow_drop_up
4
arrow_drop_down
more_vert
Host willingness to adjust Metric and data when error is found is showing a behavior of high integrity. It is unfair and discouraging to them to negatively turn a highly ethical behavior into something negative.
Beside that, there is no way to confirm if all the past Competitions before these 4, 5 months is better or worst in term of data or Metric incorrect issues. Most of them are private and never reveal to you.
reply
Reply
add_reaction
React
songningyu
Posted 23 days ago
· 1734th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Bug Report: extract_final_answer regex fails when the ground truth answer contains a literal } character
The extract_final_answer function in the metric uses the following regex to extract answers from \boxed{}:
matches = re.findall(r'\boxed{([^}]*)(?:}|$)', text)
The pattern [^}]* stops at the first } character encountered. This works correctly for most problem types, but fails systematically for equation_symbolic problems where the answer itself can contain } as a literal symbol character.
Example: problem b50cf853
Ground truth answer: |?"} (four symbols: |, ?, ", })
The model is instructed to output \boxed{|?"}
In the raw output this appears as: \boxed{|?"}}
The regex [^}]* matches |?" and stops at the first }, extracting |?" instead of |?"}
Result: |?" ≠ |?"} → marked incorrect, even though the model produced the right answer
Impact:
94 out of 9500 problems in the training set (all equation_symbolic type) have answers containing }. These are impossible to answer correctly under the current extraction logic, regardless of model quality. This means the theoretical maximum accuracy is capped at approximately 99.0% instead of 100%.
Suggested fix:
Use a greedy/balanced-brace matching approach instead of [^}]*, for example:
Match the LAST \boxed{…}, allowing nested braces
matches = re.findall(r'\boxed{((?:[^{}]|{[^{}]}))}', text)
Or alternatively, accept escaped braces like } inside boxed content.
reply
Reply
add_reaction
React
Muhammad
Posted 2 months ago
· 3453rd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@ryanholbrook I just want to do inference on the model to check results but """PermissionError: [Errno 13] Permission denied: '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia-utility-script/triton/backends/nvidia/bin/ptxas-blackwell'"""
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
@ryanholbrook
In the overview tab we can find this.
but in the last version (14th) of the NVIDIA Nemotron Metric notebook I see this
def score(
    solution: pd.DataFrame,
    submission: pd.DataFrame,
    row_id_column_name: str,
    max_lora_rank: int = 32,
    max_tokens: int = 3584,
    top_p: float = 1.0,
    temperature: float = 1.0,
    max_num_seqs: int = 128,
    gpu_memory_utilization: float = 0.85,
    max_model_len: int = 4096,
    debug: bool = False,
)
Is it a placeholder and actual scoring parameters are correct in the overview tab. I'm specifically interested in max_tokens and max_model_length
reply
Reply
add_reaction
React
Ryan Holbrook
KAGGLE STAFF
Posted 2 months ago
arrow_drop_up
2
arrow_drop_down
more_vert
The defaults are only defaults. The correct parameters are in the Overview tab.
reply
Reply
add_reaction
React
Yashpal M
Posted 24 days ago
· 2225th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
@ryanholbrook I need to update the bitsandbytes package in the run (I am using the 2026-02-18 PIN to Environment) 2/ Can I include any other POST training for LoRA.DoRA any specific training requirements.
/edit @ryanholbrook @cpmpml What is the PYTHONPATH you used in the utility script. I can not edit the export in the utility script.
reply
Reply
add_reaction
React

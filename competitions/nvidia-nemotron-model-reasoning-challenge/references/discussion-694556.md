# symbol_transformation would benefit from a stated rule class: finite examples cannot identify arbitrary operations

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694556
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 24258

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
[update] Read CPMP's reply. [original] Do not distill models that do not allow distillation (e.g. gemini, gpt5)
[Fake Notebook Alert] Watch out for fake laptops that copy and upload other people's submission.
Are problem types the same for train and test?
Training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences
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
TOOLAZYHHH123 · POSTED A MONTH AGO
arrow_drop_up
24
arrow_drop_down
more_vert
symbol_transformation class problem can have multiple valid candidate answer
symbol_transformation would benefit from a stated rule class: finite examples cannot identify arbitrary operations
First off — thank you to the organizers for putting this benchmark together. Rule-induction puzzles are a great testbed, and I've enjoyed working on this category. I'd like to share a concern in the spirit of making the task even stronger, and I'd love to hear the team's thoughts.
Quick terminology note: I don't mean to imply that symbol_transformation is an official competition label unless the organizers use that term elsewhere. I'm using it as a shorthand for the prompt family identifiable by wording like "a secret set of transformation rules is applied to equations." In other words, this is the equation/symbol rule-induction family, not a claim about a published taxonomy column.
TL;DR
The symbol_transformation tasks ask models to infer hidden operations from a few examples. My worry is that finite examples cannot uniquely determine an arbitrary binary operation: for any proposed query answer, one can construct a function that fits all given examples and still produces that answer. So the task is well-defined only relative to a restricted rule class or DSL. Without publishing or validating against that rule class, exact-match scoring may end up measuring prior-matching more than reasoning from the examples. I suggest a few small changes below that I think could meaningfully sharpen the category.
The underlying issue: finite examples do not identify a binary operation
I want to raise this constructively. The puzzles being hard is not the issue — hard rule-induction puzzles are valuable, and that's part of what drew me to this category. The concern is narrower: unless the benchmark specifies a restricted class of allowed rules, the target answer isn't mathematically determined by the examples alone.
A typical puzzle is asking the model to infer a hidden binary operation:
f
(
)
from finitely many examples:
and then apply it to a held-out query:
f
(
)
?
From finitely many input-output examples, an arbitrary function $f$ is never uniquely identifiable. This isn't just a philosophical point — the ambiguity can be made fully explicit.
First, encode each input pair $(x, y)$ as a single integer $t$ (for example, by concatenating the two strings with a separator and mapping the result injectively to an integer). Encode outputs as integers as well. The examples then become:
Now pick any desired answer $a$ for the query point $t_q$. As long as $t_q$ is distinct from the observed $t_i$, we can construct a polynomial $Q_a(t)$ such that:
One explicit construction is Lagrange interpolation. Define the augmented point set:
(
)
(
)
(
)
Then set:
t
where the sum ranges over all observed points plus the query point.
By construction, this polynomial agrees with every provided example and gives the query answer $a$. Since $a$ was arbitrary, every possible query answer is consistent with the examples under some valid function.
There are in fact infinitely many such functions. Once we have one interpolating polynomial $Q_a(t)$, we can add:
R
(
)
(
)
(
)
(
)
(
)
for any polynomial $R(t)$. This changes the function elsewhere while preserving every observed example and the chosen query answer. So the finite examples don't identify one operation; they identify an infinite equivalence class of operations.
Why this matters for the benchmark
Of course, human solvers don't consider arbitrary polynomials over encoded strings. People naturally prefer "simple" rules: digit-wise arithmetic, concatenation, reversal, indexing, sorting, substitution, deletion, and so on. That's a perfectly reasonable design choice, and I suspect it's what the generator is leaning on too.
The friendly suggestion is just that, in that case, it would help if the benchmark either specified the restricted rule family or validated that the official answer is unique within it. Without such a rule class, the puzzle is effectively asking:
Which hidden rule did the puzzle generator probably have in mind?
rather than:
What answer follows from the examples?
Both are interesting tasks, but they're different. The first one rewards alignment with an unstated prior over "natural" transformations more than reasoning from the examples themselves, and I think competitors and the organizers would both prefer the second framing.
Same-operator evidence
This matters more in practice because many puzzles provide very few examples involving the operator used in the query. Across 1,555 puzzles in our solver run:
same-operator examples available for the query count share
0 300 19.3%
1 626 40.3%
2 442 28.4%
3 156 10.0%
4+ 31 2.0%
So about 88% of puzzles provide at most two examples involving the query's operator, and about 60% provide at most one.
This statistic alone doesn't prove that every such puzzle is ambiguous — and I don't want to overclaim. But it points to a structural risk: under any reasonably broad family of digit/string transformations, one or two same-operator examples are often not enough to distinguish between many simple candidate rules.
Different-operator examples can help, but only if the puzzle states that all operators share a common meta-rule. If the prompt doesn't specify such a meta-rule, then examples involving |, \, -, or other operators may not logically constrain the queried operator at all.
Here's a concrete example that illustrates the concern (shared not to single it out, just because it's compact):
34/44 = 1
41/32 = 9
34|25 = 69
87\64 = 8853
Now, determine the result for: 69/52
The official training label is:
17/
The query uses /, but only two examples use /: 34/44 = 1 and 41/32 = 9. The other two examples use | and \. Unless the prompt establishes a shared meta-rule tying these operators together, those examples don't determine what / should do on a new input. Many different functions can satisfy:
while giving different outputs for:
52
Consequences for evaluation and training
I think this affects both evaluation and training, and I want to flag the training side carefully because it's where I think the impact is most actionable.
For evaluation, exact-match scoring implicitly assumes the official answer is uniquely determined. If multiple simple rules fit the visible examples and produce different query outputs, exact-match accuracy may reward models that share the generator's prior over models that correctly recognize the underdetermination.
For training, the concern is a bit sharper. If these examples are used for SFT or RL data and the official answer is fixed as ground truth, rationale-generating models can be nudged toward post-hoc explanations — producing a plausible-looking rationale for the selected label rather than genuinely deriving the answer from the examples. For a reasoning benchmark, that's worth being careful about, since it can train the appearance of reasoning on prompts that are underdetermined.
Concrete fixes (offered as suggestions, not demands)
I realize re-curating a dataset of this size is a lot of work, and I don't want to underestimate that. With that caveat, a few directions that I think could meaningfully strengthen the category:
Publish the rule DSL or generation process. If the task is rule induction, knowing the intended hypothesis class would let competitors search a defined space rather than guess at the prior.
Validate uniqueness programmatically. Enumerate a DSL of simple transformations and flag any puzzle where two non-equivalent rules fit all examples but produce different query answers. Even running this as a one-time audit on the existing dataset would be informative.
Require more directly relevant examples. For instance, at least three or four examples using the same operator as the query — or alternatively, drop the multi-operator framing unless the cross-operator meta-rule is made explicit.
Allow underdetermined as a valid answer label, possibly for partial credit. A model that correctly recognizes insufficient information is showing a form of reasoning rather than a failure of it.
Consider set-valued ground truth. Accept any answer produced by a rule that fits all examples within the stated DSL.
Even partial adoption — e.g. just publishing the DSL — would go a long way.
Closing
To be clear, I'm not suggesting ambiguity should be eliminated completely. Some ambiguity is natural and even interesting in puzzle solving, and I appreciate the spirit of the task. But if the benchmark aims to measure reasoning, it would be great if the official answer were derivable from the examples under a stated rule class.
As currently presented, the category appears to lean on an unstated simplicity prior. Making that prior explicit, or validating uniqueness within it, would make this a stronger and fairer test of rule induction — and I'd be happy to help where I can. I'm glad to share the solver run that produced the same-operator distribution, and I'd be keen to contribute a uniqueness-checker against any DSL the organizers are willing to share.
Thanks again to the organizers for the work that's gone into this, and to anyone reading for considering the suggestion.
add_reaction
React
9 Comments
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
NguyenThanhNhan
Posted 22 days ago
· 466th in this Competition
arrow_drop_up
3
arrow_drop_down
more_vert
@toolazyhhh123
Of the 1555 symbol_transformation puzzles in train.csv, the public DSL (pick / shift / xor) doesn't fit on 878 of them (~57%):
661 the public reference solver (Huikang's notebook) skips entirely.
217 more it traces but tags individual operators as unknown and emits a fallback guess.
I ran two independent solvers over a subset of 561 puzzles for training, and kept 53 puzzles for validation:
z3-bounded search restricted to the public DSL - pick a character from a fixed input position, Caesar-shift, xor-with-constant, xor across two positions. For each output character of each example, the search walks through which DSL operation could produce that character, then labels the position as either derivable (some same-operator example fixes the operation) or a guess (no same-operator example constrains it). One step-by-step trace per puzzle becomes one training row.
Qwen3.5-397B-A17B-FP8 + JupyterSandbox. Each puzzle is given to Qwen with one tool exposed: a Python sandbox. Within a single inference turn, Qwen runs the hypothesis-test loop itself by proposing a candidate lambda L, op, R: , calling the sandbox to execute it against every shown example pair, reading back per-example pass/fail, then either revising or commiting. I call a rule verified when the sandbox confirms it reproduces every shown example output exactly. Per puzzle, I generated 4 attempts and ended up with 2244 attempts. There were 1198 verified (the rest hit context limits, failed sandbox verification on at least one example, or didn't commit). The kept trace preserves both proposals and sandbox returns inline.
Both trace types feed the same training recipe: SFT with a rank-128 LoRA on the Nemotron-Nano-30B base.
Trained on the z3 traces alone (8332-row SFT including non-sym_tr categories): peak 1/53 on the held-out sym_tr val split. The single val puzzle the model got right had a uniform output (the keyed answer was one character repeated) and every character of the answer also appeared in the query input. Every other val puzzle required a rule shape the public DSL can't express.
Of the 1198 verified Qwen rules, 82% (982) used shapes the DSL can't express e.g. operator-conditional branching, cross-position arithmetic, aggregate operations.
Adding those 982 Qwen traces to the SFT mix and retraining: regressed val 1/53 → 0/53.
The golden answer lives in a prior that neither the public DSL nor a 397B-parameter LLM with verified hypothesis search reliably samples from
reply
Reply
1
add_reaction
toolazyhhh123
TOPIC AUTHOR
Posted 22 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
Thank you — this is genuinely useful, and the sandbox-with-verification setup is something I wanted to try but couldn't get working within batch-cost constraints (the batch APIs I was using for cost reduction don't compose cleanly with tool-use loops). Good to see what the result looks like when someone actually does it.
Two things stand out to me from your numbers:
First, the 82% finding is the strongest version of the concern. If 982 out of 1198 verified Qwen rules — rules that demonstrably reproduce every shown example — use shapes outside the public DSL, that's direct empirical evidence that "matches all examples" and "matches the keyed answer" are pulling apart at scale, not just in edge cases. The same-operator distribution in my original post was suggestive; your number is the actual measurement.
Second, the regression from 1/53 to 0/53 when adding the verified Qwen traces is the part I find most striking. SFT on rules that verifiably solve the shown examples hurt held-out performance. That's a clean signal that the keyed-answer prior is narrow enough that even self-consistent alternative hypotheses move the model away from it.
For what it's worth, I have a small-sample observation that points the same direction: I evaluated K2.5, K2.6, and DeepSeek V3.2 on the first 100 train puzzles, which included 11 symbol_transformation puzzles. K2.5 and DeepSeek hit 1/11 each, K2.6 hit 3/11. Small sample and not a symbol_transformation-targeted study like yours, but consistent with your conclusion that frontier-reasoning LLMs don't reliably sample from this prior.
Your closing line is the right summary: the keyed answer lives in a prior that neither the public DSL nor a verified-hypothesis-search LLM reliably samples from. That makes the operationalization question — what grounds the keyed answer as canonical/natural/plausible — sharper rather than weaker.
reply
Reply
add_reaction
React
Chew Kok Wah
Posted 21 days ago
· 82nd in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Are you able to provide a few example from the training samples to show that indeed there exist questions where more than one answer fit the provided query and examples?
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
Posted 22 days ago
· 1665th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
For cryptarithm_deduce category of problems, Gemini AI recommended "Constraint Satisfaction Problem (CSP) Backtracking solver" - a python program does an elaborate brute-force search and finds the accurate solution.
But how to give the reasoning for this solution?!😀 If you give one reasoning path, the model would only learn to provide perfect reasoning for a hallucinated answer!
So, even if there is just one solution for the problem, we cannot make it as part of the reasoning CoTs
reply
Reply
add_reaction
React
toolazyhhh123
TOPIC AUTHOR
Posted 22 days ago
arrow_drop_up
0
arrow_drop_down
more_vert
I think this is a significant practical risk for training, although I am not an expert in this topic. If I do find something significant in the literature I may drop it here.
reply
Reply
add_reaction
React
toolazyhhh123
TOPIC AUTHOR
Posted 22 days ago
arrow_drop_up
2
arrow_drop_down
more_vert
you may be interested in this paper https://arxiv.org/abs/2404.03683 On Countdown (a pure CSP-style task), training on search trajectories with backtracking gives 51% vs. 26% for training on optimal paths only — roughly 2× better. Searchformer finds 5–10× smaller models suffice when trained on A* search dynamics vs. optimal plans.
My take on this is training on optimal path can help but on trajectories with backtracking likely help more.
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
Posted 22 days ago
· 1665th in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
Did you notice that there are a lot of duplicate prompts in symbol transformation category?
Only 54 prompts are unique in cryptarithm_deduce category and overall only 10% of around 1000 prompts are unique!
I spent time and gpu hours on creating new accurate CoT and training for crypatrithm_deduce and equation_numeric, but there was no change in LB score, then I realized that I am training for some 21 prompts, 54 prompts etc!!
Note: this analysis is on @huikang's dataset titled 'problem_ids_matched.csv'
reply
Reply
add_reaction
React
Murugesan Narayanaswamy
Posted 22 days ago
· 1665th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Another observation - I guess this one most would have noticed - that in the 'guess' variety of prompts - almost all of them - have operators which are not there in in-context examples.
But still @huikang's synthetic CoT gives elaborate boiler-plate reasoning only to be discarded when it comes to solution! But if I remove Tong's CoT, the score goes down!
So, I think the objective is to learn both positive and negative examples - hence I recreated the CoT's to be more accurate..
reply
Reply
add_reaction
React
gomerry
Posted 22 days ago
· 591st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
In @huikang 's dataset, there are a lot of duplicated "id" values. That’s why training on that dataset gives about a ±0.85 LB score.
reply
Reply
add_reaction
React
jane96
Posted a day ago
· 1157th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Why there are a lot of duplicated "id" values?
reply
Reply
add_reaction
React
NguyenThanhNhan
Posted 24 days ago
· 466th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
Hi @ryanholbrook and @cpmpml , this post raised some valid concerns that you might’ve missed.
I personally think publishing the dsl / data generator is a bad idea, however, addressing the non-uniqueness of certain puzzles in symbol transformation category is reasonable.
reply
Reply
add_reaction
React
CPMP
COMPETITION HOST
Posted 24 days ago
arrow_drop_up
2
arrow_drop_down
more_vert
The post expresses the complexity of induction. The issue is not limited by any mean to this competition.
in arc agi2 I can often think of more than one possible function that solves a given puzzle.
And in IQ tests I always struggle with series completion given I often can justify different logical continuations.
There is no "fix" for induction. There are various methods to pick/learn the most plausible function given the input/output pairs.
reply
Reply
add_reaction
React
toolazyhhh123
TOPIC AUTHOR
Posted 23 days ago
arrow_drop_up
3
arrow_drop_down
more_vert
Thanks for the response — and to concede the right thing first: you're correct that induction is formally underdetermined everywhere, including ARC-AGI-2 and IQ series. There's no formal "fix" for Hume, and I don't want to overclaim there. But I think the question I'm raising sits one step downstream of that. Given induction is underdetermined, how does a benchmark operationalize "most plausible" as ground truth? Different benchmarks answer this differently, and I think that's where symbol_transformation is currently under-specified relative to comparable work. ARC-AGI is actually a useful comparison precisely because it had a version of this problem and explicitly addressed it. The ARC-AGI-2 technical report (Chollet et al. 2025, arXiv:2505.11831) lists "Lack of reliable first-party human testing data" as one of the named limitations of ARC-AGI-1, noting that prior to ARC-AGI-2 there was no official first-party human baseline score derived under consistent conditions for the hidden tasks. They describe the consequence directly:
"The lack of such a human baseline makes a definitive understanding of human performance challenging."
Their response in ARC-AGI-2 was to run extensive human-facing calibration testing: 407 unique participants attempting 1,848 candidate task test pairs, and a task only advanced from testing if at least two independent participants solved it within their first two attempts. After selection and validation, 100% of included tasks were solved by at least two non-expert human testers, with each task attempted by between 2 and 10 humans. So the ARC team's answer to the underdetermination problem was to ground "the right answer" in measured human convergence rather than treating the generator's output as ground truth by fiat. IQ tests do something analogous through psychometrics. Items are administered to a standardization sample before deployment, and item response theory, item discrimination, and differential-item-functioning analyses determine whether the keyed answer survives empirical scrutiny. Items where the keyed answer doesn't separate stronger from weaker reasoners get revised or dropped. Neither of these is a fix for induction. They're operationalizations — they turn "most plausible function" from a philosophical question into a measured one. That's the move I'm suggesting symbol_transformation is currently missing: the ground truth is what the generator emitted, without an independent check that competent solvers actually converge on it. As @NguyenThanhNhan noted, addressing the non-uniqueness specifically (even without publishing the DSL) is the reasonable middle ground. Concretely: even a partial audit — running a subset of puzzles past a handful of solvers and measuring convergence rates on the keyed answer — would convert this from "match the generator's unstated prior" to "match a measured prior." Not arguing for a full re-curation, just that the gap between "induction is hard" and "ground truth is generator-emitted without convergence validation" is meaningful, and the latter is what the same-operator distribution makes me worry about.
reply
Reply
add_reaction
React
trantrikien239
Posted 22 days ago
· 1236th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Thanks for the response.
If I understand your point correctly, you are saying: There is a implicit, hidden "taste/preference" of rules that the Data generator use and our job is to train the model to learn that taste beside learning to reason. Am I getting warm?
reply
Reply
add_reaction
React
toolazyhhh123
TOPIC AUTHOR
Posted 22 days ago
arrow_drop_up
1
arrow_drop_down
more_vert
Yes, that's close.
I would phrase it as: the task is not only testing whether the model can reason from examples, but also whether it can infer the generator's implicit prior over what counts as a "natural" rule.
That is not automatically bad — all induction tasks need some prior. My concern is that if this prior is hidden and not validated by human convergence / DSL uniqueness checks / multiple-answer handling, then exact-match scoring may partly measure alignment with the generator's taste rather than derivability from the shown examples alone.
reply
Reply
add_reaction
React

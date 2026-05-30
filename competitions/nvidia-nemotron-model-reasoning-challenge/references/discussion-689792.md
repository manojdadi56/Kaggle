# NVIDIA Nemotron Model Reasoning Challenge

- **source:** https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/689792
- **scraped:** 2026-05-30 (authenticated browser)
- **chars:** 12458

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
Large submission.zip can't be downloaded and Commit fails due to insufficient GPU memory
how to train unsloth multi gpu??
Kaggle Scoring
Max session time
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
MAJ0RT0M · 1779TH IN THIS COMPETITION · POSTED 2 MONTHS AGO
arrow_drop_up
0
arrow_drop_down
more_vert
Is anyone able to get inference/generation speeds >2 tokens/sec?
I'm sure we are all familiar w/ this error by now: NemotronH requires an initializedNemotronHHybridDynamicCacheto return a cache. None was provided, so no cache will be returned.
It makes generating reasonable length (2000 tokens+) infeasible - generation speed is ~2toks/sec - so this would take 15m
GPRO becomes impossible - local evaluation also impossible. Even sanity checks to see if the model is producing reasonable output and learning thinking formats become expensive
But I see people w/ code to evaluate locally and run GRPO - how? I also see that when people share notebooks w/ output enabled and generation code - they are getting this cache error also. Are they just eating the huge generation time?
Has anyone managed to fix this cache error? Or find a workaround?
I'm open to solutions on or off kaggle hardware
add_reaction
React
6 Comments
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
ImperfectKitto
Posted 2 months ago
· 608th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
one quick google search
reply
Reply
add_reaction
React
MAJ0RT0M
TOPIC AUTHOR
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I think the link might be broken - this guide doesnt look specific to nemotron
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
it's not broken. nemotron model is no different
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted 2 months ago
· 1896th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
https://www.kaggle.com/code/russcore/fork-of-eval-dna37000-final
takes about 40 min for me.
reply
Reply
add_reaction
React
MAJ0RT0M
TOPIC AUTHOR
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
This is using vllm though
Do you know how to integrate vllm w/ trl for some grpo training?
reply
Reply
add_reaction
React
emoji_people
Russell Kirk
Posted 2 months ago
· 1896th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
Is async GRPO not a thing? I really don't know. I know what GRPO is but I haven't tried using it yet.
reply
Reply
add_reaction
React
5 more replies
arrow_drop_down
MAJ0RT0M
TOPIC AUTHOR
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
I tried installing unsloth but ran into version incompatibility problems - but I heard that it works - can anyone confirm?
reply
Reply
add_reaction
React
m4nocha
Posted 2 months ago
· 1961st in this Competition
arrow_drop_up
1
arrow_drop_down
more_vert
It works and the training speed for 3000 token sequence is 2 hours/epoch the inference speed using vllm is 3000-4000 tokens/sec
reply
Reply
add_reaction
React
MAJ0RT0M
TOPIC AUTHOR
Posted 2 months ago
· 1779th in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
nice!
your epoch is the full 9000 rows?
If you are using vllm for inference I guess you would need to halt training first - flush memory and then load model into vllm?
Edit: also - are you able to use unsloth for inference? If so - do you see any speedup?
reply
Reply
add_reaction
React
m4nocha
Posted 2 months ago
· 1961st in this Competition
arrow_drop_up
2
arrow_drop_down
more_vert
I perform inference on my validation dataset after SFT is completed. instead of flushing memory I delete the model and then reload it with LoRA adapter Inference with only the model gives 3000-4000 tokens/sec but on loading the LoRA adapter it drops to 2000 tokens/sec here is my inference script
# ============================================================
# STEP 5 — INFERENCE CONFIG & VRAM NUKE
# ============================================================
import gc, torch, os, time, json, re, math
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
USE_LORA = True
OUTPUT_JSON = "/kaggle/working/evaluation_results.json"
print("Clearing VRAM for inference...")
# Clean up training objects to free memory for vLLM
for var in ['trainer', 'model']:
if var in globals(): del globals()[var]
gc.collect()
torch.cuda.empty_cache()
torch.cuda.synchronize()
os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
# ============================================================
# STEP 6 — UPDATED HELPERS & PROMPT PREP
# ============================================================
def classify_puzzle(prompt):
if not isinstance(prompt, str): return 'Unknown'
p = prompt.lower()
if re.search(r'numeral system|base[- ]?\d|number.*convert|radix|secret number', p):
return 'Number Base Conversion'
elif re.search(r'gravit|gravity|falling|free.?fall|acceleration due to', p):
return 'Gravitational Constant'
elif re.search(r'transformation rule|equation.*transform|secret.*rule.*equation|rule.*applied.*equation', p):
return 'Equation Transformation'
elif re.search(r'encrypt|cipher|secret.*code.*letter|coded.*message|secret.*text', p):
return 'Text Encryption'
elif re.search(r'bit.?manipul|binary|8.?bit|bitwise|bit.*transform', p):
return 'Bit Manipulation'
elif re.search(r'unit.?conver|measurement|becomes.*\d|secret.*conver.*measur', p):
return 'Unit Conversion'
return 'Unknown'
def extract_final_answer(text: str | None) -> str:
r"""Extracts the final answer from the model response.
Prioritizes extracting answers inside `\boxed{}`.
"""
if text is None:
return 'NOT_FOUND'
# Search for boxed answer
matches = re.findall(r'\\boxed\{([^}]*)(?:\}|$)', text)
if matches:
non_empty = [m.strip() for m in matches if m.strip()]
if non_empty:
return non_empty[-1]
return matches[-1].strip()
# Other common formats if \boxed{} is not found
patterns = [
r'The final answer is:\s*([^\n]+)',
r'Final answer is:\s*([^\n]+)',
r'Final answer\s*[:：]\s*([^\n]+)',
r'final answer\s*[:：]\s*([^\n]+)',
]
for pattern in patterns:
matches = re.findall(pattern, text, re.IGNORECASE)
if matches:
return matches[-1].strip()
# If no structured format is found, extract the last valid number
matches = re.findall(r'-?\d+(?:\.\d+)?', text)
if matches:
return matches[-1]
# Fallback to the last line of text
lines = [line.strip() for line in text.splitlines() if line.strip()]
return lines[-1] if lines else 'NOT_FOUND'
def verify(stored_answer: str, predicted: str) -> bool:
"""Verify if the answer matches with binary and numeric tolerance."""
stored_answer = stored_answer.strip()
predicted = predicted.strip()
# If the answer is a binary string, compare strictly as strings
if re.fullmatch(r'[01]+', stored_answer):
return predicted.lower() == stored_answer.lower()
try:
# Try to convert the answers to floating point numbers
stored_num = float(stored_answer)
predicted_num = float(predicted)
return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
except Exception:
# Fallback to case-insensitive string comparison
return predicted.lower() == stored_answer.lower()
eval_records = []
print("Preparing evaluation records...")
for i, ex in enumerate(eval_dataset):
orig_prompt = ex["prompt"]
gt_answer   = str(ex["answer"])
chat_messages = [{"role": "user", "content": orig_prompt}]
formatted_prompt = tokenizer.apply_chat_template(
chat_messages,
tokenize=False,
add_generation_prompt=True
)
eval_records.append({
"id": ex.get("id", i),
"prompt": formatted_prompt,
"answer": gt_answer,
"category": classify_puzzle(orig_prompt)
})
# ============================================================
# STEP 7 — vLLM GENERATION
# ============================================================
print(f"\nStarting vLLM Engine... (LoRA Enabled: {USE_LORA})")
llm = LLM(
model=MODEL_PATH,
tensor_parallel_size=1,
max_num_seqs=128,
gpu_memory_utilization=0.9,
dtype='auto',
max_model_len=7000,
trust_remote_code=True,
enable_lora=USE_LORA,
max_lora_rank=LORA_RANK if USE_LORA else None,
)
sampling_params = SamplingParams(temperature=0, top_p=1.0, max_tokens=MAX_SEQ_LEN)
prompts = [item["prompt"] for item in eval_records]
print(f"Generating {len(prompts)} predictions...")
start_time = time.time()
lora_req = LoRARequest('adapter', 1, OUTPUT_DIR) if USE_LORA else None
outputs = llm.generate(prompts, sampling_params=sampling_params, lora_request=lora_req)
elapsed = time.time() - start_time
# ============================================================
# STEP 8 — SCORING & JSON EXPORT
# ============================================================
results = []
num_correct = 0
category_stats = {}
total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
tps = total_tokens / elapsed if elapsed > 0 else 0
for item, output in zip(eval_records, outputs):
raw_generated_text = output.outputs[0].text
predicted = extract_final_answer(raw_generated_text)
# Use the updated verify function
is_correct = verify(item["answer"], predicted)
cat = item["category"]
if cat not in category_stats:
category_stats[cat] = {"correct": 0, "total": 0}
category_stats[cat]["total"] += 1
if is_correct:
num_correct += 1
category_stats[cat]["correct"] += 1
results.append({
"id": item["id"],
"category": cat,
"ground_truth": item["answer"],
"predicted": predicted,
"is_correct": is_correct,
"full_output": raw_generated_text
})
accuracy = num_correct / len(eval_records) if eval_records else 0
# Save to JSON
json_data = {
"summary": {
"overall_accuracy": accuracy,
"correct": num_correct,
"total_samples": len(eval_records),
"category_metrics": category_stats,
"tokens_per_second": round(tps, 2),
"elapsed_seconds": round(elapsed, 2)
},
"results": results
}
with open(OUTPUT_JSON, "w") as f:
json.dump(json_data, f, indent=4)
print("\n" + "="*55)
print(f"✅ OVERALL ACCURACY : {accuracy:.2%} ({num_correct}/{len(eval_records)})")
print("-" * 55)
for cat, stats in sorted(category_stats.items()):
cat_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
print(f"  > {cat:<25}: {cat_acc:>6.2%}  ({stats['correct']}/{stats['total']})")
print("-" * 55)
print(f"🚀 SPEED    : {tps:.2f} tokens/s | 💾 SAVED TO : {OUTPUT_JSON}")
print("="*55)
and here is the result it got
=======================================================
✅ OVERALL ACCURACY : 81.34% (693/852)
-------------------------------------------------------
> Bit Manipulation         :  9.23%  (12/130)
> Equation Transformation  : 52.11%  (37/71)
> Gravitational Constant   : 100.00%  (148/148)
> Number Base Conversion   : 100.00%  (162/162)
> Text Encryption          : 95.86%  (162/169)
> Unit Conversion          : 100.00%  (172/172)
-------------------------------------------------------
🚀 SPEED    : 1815.43 tokens/s | 💾 SAVED TO : /kaggle/working/evaluation_results.json
=======================================================
reply
Reply
add_reaction
React
Komil Parmar
Posted 2 months ago
· 1451st in this Competition
arrow_drop_up
0
arrow_drop_down
more_vert
I am trying to do the same but I am bound by the input tokens/s rather than the output tokens/s . Have you encountered the same earlier? If yes, please provide the fix.
1032/38000 [19:45<12:00:46,  1.17s/it, est. speed input: 134.58 toks/s, output: 1736.83 toks/s]
reply
Reply
add_reaction
React

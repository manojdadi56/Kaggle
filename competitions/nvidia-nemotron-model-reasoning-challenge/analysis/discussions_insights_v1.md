# Ranked Actionable Insights from Discussions

Extracted from `competitions/nvidia-nemotron-model-reasoning-challenge/references/` (217 discussions + DIGEST).

## Top 20 Ranked Insights

1. **[DATA_TRICK]** Use deterministic Python solvers per category to generate verified CoT traces.
   - *Source:* `discussion-691978.md`
   - *Expected Impact:* 10/10

2. **[SUBMIT_TIP]** Submission must be a zip containing adapter weights and adapter_config.json.
   - *Source:* `discussion-682355.md`
   - *Expected Impact:* 9/10

3. **[GOTCHA]** Avoid FastLanguageModel.get_peft_model() for MoE architectures to prevent hanging.
   - *Source:* `discussion-681820.md`
   - *Expected Impact:* 9/10

4. **[DATA_TRICK]** Tag each problem rule_found/hypothesis_formed/rule_unknown; only verified rule_found traces enter the corpus.
   - *Source:* `discussion-700197.md`
   - *Expected Impact:* 9/10

5. **[TRAIN_TRICK]** Ensure max_lora_rank is 32 or less as per competition cap.
   - *Source:* `discussion-689792.md`
   - *Expected Impact:* 9/10

6. **[GOTCHA]** Unsloth merge fails on hybrid MoE architecture layer names. Restrict target_modules to attention only.
   - *Source:* `DIGEST-community.md`
   - *Expected Impact:* 9/10

7. **[EVAL_TRICK]** Evaluation metric allows 1e-2 numeric tolerance for content inside boxed{}.
   - *Source:* `discussion-692667.md`
   - *Expected Impact:* 8/10

8. **[EVAL_TRICK]** Host uses vLLM, temp 0, max_lora_rank 32. Build local vLLM eval mirroring these.
   - *Source:* `discussion-696059.md`
   - *Expected Impact:* 8/10

9. **[DATA_TRICK]** Use rule-based data augmentation (spelling, concat, split) instead of LLMs.
   - *Source:* `discussion-685922.md`
   - *Expected Impact:* 8/10

10. **[TRAIN_TRICK]** LoRA target modules must explicitly target Mamba mixer layers, not just regex everything.
   - *Source:* `discussion-684251.md`
   - *Expected Impact:* 8/10

11. **[TRAIN_TRICK]** Plain cross entropy loss is sufficient; RL is not strictly necessary for top performance.
   - *Source:* `discussion-694710.md`
   - *Expected Impact:* 8/10

12. **[EVAL_TRICK]** Metric checks for exact string match or numeric tolerance on boxed content.
   - *Source:* `discussion-683853.md`
   - *Expected Impact:* 8/10

13. **[DATA_TRICK]** Wrap reasoning steps in <think></think> tags and enable thinking in chat template.
   - *Source:* `DIGEST-community.md`
   - *Expected Impact:* 8/10

14. **[DATA_TRICK]** Ensure completion format precisely matches (reasoning)</think>\boxed{(answer)}<|im_end|>.
   - *Source:* `DIGEST-community.md`
   - *Expected Impact:* 8/10

15. **[DATA_TRICK]** Curate generic CoT: drop repetitive/low-quality, prioritize difficulty.
   - *Source:* `discussion-688120.md`
   - *Expected Impact:* 7/10

16. **[TRAIN_TRICK]** Batch size of 64, micro-batch 16, 1 epoch is optimal for SFT.
   - *Source:* `discussion-684212.md`
   - *Expected Impact:* 7/10

17. **[TRAIN_TRICK]** Use a learning rate of 2e-4 with StepLinearDecayLRSchedule.
   - *Source:* `discussion-697491.md`
   - *Expected Impact:* 7/10

18. **[GPU_TIP]** Use 4-bit NF4 quantization to fit the 30B model on limited VRAM.
   - *Source:* `discussion-698277.md`
   - *Expected Impact:* 7/10

19. **[TRAIN_TRICK]** A single-epoch LoRA SFT on verified traces is sufficient.
   - *Source:* `DIGEST-community.md`
   - *Expected Impact:* 7/10

20. **[SUBMIT_TIP]** Run an adapter validation notebook on a free instance before submission.
   - *Source:* `discussion-689915.md`
   - *Expected Impact:* 6/10

## Fixes for our current notebook

These fixes target `notebook_fork_working.ipynb` directly based on the highest-impact insights.

1. **Explicit LoRA Target Modules**
   - **Where:** Line 161-163 and Line 236-238
   - **Code Change:**
     ```python
     # Old:
     # lora_config = LoraConfig(r=LORA_RANK, lora_alpha=16,
     #    target_modules=r'.*\.(in_proj|out_proj|up_proj|down_proj)$',
     #    lora_dropout=0.05, bias='none', task_type=TaskType.CAUSAL_LM)
     # New:
     lora_config = LoraConfig(r=LORA_RANK, lora_alpha=16,
         target_modules=['in_proj', 'out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'],
         lora_dropout=0.05, bias='none', task_type=TaskType.CAUSAL_LM)
     ```
   - **Why:** Mamba hybrid architecture fails on default regex scanning and merge step.

2. **Mask `-100` on prompts**
   - **Where:** Line 174 and Line 249
   - **Code Change:**
     ```python
     # Old:
     # t = (pt + at)[:MAX_SEQ]; m = ([0]*len(pt) + [1]*len(at))[:MAX_SEQ]
     # New:
     t = (pt + at)[:MAX_SEQ]; m = ([-100]*len(pt) + [1]*len(at))[:MAX_SEQ]
     ```
   - **Why:** Compute cross-entropy loss only on the completion/reasoning trace, not the system prompt.

3. **Ensure exact Data format `<think>` & `oxed{}`**
   - **Where:** Line 171 and 246 (in `datum` function)
   - **Code Change:**
     ```python
     # Old:
     # at = tokenizer(a, add_special_tokens=False)['input_ids'] + [tokenizer.eos_token_id]
     # New (assuming 'a' contains the answer and we need to wrap it):
     formatted_a = f"<think>{a.get('reasoning', '')}</think>\boxed{{{a.get('answer', '')}}}"
     at = tokenizer(formatted_a, add_special_tokens=False)['input_ids'] + [tokenizer.eos_token_id]
     ```
   - **Why:** The SFT data must exactly match the format expected by the host's greedy decoding.

4. **Add Stratified Batching for SFT Loop**
   - **Where:** Line 177 and Line 252
   - **Code Change:**
     ```python
     # Old:
     # for d in train_data:
     # New:
     import random
     # Group by category assuming d['category'] exists, then zip to interleave
     from collections import defaultdict
     categorized = defaultdict(list)
     for d in train_data: categorized[d.get('category', 'misc')].append(d)
     for k in categorized: random.shuffle(categorized[k])
     stratified_data = []
     while any(categorized.values()):
         for k in list(categorized.keys()):
             if categorized[k]: stratified_data.append(categorized[k].pop())
     for d in stratified_data:
     ```
   - **Why:** Spread the different puzzle categories evenly across batches to prevent catastrophic forgetting.

5. **Fix inference to parse last boxed match**
   - **Where:** Line 275-285
   - **Code Change:**
     ```python
     # Old:
     # def boxed(t):
     #     if not t: return None
     #     i = t.rfind(chr(92) + 'boxed{')
     #     if i < 0: return None
     #     s = i + 7; d = 1
     #     for j in range(s, len(t)):
     #         if t[j] == '{': d += 1
     #         elif t[j] == '}':
     #             d -= 1
     #             if d == 0: return t[s:j]
     #     return None
     # New:
     import re
     def boxed(t):
         if not t: return None
         # match the last occurrence safely
         matches = list(re.finditer(r'\boxed{', t))
         if not matches: return None
         i = matches[-1].start()
         s = i + 7; d = 1
         for j in range(s, len(t)):
             if t[j] == '{': d += 1
             elif t[j] == '}':
                 d -= 1
                 if d == 0: return t[s:j]
         return None
     ```
   - **Why:** The evaluation logic dictates that the LAST non-empty match of `oxed{...}` is parsed. The original implementation was naive string search that might fail on escaping.

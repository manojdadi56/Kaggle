# Hypothesis — Nemotron Model Reasoning Challenge

Synthesized 2026-05-30 from analysis of the Progress-Prize-winning repo
(`github.com/tonghuikang/nemotron`, LB 0.85), 22 community sources, and the
competition's fixed constraints.

---

## 1. Core Hypothesis

**Accuracy on this benchmark is overwhelmingly determined by the data engine, not
by model scale, RL, or hyperparameter tuning.**

The benchmark consists of procedurally generated puzzles in 9 categories. Each
category has a deterministic generating rule. The winning strategy is:

1.  **Reverse-engineer each category's rule** → deterministic Python solvers.
2.  **Generate verified Chain-of-Thought traces** from those solvers — only
    `rule_found` traces (solver output matches ground truth) enter the corpus.
3.  **Augment** the corpus with 5 rule-based text-manipulation tasks.
4.  **Single-epoch LoRA SFT** (rank ≤ 32) on clean, verified traces.

Evidence for this hypothesis:

| Approach | LB Score | Delta |
|----------|----------|-------|
| No synthetic data, plain SFT | 0.65 | baseline |
| Generic API-distilled CoT | 0.82 | +0.17 |
| Winner hand-engineered corpus | **0.85** | +0.20 |

The 0.20 gap between naive SFT and the winning score is almost entirely **data
quality** — not compute, not RL, not model architecture. RL losses exist in the
winner's repo but were **unused** in the winning run.

**Sub-hypothesis:** The residual headroom above 0.85 lives in the categories the
winner left unsolved — primarily `cryptarithm_guess` and any `rule_unknown`
problems — not in marginal improvements to already-solved categories.

---

## 2. Analysis Observations

### 2.1 The Competition's Hidden Structure

The problems are NOT open-ended reasoning. They are **procedurally generated** with
deterministic input→output rules. This means:

- A correct solver produces a **provably correct** answer — there is no ambiguity
  (except `cryptarithm_guess` and `equation_numeric_guess`).
- The model's job is to **reproduce the reasoning**, not to discover new math.
- CoT traces can be **programmatically verified** before entering the corpus.
- The host scoring uses `temperature=0.0` — deterministic greedy decoding. This
  rewards exactly one thing: producing the correct `\boxed{answer}`.

### 2.2 What the Winner Actually Built

The winner (`tonghuikang/nemotron`) wrote **6 deterministic solvers** serving 9
categories:

| Category | Solver File | Strategy |
|----------|-------------|----------|
| `bit_manipulation` | `reasoners/bit_manipulation.py` | Decompose 8-bit strings column-by-column; test 9 logical families (Identity, NOT, Constant, AND, OR, XOR, + 3 NOT-variants); find left/right runs; compose composite rule |
| `cipher` | `reasoners/cipher.py` | Build cipher→plain mapping from examples; when stuck, dictionary pattern-matching with partial templates against Wonderland word list |
| `equation_numeric_deduce` | `reasoners/equation_numeric.py` | Parse operator; enumerate ~30 candidate operations in priority order (common 8 → rare 22); validate against all examples |
| `equation_numeric_guess` | same as deduce | Same solver; the "guess" variant means fewer/ambiguous examples |
| `cryptarithm_deduce` | `reasoners/cryptarithm.py` | Decompose 5-char input into (A₁,A₂,op,B₁,B₂); test forward concat (A₁A₂B₁B₂) vs reverse concat (B₁B₂A₁A₂); label each operator |
| `cryptarithm_guess` | same as deduce | **Explicitly skipped** — produces `rule_unknown` |
| `gravity` | `reasoners/gravity.py` | Compute d = k·t² per example; take median k; apply to question; truncate 3dp |
| `numeral` | `reasoners/numeral.py` | Greedy subtraction against Roman numeral value table |
| `unit_conversion` | `reasoners/unit_conversion.py` | Linear factor per example; median consolidation; apply; 3dp |

### 2.3 The 5 Augmentation Tasks

These are NOT competition categories — they train basic text-manipulation
formatting that the model needs for `\boxed{}` extraction and bracket handling:

| Augmenter | Task | Purpose |
|-----------|------|---------|
| `spelling` | `hello` → `–h–e–l–l–o–` | Character-level decomposition for bracket manipulation |
| `concatenation` | `【h】【e】【l】【l】【o】` → `【hello】` | Merging individually-bracketed chars |
| `splitting` | `【hello】` → `【h】【e】【l】【l】【o】` | Inverse of concatenation — per-char bracketing |
| `matching` | bit-column pattern matching from reasoning traces | Training on the output/left/right column analysis format used in bit_manipulation |
| `lstrip` | `【 hello】` → `【hello】` | Removing leading whitespace from brackets |

Observation: the augmenters produce ~1500 problems each, totaling ~7500 auxiliary
examples. These are pure format training — they teach the model to manipulate
bracket-delimited text, which is critical for consuming the competition's `【】`
notation and producing `\boxed{}` output.

### 2.4 Training Configuration (Verbatim from Winner)

```
Base model:   Nemotron-3-Nano-30B-A3B-BF16 (30B MoE, ~3B active)
LoRA:         rank=32, train MLP + attention + unembed
LR:           2e-4, StepLinearDecay schedule
Batch:        64 (micro-batch 16)
Epochs:       1
Max seq len:  8192
Optimizer:    Adam (β₁=0.9, β₂=0.95, ε=1e-8, weight_decay=0)
Loss:         Cross-entropy, label-masked (prompt tokens → -100)
Batching:     Stratified across 9 categories
Precision:    BF16 (winner used cloud; we use 4-bit QLoRA on 2×T4)
```

### 2.5 Reproducibility Gap

| Component | Winner's Setup | Our 2×T4 Setup |
|-----------|---------------|----------------|
| Data engine | CPU, pure Python | **Fully reproducible** ✅ |
| Augmenters | CPU, pure Python | **Fully reproducible** ✅ |
| SFT training | BF16, cloud GPU (Modal/Tinker) | 4-bit QLoRA, max_seq=2048, sharded across 2×T4 |
| LoRA targets | MLP + attention + unembed | Attention-only initially; expand as memory allows |
| Max seq len | 8192 | 2048 (T4 constraint) |
| RL stage | Available but unused | Not feasible on 2×T4 |

The **data engine is fully portable**. The training gap (BF16→4-bit, 8192→2048,
MLP+attn+unembed→attention-only) likely costs some accuracy but the high-leverage
component (verified CoT traces) transfers completely.

---

## 3. Per-Category Optimal CoT Templates

Each category demands a **structurally different reasoning pattern**. A generic
"think step by step" CoT will not work — the model must route to the correct
solver logic. Our hypothesis is that **explicit two-phase CoT (classify → solve)**
outperforms implicit reasoning.

### 3.1 Universal CoT Shell

Every trace follows this structure:

```
<think>
## Classification
I need to identify what type of problem this is.
[Category-specific evidence from input-output patterns]
This is a [CATEGORY] problem.

## Reasoning
[Category-specific deterministic chain — see below]

</think>
\boxed{<answer>}<|im_end|>
```

The classification phase is critical because:
- 9 distinct solver algorithms exist — misclassification = wrong answer.
- Error attribution: classification accuracy and solver accuracy are separable.
- Fallback: if classification is uncertain, the model can try multiple solvers
  and pick the one whose output is consistent with all examples.
- The `_guess` variants (`cryptarithm_guess`, `equation_numeric_guess`) are
  deliberately underspecified — explicit classification lets the model acknowledge
  ambiguity rather than confidently applying the wrong rule.

### 3.2 Bit Manipulation CoT

```
## Classification
The examples show fixed-width binary strings being transformed.
Each bit position follows a consistent logical operation.
This is BIT_MANIPULATION.

## Reasoning
### Output bit columns (with bitsum as hash)
Bit 0: [1,0,1,1,1] → hash a3
Bit 1: [0,1,0,1,0] → hash 7c
... [all 8 columns]

### Identify operation per column
Testing: Identity → NOT → Constant → XOR → OR → AND → AND-NOT → XOR-NOT → OR-NOT
- Bit 0: NOT matches 5/5 examples ✓
- Bit 1: XOR(in₀, in₁) matches 5/5 ✓
- Bit 2: AND-NOT(in₀, in₃) matches 5/5 ✓
... [per-column result]

### Composite rule
- Left run (bits 0-3): NOT
- Right run (bits 4-7): XOR(in, in>>2)

### Apply to question
[Bit-by-bit application of each sub-rule to the question input]
\boxed{<8-bit binary string>}
```

### 3.3 Cipher CoT

```
## Classification
Letters are consistently substituted across examples — the same ciphertext
letter always maps to the same plaintext letter. This is CIPHER.

## Reasoning
### Build mapping from examples
[Example-by-example mapping extraction]
Current mapping: [A-Z grid showing known mappings]

### Decrypt the question
[Partial decryption with known mappings]
For unknown letters: search dictionary for matching word pattern
- Pattern: (0,1,2,0,3) length 5
- Candidates: [word1, word2, ...]
- Testing each: cross-check consistency with known mappings

[Resolve all mappings → full decryption]
\boxed{<plaintext>}
```

### 3.4 Equation Numeric CoT

```
## Classification
Input numbers are transformed into output numbers via a mathematical operation.
The examples include an operator symbol. This is EQUATION_NUMERIC.

## Reasoning
### Parse examples
- "12 + 5 = 17": a=12, op=+, b=5, out=17

### Find the operation
Trying common operations (8):
  addition:      12+5=17 ✓, 8+3=11 ✓, 25+7=32 ✓  → MATCH
Trying rare operations (22) only if no common match:
  [skipped — common match found]

### Apply to question
Question: 15 + 9 = ?
Operation: addition
15 + 9 = 24

\boxed{24}
```

### 3.5 Cryptarithm CoT

```
## Classification
Each input is exactly 5 characters: two symbols, an operator, and two more
symbols. The output is a rearrangement. This is CRYPTARITHM.

## Reasoning
### Analyze each example
【A】【B】+【C】【D】 = 【A】【B】【C】【D】
  concatenation: 【A】【B】【C】【D】 → match ✓
  reverse concat: 【C】【D】【A】【B】 → mismatch ✗
  operator + → concatenation

### Apply to question
Question operator: *
* → [type determined from examples]
Result: [apply rule]

\boxed{<4-char result>}
```

### 3.6 Gravity CoT

```
## Classification
The examples relate a time value to a distance value. The relationship
follows d = k·t². This is GRAVITY.

## Reasoning
### Find k from examples
Example 1: t=3.0  →  t² = 9.0  →  k = 44.145/9.0 = 4.905
Example 2: t=7.0  →  t² = 49.0  →  k = 240.345/49.0 = 4.905

### Select k
k values: [4.905, 4.905]
Median: 4.905

### Apply to question
t = 5.0  →  t² = 25.0  →  d = 4.905 × 25.0 = 122.625

\boxed{122.625}
```

### 3.7 Numeral CoT

```
## Classification
Numbers are being converted between Arabic and Roman numeral representations.
This is NUMERAL.

## Reasoning
Converting [N]:
[N] >= 1000 → M, remainder [N-1000]
[N] >= 900  → CM, remainder [...]
... [greedy subtraction through value table]

Result: [Roman numeral]

\boxed{<roman numeral>}
```

### 3.8 Unit Conversion CoT

```
## Classification
Input values are being scaled by a constant factor to produce output values.
This is UNIT_CONVERSION.

## Reasoning
### Find factor from examples
Example 1: 3.0 → 12.0  →  factor = 12.0/3.0 = 4.0
Example 2: 5.0 → 20.0  →  factor = 20.0/5.0 = 4.0

### Select median factor: 4.0

### Apply to question
7.0 × 4.0 = 28.0

\boxed{28.000}
```

---

## 4. Tactics & Strategies

### 4.1 Data Engine First (Highest Leverage)

The data engine is the single largest lever (+0.15–0.20 LB vs naive SFT) and it
runs **entirely on CPU with no API calls**. This is the ideal first Jules task.

Execution order:
1. Port `reasoners/` from `tonghuikang/nemotron` (6 solvers for 9 categories).
2. Port `augmenters/` (5 rule-based augmenters, ~7500 auxiliary problems).
3. Port `corpus.py` (tokenize + mask prompts → training-ready JSONL).
4. Adapt CoT templates to include explicit **Classification** + **Reasoning**
   two-phase structure (the winner's solvers generated category-specific reasoning
   but never explicitly labeled the category).

### 4.2 Training Strategy (Constrained by 2×T4)

| Priority | Step | Effort | Expected Gain |
|----------|------|--------|---------------|
| 1 | 2×T4 QLoRA smoke test: 4-bit base, explicit Mamba-mixer LoRA targets, max_memory sharding, 10 samples / 1 step | M | Unblocks all training; catches the MoE-hang and merge-mismatch bugs |
| 2 | First SFT on ported corpus: rank=32 attention-only, LR=2e-4, max_seq=2048, label-masked loss | L | First real LB number |
| 3 | Stratified batching across 9 categories | S | Stability; matches winner config |
| 4 | CoT data selection (Select2Reason-style): keep only boxed-correct traces, drop repetitive, prioritize by difficulty + trace length | S | Smaller corpus → faster training; often improves accuracy |
| 5 | Expand: max_seq 2048→4096→8192, LoRA attention-only→+MLP→+unembed | M | Closes T4-induced gap toward 0.85 |
| 6 | Cover unsolved categories: solver for `cryptarithm_guess`, audit `rule_unknown` | M | Targets residual headroom above 0.85 |

### 4.3 The Classification → Solve Pipeline

Instead of a single monolithic CoT, the training data should encode a **two-phase
reasoning structure**:

```
Phase 1 (Classification):
  - Examine the structure of the input-output examples
  - Match against known category signatures
  - Declare the category with evidence
  - If ambiguous, acknowledge uncertainty and plan fallback

Phase 2 (Category-specific solving):
  - Apply the deterministic algorithm for that category
  - Show intermediate steps (not just the answer)
  - Verify the answer against the given examples before finalizing
  - Box the answer
```

This separation:
- **Improves accuracy**: the model learns to route to the right solver.
- **Enables debugging**: if wrong, was it a classification error or solver error?
- **Enables fallback**: if the primary classification is uncertain, the model can
  try multiple solvers and select the one consistent with all examples.

### 4.4 Corpus Assembly Rules

From the winner's approach, these rules produced the 0.85 corpus:

1. **Only `rule_found` traces enter the corpus.** Any problem where the solver's
   boxed answer doesn't match ground truth → `rule_unknown` → excluded.
2. **Stratify categories** so the corpus has roughly balanced representation across
   all 9 types.
3. **Mask prompt tokens to -100** — loss is computed only on the completion
   (reasoning trace + boxed answer).
4. **Completion format**: `(reasoning)</think>\boxed{answer}<|im_end|>`
5. **Mix in augmentation tasks** (~20% of corpus) to maintain bracket-manipulation
   and formatting skills.

### 4.5 Submission Policy

- **Submit only when local CV beats best-known CV** AND under the daily cap.
- **Adapter validation pre-submit gate**: load adapter under vLLM-mirrored config,
  confirm rank ≤ 32, validate parseable `\boxed{}` output on a held-out set.
- **Daily cap**: set in `.env` as `MAX_AUTO_SUBMITS_PER_DAY` — the gate reads
  remaining submissions live and will not exceed the limit.

---

## 5. Techniques (Concrete Implementation Notes)

### 5.1 2×T4 Memory Map

```
GPU 0: max 13 GiB
GPU 1: max 13 GiB
CPU:   max 12 GiB (NEMOTRON_MAX_MEMORY_CPU)
Disk:  offload_folder for MoE weight spillage
```

### 5.2 Critical Dependency Pins

```
transformers>=4.45,<5    # v5 OOMs on 16 GB
mamba-ssm                 # Mamba layer support
causal-conv1d             # SSM convolution kernel
peft                      # LoRA adapter loading
```

### 5.3 LoRA Targeting — Avoid the Two Known Killers

**Killer 1 — MoE expert scan hang:**
`FastLanguageModel.get_peft_model()` and regex-based `target_modules` hang while
scanning ~5980 MoE experts. **Fix**: use `peft.get_peft_model()` with an explicit
module list targeting only the 46 Mamba mixer layers (`mixer.in_proj`,
`mixer.out_proj`).

**Killer 2 — LoRA merge layer-name mismatch:**
The `merge_and_unload()` step fails on the hybrid Mamba-Transformer MoE because
layer names don't match between the adapter and base. **Fix**: restrict
`target_modules` to attention-only `[q_proj, k_proj, v_proj, o_proj]`; avoid
`in_proj/out_proj` and MoE gate/expert layers.

### 5.4 Host vLLM Configuration (for local CV harness)

```
temperature: 0.0
top_p: 1.0
max_tokens: 7680
max_model_len: 8192
max_lora_rank: 32
gpu_memory_utilization: 0.85
max_num_seqs: 64
```

### 5.5 Answer Extraction (for CV and verification)

```python
# Extract last non-empty \boxed{...} from model output
match = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", output)
answer = match[-1].strip() if match else None

# Compare with ground truth
if is_binary_string(answer) and is_binary_string(truth):
    correct = answer == truth                          # strict for binary
elif is_numeric(answer) and is_numeric(truth):
    correct = math.isclose(float(answer), float(truth),
                           rel_tol=1e-2, abs_tol=1e-5) # ±1e-2 for numeric
else:
    correct = answer.lower() == truth.lower()          # case-insensitive string
```

---

## 6. Risks & Unknowns

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Winner's solvers overfit to specific problem generators — don't generalize to the full test set | Medium | High | The solvers handle the known patterns; flag `rule_unknown` problems and iterate |
| 4-bit QLoRA + max_seq=2048 + attention-only LoRA loses significant accuracy vs BF16/8192/MLP+attn+unembed | Medium | Medium | Benchmark the gap; expand as the 40 GB executor becomes available |
| `cryptarithm_guess` and `equation_numeric_guess` are fundamentally harder — ambiguous examples mean no single deterministically correct rule | High | Medium | These categories are where the +0.85 headroom lives; they need probabilistic/consensus approaches, not just deterministic solvers |
| Mamba-Transformer MoE architecture has undocumented sharp edges (hangs, merge failures) | High | High | Smoke test first; pin exact dependency versions; use explicit module lists |
| Kaggle free GPU session limits (9–12h) may not be enough for full SFT | Medium | Medium | Start with small corpus; use QLoRA + packing for throughput; plan for the 40 GB box |
| Competition data distribution shifts between public LB and private test | Medium | Medium | Build robust per-category solvers that don't overfit to specific prompt wording |

---

## 7. Test Plan — Validating the Hypothesis

### 7.1 Data Engine Validation (offline, no GPU)

- Run each solver against all known problems in its category.
- Measure: % `rule_found` vs `rule_unknown` per category.
- Target: >80% `rule_found` for all non-guess categories before training.
- Output: verified `corpus.jsonl` ready for SFT.

### 7.2 2×T4 Smoke Test

- Load 4-bit Nemotron-3-Nano-30B-A3B on 2×T4 with memory sharding.
- Train on 10 samples, 1 step.
- Verify: no OOM, no MoE scan hang, no merge mismatch.
- Compare loss before/after: should decrease from ~45→~17→~0.99 after label masking
  (per community reports).

### 7.3 CV Harness Validation

- Build local vLLM eval mirroring host config exactly.
- Run adapter-validation on a held-out set.
- Confirm: same accuracy as host within tolerance.
- Gate: CV must match host before trusting CV for submit decisions.

### 7.4 Ablation Study (if resources permit)

| Ablation | Expected Effect |
|----------|----------------|
| No augmentation tasks | Small accuracy drop (~1–3%); format errors increase |
| No classification preamble | Modest drop (~2–5%); more misrouted reasoning |
| Generic "think step-by-step" CoT (no category-specific template) | Large drop (~5–10%); equivalent to API-distilled CoT quality |
| Attention-only LoRA vs attention+MLP+unembed | Modest gap (~2–4%) |
| max_seq=2048 vs 8192 | Small gap (~1–2%); long CoT traces get truncated |

---

## 8. Summary — The Bet

We're betting that:

1. **The data engine IS the moat.** Porting the winner's deterministic solvers +
   augmentation pipeline gives us a verified, high-quality corpus that should reach
   LB ≥ 0.80 on its first submission.
2. **Explicit two-phase CoT (classify → solve) beats implicit reasoning.** The
   classification step routes the model to the correct solver, reducing
   misclassification errors that a generic CoT would make across 9 distinct
   categories.
3. **The residual headroom above 0.85 is in the unsolved categories**
   (`cryptarithm_guess`, `rule_unknown` problems), not in squeezing more out of
   already-solved ones.
4. **The reproducibility gap (BF16→4-bit, 8192→2048) costs some accuracy** but
   doesn't invalidate the approach — the data engine transfers completely, and
   training can scale up on the 40 GB box later.

**If this hypothesis holds:** first submission should land between 0.78–0.83.
**If it doesn't:** the solvers are overfit to the winner's specific problem
generators and we need to generalize them — which is still a CPU-only iteration.

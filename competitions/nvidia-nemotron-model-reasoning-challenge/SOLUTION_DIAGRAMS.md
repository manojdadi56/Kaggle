# Final Submission Solution — Visual Diagrams (2026-05-31)

Three views of the solution: (1) the end-to-end data→model→submission pipeline,
(2) the autonomous campaign orchestration, (3) the per-example mechanics + host scoring.

---

## Diagram 1 — Data → Model → Submission pipeline (what gets submitted)

```
 train.csv  (9,500 rows · columns: id, prompt, answer · NO category label)
      │
      ▼   data/classify/classify.py   — signature-phrase classifier (100% verified, 0 unknown)
 ┌──────────────────────────────────────────────────────────────────────┐
 │  6 REAL categories (this competition):                                 │
 │   ✅ gravity 1597   ✅ numeral 1576   ✅ unit_conversion 1594  (verified)│
 │   ⚠ bit_manipulation 1602 (8-bit binary)                               │
 │   ⚠ cipher 1576 (word substitution)                                    │
 │   ⚠ equation_numeric 1555 (SYMBOLIC transform)   → solve + verify      │
 │   ✗ cryptarithm / cryptarithm_guess / select2reason  = DO NOT EXIST    │
 └──────────────────────────────────────────────────────────────────────┘
      │   per-category DETERMINISTIC solvers (pure Python, no LLM)
      │   → emit chain-of-thought ending in \boxed{answer}
      ▼   VERIFY every \boxed{} == train.csv gold (exact or rel-tol 1e-2); drop mismatches
 verified CoT corpus  v13   (all-real, all-verified; fabricated categories removed)
      │   render with HOST chat template:
      │     system = "reasoning_on"  ·  user += "put final answer in \boxed{}"  ·  enable_thinking=True
      ▼   ANSWER-MASKED SFT  (cross-entropy on the assistant span only)
 ┌──────────────────────────────────────────────────────────────────────┐
 │  Base: NVIDIA Nemotron-3-Nano-30B-A3B-BF16   (FROZEN, never full-FT)   │
 │  LoRA adapter: rank 32 · MLP+attention targets · 1 epoch               │
 │  LR: step-linear 2e-5 → 1e-5    ·    RTX Pro 6000 (95GB, full bf16)    │
 └──────────────────────────────────────────────────────────────────────┘
      │   package  (rank ≤ 32 enforced)
      ▼
 submission.zip  =  adapter_config.json  +  adapter_model.safetensors
      │
      ▼   HOST evaluation (Kaggle):  base model + OUR adapter under vLLM
          greedy temperature=0.0 · top_p=1.0 · max_tokens=7680 · max_model_len=8192
      ▼
 SCORE = fraction of test prompts whose extracted \boxed{} answer matches gold
         (exact string OR relative numeric tolerance 1e-2)
```

---

## Diagram 2 — Autonomous campaign orchestration (how the solution is produced)

```
        ┌──────────────── OPERATOR  (Claude Code, subscription session) ────────────────┐
        │  EACH CYCLE:  status → monitor GPU + Jules → role-select → act → dashboard →   │
        │               commit/push → pace (ScheduleWakeup, never busy-loop)             │
        └───┬───────────────────────┬────────────────────────┬──────────────────────────┘
            │ reads/writes           │ polls/acts             │ polls/acts
   ┌────────▼─────────┐    ┌─────────▼──────────┐   ┌─────────▼───────────────┐
   │  LEDGER (git-JSON)│    │  JULES FLEET ≤5    │   │  KAGGLE  (via MCP + KGAT)│
   │ state.json        │    │  parallel coders   │   │  notebook v45 fork       │
   │ events.jsonl      │    │  write solvers /   │   │  RTX Pro 6000 GPU        │
   │ tasks/hypotheses/ │    │  tooling (NO raw   │   │  Save&RunAll → adapter   │
   │ experiments       │    │  data on VM) → PRs │   │  + cv_score.json         │
   └────────┬──────────┘    └─────────┬──────────┘   └─────────┬───────────────┘
            │                         │ R-007 auto-merge        │ pull → compare CV
            │                         ▼ (secret-scan gate)      ▼
            │                    main branch ◄───────────  SUBMIT GATE
            │                                              CV > best_cv ?
            └──────────────── next hypothesis ◄────────────  ≤3 auto/day, reserve 2 finals
                                                                  │ yes
                                                                  ▼
                                                          Kaggle leaderboard rank
```

---

## Diagram 3 — The "unit": one example → training row → test-time scoring

```
  ONE train.csv row
  prompt = "In Alice's Wonderland, a secret <rule>... examples ... Now solve: X"
  answer = "Y"
        │
        ├─► classify(prompt) → category            (e.g. cipher / bit_manipulation / …)
        ▼
  DETERMINISTIC SOLVER  (category-specific, no LLM, fully reproducible)
     parse examples → infer the hidden rule → apply to X
     → write step-by-step reasoning → final \boxed{Y'}
        │
        ▼   VERIFY:  Y' == Y ?
        │              └── NO ──► DROP (never train on wrong reasoning)
        │ YES
        ▼
  TRAINING ROW  (host chat template, loss masked to assistant span):
     [system]    reasoning_on
     [user]      <prompt> + "Please put your final answer inside \boxed{}"
     [assistant] <think> …verified CoT… </think>  \boxed{Y}     ◄── loss only here
        │
        │   (× N verified rows, all 6 real categories)
        ▼
  SFT → LoRA adapter  ──package──►  submission.zip
        │
        ▼   TEST TIME (host, unseen prompt):
     model + adapter  ──vLLM, greedy──►  "<think> … </think> \boxed{Z}"
        ▼
     extract Z  →  correct iff  Z == gold  (exact OR rel-tol 1e-2)
```

---

### Current status vs. this target (2026-05-31)
- **Working now:** v45 notebook loads the 30B model on RTX Pro 6000 and trains; first **baseline** uses the older v12 corpus (3 verified + 3 synthetic + 3 fabricated categories) — validates the pipeline, gives a first CV.
- **In progress toward the target:** classifier ✅ done → run verified solvers on real rows → assemble **v13** (all-real, all-verified) → retrain → submit. Jules fleet builds curation + per-category CV tooling in parallel.
- **Guardrails:** ≤3 auto-submits/day (reserve 2 finals), submit only when local CV beats best, LoRA rank ≤ 32, base model never full-fine-tuned.
```
```

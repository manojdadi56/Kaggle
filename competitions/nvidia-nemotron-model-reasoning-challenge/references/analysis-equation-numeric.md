# equation_numeric — structural analysis (why it's DEFERRED, evidence-based 2026-05-31)

Category `equation_numeric` (1555/9500 real rows, ~16% of test). Prompt signature:
"In Alice's Wonderland, a secret set of transformation rules is applied to equations."

## Format
Each puzzle gives ~4 examples of the form `INPUT = OUTPUT`, then `Now, determine the result for: TARGET`.
INPUT/OUTPUT are single tokens of symbols (NOT `a OP b`). Examples:
```
`!*[{ = '"[`
\'*'> = ![@
34/44 = 1
87\64 = 8853   ← input/output LENGTHS DIFFER (5 → 4, 5 → 1, 5 → 2) ⇒ NUMERIC transform, not per-char substitution
```

## Why a deterministic solver is hard (each ruled out by evidence)
1. **Separator is NOT an operator.** Within ONE puzzle the separators are mixed (`/`, `|`, `\` all appear), so they can't be per-example operators. The whole token is one symbol-encoded number.
2. **Not a per-character substitution** (would preserve length; lengths differ).
3. **No simple global base.** Across 400 puzzles the alphabet is 36 distinct chars, ASCII !..} but NON-contiguous (gaps 1/2/27). Some puzzles use literal digits `0-9`, others pure punctuation ⇒ each puzzle likely uses its OWN contiguous ASCII slice as digits 0..k-1 (a per-puzzle alphabet + base).
4. **Per-puzzle inference is underdetermined.** Solving one puzzle needs: (a) the local digit alphabet/base, (b) decode in/out tokens to numbers, (c) infer the arithmetic f with only 4 (in,out) pairs, (d) encode the target. (a)+(c) jointly from 4 examples is brittle.

## Decision
DEFERRED — genuinely research-grade, NOT tick-sized. Held OUT of v13 (kept neither synthetic nor
half-solved, to avoid teaching wrong reasoning). v13 covers the other 5 categories at 100% verified
(~75% of train.csv). Priority order is correct: a first SUBMISSION (currently 0) dominates a +16%
category refinement. Revisit equation_numeric as a dedicated multi-hour task IF a baseline shows it's
the marginal bottleneck.

## If pursued later (sketch)
- Per puzzle: alphabet = sorted(distinct chars in this puzzle's tokens) → values 0..k-1; base = k (or fixed).
- Decode in/out to ints; search f over {+c, *c, //c, %m, reverse-digits, base-shift, ...} fitting all 4 examples.
- Apply f to target, re-encode in the local alphabet. KEEP ONLY rows that verify == gold.

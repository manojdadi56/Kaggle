# Verified CoT SFT Example Schema

This document outlines the expected format for SFT examples generated from deterministic solvers for the NVIDIA Nemotron Model Reasoning Challenge.

## JSONL Format

The output of the generator is a JSONL file where each line is a single training example represented as a JSON object.

### Schema

```json
{
  "problem_id": "string",
  "category": "string",
  "prompt": "string",
  "completion": "string",
  "expected_answer": "string",
  "extracted_answer": "string",
  "is_correct": "boolean"
}
```

### Field Descriptions

- **`problem_id`**: An identifier for the problem (if available).
- **`category`**: The category of the problem (e.g., `gravity`, `bit_manipulation`).
- **`prompt`**: The exact question string that is fed into the model.
- **`completion`**: The verified reasoning trace ending with the required tags. It takes the form:
  `[reasoning trace...]\n</think>\n\\boxed{[extracted_answer]}<|im_end|>`
- **`expected_answer`**: The known true answer to the problem.
- **`extracted_answer`**: The answer parsed from the reasoning trace's `\\boxed{}`.
- **`is_correct`**: Must be `true`. Examples where the extracted answer does not match the expected answer are dropped and not included in the SFT corpus.

## Verification Rules

To determine if an `extracted_answer` matches the `expected_answer`, the following rules are applied in order:

1. **Binary Strings**: If the expected answer is entirely composed of '0's and '1's, an exact case-insensitive string match is required.
2. **Floats / Numerics**: The answers are parsed as floats. They match if they are close within a relative tolerance of `1e-2` and an absolute tolerance of `1e-5` (i.e., `math.isclose(a, b, rel_tol=1e-2, abs_tol=1e-5)`).
3. **Fallback**: Exact case-insensitive string comparison.

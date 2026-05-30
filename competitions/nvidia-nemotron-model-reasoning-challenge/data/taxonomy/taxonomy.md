# Category Taxonomy & Value Ranking

This document defines the 9 problem categories in the NVIDIA Nemotron Model Reasoning Challenge, their frequencies in the training dataset (`train.csv`), and their value ranking based on expected gain. The expected gain represents the number of solvable problems using deterministic rule-discovery solvers and chain-of-thought (CoT) traces.

## 1. Category Definitions

*   **bit_manipulation**: Discover a per-bit transformation rule from input-output examples of 8-bit binary numbers.
*   **cipher**: Decrypt a substitution cipher. Given several example encryptions of Alice in Wonderland-themed sentences, deduce the character-level mapping and apply it to decrypt a new sentence.
*   **cryptarithm_deduce**: A verbal arithmetic puzzle to deduce operations (such as multiplication, division, absolute difference, concatenation, or reverse concatenation) applied to variables.
*   **cryptarithm_guess**: A more complex verbal arithmetic variant of the cryptarithm task that requires guessing unknown rules or operators.
*   **equation_numeric_deduce**: Discover the arithmetic rule applied to two-number equations (e.g., `64-65 = 201`). Involves figuring out which of 32 operators maps the two operands to the result, considering possible transformations (reversed operands, reversed result).
*   **equation_numeric_guess**: A variant of equation solving where operators might not be found in the examples, requiring assumptions (e.g., absolute difference) and guessing.
*   **gravity**: Determine a scalar value from examples and apply a multiplication operation to the question input. Solved optimally by splitting multiplication and division into multiple reasoning steps.
*   **numeral**: Convert a Roman numeral into an integer. All Roman numerals in the training set are between 1 and 100.
*   **unit_conversion**: Similar to gravity, figure out a scalar value representing the conversion factor and apply multiplication/division to the question input.

## 2. Training Frequencies & Value Ranking

The dataset contains a total of **9,500** training problems. The value ranking is calculated by multiplying the frequency of the category by the expected gain (target solver accuracy achievable through deterministic CoT generation, derived from the Progress-Prize winning solution).

| Rank | Category | Frequency (Total) | Expected Accuracy | Expected Gain (Found) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `gravity` | 1597 | 100.0% | **1597** |
| **2** | `unit_conversion` | 1594 | 100.0% | **1594** |
| **3** | `cipher` | 1576 | 100.0% | **1576** |
| **3** | `numeral` | 1576 | 100.0% | **1576** |
| **5** | `bit_manipulation` | 1602 | 85.1% | **1364** |
| **6** | `equation_numeric_deduce` | 596 | 90.6% | **540** |
| **7** | `cryptarithm_deduce` | 659 | 8.2% | **54** |
| **8** | `equation_numeric_guess` | 136 | 15.4% | **21** |
| **9** | `cryptarithm_guess` | 164 | 6.7% | **11** |
| | **TOTAL** | **9500** | **87.7%** | **8333** |

## Summary

The optimal strategy relies heavily on the top 6 categories (`gravity`, `unit_conversion`, `cipher`, `numeral`, `bit_manipulation`, and `equation_numeric_deduce`), which account for the vast majority of the expected gain (8,247 out of 8,333 achievable points). The `cryptarithm` categories and `equation_numeric_guess` provide marginal expected gains due to the extreme difficulty of crafting programmable, deterministic chain-of-thought traces for them.

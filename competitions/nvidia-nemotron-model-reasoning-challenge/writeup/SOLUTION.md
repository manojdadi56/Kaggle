# Nemotron Model Reasoning Challenge - Solution Writeup

**License:** CC BY 4.0

## Summary
Our method focuses on deterministic chain-of-thought (CoT) generation and finetuning to maximize the minimum logprob, following an approach heavily inspired by the Open Progress Prize winner. We utilize deterministic, hard-coded CoT templates to generate synthetic data for the 7 competition categories (Numeral, Unit Conversion, Gravity, Cipher, Logic, Mathematics, Coding). The base model `Nemotron-3-Nano-30B-A3B-BF16` is then fine-tuned with a 1-epoch LoRA SFT (rank $\le$ 32). This approach capitalizes on the idea that Nemotron can act as a reliable computing engine after targeted LoRA training without the need for reinforcement learning or complex decoding strategies (temperature=0.0).

## Data Pipeline
### Category Solvers & Deterministic CoT
We generated comprehensive CoT responses tailored to each category, minimizing the token choices the model has to make:
- **Design Principles:**
  - **Deterministic:** The training objective is to maximize the likelihood of the correct step-by-step path, ensuring high confidence greedy decoding.
  - **Simple:** Operations are broken down into granular steps (e.g., division broken down to subtraction/addition) to avoid computation errors.
  - **Coverage:** Rare operations are exhaustively covered in the synthetic data to ensure the model generalizes properly.
  - **Tokenization Awareness:** Avoids sequences that tokenizers handle poorly, simplifying the model's generation task.
  - **Generalizable:** Memorization is strictly avoided; the task focuses on learning algorithmic steps (aside from fixed dictionaries like Wonderland words).

## Training Configuration
- **Base Model:** `Nemotron-3-Nano-30B-A3B-BF16`
- **Method:** LoRA (Low-Rank Adaptation) Supervised Fine-Tuning (SFT)
- **LoRA Rank:** $\le$ 32
- **Epochs:** 1 (minimizes overfitting while learning deterministic mappings)
- **Objective:** Maximize the minimum logprob for the exact target traces.

## Cross-Validation (CV) Methodology
We perform local cross-validation by separating out held-out examples from our synthetic generators across all categories. We measure exact-match accuracy on the extracted final answer within `\boxed{...}`.
- CV Strategy: [Placeholder for detailed CV split methodology]
- CV Score: [Placeholder for local CV score]

## Results
| Metric | Score |
| ------ | ----- |
| Public LB | [Placeholder] |
| Private LB | [Placeholder] |
| Local CV | [Placeholder] |

## Reproducibility Steps
1. **Environment Setup:** Create the environment utilizing `uv` or `pip` to install dependencies.
2. **Data Generation:** Run the dataset curation scripts to create the synthetic reasoning traces.
3. **Training:** Execute the SFT script using the base Nemotron model.
4. **Inference:** Load the generated adapter alongside the base model using `vllm` for fast offline inference. Our `public_notebook.ipynb` outlines this process.

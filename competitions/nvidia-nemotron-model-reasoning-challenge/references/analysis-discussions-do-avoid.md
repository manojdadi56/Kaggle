# Ranked DOs and AVOIDs for Nemotron Model Reasoning Challenge

This document extracts actionable signals from 217 community discussions, ranked by evidence strength.

## Ranked DOs

### 1. [Discussion 681821](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681821)
- **Do:** Toggle the Kaggle internet setting off and on 3-4 times if pip installations fail.
- **Evidence/Signal:** "When your code runs in the session, if you turn the internet off and on three to four times at that moment, the problem will be fixed. That’s how I solved it."

### 2. [Discussion 692815](https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/692815)
- **Do:** Force reinstall specific numpy and pandas versions, and restart the kernel to fix binary incompatibilities.
- **Evidence/Signal:** "This error usually happens due to a NumPy–Pandas version mismatch (binary incompatibility). Fix (recommended): reinstall both with compatible versions: !pip install numpy==1.26.4 pandas==2.2.2 Then restart the runtime/kernel(very important)."

### 3. [Discussion 700197](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/700197)
- **Do:** Filter training problems where the min log-prob is already close to zero, and up-weight difficult examples.
- **Evidence/Signal:** "I do not want to train on sequences that would have been already well-trained... If the min logprob has not approach zero by the end of training I would increase the number of times I repeat the problem category."

### 4. [Discussion 685922](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/685922)
- **Do:** Use community-provided notebook baselines designed to correctly load Nemotron-3.
- **Evidence/Signal:** "use this notebook 'https://www.kaggle.com/code/mohamedamr992/easy-loading-of-nemotron-3'"

### 5. [Discussion 686794](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686794)
- **Do:** Write custom scripts to correctly load model adapters locally and evaluate them against valid data.
- **Evidence/Signal:** "To evaluate submissions offline and debug training issues, building a local vLLM CV/eval harness mirroring host parameters is recommended."

### 6. [Discussion 691641](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/691641)
- **Do:** Fallback to absolute difference `|a-b|` if the operator rule in equation puzzles cannot be found.
- **Evidence/Signal:** "If the operator is not found for this problem, I just assume that it is absolute difference... Output length is the strongest signal."

### 7. [Discussion 683172](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683172)
- **Do:** Verify kernel outputs are saved in `/kaggle/working/` and use the Kaggle CLI to fetch logs.
- **Evidence/Signal:** "CLI older than v2.1.2 — saves logs/kernel-slug.log... Second, where are you saving your outputs in the code? Everything needs to go to /kaggle/working/."

### 8. [Discussion 687119](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687119)
- **Do:** Create wheels offline and use pre-compiled dependencies to run without internet on inference.
- **Evidence/Signal:** "CPMP COMPETITION HOST when running notebooks before submitting... with internet access, pip installations can be much easier done without having to create multiple notebooks or wheels..."

### 9. [Discussion 699829](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/699829)
- **Do:** Use vLLM to maximize inference throughput.
- **Evidence/Signal:** "using vLLM I am getting 3000 Token/s"

### 10. [Discussion 681968](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681968)
- **Do:** Reference public notebooks to properly setup the Kaggle environment for submission.
- **Evidence/Signal:** "There are lots and lots of Amazing Public notebooks that people have shared. Use one of them for reference... In the practice, You will notice how to set up the environment properly."


## Ranked AVOIDs

### 1. [Discussion 682877](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/682877)
- **Avoid:** Relying on the default `mamba_ssm` and `causal_conv1d` packages on the RTX Pro 6000 architecture.
- **Evidence/Signal:** "AcceleratorError: CUDA error: no kernel image is available for execution on the device; causal_conv1d; mamba_ssm On Kaggle notebook runtime GPU RTX Pro 6000... This looks like the CUDA extension was built without support for the assigned GPU architecture."

### 2. [Discussion 684138](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/684138)
- **Avoid:** Building dependencies that require network access during offline inference.
- **Evidence/Signal:** "pip subprocess to install build dependencies did not run successfully... This error originates from a subprocess... Failed to establish a new connection"

### 3. [Discussion 686431](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686431)
- **Avoid:** Running QLoRA with `bitsandbytes` mismatched target modules that cause matrix shape errors.
- **Evidence/Signal:** "I am encountering the following error when training on a model that has been quantized using bitsandbytes: RuntimeError: mat1 and mat2 shapes cannot be multiplied (302x4096 and 1x2752512)"

### 4. [Discussion 686431](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686431)
- **Avoid:** Mixed precision index additions without explicit casting `Float` to `Half`.
- **Evidence/Signal:** "i now get an error called 'RuntimeError: index_add_(): self (Half) and source (Float) must have the same scalar type'"

### 5. [Discussion 686995](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/686995)
- **Avoid:** Depending solely on example outputs to determine bitwise equations without considering logical operators.
- **Evidence/Signal:** "Why every bit problem always has INFINITE AMOUNT OF WRONG SOLUTIONS... This proofs that there is infite amount of bitwise formula that are wrong solutions, but satisfy condtiion."

### 6. [Discussion 701924](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/701924)
- **Avoid:** Emitting trailing zeroes and unformatted numbers when the evaluation metric expects exact integer matching.
- **Evidence/Signal:** "say for a gravity problem, the answer is 10, but the model outputs 10.00, this will be wrongfully categorized... The metric code checks if the answer has only 1 and 0, and if so falls to string matching"

### 7. [Discussion 683311](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683311)
- **Avoid:** Testing model generation directly without verifying CUDA driver compatibility first.
- **Evidence/Signal:** "I tried to test the model with model.generate(), but I got the following error: AcceleratorError: CUDA error: no kernel image is available for execution on the device"

### 8. [Discussion 696993](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/696993)
- **Avoid:** Over-tuning on easy deterministic puzzles which drops score below the baseline.
- **Evidence/Signal:** "SFT on Deterministic Puzzles Dropping Score Below Baseline Hi everyone, I’ve been working on fine-tuning Nemotron-3-Nano-30B with LoRA on the 4 deterministic puzzle types... and experiencing score drops below baseline."

### 9. [Discussion 687063](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/687063)
- **Avoid:** Assuming all symbolic puzzles contain sufficient information to be uniquely solvable.
- **Evidence/Signal:** "Are all symbolic puzzles guaranteed to be uniquely solvable? Some seem to lack enough information"

### 10. [Discussion 694041](https://kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/694041)
- **Avoid:** Interpreting puzzle rules strictly from instructions instead of identifying the underlying generated operator sets.
- **Evidence/Signal:** "2 interpretations of the bit manipulation problem... corrupt or puzzle (numeric equations)... There is no clear relationship between the question and the examples."

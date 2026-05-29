# US-4 — Training tasks

> As the system, I want to train and CV LoRA adapters, picking the best for submission.

Tasks: TASK-4.0 (Jules: author the QLoRA training script + config, rank ≤ 32, multi-GPU aware for local_40g) → TASK-4.x (operator: dispatch training runs on `kaggle_gpu`/`local_40g`, write `experiments/<id>/cv_score.json`). Variants can train in parallel across backends. First pass = the baseline submission.

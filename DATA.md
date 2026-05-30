# Competition data — how to get it, where it lives, what NOT to commit

The Nemotron Reasoning Challenge data is **not committed to this repository**. Doing so would violate Kaggle's competition rules (line 117 of `competitions/nvidia-nemotron-model-reasoning-challenge/references/tab-rules.md`):

> *"You agree not to transmit, duplicate, publish, redistribute or otherwise provide or make available the Competition Data to any party not participating in the Competition."*

A public GitHub repo = redistribution to non-participants = disqualification risk.

## How to fetch it (laptop or Jules VM)
Both locations are valid because both have `KAGGLE_API_TOKEN` (KGAT) configured per `JULES_SETUP.md`. From the repo root:

```bash
python tools/download_competition_data.py
```

That lands the raw files under `competitions/nvidia-nemotron-model-reasoning-challenge/data/raw/`:
| File | Size | Schema | Notes |
|---|---|---|---|
| `train.csv` | ~3.07 MB | `id, prompt, answer` | ~9 500 problems across 9 categories |
| `test.csv`  | ~1.46 KB | `id, prompt` | Public sample only (~5 rows). Hidden test set replaces this at host scoring time. |

`competitions/*/data/raw/` is `.gitignore`d (`competitions/*/data/raw/*`), so the CSVs cannot be accidentally committed. Only `.gitkeep` + this README are tracked.

## What you CAN commit (and we do)
- **Tooling** that processes the data (`data/taxonomy/`, `data/curation/`, `data/solvers/<category>/`, `data/cot/`, `data/synthetic/`, `eval/`).
- **A small documentation sample**: see `competitions/<slug>/data/sample/train_sample.csv` — 5 train rows with the **answer column dropped**, used as fixtures for offline tests. That's documentation/fair-use, not redistribution of the dataset.
- **Generated synthetic data** that we produce ourselves via the deterministic per-category solvers — that's our IP, not Kaggle's data.

## What you must NEVER commit
- Anything under `data/raw/`.
- A CSV that contains real `answer` values from train.csv (regardless of folder).
- A notebook that pastes raw rows in its output.
- The hidden test set.

## Per-Jules-task note
Jules workers fetching this data must run `python tools/download_competition_data.py` as a setup step (or rely on the `setup_script` configured per `JULES_SETUP.md`). They MUST NOT include any downloaded row content in their PR diffs.

## License attribution
Per rules line 115, Competition Data carries CC BY 4.0 — when we publish the prize-eligibility writeup we will attribute: *"Built using data from the NVIDIA Nemotron Model Reasoning Challenge (NVIDIA Research)."* That attribution does NOT override the redistribution prohibition above.

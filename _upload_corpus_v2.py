"""Upload corpus v2 (243KB jsonl) as a private Kaggle dataset for notebook attachment."""
import os, json, shutil, tempfile
from pathlib import Path

env = {l.split("=",1)[0]: l.split("=",1)[1] for l in Path(".env").read_text(encoding="utf-8").splitlines()
       if l and "=" in l and not l.startswith("#")}
for k,v in env.items():
    if k.startswith("KAGGLE"): os.environ[k] = v

import kaggle
api = kaggle.KaggleApi()
api.authenticate()

CORPUS = Path("competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v2/corpus.jsonl")
USER = env["KAGGLE_USERNAME"]
SLUG = "nemotron-cot-corpus-v2"

# Stage the upload dir with dataset-metadata.json + the corpus file
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    shutil.copy(CORPUS, td / "corpus.jsonl")
    (td / "dataset-metadata.json").write_text(json.dumps({
        "title": "Nemotron CoT Corpus v2 (398 rows, 4 cats)",
        "id": f"{USER}/{SLUG}",
        "licenses": [{"name": "CC0-1.0"}],
        "subtitle": "First-iteration CoT corpus, 398 rows, 4 categories",
        "description": "Self-generated CoT corpus rows from train.csv. v3/v4 in progress with all 9 categories + verified CoT.",
        "keywords": ["nemotron", "reasoning", "cot", "synthetic"],
    }, indent=2), encoding="utf-8")

    print(f"staged {td}")
    for f in td.iterdir(): print(f"  {f.name}: {f.stat().st_size:,} bytes")

    # Try dataset_create_new
    try:
        r = api.dataset_create_new(folder=str(td), public=False, quiet=False)
        print("\ncreate result:", r)
    except Exception as e:
        print(f"\ncreate err: {e}")
        # If dataset already exists, try create_version
        try:
            r = api.dataset_create_version(folder=str(td), version_notes="auto-upload v2", quiet=False)
            print("create_version result:", r)
        except Exception as e2:
            print(f"create_version err: {e2}")

print(f"\nDataset URL: https://www.kaggle.com/datasets/{USER}/{SLUG}")
print(f"Attach in notebook: 'datasetDataSources': ['{USER}/{SLUG}']")

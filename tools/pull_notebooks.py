#!/usr/bin/env python3
"""Pull notebook SOURCE CODE via the Kaggle API (needs creds).

Browser scraping can't read Kaggle's Monaco-based notebook viewer (code is fetched
by an authenticated API call, never rendered into the DOM). The reliable path is
the official API. Set KAGGLE_USERNAME / KAGGLE_KEY in .env (or ~/.kaggle/kaggle.json),
then run this to fetch the top community notebooks' real source into references/.

  python tools/pull_notebooks.py            # uses NOTEBOOKS list below
  python tools/pull_notebooks.py owner/slug owner2/slug2 ...
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "nvidia-nemotron-model-reasoning-challenge"
OUT = Path(f"competitions/{SLUG}/references")

# Top community notebooks worth pulling (owner/slug), from the code-tab listing.
NOTEBOOKS = [
    "kienngx/nvidia-nemotron-training-copy-run-instantly",
    "kienngx/nvidia-nemotron-trained-models-submission",
    "kienngx/nvidia-nemotron-training-cot-labels",
    "ryanholbrook/nvidia-nemotron-submission-demo",
    "huikang/end-to-end-finetuning-for-lb-0-85",
    "huikang/adapter-validation-notebook",
]


def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def have_creds() -> bool:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    return (Path.home() / ".kaggle" / "kaggle.json").exists()


def pull_one(ref: str) -> bool:
    safe = ref.replace("/", "__")
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(["kaggle", "kernels", "pull", ref, "-p", td, "-m"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  FAIL {ref}: {r.stderr.strip()[:120]}")
            return False
        td = Path(td)
        src = next((f for f in td.iterdir() if f.suffix in (".ipynb", ".py", ".r", ".R")), None)
        if not src:
            print(f"  FAIL {ref}: no source file pulled")
            return False
        code = src.read_text(encoding="utf-8", errors="ignore")
        if src.suffix == ".ipynb":
            code = ipynb_to_text(code)
        OUT.mkdir(parents=True, exist_ok=True)
        url = f"https://www.kaggle.com/code/{ref}"
        (OUT / f"notebook-{safe}.md").write_text(
            f"# Notebook: {ref}\n\n- **source:** {url}\n- **pulled:** kaggle kernels pull\n"
            f"- **chars:** {len(code)}\n\n---\n\n```python\n{code}\n```\n", encoding="utf-8")
        print(f"  OK   notebook-{safe}.md ({len(code)} chars)")
        return True


def ipynb_to_text(raw: str) -> str:
    import json
    try:
        nb = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    parts = []
    for c in nb.get("cells", []):
        src = "".join(c.get("source", []))
        if c.get("cell_type") == "markdown":
            parts.append(f"# --- markdown ---\n{src}")
        else:
            parts.append(src)
    return "\n\n".join(parts)


def main() -> int:
    load_env()
    if not have_creds():
        print("No Kaggle creds. Set KAGGLE_USERNAME/KAGGLE_KEY in .env or ~/.kaggle/kaggle.json.")
        return 2
    try:
        subprocess.run(["kaggle", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("kaggle CLI not installed. Run: pip install kaggle")
        return 3
    refs = sys.argv[1:] or NOTEBOOKS
    print(f"pulling {len(refs)} notebooks...")
    ok = sum(pull_one(r) for r in refs)
    print(f"DONE: {ok}/{len(refs)} pulled")
    return 0


if __name__ == "__main__":
    sys.exit(main())

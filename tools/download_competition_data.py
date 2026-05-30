"""Download competition train/test data via the Kaggle web API using KGAT bearer.

Run locally (laptop or jules.google VM with KAGGLE_API_TOKEN env var set).
Files land in `competitions/<slug>/data/raw/` which is gitignored — see DATA.md
for the no-redistribution rule (Kaggle competition rules line 117).

Usage:
  python tools/download_competition_data.py [--slug nvidia-nemotron-model-reasoning-challenge]
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("error: httpx not installed; pip install httpx", file=sys.stderr); sys.exit(2)

SLUG_DEFAULT = "nvidia-nemotron-model-reasoning-challenge"
API = "https://www.kaggle.com/api/v1"


def _token() -> str:
    tok = os.environ.get("KAGGLE_API_TOKEN") or os.environ.get("KGAT")
    if not tok:
        # try .env (one-level walk from this script)
        repo = Path(__file__).resolve().parents[1]
        env = repo / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("KAGGLE_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    if not tok:
        print("error: KAGGLE_API_TOKEN (KGAT) not set", file=sys.stderr); sys.exit(3)
    return tok


def list_files(slug: str) -> list[dict]:
    tok = _token()
    r = httpx.get(f"{API}/competitions/data/list/{slug}", timeout=30,
                  headers={"Authorization": f"Bearer {tok}", "User-Agent": "orch-data-fetch"})
    r.raise_for_status()
    return r.json().get("files", [])


def download_one(slug: str, name: str, dest: Path) -> int:
    tok = _token()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", f"{API}/competitions/data/download/{slug}/{name}",
                      headers={"Authorization": f"Bearer {tok}", "User-Agent": "orch-data-fetch"},
                      follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        size = 0
        with dest.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk); size += len(chunk)
    return size


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    slug = argv[argv.index("--slug") + 1] if "--slug" in argv else SLUG_DEFAULT
    repo = Path(__file__).resolve().parents[1]
    dest_dir = repo / "competitions" / slug / "data" / "raw"
    files = list_files(slug)
    print(f"competition: {slug}")
    print(f"files to fetch: {[f['name'] for f in files]}")
    for f in files:
        name = f["name"]
        path = dest_dir / name
        size = download_one(slug, name, path)
        print(f"  ✓ {name}: {size:,} bytes -> {path}")
    print(f"\nDestination: {dest_dir}  (gitignored — see DATA.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

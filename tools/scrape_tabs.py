#!/usr/bin/env python3
"""Targeted, sequential scrape of specific competition tabs (no overlap/races).

  python tools/scrape_tabs.py --slug <comp> --tabs code,discussion-list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kaggle_scrape2 import BASE, driver, get_rendered, write_md  # reuse v2 helpers

TAB_URLS = {
    "overview": "/overview",
    "data": "/data",
    "rules": "/rules",
    "leaderboard": "/leaderboard",
    "models": "/models",
    "code": "/code?sortBy=voteCount",
    "discussion-list": "/discussion?sort=votes",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--tabs", required=True, help="comma list, e.g. code,discussion-list")
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    out = Path(f"competitions/{a.slug}/references")
    out.mkdir(parents=True, exist_ok=True)
    d = driver(a.headless)
    try:
        for name in [t.strip() for t in a.tabs.split(",") if t.strip()]:
            url = f"{BASE}/competitions/{a.slug}{TAB_URLS[name]}"
            body = get_rendered(d, url, min_len=300, expand=(name not in ("code", "discussion-list")))
            write_md(out, f"tab-{name}.md", f"Competition tab: {name}", url, body)
            print(f"tab {name}: {len(body)} chars -> tab-{name}.md")
    finally:
        d.quit()
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())

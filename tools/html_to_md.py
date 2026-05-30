#!/usr/bin/env python3
"""Offline: convert any saved raw discussion HTML -> clean markdown (flat files).

Covers threads whose HTML was saved by the first scraper but never turned into
markdown. Skips ids that already have a discussion-<id>.md unless --force.
"""
from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup

SLUG = "nvidia-nemotron-model-reasoning-challenge"
RAW = Path(f".scrape/raw/{SLUG}/discussions")
OUT = Path(f"competitions/{SLUG}/references")

SKIP = {"Skip to", "content", "Kaggle", "Create", "Home", "Competitions", "Benchmarks",
        "Game Arena", "Data Hub", "More", "Your Work", "Viewed", "Bookmarks",
        "View Active Events", "Search", "OK, Got it.", "Sign In", "Register",
        "Learn more", "menu", "explore", "emoji_events", "leaderboard", "smart_toy",
        "code", "expand_less", "expand_more", "school", "comment", "auto_awesome_motion"}


def clean(soup: BeautifulSoup) -> str:
    for t in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        t.decompose()
    main = soup.find("main") or soup.body or soup
    lines, prev = [], None
    for ln in main.get_text("\n", strip=True).split("\n"):
        ln = ln.strip()
        if not ln or ln in SKIP or ln == prev:
            continue
        lines.append(ln); prev = ln
    return "\n".join(lines)


def title_of(soup: BeautifulSoup) -> str:
    for h in soup.find_all(["h1", "h2"]):
        t = h.get_text(strip=True)
        if t and t.lower() != "nvidia nemotron model reasoning challenge":
            return t
    t = soup.find("title")
    return (t.get_text(strip=True).replace(" | Kaggle", "") if t else "(untitled)")


def main() -> int:
    force = "--force" in sys.argv
    if not RAW.exists():
        print("no raw dir"); return 0
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(RAW.glob("*.html")):
        did = f.stem
        dest = OUT / f"discussion-{did}.md"
        if dest.exists() and not force:
            continue
        soup = BeautifulSoup(f.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        body = clean(soup)
        url = f"https://www.kaggle.com/competitions/{SLUG}/discussion/{did}"
        dest.write_text(f"# {title_of(soup)}\n\n- **source:** {url}\n- **scraped:** 2026-05-30 (authenticated browser)\n- **chars:** {len(body)}\n\n---\n\n{body}\n", encoding="utf-8")
        print(f"  wrote discussion-{did}.md ({len(body)} chars)")
        n += 1
    print(f"converted {n} new discussion file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

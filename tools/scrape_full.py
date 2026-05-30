#!/usr/bin/env python3
"""Parallel-friendly full scraper: ALL discussions OR notebook source code.

Reuses the authenticated persistent profile. Each item is saved immediately and
already-saved items are skipped, so runs are resumable and two modes can run
concurrently against two profile copies.

  python tools/scrape_full.py discussions --profile .scrape/profile  [--pages 12]
  python tools/scrape_full.py notebooks   --profile .scrape/profile2 [--max 40]
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE = "https://www.kaggle.com"
SLUG = "nvidia-nemotron-model-reasoning-challenge"
OUT = Path(f"competitions/{SLUG}/references")
RAW = Path(f".scrape/raw/{SLUG}")

SKIP = {"Skip to", "content", "Kaggle", "Create", "Home", "Competitions", "Benchmarks",
        "Game Arena", "Data Hub", "More", "Your Work", "Viewed", "Bookmarks", "menu",
        "View Active Events", "Search", "OK, Got it.", "Sign In", "Register", "Learn more",
        "explore", "emoji_events", "leaderboard", "smart_toy", "code", "expand_less",
        "expand_more", "school", "comment", "auto_awesome_motion", "settings", "help"}


def driver(profile: str, headless: bool = True):
    p = Path(profile).resolve()
    p.mkdir(parents=True, exist_ok=True)
    o = Options()
    o.add_argument(f"--user-data-dir={p}")
    o.add_argument("--profile-directory=Default")
    if headless:
        o.add_argument("--headless=new")
    o.add_argument("--no-sandbox"); o.add_argument("--disable-gpu")
    o.add_argument("--disable-blink-features=AutomationControlled")
    o.add_argument("--window-size=1500,1100")
    d = webdriver.Chrome(options=o)
    d.set_page_load_timeout(60)
    return d


def main_text(d) -> str:
    try:
        return d.find_element(By.TAG_NAME, "main").text or ""
    except Exception:
        try:
            return d.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return ""


def settle(d, min_len=400, timeout=22):
    last, stable, waited = -1, 0, 0.0
    while waited < timeout:
        try:
            d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass
        time.sleep(1.0); waited += 1.0
        n = len(main_text(d))
        if n >= min_len and n == last:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        last = n
    try:
        d.execute_script("window.scrollTo(0, 0);")
    except Exception:
        pass
    time.sleep(0.4)


def clean(text: str) -> str:
    out, prev = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln or ln in SKIP or ln == prev:
            continue
        out.append(ln); prev = ln
    return "\n".join(out)


def write_md(name, title, url, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        f"# {title}\n\n- **source:** {url}\n- **scraped:** 2026-05-30 (authenticated browser)\n- **chars:** {len(body)}\n\n---\n\n{body}\n",
        encoding="utf-8")


def title_of(d):
    for sel in ("h1", "h2"):
        for e in d.find_elements(By.TAG_NAME, sel):
            t = (e.text or "").strip()
            if t and t.lower() != "nvidia nemotron model reasoning challenge" and not re.match(r"^\d+\s+comments?$", t, re.I):
                return t
    return (d.title or "").replace(" | Kaggle", "").strip()


# ---------------- discussions ----------------
def enumerate_discussions(d, pages):
    seen, order = set(), []
    for p in range(1, pages + 1):
        d.get(f"{BASE}/competitions/{SLUG}/discussion?sort=votes&page={p}")
        settle(d, min_len=200, timeout=15)
        try:
            root = d.find_element(By.TAG_NAME, "main")
        except Exception:
            root = d.find_element(By.TAG_NAME, "body")
        for a in root.find_elements(By.CSS_SELECTOR, "a[href]"):
            m = re.search(r"/discussion/(\d+)", a.get_attribute("href") or "")
            if m and m.group(1) not in seen:
                seen.add(m.group(1)); order.append(m.group(1))
    return order


def run_discussions(d, pages):
    (RAW / "discussions").mkdir(parents=True, exist_ok=True)
    ids = enumerate_discussions(d, pages)
    print(f"enumerated {len(ids)} discussion threads", flush=True)
    done = 0
    for i, did in enumerate(ids, 1):
        dest = OUT / f"discussion-{did}.md"
        if dest.exists():
            continue
        url = f"{BASE}/competitions/{SLUG}/discussion/{did}"
        try:
            d.get(url); settle(d, min_len=300, timeout=20)
            body = clean(main_text(d))
            (RAW / "discussions" / f"{did}.html").write_text(d.page_source, encoding="utf-8")
            write_md(f"discussion-{did}.md", title_of(d), url, body)
            done += 1
            print(f"  [{i}/{len(ids)}] discussion-{did}: {len(body)} chars", flush=True)
        except Exception as e:
            print(f"  [{i}/{len(ids)}] discussion-{did} FAILED: {str(e)[:90]}", flush=True)
    print(f"DISCUSSIONS DONE: {done} new", flush=True)


# ---------------- notebooks (source code) ----------------
def enumerate_notebooks(d, pages):
    seen, order = set(), []
    for srt in ("voteCount", "hotness"):
        for p in range(1, pages + 1):
            d.get(f"{BASE}/competitions/{SLUG}/code?sortBy={srt}&page={p}")
            settle(d, min_len=200, timeout=15)
            try:
                root = d.find_element(By.TAG_NAME, "main")
            except Exception:
                root = d.find_element(By.TAG_NAME, "body")
            for a in root.find_elements(By.CSS_SELECTOR, "a[href]"):
                href = (a.get_attribute("href") or "").split("?")[0].rstrip("/")
                m = re.match(rf"{BASE}/code/([^/]+)/([^/]+)$", href)
                if m:
                    key = f"{m.group(1)}/{m.group(2)}"
                    # skip the user's own non-competition notebooks heuristically later
                    if key not in seen:
                        seen.add(key); order.append((key, href))
    return order


def extract_code(d) -> str:
    """Pull code-cell + markdown-cell text from the rendered notebook viewer."""
    blocks = []
    for sel in ("pre", "code", "div.cell", "div[class*='code']", "div[class*='source']"):
        for e in d.find_elements(By.CSS_SELECTOR, sel):
            t = (e.text or "").strip()
            if t and len(t) > 1:
                blocks.append(t)
    # dedupe consecutive
    out, prev = [], None
    for b in blocks:
        if b != prev:
            out.append(b)
        prev = b
    return "\n\n".join(out)


def run_notebooks(d, pages, mx):
    (RAW / "notebooks").mkdir(parents=True, exist_ok=True)
    nbs = enumerate_notebooks(d, pages)
    print(f"enumerated {len(nbs)} notebooks", flush=True)
    done = 0
    for i, (key, url) in enumerate(nbs, 1):
        if done >= mx:
            break
        safe = key.replace("/", "__")
        dest = OUT / f"notebook-{safe}.md"
        if dest.exists():
            continue
        try:
            d.get(url); settle(d, min_len=400, timeout=30)
            code = extract_code(d)
            body = main_text(d)
            combined = f"## Notebook page\n{clean(body)}\n\n## Extracted code/markdown cells\n{code}" if code else clean(body)
            (RAW / "notebooks" / f"{safe}.html").write_text(d.page_source, encoding="utf-8")
            write_md(f"notebook-{safe}.md", title_of(d), url, combined)
            done += 1
            print(f"  [{i}] notebook-{safe}: body={len(body)} code={len(code)}", flush=True)
        except Exception as e:
            print(f"  [{i}] notebook {key} FAILED: {str(e)[:90]}", flush=True)
    print(f"NOTEBOOKS DONE: {done} new", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["discussions", "notebooks"])
    ap.add_argument("--profile", default=".scrape/profile")
    ap.add_argument("--pages", type=int, default=12)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--no-headless", action="store_true")
    a = ap.parse_args()
    d = driver(a.profile, headless=not a.no_headless)
    try:
        if a.mode == "discussions":
            run_discussions(d, a.pages)
        else:
            run_notebooks(d, a.pages, a.max)
    finally:
        d.quit()


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Robust Kaggle scraper v2 — waits for client-side render, captures VISIBLE text.

Uses the persistent authenticated profile (.scrape/profile). For each page it
polls until the content region actually renders (not just the nav shell), scrolls
to load comments/cells, then saves the rendered text as clean markdown directly
into competitions/<slug>/references/ as FLAT files (so .gitignore `references/*/`
does not exclude them).

  python tools/kaggle_scrape2.py --slug <comp> [--discussions N] [--notebooks N] [--headless]
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
PROFILE = Path(".scrape/profile").resolve()


def driver(headless: bool):
    o = Options()
    PROFILE.mkdir(parents=True, exist_ok=True)
    o.add_argument(f"--user-data-dir={PROFILE}")
    o.add_argument("--profile-directory=Default")
    if headless:
        o.add_argument("--headless=new")
    o.add_argument("--no-sandbox")
    o.add_argument("--disable-blink-features=AutomationControlled")
    o.add_argument("--window-size=1500,1100")
    o.add_argument("--disable-gpu")
    d = webdriver.Chrome(options=o)
    d.set_page_load_timeout(60)
    return d


def _main_text(d) -> str:
    try:
        return d.find_element(By.TAG_NAME, "main").text or ""
    except Exception:
        try:
            return d.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return ""


EXPAND_TEXTS = ("show more", "see more", "load more", "view more", "show replies",
                "more comment", "more repl", "read more", "show 1 more", "expand",
                "show all", "show full")


def _expand_all(d, max_rounds: int = 30):
    """Click every 'show more / see more / N replies' control and lazy-scroll
    until the page stops growing — so collapsed comments/cells are captured."""
    last_h = 0
    for _ in range(max_rounds):
        clicked = 0
        try:
            btns = d.find_elements(By.XPATH,
                "//button | //a[@role='button'] | //span[@role='button'] | //div[@role='button']")
        except Exception:
            btns = []
        for b in btns:
            try:
                t = (b.text or "").strip().lower()
            except Exception:
                continue
            if not t or len(t) > 45:
                continue
            if any(k in t for k in EXPAND_TEXTS) or re.match(r"^\d+\s+(more|repl)", t):
                try:
                    d.execute_script("arguments[0].scrollIntoView({block:'center'});", b)
                    d.execute_script("arguments[0].click();", b)
                    clicked += 1
                    time.sleep(0.35)
                except Exception:
                    pass
        try:
            d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass
        time.sleep(0.9)
        try:
            h = d.execute_script("return document.body.scrollHeight")
        except Exception:
            h = last_h
        if h == last_h and clicked == 0:
            break
        last_h = h


def get_rendered(d, url: str, min_len: int = 400, timeout: int = 35, expand: bool = True) -> str:
    """Navigate, wait for initial render, expand all collapsed content, capture text."""
    d.get(url)
    last, stable, waited = -1, 0, 0.0
    while waited < timeout:                     # wait for client-side render to settle
        time.sleep(1.2)
        waited += 1.2
        n = len(_main_text(d))
        if n >= min_len and n == last:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        last = n
    if expand:
        _expand_all(d)                          # click see-more / load lazy content
    try:
        d.execute_script("window.scrollTo(0, 0);")
    except Exception:
        pass
    time.sleep(0.5)
    return _main_text(d)


def slug_title(d) -> str:
    bad = re.compile(r"^\d+\s+comments?$", re.I)
    for sel in ("h1", "h2"):
        for e in d.find_elements(By.TAG_NAME, sel):
            t = (e.text or "").strip()
            if t and t.lower() != "nvidia nemotron model reasoning challenge" and not bad.match(t):
                return t
    return (d.title or "").replace(" | Kaggle", "").strip()


def write_md(out: Path, name: str, title: str, url: str, body: str):
    md = (f"# {title}\n\n- **source:** {url}\n- **scraped:** 2026-05-30 (authenticated browser)\n"
          f"- **chars:** {len(body)}\n\n---\n\n{body}\n")
    (out / name).write_text(md, encoding="utf-8")


def enumerate_links(d, list_url_tmpl: str, pattern: str, pages: int):
    found, seen = [], set()
    for p in range(1, pages + 1):
        get_rendered(d, list_url_tmpl.format(page=p), min_len=200, timeout=20, expand=False)
        try:                                  # scope to main content (exclude left nav / "Your Work")
            root = d.find_element(By.TAG_NAME, "main")
        except Exception:
            root = d.find_element(By.TAG_NAME, "body")
        for a in root.find_elements(By.CSS_SELECTOR, "a[href]"):
            href = a.get_attribute("href") or ""
            m = re.search(pattern, href)
            if m:
                key = href.split("?")[0].split("#")[0].rstrip("/")  # ignore query + anchor
                if key not in seen:
                    seen.add(key); found.append((m.group(1), key))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--discussions", type=int, default=25)
    ap.add_argument("--notebooks", type=int, default=15)
    ap.add_argument("--pages", type=int, default=10)
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()

    out = Path(f"competitions/{a.slug}/references")
    out.mkdir(parents=True, exist_ok=True)
    d = driver(a.headless)
    log = print

    try:
        # ---- static tabs ----
        tabs = {
            "overview": f"{BASE}/competitions/{a.slug}/overview",
            "data": f"{BASE}/competitions/{a.slug}/data",
            "rules": f"{BASE}/competitions/{a.slug}/rules",
            "leaderboard": f"{BASE}/competitions/{a.slug}/leaderboard",
            "models": f"{BASE}/competitions/{a.slug}/models",
            "code": f"{BASE}/competitions/{a.slug}/code?sortBy=voteCount",
            "discussion-list": f"{BASE}/competitions/{a.slug}/discussion?sort=votes",
        }
        for name, url in tabs.items():
            try:
                body = get_rendered(d, url, min_len=300)
                write_md(out, f"tab-{name}.md", f"Competition tab: {name}", url, body)
                log(f"tab {name}: {len(body)} chars")
            except Exception as e:
                log(f"tab {name} FAILED: {e}")

        index = ["# Scraped competition references (authenticated)", "",
                 "Captured via a logged-in browser session, 2026-05-30. Static tabs + top discussions + top notebooks.", ""]

        # ---- discussions ----
        log("enumerating discussions...")
        threads = enumerate_links(d, f"{BASE}/competitions/{a.slug}/discussion?sort=votes&page={{page}}",
                                  r"/discussion/(\d+)", a.pages)
        log(f"found {len(threads)} discussion threads; scraping top {a.discussions}")
        index.append("## Discussions")
        for i, (tid, url) in enumerate(threads[: a.discussions], 1):
            try:
                body = get_rendered(d, url, min_len=400)
                title = slug_title(d)
                write_md(out, f"discussion-{tid}.md", title, url, body)
                index.append(f"- [{title[:70]}](discussion-{tid}.md) — {url} ({len(body)} chars)")
                log(f"  [{i}] discussion-{tid}: {len(body)} chars — {title[:50]}")
            except Exception as e:
                log(f"  [{i}] discussion {tid} FAILED: {e}")

        # ---- notebooks/code ----
        log("enumerating notebooks...")
        nbs = enumerate_links(d, f"{BASE}/competitions/{a.slug}/code?sortBy=voteCount&page={{page}}",
                              r"/code/([^/?#]+/[^/?#]+)", a.pages)
        log(f"found {len(nbs)} notebooks; scraping top {a.notebooks}")
        index.append("\n## Notebooks / code")
        for i, (nid, url) in enumerate(nbs[: a.notebooks], 1):
            try:
                body = get_rendered(d, url, min_len=400)
                title = slug_title(d)
                safe = nid.replace("/", "__")
                write_md(out, f"notebook-{safe}.md", title, url, body)
                index.append(f"- [{title[:70]}](notebook-{safe}.md) — {url} ({len(body)} chars)")
                log(f"  [{i}] notebook {safe}: {len(body)} chars — {title[:50]}")
            except Exception as e:
                log(f"  [{i}] notebook {nid} FAILED: {e}")

        (out / "scraped-index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
        log(f"index written: {out/'scraped-index.md'}")
    finally:
        d.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

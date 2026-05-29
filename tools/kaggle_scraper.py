"""Selenium scraper for gated Kaggle competition content (discussions + notebooks).

Kaggle pages are JS-rendered and login-gated, so search/WebFetch can't read them.
This drives a REAL Chrome with a PERSISTENT profile: you log in once (`login`
mode), the session cookie is saved into the profile, and the scraper then reuses
it non-interactively (`scrape` mode).

Usage (from repo root):
    python tools/kaggle_scraper.py login         # opens Chrome; log in; auto-detects + closes
    python tools/kaggle_scraper.py scrape         # discussions + notebooks -> references/ + .scrape/
    python tools/kaggle_scraper.py scrape-discussions
    python tools/kaggle_scraper.py scrape-code
Options: --slug <comp> --max-pages N --max-items N --headless

Outputs:
    competitions/<slug>/references/kaggle-discussions.md   (committed)
    competitions/<slug>/references/kaggle-notebooks.md     (committed)
    .scrape/raw/...                                        (gitignored raw html + json)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import WebDriverException, TimeoutException
except ImportError:
    sys.exit("selenium not installed. Run: pip install selenium")

REPO = Path(__file__).resolve().parents[1]
SCRAPE_DIR = REPO / ".scrape"
PROFILE_DIR = SCRAPE_DIR / "profile"
RAW_DIR = SCRAPE_DIR / "raw"
DEFAULT_SLUG = "nvidia-nemotron-model-reasoning-challenge"
BASE = "https://www.kaggle.com"


# ---------------- driver ----------------
def make_driver(headless: bool = False) -> "webdriver.Chrome":
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--window-size=1440,1000")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    if headless:
        opts.add_argument("--headless=new")
    d = webdriver.Chrome(options=opts)  # Selenium Manager auto-resolves the driver
    d.set_page_load_timeout(60)
    return d


def is_logged_in(d) -> bool:
    """Logged-out Kaggle shows a link to /account/login in the header; logged-in does not."""
    try:
        d.get(BASE + "/")
    except WebDriverException:
        return False
    time.sleep(2)
    return len(d.find_elements(By.CSS_SELECTOR, 'a[href*="/account/login"]')) == 0


def _scroll(d, rounds: int = 6, pause: float = 1.0):
    last = 0
    for _ in range(rounds):
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        h = d.execute_script("return document.body.scrollHeight")
        if h == last:
            break
        last = h


# ---------------- login ----------------
def cmd_login(args) -> int:
    print("Opening Chrome. Log in to Kaggle in the window that appears...")
    d = make_driver(headless=False)
    try:
        d.get(BASE + "/account/login")
        deadline = time.time() + args.login_timeout
        while time.time() < deadline:
            time.sleep(3)
            try:
                if len(d.find_elements(By.CSS_SELECTOR, 'a[href*="/account/login"]')) == 0 \
                        and d.current_url.startswith(BASE):
                    # double-check on the home page
                    if is_logged_in(d):
                        print("Login detected — session saved to the persistent profile.")
                        return 0
            except WebDriverException:
                print("Browser window was closed before login completed.")
                return 1
        print("Timed out waiting for login.")
        return 1
    finally:
        try:
            d.quit()
        except Exception:
            pass


# ---------------- discussions ----------------
def collect_discussion_links(d, slug: str, max_pages: int) -> dict:
    threads = {}
    for page in range(1, max_pages + 1):
        d.get(f"{BASE}/competitions/{slug}/discussion?sort=votes&page={page}")
        try:
            WebDriverWait(d, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'a[href*="/competitions/{slug}/discussion/"]')))
        except TimeoutException:
            break
        _scroll(d, rounds=4)
        before = len(threads)
        for a in d.find_elements(By.CSS_SELECTOR, f'a[href*="/competitions/{slug}/discussion/"]'):
            href = (a.get_attribute("href") or "").split("?")[0]
            m = re.search(r"/discussion/(\d+)", href)
            if not m:
                continue
            tid = m.group(1)
            if tid not in threads:
                threads[tid] = {"id": tid, "url": href, "title": (a.text or "").strip()}
        print(f"  discussion page {page}: total unique threads = {len(threads)}")
        if len(threads) == before:
            break
    return threads


def scrape_one(d, url: str) -> dict:
    d.get(url)
    time.sleep(2)
    _scroll(d, rounds=8)
    title = (d.title or "").replace(" | Kaggle", "").strip()
    try:
        body = d.find_element(By.TAG_NAME, "body").text
    except WebDriverException:
        body = ""
    return {"url": url, "title": title, "text": body, "html": d.page_source}


def cmd_scrape_discussions(args, d=None) -> int:
    own = d is None
    if own:
        d = make_driver(headless=args.headless)
    try:
        if not is_logged_in(d):
            print("Not logged in. Run: python tools/kaggle_scraper.py login")
            return 2
        slug = args.slug
        raw = RAW_DIR / slug / "discussions"
        raw.mkdir(parents=True, exist_ok=True)
        threads = collect_discussion_links(d, slug, args.max_pages)
        items = list(threads.values())[: args.max_items]
        print(f"Scraping {len(items)} discussion threads...")
        out = []
        for i, t in enumerate(items, 1):
            try:
                rec = scrape_one(d, t["url"])
                (raw / f"{t['id']}.html").write_text(rec["html"], encoding="utf-8")
                out.append({"id": t["id"], "url": rec["url"],
                            "title": rec["title"] or t["title"], "text": rec["text"]})
                print(f"  [{i}/{len(items)}] {rec['title'][:60]}")
            except WebDriverException as e:
                print(f"  [{i}/{len(items)}] FAILED {t['url']}: {e}")
            time.sleep(1)
        _write_md(slug, "kaggle-discussions.md", "Kaggle discussions (scraped)", out)
        (RAW_DIR / slug / "discussions.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"Wrote {len(out)} discussions.")
        return 0
    finally:
        if own:
            d.quit()


# ---------------- notebooks / code ----------------
def collect_code_links(d, slug: str, max_pages: int) -> dict:
    nbs = {}
    for sort in ("voteCount", "hotness"):
        for page in range(1, max_pages + 1):
            d.get(f"{BASE}/competitions/{slug}/code?sort={sort}&page={page}")
            try:
                WebDriverWait(d, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/code/"]')))
            except TimeoutException:
                break
            _scroll(d, rounds=4)
            before = len(nbs)
            for a in d.find_elements(By.CSS_SELECTOR, 'a[href*="/code/"]'):
                href = (a.get_attribute("href") or "").split("?")[0]
                m = re.match(r"https://www\.kaggle\.com/code/[^/]+/[^/]+$", href)
                if m and href not in nbs:
                    nbs[href] = {"url": href, "title": (a.text or "").strip()}
            if len(nbs) == before:
                break
    return nbs


def cmd_scrape_code(args, d=None) -> int:
    own = d is None
    if own:
        d = make_driver(headless=args.headless)
    try:
        if not is_logged_in(d):
            print("Not logged in. Run: python tools/kaggle_scraper.py login")
            return 2
        slug = args.slug
        raw = RAW_DIR / slug / "notebooks"
        raw.mkdir(parents=True, exist_ok=True)
        nbs = list(collect_code_links(d, slug, args.max_pages).values())[: args.max_items]
        print(f"Scraping {len(nbs)} notebooks...")
        out = []
        for i, n in enumerate(nbs, 1):
            try:
                rec = scrape_one(d, n["url"])
                slugname = re.sub(r"[^a-zA-Z0-9_-]", "_", n["url"].split("/code/")[-1])
                (raw / f"{slugname}.html").write_text(rec["html"], encoding="utf-8")
                out.append({"url": rec["url"], "title": rec["title"] or n["title"], "text": rec["text"]})
                print(f"  [{i}/{len(nbs)}] {rec['title'][:60]}")
            except WebDriverException as e:
                print(f"  [{i}/{len(nbs)}] FAILED {n['url']}: {e}")
            time.sleep(1)
        _write_md(slug, "kaggle-notebooks.md", "Kaggle notebooks (scraped)", out)
        (RAW_DIR / slug / "notebooks.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"Wrote {len(out)} notebooks.")
        return 0
    finally:
        if own:
            d.quit()


def _write_md(slug: str, name: str, heading: str, items: list):
    ref = REPO / "competitions" / slug / "references"
    ref.mkdir(parents=True, exist_ok=True)
    lines = [f"# {heading}", "",
             f"Scraped via Selenium (logged-in session) on demand. {len(items)} items.", ""]
    for it in items:
        lines.append(f"## {it['title'] or '(untitled)'}")
        lines.append(f"- url: {it['url']}")
        lines.append("")
        body = (it.get("text") or "").strip()
        if len(body) > 12000:
            body = body[:12000] + "\n\n…[truncated — full HTML in .scrape/raw/]"
        lines.append(body)
        lines.append("\n---\n")
    (ref / name).write_text("\n".join(lines), encoding="utf-8")


# ---------------- cli ----------------
def main() -> int:
    p = argparse.ArgumentParser(description="Kaggle Selenium scraper")
    p.add_argument("command", choices=["login", "scrape", "scrape-discussions", "scrape-code"])
    p.add_argument("--slug", default=DEFAULT_SLUG)
    p.add_argument("--max-pages", type=int, default=10)
    p.add_argument("--max-items", type=int, default=40)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--login-timeout", type=int, default=900)
    args = p.parse_args()

    if args.command == "login":
        return cmd_login(args)
    if args.command == "scrape-discussions":
        return cmd_scrape_discussions(args)
    if args.command == "scrape-code":
        return cmd_scrape_code(args)
    if args.command == "scrape":
        d = make_driver(headless=args.headless)
        try:
            rc1 = cmd_scrape_discussions(args, d=d)
            rc2 = cmd_scrape_code(args, d=d)
            return rc1 or rc2
        finally:
            d.quit()
    return 1


if __name__ == "__main__":
    sys.exit(main())

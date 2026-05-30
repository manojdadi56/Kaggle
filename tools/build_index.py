"""Regenerate the master scraped-index.md from reference files."""
from pathlib import Path
import re

R = Path("competitions/nvidia-nemotron-model-reasoning-challenge/references")
SEP = "\n---\n\n"


def meta(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    title = t.split("\n", 1)[0].lstrip("# ").strip()
    m = re.search(r"\*\*source:\*\*\s*(\S+)", t)
    url = m.group(1) if m else ""
    i = t.find(SEP)
    body = len(t[i + len(SEP):].strip()) if i >= 0 else len(t)
    return title, url, body


lines = ["# Scraped competition references — master index", "",
         "Authenticated full-text capture (logged-in browser) + winner repo clone, "
         "2026-05-30. Re-runnable via tools/scrape_full.py, scrape_tabs.py, "
         "flatten_winner.py, pull_notebooks.py.", ""]

tabs = sorted(R.glob("tab-*.md"))
lines.append(f"## Competition tabs ({len(tabs)})")
for p in tabs:
    _, _, b = meta(p)
    lines.append(f"- [{p.name}]({p.name}) — {b} chars")

winner = [p for p in sorted(R.glob("winner-*.md"), key=lambda x: -meta(x)[2]) if p.name != "winner-INDEX.md"]
lines.append(f"\n## Winner solution source — tonghuikang/nemotron LB 0.85 ({len(winner)})")
lines.append("Pipeline map in winner-INDEX.md. Key: winner-train_sft.py.md (LORA_RANK=32), winner-reasoning.py.md (data engine).")
for p in winner:
    _, _, b = meta(p)
    lines.append(f"- [{p.name}]({p.name}) — {b} chars")

nb = sorted(R.glob("notebook-*.md"), key=lambda x: -meta(x)[2])
lines.append(f"\n## Community notebook source ({len(nb)})")
if not nb:
    lines.append("_None — Kaggle's Monaco viewer isn't browser-readable and the kernels API needs creds. Run tools/pull_notebooks.py after adding KAGGLE creds to .env. Notebook techniques are synthesized in community-sources.md / technique-backlog.md._")
for p in nb:
    t, u, b = meta(p)
    lines.append(f"- [{t[:64]}]({p.name}) — {u} ({b} chars)")

disc = sorted(R.glob("discussion-*.md"), key=lambda x: -meta(x)[2])
lines.append(f"\n## Discussion threads ({len(disc)})")
for p in disc:
    t, u, b = meta(p)
    lines.append(f"- [{t[:64]}]({p.name}) — {b} chars")

synth = [p for p in sorted(R.glob("*.md")) if p.name in
         ("DIGEST-community.md", "community-sources.md", "technique-backlog.md",
          "analysis-community.md", "analysis-data-and-scoring.md", "INDEX.md", "winner-INDEX.md")]
lines.append(f"\n## Synthesis / analysis ({len(synth)})")
for p in synth:
    lines.append(f"- [{p.name}]({p.name})")

(R / "scraped-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"index: {len(tabs)} tabs, {len(winner)} winner-src, {len(nb)} notebooks, {len(disc)} discussions, {len(synth)} synthesis")

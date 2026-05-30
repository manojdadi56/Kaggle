"""Flatten the winner's cloned repo TOP-LEVEL source into references/ as flat files.

Only top-level source (.py/.sh/.json/.md/.txt/.toml) — skips the thousands of
augmentations/*.txt and corpus data files. .gitignore excludes references/*/
subdirs, so each file becomes a top-level `winner-<name>.md` (code-fenced).
"""
import json
from pathlib import Path

SRC = Path(".scrape/winner")
OUT = Path("competitions/nvidia-nemotron-model-reasoning-challenge/references")
URL = "https://github.com/tonghuikang/nemotron"

LANG = {".py": "python", ".sh": "bash", ".json": "json", ".txt": "text",
        ".md": "markdown", ".toml": "toml"}
WANT = {".py", ".sh", ".json", ".md", ".txt", ".toml"}
SKIP = {"uv.lock", "LICENSE"}
written = []

for f in sorted(SRC.iterdir()):              # top-level only (no recursion)
    if not f.is_file() or f.suffix not in WANT or f.name in SKIP:
        continue
    raw = f.read_text(encoding="utf-8", errors="ignore")
    if len(raw) > 200_000:                    # guard against giant data files
        continue
    lang = LANG.get(f.suffix, "text")
    dest = OUT / f"winner-{f.name}.md"
    dest.write_text(
        f"# Winner solution — `{f.name}`\n\n"
        f"- **source repo:** {URL} (tonghuikang, Open Progress Prize, LB ~0.85)\n"
        f"- **file:** {f.name}\n- **chars:** {len(raw)}\n\n---\n\n```{lang}\n{raw}\n```\n",
        encoding="utf-8")
    written.append((dest.name, len(raw)))

idx = ["# Winner solution source (tonghuikang/nemotron) — index", "",
       f"Cloned from {URL} — Open Progress Prize winning solution (LB ~0.85). The real "
       "data-engine + training code. Pipeline: reasoning.py -> augmentation.py -> corpus.py "
       "-> train_sft.py -> upload_adapter.py (eval.py = local CV). The ~thousands of "
       "augmentations/*.txt generated examples are NOT vendored (regenerable from the code).", ""]
for name, n in sorted(written, key=lambda x: -x[1]):
    idx.append(f"- [{name}]({name}) — {n} chars")
(OUT / "winner-INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
print(f"wrote {len(written)} winner files + winner-INDEX.md")
for name, n in sorted(written, key=lambda x: -x[1]):
    print(f"  {n:7d}  {name}")

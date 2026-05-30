"""Filter scraped refs: drop nav-only/thin discussions, own/non-competition notebooks."""
from pathlib import Path

R = Path("competitions/nvidia-nemotron-model-reasoning-challenge/references")
SEP = "\n---\n\n"
OWN = ("manojdadi56__", "sai1881__")


def body_chars(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    i = t.find(SEP)
    return len(t[i + len(SEP):].strip()) if i >= 0 else len(t.strip())


removed = []
for p in sorted(R.glob("discussion-*.md")):
    if body_chars(p) < 500:
        removed.append(("disc-thin", p.name)); p.unlink()
for p in sorted(R.glob("notebook-*.md")):
    nm = p.name.replace("notebook-", "")
    if nm.startswith(OWN):
        removed.append(("nb-own", p.name)); p.unlink()
    elif body_chars(p) < 400:
        removed.append(("nb-thin", p.name)); p.unlink()

disc = sorted(R.glob("discussion-*.md"))
nb = sorted(R.glob("notebook-*.md"))
print(f"DISCUSSIONS kept: {len(disc)} | NOTEBOOKS kept: {len(nb)} | removed: {len(removed)}")
ds = sorted(body_chars(p) for p in disc)
if ds:
    print(f"discussion chars: min={ds[0]} med={ds[len(ds)//2]} max={ds[-1]} total={sum(ds)}")

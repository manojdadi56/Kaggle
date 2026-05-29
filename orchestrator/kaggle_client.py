"""Kaggle client — CLI wrappers (deterministic submit path) + kernels API.

`runner(cmd: list[str]) -> (returncode, stdout)` is injected so tests are offline.
Default shells the `kaggle` CLI (auth via KAGGLE_USERNAME/KAGGLE_KEY env).

Submit uses the file path: `kaggle competitions submit <comp> -f <file> -m <msg>`.
The kernels sub-API (push/status/output) feeds the kaggle_gpu executor.
"""
from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path
from typing import Callable

Runner = Callable[[list], tuple]


def _default_runner(cmd: list) -> tuple:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (("\n" + p.stderr) if p.returncode else "")


def _parse_csv(text: str) -> list[dict]:
    text = (text or "").strip()
    if not text or "," not in text:
        return []
    # skip any leading non-CSV warning lines; find the header row
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "date" in ln.lower() or "fileName" in ln or "ref" in ln.lower():
            text = "\n".join(lines[i:])
            break
    return list(csv.DictReader(io.StringIO(text)))


class KaggleKernelApi:
    """kaggle kernels push/status/output — used by the kaggle_gpu executor."""
    def __init__(self, runner: Runner = _default_runner):
        self.runner = runner

    def push(self, kernel_dir) -> str:
        rc, out = self.runner(["kaggle", "kernels", "push", "-p", str(kernel_dir)])
        if rc != 0:
            raise RuntimeError(f"kernels push failed: {out}")
        # output typically: "Your kernel was successfully pushed. ... ref: owner/slug"
        for tok in out.replace("\n", " ").split():
            if "/" in tok and not tok.startswith("http"):
                return tok
        return out.strip()

    def status(self, slug: str) -> str:
        rc, out = self.runner(["kaggle", "kernels", "status", slug])
        return out.strip().lower()

    def output(self, slug: str, dest) -> None:
        Path(dest).mkdir(parents=True, exist_ok=True)
        rc, out = self.runner(["kaggle", "kernels", "output", slug, "-p", str(dest)])
        if rc != 0:
            raise RuntimeError(f"kernels output failed: {out}")


class KaggleClient:
    def __init__(self, runner: Runner = _default_runner):
        self.runner = runner
        self.kernels = KaggleKernelApi(runner)

    def submit(self, competition: str, file: str, message: str) -> tuple:
        rc, out = self.runner([
            "kaggle", "competitions", "submit", competition,
            "-f", str(file), "-m", message,
        ])
        return rc, out

    def list_submissions(self, competition: str) -> list[dict]:
        rc, out = self.runner(["kaggle", "competitions", "submissions", competition, "--csv"])
        if rc != 0:
            return []
        return _parse_csv(out)

    def count_submissions_on(self, competition: str, day: str) -> int:
        """Count submissions whose date starts with `day` (YYYY-MM-DD)."""
        rows = self.list_submissions(competition)
        return sum(1 for r in rows if str(r.get("date", "")).startswith(day))

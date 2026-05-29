"""Concurrency control for parallel Jules sessions / GPU runs.

Two guards (REPORT §3, F-030/F-033):
  1. a global concurrency cap (Jules free tier = 3 concurrent), and
  2. per-area path-prefix locks so two in-flight tasks never touch overlapping
     file areas — the operator may only fan out *certified-independent* work.

State persists in `locks.json`:
  {"cap": int, "holders": {holder_id: {"area": str, "kind": str}}}
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from . import config


def _norm_segments(area: str) -> list[str]:
    """Normalize an area/path-glob to comparable segments.

    Strips trailing '/**', '/*', leading './', and splits on '/'.
    """
    a = (area or "").replace("\\", "/").strip().strip("/")
    for suffix in ("/**", "/*"):
        if a.endswith(suffix):
            a = a[: -len(suffix)]
    a = a.removeprefix("./")
    return [seg for seg in a.split("/") if seg and seg != "."]


def areas_overlap(a: str, b: str) -> bool:
    """True if path-areas conflict (one is an ancestor-or-equal of the other)."""
    sa, sb = _norm_segments(a), _norm_segments(b)
    if not sa or not sb:  # an empty/root area conflicts with everything
        return True
    n = min(len(sa), len(sb))
    return sa[:n] == sb[:n]


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


class LockManager:
    def __init__(self, locks_file: Path | None = None, cap: int = 3):
        self.locks_file = Path(locks_file) if locks_file else config.LOCKS_FILE
        self.cap = cap
        self.data = {"cap": cap, "holders": {}}
        self.load()

    def load(self) -> dict:
        if self.locks_file.exists():
            self.data = json.loads(self.locks_file.read_text(encoding="utf-8"))
            self.data.setdefault("holders", {})
            self.cap = self.data.get("cap", self.cap)
        else:
            self.data = {"cap": self.cap, "holders": {}}
        return self.data

    def _persist(self) -> None:
        self.data["cap"] = self.cap
        _atomic_write(self.locks_file, json.dumps(self.data, indent=2, sort_keys=True))

    def active_count(self) -> int:
        return len(self.data["holders"])

    def free_slots(self) -> int:
        return max(0, self.cap - self.active_count())

    def held_areas(self) -> list[str]:
        return [h["area"] for h in self.data["holders"].values()]

    def can_launch(self, holder_id: str, area: str) -> tuple[bool, str]:
        """Return (ok, reason). Checks cap + area independence."""
        if holder_id in self.data["holders"]:
            return False, "holder_already_active"
        if self.free_slots() <= 0:
            return False, "concurrency_cap_reached"
        for hid, h in self.data["holders"].items():
            if areas_overlap(area, h["area"]):
                return False, f"area_conflict_with:{hid}({h['area']})"
        return True, "ok"

    def acquire(self, holder_id: str, area: str, kind: str = "jules") -> bool:
        ok, _ = self.can_launch(holder_id, area)
        if not ok:
            return False
        self.data["holders"][holder_id] = {"area": area, "kind": kind}
        self._persist()
        return True

    def release(self, holder_id: str) -> bool:
        existed = self.data["holders"].pop(holder_id, None) is not None
        if existed:
            self._persist()
        return existed

"""Executor interface — the GPU/training backend abstraction.

Every backend implements the same 3-call contract so the operator can pick one
per run and even run several in parallel across backends:

    handle = ex.submit_run(spec)     # spec: {experiment_id, ...backend-specific}
    state  = ex.poll(handle)         # one of QUEUED/RUNNING/COMPLETED/FAILED
    result = ex.fetch(handle, dest)  # {adapter_dir, cv_score, logs}

Backends that aren't wired up yet raise NotConfigured from submit_run.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

QUEUED = "QUEUED"
RUNNING = "RUNNING"
COMPLETED = "COMPLETED"
FAILED = "FAILED"
TERMINAL = {COMPLETED, FAILED}


class NotConfigured(RuntimeError):
    """Raised when a backend is selected but its connection isn't configured."""


@dataclass
class RunHandle:
    backend: str
    experiment_id: str
    native_id: str | None = None      # e.g. kaggle kernel slug
    state: str = QUEUED
    meta: dict = field(default_factory=dict)


class Executor(ABC):
    name: str = "base"

    @abstractmethod
    def submit_run(self, spec: dict) -> RunHandle:
        ...

    @abstractmethod
    def poll(self, handle: RunHandle) -> str:
        ...

    @abstractmethod
    def fetch(self, handle: RunHandle, dest: Path) -> dict:
        ...

    # shared helper: read cv_score.json from a fetched output dir
    @staticmethod
    def read_cv_score(out_dir: Path) -> float | None:
        f = Path(out_dir) / "cv_score.json"
        if f.exists():
            try:
                return float(json.loads(f.read_text(encoding="utf-8")).get("cv_score"))
            except (ValueError, TypeError):
                return None
        return None

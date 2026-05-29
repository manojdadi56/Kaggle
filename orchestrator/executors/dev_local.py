"""Local dev/smoke backend (e.g. RTX 3050 4 GB).

For validating the training *script* on a tiny toy model — NOT the real 30B run.
Runs synchronously via an injected `runner(cmd, cwd) -> (returncode, stdout)`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .base import COMPLETED, FAILED, Executor, RunHandle


def _default_runner(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class DevLocalExecutor(Executor):
    name = "dev_local"

    def __init__(self, runner=_default_runner):
        self.runner = runner

    def submit_run(self, spec: dict) -> RunHandle:
        cmd = spec["train_cmd"]            # list[str]
        cwd = spec.get("cwd")
        out_dir = Path(spec["out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        rc, log = self.runner(cmd, cwd)
        state = COMPLETED if rc == 0 else FAILED
        return RunHandle(backend=self.name, experiment_id=spec["experiment_id"],
                         native_id=spec["experiment_id"], state=state,
                         meta={"out_dir": str(out_dir), "rc": rc, "log_tail": log[-2000:]})

    def poll(self, handle: RunHandle) -> str:
        return handle.state  # synchronous: already terminal after submit

    def fetch(self, handle: RunHandle, dest: Path) -> dict:
        out_dir = Path(handle.meta.get("out_dir", dest))
        adapter_dir = out_dir / "adapter"
        return {
            "adapter_dir": str(adapter_dir) if adapter_dir.exists() else None,
            "cv_score": self.read_cv_score(out_dir),
            "logs": handle.meta.get("log_tail", ""),
        }

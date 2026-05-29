"""Kaggle Notebooks GPU backend — push a kernel, poll status, pull output.

`kernel_api` is injected (the kaggle client's kernels interface) so this is
fully testable offline. It must expose:
    push(kernel_dir: Path) -> slug
    status(slug: str) -> str         # mapped to QUEUED/RUNNING/COMPLETED/FAILED
    output(slug: str, dest: Path) -> None
"""
from __future__ import annotations

from pathlib import Path

from .base import COMPLETED, FAILED, QUEUED, RUNNING, Executor, NotConfigured, RunHandle

_STATUS_MAP = {
    "queued": QUEUED, "running": RUNNING, "complete": COMPLETED,
    "completed": COMPLETED, "error": FAILED, "failed": FAILED, "cancelAcknowledged": FAILED,
}


class KaggleGpuExecutor(Executor):
    name = "kaggle_gpu"

    def __init__(self, kernel_api=None):
        self.kernel_api = kernel_api

    def _require(self):
        if self.kernel_api is None:
            raise NotConfigured("kaggle_gpu: kernel_api not configured (set KAGGLE_USERNAME/KAGGLE_KEY)")

    def submit_run(self, spec: dict) -> RunHandle:
        self._require()
        kernel_dir = Path(spec["kernel_dir"])
        slug = self.kernel_api.push(kernel_dir)
        return RunHandle(backend=self.name, experiment_id=spec["experiment_id"],
                         native_id=slug, state=QUEUED, meta={"kernel_dir": str(kernel_dir)})

    def poll(self, handle: RunHandle) -> str:
        self._require()
        raw = str(self.kernel_api.status(handle.native_id)).strip()
        handle.state = _STATUS_MAP.get(raw, _STATUS_MAP.get(raw.lower(), RUNNING))
        return handle.state

    def fetch(self, handle: RunHandle, dest: Path) -> dict:
        self._require()
        dest = Path(dest)
        dest.mkdir(parents=True, exist_ok=True)
        self.kernel_api.output(handle.native_id, dest)
        adapter_dir = dest / "adapter"
        return {
            "adapter_dir": str(adapter_dir) if adapter_dir.exists() else None,
            "cv_score": self.read_cv_score(dest),
            "logs": str(dest),
        }

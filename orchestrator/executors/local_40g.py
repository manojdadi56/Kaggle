"""Local 40 GB 2-GPU backend — PRIMARY trainer once configured.

Stub until the user shares the box details (Q-014): GPU models, per-GPU VRAM,
OS, and reach mechanism (SSH / a small job-runner agent). Wiring it in later =
fill these three methods; no orchestrator/loop changes needed.
"""
from __future__ import annotations

from pathlib import Path

from .base import Executor, NotConfigured, RunHandle


class Local40gExecutor(Executor):
    name = "local_40g"

    def __init__(self, endpoint=None):
        # endpoint: SSH target / job-runner client (None until configured)
        self.endpoint = endpoint

    def _require(self):
        if self.endpoint is None:
            raise NotConfigured(
                "local_40g: endpoint not configured yet — share GPU specs + reach "
                "mechanism (Q-014), then implement submit/poll/fetch against it."
            )

    def submit_run(self, spec: dict) -> RunHandle:
        self._require()
        # TODO: submit job to the 40 GB box via self.endpoint
        raise NotConfigured("local_40g: submit_run not implemented")

    def poll(self, handle: RunHandle) -> str:
        self._require()
        raise NotConfigured("local_40g: poll not implemented")

    def fetch(self, handle: RunHandle, dest: Path) -> dict:
        self._require()
        raise NotConfigured("local_40g: fetch not implemented")

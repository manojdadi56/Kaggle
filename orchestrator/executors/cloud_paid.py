"""Paid-cloud backend (RunPod / Lambda / Colab Pro) — upgrade path.

Stub until a provider is chosen + funded. Same interface as every backend.
"""
from __future__ import annotations

from pathlib import Path

from .base import Executor, NotConfigured, RunHandle


class CloudPaidExecutor(Executor):
    name = "cloud_paid"

    def __init__(self, provider=None, client=None):
        self.provider = provider
        self.client = client

    def _require(self):
        if self.client is None:
            raise NotConfigured("cloud_paid: provider/client not configured (choose RunPod/Lambda/Colab Pro)")

    def submit_run(self, spec: dict) -> RunHandle:
        self._require()
        raise NotConfigured("cloud_paid: submit_run not implemented")

    def poll(self, handle: RunHandle) -> str:
        self._require()
        raise NotConfigured("cloud_paid: poll not implemented")

    def fetch(self, handle: RunHandle, dest: Path) -> dict:
        self._require()
        raise NotConfigured("cloud_paid: fetch not implemented")

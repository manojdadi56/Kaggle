"""Executor registry — pick a training backend by key.

    ex = build_executor("kaggle_gpu", kernel_api=...)
    ex = build_executor("dev_local")

`local_40g` (primary, once configured) and `cloud_paid` are stubs that raise
NotConfigured until wired up — adding a backend = one module + one registry entry.
"""
from __future__ import annotations

from .base import COMPLETED, FAILED, QUEUED, RUNNING, TERMINAL, Executor, NotConfigured, RunHandle
from .cloud_paid import CloudPaidExecutor
from .dev_local import DevLocalExecutor
from .kaggle_gpu import KaggleGpuExecutor
from .local_40g import Local40gExecutor

REGISTRY = {
    "kaggle_gpu": KaggleGpuExecutor,
    "dev_local": DevLocalExecutor,
    "local_40g": Local40gExecutor,
    "cloud_paid": CloudPaidExecutor,
}

DEFAULT_BACKEND = "kaggle_gpu"


def available_backends() -> list[str]:
    return sorted(REGISTRY)


def build_executor(backend_key: str, **deps) -> Executor:
    if backend_key not in REGISTRY:
        raise KeyError(f"unknown backend '{backend_key}'; available: {available_backends()}")
    return REGISTRY[backend_key](**deps)


__all__ = [
    "REGISTRY", "DEFAULT_BACKEND", "build_executor", "available_backends",
    "Executor", "RunHandle", "NotConfigured",
    "QUEUED", "RUNNING", "COMPLETED", "FAILED", "TERMINAL",
]

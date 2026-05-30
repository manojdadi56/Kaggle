"""Monitoring: `python -m orchestrator.status` prints the current loop state."""
from __future__ import annotations

import sys

from . import config
from .locks import LockManager
from .state import StateStore


def summarize(state: dict, free_slots: int | None = None) -> dict:
    sessions = state.get("sessions", {})
    gpu = state.get("gpu_runs", {})
    today_counts = state.get("submit_counter", {})
    return {
        "active_competition": state.get("active_competition"),
        "updated_at": state.get("updated_at"),
        "in_flight_sessions": len(sessions),
        "sessions": {sid: s.get("state") for sid, s in sessions.items()},
        "in_flight_gpu_runs": len(gpu),
        "gpu_runs": {eid: g.get("state") for eid, g in gpu.items()},
        "best_cv": state.get("best_cv"),
        "best_cv_source": state.get("best_cv_source"),
        "submits_by_day": today_counts,
        "free_jules_slots": free_slots,
        "tasks_tracked": len(state.get("tasks", {})),
    }


def render(summary: dict) -> str:
    lines = ["=== Orchestrator status ==="]
    for k, v in summary.items():
        lines.append(f"{k:>22}: {v}")
    return "\n".join(lines)


def main() -> int:
    settings = config.Settings.load()
    store = StateStore(active_competition=settings.active_competition)
    locks = LockManager(cap=settings.concurrency_cap)
    summary = summarize(store.state, free_slots=locks.free_slots())
    print(render(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())

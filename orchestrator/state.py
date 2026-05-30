"""Event-sourced state store.

`events.jsonl` is append-only truth; `state.json` is a projection rebuildable
by replaying events. Every operation carries an `idempotency_key`; re-applying a
seen key is a silent no-op, so retries (poll re-fires, crashes) collapse cleanly.

A StatePatch is ``{"patch_id","tick_id","operations":[{op,idempotency_key,data,summary?}]}``.
The same pure projection function (`_apply_op`) is used for live apply and replay.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import config

SCHEMA_VERSION = 1

# Operations the projection understands. Each appends a matching event.
OPS = {
    "append_event",
    "record_session", "update_session", "clear_session",
    "record_gpu_run", "update_gpu_run", "clear_gpu_run",
    "set_task_status",
    "increment_submit_counter", "set_best_cv", "set_cursor",
    # --- ledger ops (R-004): planning/innovation auto-append work into ONE store ---
    "create_task", "create_hypothesis", "create_experiment",
    "create_suggestion", "create_decision", "add_metric",
    "set_status",          # generic status transition: data={collection, id, status}
    "update_entity",       # generic field merge: data={collection, id, ...fields}
}

# ledger collections (the "sheets") + the status vocabulary, ported from the SDLC workbook
LEDGER_COLLECTIONS = ("tasks", "hypotheses", "experiments", "suggestions", "decisions")
TASK_STATUSES = (
    "BACKLOG", "READY", "CLAIMED", "IN_PROGRESS", "SATURATED", "BLOCKED",
    "READY_FOR_REVIEW", "CHANGES_REQUESTED", "MERGED", "DONE", "SUPERSEDED",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_state(active_competition: str = "") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "active_competition": active_competition,
        "updated_at": None,
        "sessions": {},        # session_id -> {...}  (in-flight Jules)
        "gpu_runs": {},        # experiment_id -> {...} (in-flight training)
        # --- the single work ledger (planner/innovator auto-append here) ---
        "tasks": {},           # task_id -> {title,status,allowed_area,hypothesis,story,acceptance,dod,spec_path,...}
        "hypotheses": {},      # H-id -> {statement,status,expected_effect,source_refs,experiments:[]}
        "experiments": {},     # E-id -> {hypothesis,config,backend,cv_score,status,...}
        "suggestions": {},     # S-id -> {title,change_size,status,...}
        "decisions": {},       # D-id -> {entity,decision,rationale,...}
        "metrics": [],         # append-only [{name,value,unit,at}]
        "submit_counter": {},  # "YYYY-MM-DD" -> int
        "best_cv": None,
        "cursors": {},
    }


def _apply_op(state: dict, op: str, data: dict) -> None:
    """Pure projection: mutate `state` for one operation. Used by apply + replay."""
    if op == "append_event":
        return  # event-only; no projection change
    if op == "record_session":
        sid = data["session_id"]
        state["sessions"][sid] = {
            "task_id": data.get("task_id"),
            "state": data.get("state", "QUEUED"),
            "branch": data.get("branch"),
            "allowed_area": data.get("allowed_area"),
            "pr_url": data.get("pr_url"),
            "created_at": data.get("created_at"),
        }
    elif op == "update_session":
        sid = data["session_id"]
        state["sessions"].setdefault(sid, {}).update(
            {k: v for k, v in data.items() if k != "session_id"}
        )
    elif op == "clear_session":
        state["sessions"].pop(data["session_id"], None)
    elif op == "record_gpu_run":
        eid = data["experiment_id"]
        state["gpu_runs"][eid] = {
            "backend": data.get("backend"),
            "state": data.get("state", "QUEUED"),
            "cv_score": data.get("cv_score"),
            "created_at": data.get("created_at"),
        }
    elif op == "update_gpu_run":
        eid = data["experiment_id"]
        state["gpu_runs"].setdefault(eid, {}).update(
            {k: v for k, v in data.items() if k != "experiment_id"}
        )
    elif op == "clear_gpu_run":
        state["gpu_runs"].pop(data["experiment_id"], None)
    elif op == "set_task_status":
        tid = data["task_id"]
        entry = state["tasks"].setdefault(tid, {})
        entry["status"] = data["status"]
        if "allowed_area" in data:
            entry["allowed_area"] = data["allowed_area"]
    elif op == "increment_submit_counter":
        day = data["date"]
        state["submit_counter"][day] = state["submit_counter"].get(day, 0) + 1
    elif op == "set_best_cv":
        state["best_cv"] = data["score"]
    elif op == "set_cursor":
        state["cursors"][data["key"]] = data["value"]
    # --- ledger ops (R-004) ---
    elif op == "create_task":
        tid = data["id"]
        rec = {k: v for k, v in data.items() if k != "id"}
        rec.setdefault("status", "BACKLOG")
        state["tasks"][tid] = {**state["tasks"].get(tid, {}), **rec}
    elif op == "create_hypothesis":
        state["hypotheses"][data["id"]] = {
            **state["hypotheses"].get(data["id"], {}),
            **{k: v for k, v in data.items() if k != "id"},
        }
    elif op == "create_experiment":
        state["experiments"][data["id"]] = {
            **state["experiments"].get(data["id"], {}),
            **{k: v for k, v in data.items() if k != "id"},
        }
    elif op == "create_suggestion":
        state["suggestions"][data["id"]] = {
            **state["suggestions"].get(data["id"], {}),
            **{k: v for k, v in data.items() if k != "id"},
        }
    elif op == "create_decision":
        state["decisions"][data["id"]] = {
            **state["decisions"].get(data["id"], {}),
            **{k: v for k, v in data.items() if k != "id"},
        }
    elif op == "add_metric":
        state["metrics"].append({k: v for k, v in data.items()})
    elif op == "set_status":
        coll = state.setdefault(data["collection"], {})
        coll.setdefault(data["id"], {})["status"] = data["status"]
    elif op == "update_entity":
        coll = state.setdefault(data["collection"], {})
        coll.setdefault(data["id"], {}).update(
            {k: v for k, v in data.items() if k not in ("collection", "id")}
        )
    else:
        raise ValueError(f"unknown op: {op}")


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


class StateStore:
    def __init__(
        self,
        state_file: Path | None = None,
        events_file: Path | None = None,
        active_competition: str = "",
        now_fn: Callable[[], str] = _utc_now_iso,
    ):
        self.state_file = Path(state_file) if state_file else config.STATE_FILE
        self.events_file = Path(events_file) if events_file else config.EVENTS_FILE
        self.now_fn = now_fn
        self._active_competition = active_competition
        self.state = default_state(active_competition)
        self._seen: set[str] = set()
        self._event_count = 0
        self.load()

    # ---- persistence ----
    def load(self) -> dict:
        if self.state_file.exists():
            self.state = json.loads(self.state_file.read_text(encoding="utf-8"))
        elif self._active_competition:
            self.state.setdefault("active_competition", self._active_competition)
        self._seen.clear()
        self._event_count = 0
        if self.events_file.exists():
            for line in self.events_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                evt = json.loads(line)
                self._seen.add(evt["idempotency_key"])
                self._event_count += 1
        return self.state

    def _persist_state(self) -> None:
        self.state["updated_at"] = self.now_fn()
        _atomic_write(self.state_file, json.dumps(self.state, indent=2, sort_keys=True))

    def _append_event(self, evt: dict) -> None:
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(evt, sort_keys=True) + "\n")

    # ---- apply ----
    def apply_patch(self, patch: dict) -> dict:
        """Apply a StatePatch. Returns {applied:[keys], skipped:[keys]}."""
        applied, skipped = [], []
        ops = patch.get("operations", [])
        for op_obj in ops:
            op = op_obj["op"]
            key = op_obj["idempotency_key"]
            if op not in OPS:
                raise ValueError(f"unknown op: {op}")
            if key in self._seen:
                skipped.append(key)
                continue
            data = op_obj.get("data", {})
            _apply_op(self.state, op, data)
            self._event_count += 1
            evt = {
                "event_id": f"EVT-{self._event_count:06d}",
                "ts": self.now_fn(),
                "tick_id": patch.get("tick_id"),
                "patch_id": patch.get("patch_id"),
                "op": op,
                "idempotency_key": key,
                "summary": op_obj.get("summary", ""),
                "data": data,
            }
            self._append_event(evt)
            self._seen.add(key)
            applied.append(key)
        if applied:
            self._persist_state()
        return {"applied": applied, "skipped": skipped}

    # ---- replay / projection rebuild ----
    def rebuild_state_from_events(self) -> dict:
        """Drop the projection and re-derive it purely from events.jsonl."""
        state = default_state(self.state.get("active_competition", self._active_competition))
        if self.events_file.exists():
            for line in self.events_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                evt = json.loads(line)
                _apply_op(state, evt["op"], evt.get("data", {}))
        self.state = state
        self._persist_state()
        return state

    # ---- convenience reads ----
    def in_flight_sessions(self) -> dict:
        return dict(self.state["sessions"])

    def in_flight_gpu_runs(self) -> dict:
        return dict(self.state["gpu_runs"])

    def submits_today(self, day: str) -> int:
        return self.state["submit_counter"].get(day, 0)

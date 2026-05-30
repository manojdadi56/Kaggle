"""Owner-role dispatcher — turn READY ledger tasks into real Jules sessions.

Each tick the operator (or the goal-loop) calls `dispatch_ready()`: pull the top
N READY tasks from the ledger (oldest first within priority), acquire per-area
locks, render the deep-worker prompt, create one Jules session per task, then
record record_session + set_status(IN_PROGRESS) into the ledger via a single
StatePatch. Free-slot count is `min(concurrency_cap - in_flight, daily_budget_left)`.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import config
from .jules_client import JulesClient, session_id_of


SLUG_PREFIX = "competitions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _render_prompt(template: str, task: dict, slug: str) -> str:
    return (template
            .replace("{{task_id}}", task["id"])
            .replace("{{title}}", task.get("title", task["id"]))
            .replace("{{goal}}", task.get("spec", task.get("title", "")))
            .replace("{{allowed_area}}", task.get("allowed_area", f"{SLUG_PREFIX}/{slug}/"))
            .replace("{{acceptance_criteria}}", task.get("acceptance_criteria", "See task spec; ensure the deliverable is complete and tests pass."))
            .replace("{{definition_of_done}}", task.get("definition_of_done", "Committed via one PR; tests green; acceptance criteria met."))
            .replace("{{slug}}", slug))


def select_ready(state: dict, n: int, locks) -> list[dict]:
    """Pick up to `n` READY tasks whose allowed_area is free of lock conflicts.

    Skips tasks that are BLOCKED, already IN_PROGRESS, or whose blocked_by parent
    isn't DONE/MERGED yet.
    """
    tasks = state.get("tasks", {})
    in_flight_task_ids = {s.get("task_id") for s in state.get("sessions", {}).values() if s.get("task_id")}
    out = []
    for tid, t in tasks.items():
        if t.get("status") != "READY":
            continue
        if tid in in_flight_task_ids:
            continue
        parent = t.get("blocked_by")
        if parent and tasks.get(parent, {}).get("status") not in ("DONE", "MERGED"):
            continue
        area = t.get("allowed_area") or ""
        ok, _ = locks.can_launch(tid, area)
        if not ok:
            continue
        out.append({**t, "id": tid})
        if len(out) >= n:
            break
    return out


def dispatch_ready(state_store, locks, jules: JulesClient, *,
                   slug: str, tick_id: str,
                   concurrency_cap: int, daily_budget_left: int,
                   prompt_template_path: Path | str | None = None,
                   starting_branch: str = "main") -> dict:
    """End-to-end owner-role dispatch. Returns summary {created:[...], skipped:[...]}."""
    free_slots = locks.free_slots()
    n = max(0, min(free_slots, daily_budget_left, concurrency_cap))
    if n == 0:
        return {"created": [], "skipped": [], "reason": "no free slots / budget"}

    tpl_path = Path(prompt_template_path) if prompt_template_path else (config.PROMPTS_DIR / "jules_deep_worker.md")
    template = tpl_path.read_text(encoding="utf-8")

    picks = select_ready(state_store.state, n, locks)
    created, skipped = [], []
    ops = []
    for task in picks:
        tid = task["id"]
        prompt = _render_prompt(template, task, slug)
        sess = jules.create_session(prompt=prompt, title=f"{tid} — {task.get('title','')}",
                                    starting_branch=starting_branch)
        sid = session_id_of(sess.get("id") or sess.get("name", ""))
        if not sid:
            skipped.append({"task_id": tid, "reason": "no session id returned"})
            continue
        locks.acquire(tid, task.get("allowed_area") or "", kind="jules")
        created.append({"task_id": tid, "session_id": sid, "title": task.get("title")})
        ops += [
            {"op": "record_session", "idempotency_key": f"{tick_id}:{sid}:create",
             "data": {"session_id": sid, "task_id": tid,
                      "allowed_area": task.get("allowed_area"),
                      "branch": starting_branch, "state": "QUEUED",
                      "created_at": _now()}},
            {"op": "set_status", "idempotency_key": f"{tick_id}:{tid}:inprogress",
             "data": {"collection": "tasks", "id": tid, "status": "IN_PROGRESS"}},
            {"op": "update_entity", "idempotency_key": f"{tick_id}:{tid}:session_link",
             "data": {"collection": "tasks", "id": tid, "session_id": sid,
                      "branch": starting_branch}},
        ]

    if ops:
        state_store.apply_patch({"tick_id": tick_id, "operations": ops})

    return {"created": created, "skipped": skipped, "free_slots_used": len(created)}


def promote_backlog(state_store, *, tick_id: str, max_promote: int) -> dict:
    """Promote up to N BACKLOG tasks to READY (oldest first, blocked-by aware).

    The planner role would normally do this; we expose a deterministic helper so
    the goal-loop can keep the ready queue topped between operator decisions.
    """
    tasks = state_store.state.get("tasks", {})
    ops = []
    promoted = []
    for tid, t in tasks.items():
        if len(promoted) >= max_promote:
            break
        if t.get("status") != "BACKLOG":
            continue
        parent = t.get("blocked_by")
        if parent and tasks.get(parent, {}).get("status") not in ("DONE", "MERGED"):
            continue
        ops.append({"op": "set_status", "idempotency_key": f"{tick_id}:{tid}:promote",
                    "data": {"collection": "tasks", "id": tid, "status": "READY"}})
        promoted.append(tid)
    if ops:
        state_store.apply_patch({"tick_id": tick_id, "operations": ops})
    return {"promoted": promoted}

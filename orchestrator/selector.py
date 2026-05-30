"""Role selector — ported from the SDLC skill's score_roles.py to the git-JSON ledger.

Each run, the operator calls this to pick exactly ONE feasible role/move from the
single work store (state.json), deterministically: feasibility gate → numeric
score → rank (tie-break alphabetically) → drop the previous role (no adjacent
repeat) unless overridden. No openpyxl, no Excel.
"""
from __future__ import annotations

ROLES = ["planner", "innovator", "owner", "reviewer", "validator", "reporter"]


def _by_status(coll: dict, *statuses) -> list:
    return [v for v in coll.values() if v.get("status") in statuses]


def feasibility(state: dict, free_slots: int = 0, open_prs: int = 0,
                concurrency_target: int = 5) -> dict:
    tasks = state.get("tasks", {})
    suggestions = state.get("suggestions", {})
    hypotheses = state.get("hypotheses", {})

    ready = _by_status(tasks, "READY")
    in_progress = _by_status(tasks, "IN_PROGRESS", "SATURATED", "CLAIMED")
    review_queue = _by_status(tasks, "READY_FOR_REVIEW")
    backlog = _by_status(tasks, "BACKLOG")
    blocked = _by_status(tasks, "BLOCKED")
    open_sugg = _by_status(suggestions, "PROPOSED", "VALIDATION_REQUIRED")
    need_validation = _by_status(suggestions, "VALIDATION_REQUIRED")
    open_hyp = _by_status(hypotheses, "proposed", "PROPOSED")
    reviewable = len(review_queue) + open_prs
    dispatchable = min(len(ready) + len(backlog), max(0, free_slots))

    return {
        "planner": {
            # plan when the ready queue can't fill the pool, or there's triage/blocked work
            "feasible": bool(open_sugg or blocked or (len(ready) + len(in_progress)) < concurrency_target),
            "score": 3 * len(open_sugg) + 2 * len(blocked)
                     + (4 if (len(ready) + len(in_progress)) < concurrency_target else 0)
                     + (2 if len(backlog) < concurrency_target else 0),
            "reason": f"{len(open_sugg)} suggestions, {len(blocked)} blocked, {len(ready)} ready, {len(backlog)} backlog",
        },
        "innovator": {
            "feasible": True,
            "score": 1 + (3 if len(open_hyp) < 3 else 0),
            "reason": f"{len(open_hyp)} open hypotheses (mine refs/results for more)",
        },
        "owner": {  # = dispatch Jules on ready tasks, up to free slots
            "feasible": dispatchable > 0,
            "score": 8 * dispatchable + 6 * len(in_progress),
            "reason": f"{dispatchable} dispatchable (ready+backlog vs {free_slots} free slots), {len(in_progress)} in progress",
        },
        "reviewer": {
            "feasible": reviewable > 0,
            "score": 7 * reviewable,
            "reason": f"{reviewable} awaiting review (PRs/tasks)",
        },
        "validator": {
            "feasible": bool(need_validation),
            "score": 5 * len(need_validation),
            "reason": f"{len(need_validation)} suggestions awaiting validation",
        },
        "reporter": {
            "feasible": True,
            "score": 0,
            "reason": "fallback when nothing else fits",
        },
    }


def select(state: dict, free_slots: int = 0, open_prs: int = 0,
           previous_role: str | None = None, override: str | None = None,
           concurrency_target: int = 5) -> dict:
    feas = feasibility(state, free_slots, open_prs, concurrency_target)
    candidates, rejected = [], []
    for role in ROLES:
        info = feas[role]
        if override and role != override:
            rejected.append({"role": role, "reason": "override_excluded"}); continue
        if not info["feasible"]:
            rejected.append({"role": role, "reason": f"infeasible: {info['reason']}"}); continue
        if not override and previous_role and role == previous_role and role not in ("owner", "reviewer"):
            rejected.append({"role": role, "reason": "adjacent_repeat"}); continue
        candidates.append({"role": role, "score": info["score"], "reason": info["reason"]})
    candidates.sort(key=lambda x: (-x["score"], x["role"]))
    return {
        "ranked": candidates,
        "rejected": rejected,
        "selected": candidates[0]["role"] if candidates else "reporter",
        "selected_reason": candidates[0]["reason"] if candidates else "no feasible role",
    }

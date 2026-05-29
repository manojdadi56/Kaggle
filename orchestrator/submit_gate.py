"""Submission gate — the operator may auto-submit only when it's safe.

Rules (REPORT §4.3): submit only if the candidate beats the current best local
CV AND today's auto-submit count is below the (live, never hard-coded) cap.
Otherwise queue for human approval.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SubmitVerdict:
    action: str   # "submit" | "queue"
    reason: str


def decide_submit(cv_score, best_cv, submits_today: int, cap: int) -> SubmitVerdict:
    if cv_score is None:
        return SubmitVerdict("queue", "no CV score for candidate")
    if best_cv is not None and cv_score <= best_cv:
        return SubmitVerdict("queue", f"CV {cv_score} does not beat best {best_cv}")
    if submits_today >= cap:
        return SubmitVerdict("queue", f"daily auto-submit cap reached ({submits_today}/{cap})")
    return SubmitVerdict("submit", f"CV {cv_score} beats best {best_cv}; budget {submits_today}/{cap}")

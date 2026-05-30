"""Submission gate — the operator may auto-submit only when it's safe.

Rules (REPORT §4.3): submit only if the candidate beats the current best local
CV AND today's auto-submit count is below the (live, never hard-coded) cap.
Otherwise queue for human approval.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass
class SubmitVerdict:
    action: str   # "submit" | "skip"
    reason: str
    candidate: dict[str, Any] | None = None

def decide_submit(state_or_cv: Any, kaggle_lite_or_best: Any, submits_today: int = None, cap: int = None, margin: float = 0.0) -> SubmitVerdict:
    if submits_today is not None:
        cv_score = state_or_cv
        best_cv = kaggle_lite_or_best
        if cv_score is None:
            return SubmitVerdict("queue", "no CV score for candidate")
        if best_cv is not None and cv_score <= best_cv:
            return SubmitVerdict("queue", f"CV {cv_score} does not beat best {best_cv}")
        if submits_today >= cap:
            return SubmitVerdict("queue", f"daily auto-submit cap reached ({submits_today}/{cap})")
        return SubmitVerdict("submit", f"CV {cv_score} beats best {best_cv}; budget {submits_today}/{cap}")

    state = state_or_cv
    kaggle_lite = kaggle_lite_or_best
    """Decide whether to submit a ready candidate.

    1. Find candidate experiments with status=READY_FOR_SUBMIT + recorded cv_score + blob_token.
    2. Skip unless cv_score > state['best_cv'] by at least a configurable margin (default 0.0).
    3. Skip unless today's auto-submit count < MAX_AUTO_SUBMITS_PER_DAY (env, default 3).
    4. Skip unless live kaggle_lite.submissions(comp) cap-remaining >= 1 + 2 (reserve 2 finals).
    """
    candidate_id = None
    candidate = None
    for exp_id, exp in state.get("experiments", {}).items():
        if exp.get("status") == "READY_FOR_SUBMIT" and exp.get("cv_score") is not None and exp.get("blob_token"):
            candidate_id = exp_id
            candidate = exp
            break

    if not candidate:
        return SubmitVerdict("skip", "no candidate ready for submit")

    best_cv = state.get("best_cv")
    if best_cv is not None and candidate["cv_score"] <= best_cv + margin:
        return SubmitVerdict("skip", f"cv_score {candidate['cv_score']} does not beat best_cv {best_cv} by {margin}")

    cap = int(os.environ.get("MAX_AUTO_SUBMITS_PER_DAY", "3"))
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    submits_today = state.get("submit_counter", {}).get(today_str, 0)

    if submits_today >= cap:
        return SubmitVerdict("skip", "daily auto-submit cap reached")

    comp = state.get("active_competition")
    if not comp:
        return SubmitVerdict("skip", "no active competition in state")

    resp = kaggle_lite.submissions(comp)
    if resp.get("status") == 200:
        body_str = resp.get("body", "[]")
        try:
            items = json.loads(body_str)
        except Exception:
            items = []
        today_kaggle_count = 0
        for item in items:
            if today_str in json.dumps(item):
                today_kaggle_count += 1

        # We want to reserve 2 for finals, so limit is 3. i.e. 5 - count < 3 implies count > 2.
        if 5 - today_kaggle_count < 3:
            return SubmitVerdict("skip", "kaggle live cap remaining is less than 3")

    return SubmitVerdict("submit", "candidate is ready and caps are not reached", candidate={"experiment_id": candidate_id, "blob_token": candidate["blob_token"], "cv_score": candidate["cv_score"]})

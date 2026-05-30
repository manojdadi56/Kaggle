import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from unittest.mock import patch, MagicMock

import pytest

from orchestrator.submit_gate import decide_submit

class FakeKaggleLite:
    def __init__(self, submissions_data, status=200):
        self.data = submissions_data
        self.status = status
    def submissions(self, comp):
        return {"status": self.status, "body": json.dumps(self.data)}

@pytest.fixture
def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def test_decide_submit_no_candidates():
    state = {"experiments": {}}
    verdict = decide_submit(state, FakeKaggleLite([]))
    assert verdict.action == "skip"
    assert "no candidate" in verdict.reason

def test_decide_submit_cv_not_better():
    state = {
        "best_cv": 0.8,
        "experiments": {
            "E-1": {"status": "READY_FOR_SUBMIT", "cv_score": 0.79, "blob_token": "abc"}
        }
    }
    verdict = decide_submit(state, FakeKaggleLite([]))
    assert verdict.action == "skip"
    assert "does not beat best_cv" in verdict.reason

@patch.dict(os.environ, {"MAX_AUTO_SUBMITS_PER_DAY": "3"})
def test_decide_submit_local_cap_reached(today_str):
    state = {
        "best_cv": 0.8,
        "submit_counter": {today_str: 3},
        "experiments": {
            "E-1": {"status": "READY_FOR_SUBMIT", "cv_score": 0.85, "blob_token": "abc"}
        }
    }
    verdict = decide_submit(state, FakeKaggleLite([]))
    assert verdict.action == "skip"
    assert "daily auto-submit cap reached" in verdict.reason

@patch.dict(os.environ, {"MAX_AUTO_SUBMITS_PER_DAY": "3"})
def test_decide_submit_kaggle_cap_reached(today_str):
    state = {
        "best_cv": 0.8,
        "active_competition": "test-comp",
        "submit_counter": {today_str: 0},
        "experiments": {
            "E-1": {"status": "READY_FOR_SUBMIT", "cv_score": 0.85, "blob_token": "abc"}
        }
    }
    # Simulate Kaggle having 3 submissions today -> 5 - 3 = 2 < 3 -> should skip
    kaggle = FakeKaggleLite([
        {"date": f"{today_str}T10:00:00"},
        {"date": f"{today_str}T11:00:00"},
        {"date": f"{today_str}T12:00:00"}
    ])
    verdict = decide_submit(state, kaggle)
    assert verdict.action == "skip"
    assert "kaggle live cap remaining is less than 3" in verdict.reason

@patch.dict(os.environ, {"MAX_AUTO_SUBMITS_PER_DAY": "3"})
def test_decide_submit_happy_path(today_str):
    state = {
        "best_cv": 0.8,
        "active_competition": "test-comp",
        "submit_counter": {today_str: 0},
        "experiments": {
            "E-1": {"status": "READY_FOR_SUBMIT", "cv_score": 0.85, "blob_token": "abc"}
        }
    }
    # Simulate Kaggle having 1 submission today -> 5 - 1 = 4 >= 3 -> should submit
    kaggle = FakeKaggleLite([
        {"date": f"{today_str}T10:00:00"}
    ])
    verdict = decide_submit(state, kaggle)
    assert verdict.action == "submit"
    assert verdict.candidate["experiment_id"] == "E-1"
    assert verdict.candidate["blob_token"] == "abc"
    assert verdict.candidate["cv_score"] == 0.85

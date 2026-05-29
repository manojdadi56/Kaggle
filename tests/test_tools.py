"""Operator toolkit CLI: context + schema-validated apply (offline)."""
import tempfile
from pathlib import Path

import pytest

from orchestrator.config import Settings
from orchestrator.locks import LockManager
from orchestrator.loop import Orchestrator
from orchestrator.state import StateStore
from orchestrator.tools import cmd_apply, cmd_context, cmd_status, _repo_slug


def _orch(tmp):
    comp = tmp / "comp"
    (comp / "tasks" / "todo").mkdir(parents=True)
    (comp / "plan.md").write_text("plan", encoding="utf-8")
    s = Settings(active_competition="nemotron", concurrency_cap=15)
    s.competition_dir = lambda slug=None: comp

    class FakeGit:
        def commit_all(self, m): return 0, "ok"

    return Orchestrator(
        state=StateStore(state_file=tmp / "s.json", events_file=tmp / "e.jsonl", active_competition="nemotron"),
        locks=LockManager(locks_file=tmp / "l.json", cap=15),
        jules=None, kaggle=None, operator=None, git=FakeGit(), settings=s, today_fn=lambda: "2026-05-30")


def test_repo_slug():
    assert _repo_slug("sources/github/manojdadi56/Kaggle") == "manojdadi56/Kaggle"


def test_cmd_context_returns_decision_context(tmp_path):
    orch = _orch(tmp_path)
    ctx = cmd_context(orch, "T1", poll=False)
    assert ctx["active_competition"] == "nemotron"
    assert ctx["free_slots"] == "15"
    assert "state_json" in ctx and "plan" in ctx


def test_cmd_status_shape(tmp_path):
    s = cmd_status(_orch(tmp_path))
    assert s["free_jules_slots"] == 15
    assert s["in_flight_sessions"] == 0


def test_cmd_apply_validates_and_applies(tmp_path):
    orch = _orch(tmp_path)
    decision = {
        "tick_id": "T1", "status": "complete", "summary": "set best cv",
        "state_patch": {"tick_id": "T1", "operations": [
            {"op": "set_best_cv", "idempotency_key": "T1:bestcv", "data": {"score": 0.5}}]},
    }
    out = cmd_apply(orch, decision)
    assert out["applied"]["applied"] == ["T1:bestcv"]
    assert orch.state.state["best_cv"] == 0.5


def test_cmd_apply_rejects_bad_decision(tmp_path):
    orch = _orch(tmp_path)
    bad = {"tick_id": "T1", "status": "explode", "summary": "x", "state_patch": {"operations": []}}
    with pytest.raises(ValueError):
        cmd_apply(orch, bad)

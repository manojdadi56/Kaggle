"""Operator: prompt rendering + schema-validated decisions (offline invoke)."""
import pytest

from orchestrator.operator import Operator, OperatorError


def _valid_decision(tick="T1"):
    return {
        "tick_id": tick, "status": "complete", "summary": "ok",
        "state_patch": {"tick_id": tick, "operations": [
            {"op": "set_cursor", "idempotency_key": f"{tick}:cursor:hb",
             "data": {"key": "last_heartbeat", "value": "2026-05-30T00:00:00Z"}}
        ]},
        "submit_action": {"action": "none", "reason": "nothing fresh"},
    }


def test_render_fills_placeholders():
    captured = {}
    def fake_invoke(prompt):
        captured["prompt"] = prompt
        return _valid_decision()
    op = Operator(invoke=fake_invoke)
    op.run_tick({
        "tick_id": "T1", "active_competition": "nemotron",
        "free_slots": "3", "submit_budget_left": "3",
        "state_json": {"a": 1}, "feedback": "none", "open_prs": [],
        "in_flight": {}, "plan": "baseline first", "todo_tasks": ["TASK-1.1"],
    })
    p = captured["prompt"]
    assert "nemotron" in p and "TASK-1.1" in p
    assert "{{tick_id}}" not in p  # placeholder was replaced


def test_run_tick_returns_valid_decision():
    op = Operator(invoke=lambda prompt: _valid_decision("T7"))
    d = op.run_tick({"tick_id": "T7"})
    assert d["status"] == "complete"
    assert d["state_patch"]["operations"][0]["op"] == "set_cursor"


def test_invalid_decision_raises():
    bad = {"tick_id": "T1", "status": "BOGUS", "summary": "x",
           "state_patch": {"operations": []}}
    op = Operator(invoke=lambda prompt: bad)
    with pytest.raises(OperatorError):
        op.run_tick({"tick_id": "T1"})

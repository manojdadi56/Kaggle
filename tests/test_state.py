"""Event-sourced state: idempotency, projections, replay, persistence."""
import itertools

import pytest

from orchestrator.state import StateStore


@pytest.fixture
def store(tmp_path):
    counter = itertools.count()
    # deterministic clock for stable assertions
    now = lambda: f"2026-05-30T00:00:{next(counter):02d}+00:00"
    return StateStore(
        state_file=tmp_path / "state.json",
        events_file=tmp_path / "events.jsonl",
        active_competition="nemotron",
        now_fn=now,
    )


def _patch(*ops, tick="T1"):
    return {"patch_id": f"P-{tick}", "tick_id": tick, "operations": list(ops)}


def op(name, idem, **data):
    return {"op": name, "idempotency_key": idem, "data": data}


def test_record_and_clear_session(store):
    store.apply_patch(_patch(
        op("record_session", "T1:s1:create", session_id="s1", task_id="TASK-1",
           branch="feat/x", allowed_area="competitions/nemotron/references", state="IN_PROGRESS"),
    ))
    assert "s1" in store.in_flight_sessions()
    assert store.state["sessions"]["s1"]["task_id"] == "TASK-1"

    store.apply_patch(_patch(op("update_session", "T2:s1:pr", session_id="s1",
                                state="COMPLETED", pr_url="http://pr/1"), tick="T2"))
    assert store.state["sessions"]["s1"]["pr_url"] == "http://pr/1"

    store.apply_patch(_patch(op("clear_session", "T3:s1:clear", session_id="s1"), tick="T3"))
    assert "s1" not in store.in_flight_sessions()


def test_idempotency_skips_duplicate_keys(store):
    p = _patch(op("increment_submit_counter", "T1:submit:2026-05-30", date="2026-05-30"))
    r1 = store.apply_patch(p)
    r2 = store.apply_patch(p)  # identical key
    assert r1["applied"] and not r1["skipped"]
    assert not r2["applied"] and r2["skipped"]
    assert store.submits_today("2026-05-30") == 1  # only counted once


def test_submit_counter_and_best_cv(store):
    store.apply_patch(_patch(
        op("increment_submit_counter", "k1", date="2026-05-30"),
        op("increment_submit_counter", "k2", date="2026-05-30"),
        op("set_best_cv", "k3", score=0.71),
    ))
    assert store.submits_today("2026-05-30") == 2
    assert store.state["best_cv"] == 0.71


def test_task_status_and_cursor(store):
    store.apply_patch(_patch(
        op("set_task_status", "k1", task_id="TASK-1", status="IN_PROGRESS",
           allowed_area="references"),
        op("set_cursor", "k2", key="feedback_mtime", value=123.0),
    ))
    assert store.state["tasks"]["TASK-1"]["status"] == "IN_PROGRESS"
    assert store.state["cursors"]["feedback_mtime"] == 123.0


def test_replay_rebuilds_identical_projection(store):
    store.apply_patch(_patch(
        op("record_session", "k1", session_id="s1", task_id="T1", state="IN_PROGRESS"),
        op("increment_submit_counter", "k2", date="2026-05-30"),
        op("set_best_cv", "k3", score=0.5),
    ))
    before = store.state.copy()
    rebuilt = store.rebuild_state_from_events()
    assert rebuilt["sessions"] == before["sessions"]
    assert rebuilt["submit_counter"] == before["submit_counter"]
    assert rebuilt["best_cv"] == before["best_cv"]


def test_reload_recovers_seen_keys(tmp_path):
    sf, ef = tmp_path / "state.json", tmp_path / "events.jsonl"
    s1 = StateStore(state_file=sf, events_file=ef, active_competition="nemotron")
    s1.apply_patch(_patch(op("set_best_cv", "once", score=0.9)))
    # fresh instance over the same files
    s2 = StateStore(state_file=sf, events_file=ef, active_competition="nemotron")
    r = s2.apply_patch(_patch(op("set_best_cv", "once", score=0.1)))
    assert r["skipped"] == ["once"]
    assert s2.state["best_cv"] == 0.9  # unchanged


def test_unknown_op_raises(store):
    with pytest.raises(ValueError):
        store.apply_patch(_patch(op("nuke_everything", "k1")))

"""Owner-role dispatcher (offline)."""
from pathlib import Path

import pytest

from orchestrator.config import REPO_ROOT
from orchestrator.dispatcher import dispatch_ready, promote_backlog, select_ready
from orchestrator.locks import LockManager
from orchestrator.state import StateStore


class FakeJules:
    def __init__(self):
        self._n = 0
        self.calls = []

    def create_session(self, prompt, title="", starting_branch="main"):
        self._n += 1
        sid = f"sess{self._n}"
        self.calls.append({"sid": sid, "title": title, "prompt_head": prompt[:80]})
        return {"id": sid}


@pytest.fixture
def store(tmp_path):
    return StateStore(state_file=tmp_path / "s.json", events_file=tmp_path / "e.jsonl",
                      active_competition="nemotron")


@pytest.fixture
def locks(tmp_path):
    return LockManager(locks_file=tmp_path / "l.json", cap=5)


def _patch(*ops, tick="T0"):
    return {"tick_id": tick, "operations": list(ops)}


def op(opname, idem, **data):
    return {"op": opname, "idempotency_key": idem, "data": data}


def _seed_three_ready(store):
    store.apply_patch(_patch(
        op("create_task", "k1", id="T1", title="A", status="READY",
           allowed_area="comp/data/a", spec="do A"),
        op("create_task", "k2", id="T2", title="B", status="READY",
           allowed_area="comp/data/b", spec="do B"),
        op("create_task", "k3", id="T3", title="C", status="READY",
           allowed_area="comp/data/c", spec="do C"),
    ))


def test_select_ready_skips_blocked_by_unfinished_parent(store, locks):
    store.apply_patch(_patch(
        op("create_task", "k1", id="P", title="parent", status="READY",
           allowed_area="comp/p"),
        op("create_task", "k2", id="C", title="child", status="READY",
           allowed_area="comp/c", blocked_by="P"),
    ))
    out = select_ready(store.state, 5, locks)
    ids = [t["id"] for t in out]
    assert "P" in ids and "C" not in ids


def test_dispatch_creates_sessions_and_marks_in_progress(store, locks):
    _seed_three_ready(store)
    j = FakeJules()
    res = dispatch_ready(store, locks, j, slug="nemotron", tick_id="T1",
                         concurrency_cap=5, daily_budget_left=10,
                         prompt_template_path=REPO_ROOT / "prompts" / "jules_deep_worker.md")
    assert len(res["created"]) == 3
    assert locks.active_count() == 3
    for t in ("T1", "T2", "T3"):
        assert store.state["tasks"][t]["status"] == "IN_PROGRESS"
        assert "session_id" in store.state["tasks"][t]
    # session records carry task ids
    by_task = {s["task_id"] for s in store.state["sessions"].values()}
    assert by_task == {"T1", "T2", "T3"}


def test_dispatch_respects_free_slots_cap(store, locks):
    _seed_three_ready(store)
    locks.cap = 2
    j = FakeJules()
    res = dispatch_ready(store, locks, j, slug="nemotron", tick_id="T1",
                         concurrency_cap=2, daily_budget_left=10,
                         prompt_template_path=REPO_ROOT / "prompts" / "jules_deep_worker.md")
    assert len(res["created"]) == 2


def test_dispatch_respects_daily_budget(store, locks):
    _seed_three_ready(store)
    j = FakeJules()
    res = dispatch_ready(store, locks, j, slug="nemotron", tick_id="T1",
                         concurrency_cap=5, daily_budget_left=1,
                         prompt_template_path=REPO_ROOT / "prompts" / "jules_deep_worker.md")
    assert len(res["created"]) == 1


def test_dispatch_skips_already_in_flight(store, locks):
    _seed_three_ready(store)
    # mark T1 as already in flight (existing session pointing at it)
    store.apply_patch(_patch(
        op("record_session", "k4", session_id="existing", task_id="T1", state="IN_PROGRESS"),
        op("set_status", "k5", collection="tasks", id="T1", status="IN_PROGRESS"),
    ))
    j = FakeJules()
    res = dispatch_ready(store, locks, j, slug="nemotron", tick_id="T1",
                         concurrency_cap=5, daily_budget_left=10,
                         prompt_template_path=REPO_ROOT / "prompts" / "jules_deep_worker.md")
    ids = [c["task_id"] for c in res["created"]]
    assert "T1" not in ids and set(ids) == {"T2", "T3"}


def test_promote_backlog_respects_blocked_by(store):
    store.apply_patch(_patch(
        op("create_task", "k1", id="P", title="parent", status="BACKLOG",
           allowed_area="comp/p"),
        op("create_task", "k2", id="C", title="child", status="BACKLOG",
           allowed_area="comp/c", blocked_by="P"),
    ))
    res = promote_backlog(store, tick_id="T1", max_promote=5)
    assert res["promoted"] == ["P"]
    assert store.state["tasks"]["P"]["status"] == "READY"
    assert store.state["tasks"]["C"]["status"] == "BACKLOG"
    # finishing the parent unblocks the child
    store.apply_patch(_patch(op("set_status", "k3", collection="tasks", id="P", status="DONE"), tick="T2"))
    res2 = promote_backlog(store, tick_id="T3", max_promote=5)
    assert res2["promoted"] == ["C"]

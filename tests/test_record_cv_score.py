import os
import json
import tempfile
import pytest
from pathlib import Path
from orchestrator.state import StateStore, default_state
from orchestrator.loop import Orchestrator
from orchestrator.config import Settings
from orchestrator.status import summarize

def test_record_cv_score_strictly_better():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        store = StateStore(state_file=tdp / "state.json", events_file=tdp / "events.jsonl")
        store.state["best_cv"] = 0.50
        store.state["best_cv_source"] = "old-eid"

        op = {
            "op": "record_cv_score",
            "idempotency_key": "k1",
            "data": {
                "experiment_id": "new-eid",
                "cv_aggregate": 0.80,
                "per_category": {"cat1": 0.8},
                "n_total": 100,
                "n_correct": 80,
                "n_boxed_missing": 0,
                "source_kernel": "new-slug"
            }
        }

        store.apply_patch({"tick_id": "t1", "operations": [op]})

        assert store.state["best_cv"] == 0.80
        assert store.state["best_cv_source"] == "new-eid"
        assert store.state["metrics"]["cv:new-eid"]["cv_aggregate"] == 0.80

def test_record_cv_score_lower():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        store = StateStore(state_file=tdp / "state.json", events_file=tdp / "events.jsonl")
        store.state["best_cv"] = 0.80
        store.state["best_cv_source"] = "old-eid"

        op = {
            "op": "record_cv_score",
            "idempotency_key": "k2",
            "data": {
                "experiment_id": "new-eid2",
                "cv_aggregate": 0.40,
                "per_category": {"cat1": 0.4},
                "n_total": 100,
                "n_correct": 40,
                "n_boxed_missing": 0,
                "source_kernel": "new-slug"
            }
        }

        store.apply_patch({"tick_id": "t2", "operations": [op]})

        # best_cv should remain unchanged
        assert store.state["best_cv"] == 0.80
        assert store.state["best_cv_source"] == "old-eid"

        # but the metric should still be recorded
        assert store.state["metrics"]["cv:new-eid2"]["cv_aggregate"] == 0.40
        assert store.state["metrics"]["cv:new-eid2"]["per_category"] == {"cat1": 0.4}

def test_record_cv_score_per_category():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        store = StateStore(state_file=tdp / "state.json", events_file=tdp / "events.jsonl")
        op = {
            "op": "record_cv_score",
            "idempotency_key": "k3",
            "data": {
                "experiment_id": "eid3",
                "cv_aggregate": 0.90,
                "per_category": {"Math": 1.0, "Science": 0.8},
                "n_total": 10,
                "n_correct": 9,
                "n_boxed_missing": 1,
                "source_kernel": "slug3"
            }
        }

        store.apply_patch({"tick_id": "t3", "operations": [op]})
        assert store.state["best_cv"] == 0.90
        assert store.state["metrics"]["cv:eid3"]["per_category"] == {"Math": 1.0, "Science": 0.8}
        assert store.state["metrics"]["cv:eid3"]["n_boxed_missing"] == 1

class DummyOperator:
    def __init__(self, action):
        self.action = action
    def run_tick(self, ctx):
        return {"tick_id": ctx["tick_id"], **self.action}

class DummyGit:
    def commit_all(self, msg): pass

class DummyLocks:
    def can_launch(self, holder, area): return True, "ok"
    def acquire(self, holder, area, kind): pass
    def release(self, holder): pass
    def free_slots(self): return 1

class DummyJules:
    def create_session(self, **kwargs): return {"id": "S-001"}
    def get_session(self, sid): return {"id": "S-001", "state": "QUEUED"}

def test_gpu_dispatch_cv_score():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        os.environ["RUN_KERNEL_MOCK"] = "1"
        st = StateStore(state_file=tdp / "state.json", events_file=tdp / "events.jsonl")

        out_dir = tdp / "out"
        out_dir.mkdir(parents=True)
        cv_score_path = out_dir / "cv_score.json"
        cv_score_path.write_text(json.dumps({
            "cv_aggregate": 0.85,
            "per_category": {"Math": 0.85},
            "n_total": 100,
            "n_correct": 85,
            "n_boxed_missing": 0
        }), encoding="utf-8")

        loop = Orchestrator(
            state=st,
            locks=DummyLocks(),
            jules=DummyJules(),
            kaggle=None,
            operator=DummyOperator({"gpu_dispatch": [{
                "experiment_id": "E-999",
                "slug": "best-slug",
                "kernel_dir": str(tdp / "kernel"),
                "owner": "testuser",
                "out_dir": str(out_dir)
            }]}),
            git=DummyGit(),
            settings=Settings()
        )

        res = loop.run_tick("TICK-1")
        assert "best-slug" in res["summary"]["gpu_started"]

        import time
        time.sleep(1.0)

        loop.operator.action = {}
        res2 = loop.run_tick("TICK-2")

        # In RUN_KERNEL_MOCK mode, TICK-2 polls the process and creates a record_cv_score op.
        assert st.state["best_cv"] == 0.85
        assert st.state["best_cv_source"] == "E-999"

        summary = summarize(st.state)
        assert summary["best_cv"] == 0.85
        assert summary["best_cv_source"] == "E-999"

import os
import json
import tempfile
import pytest
from pathlib import Path
from orchestrator.state import StateStore
from orchestrator.loop import Orchestrator
from orchestrator.config import Settings

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

def test_gpu_dispatch_flow():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        os.environ["RUN_KERNEL_MOCK"] = "1"
        st = StateStore(state_file=tdp / "state.json", events_file=tdp / "events.jsonl")

        loop = Orchestrator(
            state=st,
            locks=DummyLocks(),
            jules=DummyJules(),
            kaggle=None,
            operator=DummyOperator({"gpu_dispatch": [{
                "experiment_id": "E-001",
                "slug": "test-slug",
                "kernel_dir": str(tdp / "kernel"),
                "owner": "testuser",
                "out_dir": str(tdp / "out")
            }]}),
            git=DummyGit(),
            settings=Settings()
        )

        # 1. Dispatch
        res = loop.run_tick("TICK-1")
        assert "test-slug" in res["summary"]["gpu_started"]
        runs = st.in_flight_gpu_runs()
        assert "test-slug" in runs
        assert runs["test-slug"]["state"] == "QUEUED"

        # Wait a bit for mock subprocess to complete
        import time
        time.sleep(1.0)

        # 2. Poll
        loop.operator.action = {}
        res2 = loop.run_tick("TICK-2")
        runs2 = st.in_flight_gpu_runs()
        assert runs2["test-slug"]["state"] == "COMPLETE"
        assert runs2["test-slug"].get("cv_score") == 0.50

"""Orchestrator tick loop — dispatch+locks, GPU packaging, submit gate (mocked)."""
import json
from pathlib import Path

import pytest

from orchestrator.config import Settings
from orchestrator.executors.base import COMPLETED, RunHandle
from orchestrator.loop import Orchestrator
from orchestrator.locks import LockManager
from orchestrator.state import StateStore


# ---- fakes ----
class FakeJules:
    def __init__(self):
        self.created = []
        self._n = 0

    def create_session(self, prompt, title="", starting_branch="main"):
        self._n += 1
        sid = f"s{self._n}"
        self.created.append({"sid": sid, "title": title})
        return {"id": sid}

    def get_session(self, sid):
        return {"name": f"sessions/{sid}", "state": "COMPLETED",
                "outputs": [{"pullRequest": {"url": f"https://github.com/pr/{sid}"}}]}


class FakeKaggle:
    def __init__(self):
        self.submits = []
        self.kernels = None

    def submit(self, comp, file, message):
        self.submits.append({"comp": comp, "file": file, "message": message})
        return 0, "Successfully submitted"


class FakeGit:
    def commit_all(self, message):
        return 0, "ok"


class FakeExecutor:
    name = "fake"

    def __init__(self, cv=0.7):
        self.cv = cv

    def submit_run(self, spec):
        return RunHandle(backend="fake", experiment_id=spec["experiment_id"], state=COMPLETED)

    def poll(self, handle):
        return handle.state

    def fetch(self, handle, dest):
        adir = Path(dest) / "adapter"
        adir.mkdir(parents=True, exist_ok=True)
        (adir / "adapter_config.json").write_text(json.dumps({"r": 16}), encoding="utf-8")
        (adir / "adapter_model.safetensors").write_bytes(b"\x00")
        return {"adapter_dir": str(adir), "cv_score": self.cv, "logs": ""}


class ScriptedOperator:
    def __init__(self, decision):
        self.decision = decision

    def run_tick(self, ctx):
        return dict(self.decision, tick_id=ctx["tick_id"])


@pytest.fixture
def orch(tmp_path):
    comp = tmp_path / "comp"
    (comp / "tasks" / "todo").mkdir(parents=True)
    (comp / "submissions" / "pending").mkdir(parents=True)
    (comp / "experiments").mkdir(parents=True)
    settings = Settings(active_competition="nemotron", max_auto_submits_per_day=3)
    settings.competition_dir = lambda slug=None: comp  # redirect to tmp
    state = StateStore(state_file=tmp_path / "state.json", events_file=tmp_path / "events.jsonl",
                       active_competition="nemotron")
    locks = LockManager(locks_file=tmp_path / "locks.json", cap=3)
    return Orchestrator(state=state, locks=locks, jules=FakeJules(), kaggle=FakeKaggle(),
                        operator=None, git=FakeGit(), settings=settings,
                        executor_factory=lambda key: FakeExecutor(), today_fn=lambda: "2026-05-30")


def test_dispatch_creates_session_and_holds_lock(orch):
    decision = {"tick_id": "T1", "status": "complete", "summary": "dispatch",
                "state_patch": {"operations": []},
                "jules_dispatch": [{"task_id": "TASK-1.1", "prompt": "do x",
                                    "allowed_area": "comp/references/winner.md"}]}
    summary = orch.apply_decision(decision)
    assert summary["sessions_created"] == ["s1"]
    assert orch.locks.active_count() == 1
    assert "s1" in orch.state.in_flight_sessions()


def test_parallel_dispatch_respects_area_locks(orch):
    decision = {"tick_id": "T1", "status": "complete", "summary": "two",
                "state_patch": {"operations": []},
                "jules_dispatch": [
                    {"task_id": "A", "prompt": "p", "allowed_area": "comp/references"},
                    {"task_id": "B", "prompt": "p", "allowed_area": "comp/references/winner.md"},  # overlaps A
                ]}
    summary = orch.apply_decision(decision)
    assert len(summary["sessions_created"]) == 1
    assert summary["skipped_dispatch"][0]["task_id"] == "B"


def test_poll_completes_session_and_releases_lock(orch):
    orch.apply_decision({"tick_id": "T1", "status": "complete", "summary": "d",
                         "state_patch": {"operations": []},
                         "jules_dispatch": [{"task_id": "TASK-1.1", "prompt": "x",
                                             "allowed_area": "comp/references/winner.md"}]})
    assert orch.locks.active_count() == 1
    changed = orch.poll_in_flight("T2")
    assert "s1" in changed["sessions_terminal"]
    assert orch.locks.active_count() == 0  # lock released on completion
    assert orch.state.state["sessions"]["s1"]["pr_url"].endswith("/s1")


def test_gpu_run_fetches_and_packages(orch):
    orch.apply_decision({"tick_id": "T1", "status": "complete", "summary": "gpu",
                         "state_patch": {"operations": []},
                         "gpu_dispatch": [{"experiment_id": "exp1", "backend": "fake",
                                           "spec": {"out_dir": "x"}}]})
    orch.poll_in_flight("T2")
    run = orch.state.in_flight_gpu_runs()["exp1"]
    assert run["cv_score"] == 0.7
    zip_path = orch.settings.competition_dir() / "submissions" / "pending" / "exp1.zip"
    assert zip_path.exists()


def test_submit_gate_blocks_then_allows(orch):
    # best_cv unset -> a fresh cv submits
    adapter_zip = orch.settings.competition_dir() / "submissions" / "pending" / "cand.zip"
    adapter_zip.write_bytes(b"zip")
    dec = {"tick_id": "T1", "status": "complete", "summary": "submit",
           "state_patch": {"operations": []},
           "submit_action": {"action": "submit", "file": str(adapter_zip), "cv_score": 0.66,
                             "message": "auto"}}
    out = orch.apply_decision(dec)
    assert out["submit"]["action"] == "submitted"
    assert orch.kaggle.submits[0]["comp"] == "nemotron"
    assert orch.state.submits_today("2026-05-30") == 1
    assert orch.state.state["best_cv"] == 0.66

    # a worse cv now queues (does not beat best)
    dec2 = {"tick_id": "T2", "status": "complete", "summary": "submit2",
            "state_patch": {"operations": []},
            "submit_action": {"action": "submit", "file": str(adapter_zip), "cv_score": 0.5}}
    out2 = orch.apply_decision(dec2)
    assert out2["submit"]["action"] == "queue"
    assert orch.state.submits_today("2026-05-30") == 1  # unchanged


def test_run_tick_end_to_end_with_scripted_operator(orch):
    orch.operator = ScriptedOperator({
        "status": "complete", "summary": "seed",
        "state_patch": {"operations": [
            {"op": "set_task_status", "idempotency_key": "seed:TASK-1.1:todo",
             "data": {"task_id": "TASK-1.1", "status": "READY"}}]},
        "jules_dispatch": [{"task_id": "TASK-1.1", "prompt": "analyze winner",
                            "allowed_area": "comp/references/winner.md"}],
        "submit_action": {"action": "none"},
    })
    res = orch.run_tick("T1")
    assert res["summary"]["sessions_created"] == ["s1"]
    assert orch.state.state["tasks"]["TASK-1.1"]["status"] in ("READY", "IN_PROGRESS")

"""Full mock end-to-end dry-run: `python -m orchestrator.dryrun`.

Drives the real Orchestrator across several ticks with ALL external services
faked (no network): dispatch a Jules analysis task -> session completes -> train
on a fake GPU backend -> package the adapter -> submit within budget. Exits 0 on
success, non-zero on any failure. This is the gate behind the build's promise.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from .config import Settings
from .executors.base import COMPLETED, RunHandle
from .loop import Orchestrator
from .locks import LockManager
from .state import StateStore


# ---- fakes (self-contained; no network) ----
class _FakeJules:
    def __init__(self):
        self._n = 0

    def create_session(self, prompt, title="", starting_branch="main"):
        self._n += 1
        return {"id": f"s{self._n}"}

    def get_session(self, sid):
        return {"name": f"sessions/{sid}", "state": "COMPLETED",
                "outputs": [{"pullRequest": {"url": f"https://github.com/manojdadi56/Kaggle/pull/{sid}"}}]}


class _FakeKaggle:
    def __init__(self):
        self.submits = []
        self.kernels = None

    def submit(self, comp, file, message):
        self.submits.append((comp, file, message))
        return 0, "Successfully submitted"


class _FakeGit:
    def __init__(self):
        self.commits = []

    def commit_all(self, message):
        self.commits.append(message)
        return 0, "ok"


class _FakeExecutor:
    def __init__(self, cv=0.71):
        self.cv = cv

    def submit_run(self, spec):
        return RunHandle(backend="fake", experiment_id=spec["experiment_id"], state=COMPLETED)

    def poll(self, handle):
        return handle.state

    def fetch(self, handle, dest):
        adir = Path(dest) / "adapter"
        adir.mkdir(parents=True, exist_ok=True)
        (adir / "adapter_config.json").write_text(json.dumps({"r": 16}), encoding="utf-8")
        (adir / "adapter_model.safetensors").write_bytes(b"\x00\x01")
        return {"adapter_dir": str(adir), "cv_score": self.cv, "logs": ""}


class _DryRunOperator:
    """Stateful: decides the next move from current state (mimics the real operator)."""
    def run_tick(self, ctx):
        st = ctx["state_json"]
        tick = ctx["tick_id"]
        base = {"tick_id": tick, "status": "complete", "summary": "",
                "state_patch": {"operations": []}, "submit_action": {"action": "none"}}
        sessions, gpu = st.get("sessions", {}), st.get("gpu_runs", {})

        if not sessions and not gpu and st.get("best_cv") is None:
            return {**base, "summary": "dispatch analysis",
                    "jules_dispatch": [{"task_id": "TASK-1.1", "prompt": "analyze winner",
                                        "allowed_area": "competitions/c/references/winner.md"}]}
        if any(s.get("state") == "COMPLETED" for s in sessions.values()) and not gpu:
            return {**base, "summary": "train baseline",
                    "gpu_dispatch": [{"experiment_id": "exp1", "backend": "fake", "spec": {}}]}
        done = [g for g in gpu.values() if g.get("state") == "COMPLETED" and g.get("zip")]
        if done and st.get("best_cv") is None:
            g = done[0]
            return {**base, "summary": "submit baseline",
                    "submit_action": {"action": "submit", "file": g["zip"],
                                      "cv_score": g.get("cv_score"), "message": "baseline"}}
        return {**base, "summary": "idle (nothing actionable)"}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="orch-dryrun-"))
    comp = tmp / "comp"
    (comp / "tasks" / "todo").mkdir(parents=True)
    (comp / "submissions" / "pending").mkdir(parents=True)
    (comp / "experiments").mkdir(parents=True)
    (comp / "plan.md").write_text("baseline-first plan", encoding="utf-8")

    settings = Settings(active_competition="nemotron", max_auto_submits_per_day=3)
    settings.competition_dir = lambda slug=None: comp
    kaggle = _FakeKaggle()
    orch = Orchestrator(
        state=StateStore(state_file=tmp / "state.json", events_file=tmp / "events.jsonl",
                         active_competition="nemotron"),
        locks=LockManager(locks_file=tmp / "locks.json", cap=3),
        jules=_FakeJules(), kaggle=kaggle, operator=_DryRunOperator(), git=_FakeGit(),
        settings=settings, executor_factory=lambda key: _FakeExecutor(),
        today_fn=lambda: "2026-05-30",
    )

    log = []
    for i in range(1, 6):
        res = orch.run_tick(f"RUN-{i:06d}")
        log.append((res["decision"]["summary"], res["summary"]))
        print(f"  tick {i}: {res['decision']['summary']}")

    # ---- assertions ----
    checks = {
        "a session was created": any("s1" == s for s in orch.state.state["sessions"]),
        "a GPU run completed": orch.state.state["gpu_runs"].get("exp1", {}).get("state") == "COMPLETED",
        "adapter packaged": (comp / "submissions" / "pending" / "exp1.zip").exists(),
        "exactly one submission": len(kaggle.submits) == 1,
        "best_cv recorded": orch.state.state.get("best_cv") == 0.71,
        "submit counted": orch.state.submits_today("2026-05-30") == 1,
        "events replayable": orch.state.rebuild_state_from_events().get("best_cv") == 0.71,
    }
    print("\nChecks:")
    ok = True
    for name, passed in checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed

    print("\nDRY-RUN PASS" if ok else "\nDRY-RUN FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

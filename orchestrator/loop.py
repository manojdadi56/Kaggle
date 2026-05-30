"""The orchestrator tick loop — wires every component together.

Per tick (REPORT §5):
  1. poll all in-flight Jules sessions + GPU runs; record terminal transitions,
     release locks.
  2. gather context → run the operator → get ONE decision.
  3. apply the decision: state_patch, dispatch parallel Jules sessions (within
     cap + per-area locks), start GPU runs, and submit-within-budget.
  4. git commit.

Every external dependency is injected, so the whole loop runs offline in
`dryrun`/tests with fakes. `run_forever` adds sleeping + fire triggers.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import config
from .executors import build_executor
from .jules_client import JulesClient, session_id_of
from .packaging import package_submission
from .submit_gate import decide_submit


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class Orchestrator:
    def __init__(self, *, state, locks, jules, kaggle, operator, git,
                 settings=None, executor_factory: Callable[[str], object] | None = None,
                 today_fn: Callable[[], str] = _utc_today, github=None):
        self.state = state
        self.locks = locks
        self.jules = jules
        self.kaggle = kaggle
        self.operator = operator
        self.git = git
        self.github = github  # GitHubOps (optional; enables PR listing + auto-merge)
        self.settings = settings or config.Settings()
        self.executor_factory = executor_factory or self._default_executor
        self.today_fn = today_fn
        self._gpu_handles: dict[str, object] = {}

    def _default_executor(self, key: str):
        if key == "kaggle_gpu":
            return build_executor(key, kernel_api=self.kaggle.kernels)
        return build_executor(key)

    # ---------- 1. poll ----------
    def poll_in_flight(self, tick_id: str) -> dict:
        changed = {"sessions_terminal": [], "gpu_terminal": [], "auto_merged": []}
        auto_merge_force = (getattr(self.settings, "operator_auto_merge", "force") == "force")
        for sid, sess in list(self.state.in_flight_sessions().items()):
            # Repopulate pool ownership so polling uses the right account's key.
            acc = sess.get("account_idx")
            if acc is not None and hasattr(self.jules, "register_owner"):
                self.jules.register_owner(sid, int(acc))
            remote = self.jules.get_session(sid)
            st = JulesClient.state_of(remote)
            pr_url = JulesClient.pr_url(remote)
            ops = [{"op": "update_session", "idempotency_key": f"{tick_id}:{sid}:state:{st}",
                    "data": {"session_id": sid, "state": st, "pr_url": pr_url}}]
            self.state.apply_patch({"tick_id": tick_id, "operations": ops})
            if JulesClient.is_terminal(remote):
                self.locks.release(sess.get("task_id") or sid)
                changed["sessions_terminal"].append(sid)
                # R-007 unsupervised: COMPLETED + PR open → auto-merge to main now.
                if (st == "COMPLETED" and pr_url and auto_merge_force and self.github is not None):
                    try:
                        number = int(pr_url.rstrip("/").rsplit("/", 1)[-1])
                    except ValueError:
                        number = None
                    if number is not None:
                        rc, mout = self.github.merge_pr(number, message=f"auto-merge {sid}", force=True)
                        ok = rc == 0
                        tid = sess.get("task_id")
                        post = [{"op": "append_event", "idempotency_key": f"{tick_id}:pr{number}:auto",
                                 "data": {"pr": number, "ok": ok, "reason": "unsupervised auto-merge",
                                          "detail": (mout or "")[:200]},
                                 "summary": f"auto-merge PR #{number}: {'ok' if ok else 'refused/failed'}"}]
                        if ok and tid:
                            post.append({"op": "set_status",
                                         "idempotency_key": f"{tick_id}:{tid}:DONE",
                                         "data": {"collection": "tasks", "id": tid, "status": "DONE"}})
                        self.state.apply_patch({"tick_id": tick_id, "operations": post})
                        changed["auto_merged"].append({"pr": number, "session": sid, "ok": ok})
        for eid, run in list(self.state.in_flight_gpu_runs().items()):
            handle = self._gpu_handles.get(eid)
            if handle is None:
                continue
            ex = self.executor_factory(run.get("backend"))
            st = ex.poll(handle)
            self.state.apply_patch({"tick_id": tick_id, "operations": [
                {"op": "update_gpu_run", "idempotency_key": f"{tick_id}:{eid}:gpu:{st}",
                 "data": {"experiment_id": eid, "state": st}}]})
            if st in ("COMPLETED", "FAILED"):
                changed["gpu_terminal"].append(eid)
                if st == "COMPLETED":
                    self._fetch_and_package(tick_id, ex, handle, eid)
        return changed

    def _fetch_and_package(self, tick_id, ex, handle, eid):
        comp_dir = self.settings.competition_dir()
        dest = comp_dir / "experiments" / eid
        result = ex.fetch(handle, dest)
        cv = result.get("cv_score")
        ops = [{"op": "update_gpu_run", "idempotency_key": f"{tick_id}:{eid}:cv",
                "data": {"experiment_id": eid, "cv_score": cv}}]
        if result.get("adapter_dir"):
            try:
                zip_path = comp_dir / "submissions" / "pending" / f"{eid}.zip"
                package_submission(result["adapter_dir"], zip_path)
                ops.append({"op": "update_gpu_run", "idempotency_key": f"{tick_id}:{eid}:zip",
                            "data": {"experiment_id": eid, "zip": str(zip_path)}})
            except ValueError as e:
                ops.append({"op": "append_event", "idempotency_key": f"{tick_id}:{eid}:badzip",
                            "data": {"error": str(e)}, "summary": "adapter failed validation"})
        self.state.apply_patch({"tick_id": tick_id, "operations": ops})

    # ---------- 2. context ----------
    def gather_context(self, tick_id: str, feedback: str = "", open_prs=None) -> dict:
        cap = self.settings.max_auto_submits_per_day
        used = self.state.submits_today(self.today_fn())
        if open_prs is None and self.github is not None:
            try:
                open_prs = self.github.list_open_prs()
            except Exception as e:  # network/list failure must not crash the tick
                open_prs = [{"error": f"could not list PRs: {e}"}]
        return {
            "tick_id": tick_id,
            "active_competition": self.settings.active_competition,
            "free_slots": str(self.locks.free_slots()),
            "submit_budget_left": str(max(0, cap - used)),
            "state_json": self.state.state,
            "feedback": feedback or "none",
            "open_prs": open_prs or [],
            "in_flight": {"sessions": self.state.in_flight_sessions(),
                          "gpu_runs": self.state.in_flight_gpu_runs()},
            "plan": self._read_plan(),
            "todo_tasks": self._list_todo(),
        }

    def _read_plan(self) -> str:
        p = self.settings.competition_dir() / "plan.md"
        return p.read_text(encoding="utf-8")[:4000] if p.exists() else "(no plan yet)"

    def _list_todo(self) -> list[str]:
        d = self.settings.competition_dir() / "tasks" / "todo"
        return sorted(f.stem for f in d.glob("*.md")) if d.exists() else []

    # ---------- 3. apply ----------
    def apply_decision(self, decision: dict) -> dict:
        tick_id = decision["tick_id"]
        summary = {"applied": None, "sessions_created": [], "gpu_started": [],
                   "submit": None, "skipped_dispatch": []}

        patch = decision.get("state_patch") or {"operations": []}
        patch.setdefault("tick_id", tick_id)
        summary["applied"] = self.state.apply_patch(patch)

        for d in decision.get("jules_dispatch", []) or []:
            holder = d["task_id"]
            area = d["allowed_area"]
            ok, reason = self.locks.can_launch(holder, area)
            if not ok:
                summary["skipped_dispatch"].append({"task_id": holder, "reason": reason})
                continue
            sess = self.jules.create_session(
                prompt=d["prompt"], title=d.get("title", holder),
                starting_branch=d.get("starting_branch", self.settings.starting_branch))
            sid = session_id_of(sess.get("id") or sess.get("name", ""))
            self.locks.acquire(holder, area, kind="jules")
            self.state.apply_patch({"tick_id": tick_id, "operations": [
                {"op": "record_session", "idempotency_key": f"{tick_id}:{sid}:create",
                 "data": {"session_id": sid, "task_id": holder, "allowed_area": area,
                          "state": "QUEUED", "branch": d.get("starting_branch")}},
                {"op": "set_task_status", "idempotency_key": f"{tick_id}:{holder}:inprogress",
                 "data": {"task_id": holder, "status": "IN_PROGRESS", "allowed_area": area}}]})
            summary["sessions_created"].append(sid)

        for g in decision.get("gpu_dispatch", []) or []:
            eid = g["experiment_id"]
            ex = self.executor_factory(g["backend"])
            spec = dict(g.get("spec", {})); spec.setdefault("experiment_id", eid)
            handle = ex.submit_run(spec)
            self._gpu_handles[eid] = handle
            self.state.apply_patch({"tick_id": tick_id, "operations": [
                {"op": "record_gpu_run", "idempotency_key": f"{tick_id}:{eid}:start",
                 "data": {"experiment_id": eid, "backend": g["backend"], "state": handle.state}}]})
            summary["gpu_started"].append(eid)

        summary["merged_prs"] = []
        for m in decision.get("pr_merges", []) or []:
            if self.github is None:
                summary["merged_prs"].append({"number": m["number"], "result": "no_github_ops"})
                continue
            rc, out = self.github.merge_pr(m["number"], message=m.get("reason"))
            ok = rc == 0
            self.state.apply_patch({"tick_id": tick_id, "operations": [
                {"op": "append_event", "idempotency_key": f"{tick_id}:pr{m['number']}:merge",
                 "data": {"pr": m["number"], "ok": ok, "reason": m.get("reason")},
                 "summary": f"merge PR #{m['number']}: {'ok' if ok else 'failed'}"}]})
            summary["merged_prs"].append({"number": m["number"], "ok": ok, "detail": out[:200]})

        sa = decision.get("submit_action") or {"action": "none"}
        if sa.get("action") == "submit":
            summary["submit"] = self._do_submit(tick_id, sa)

        self.git.commit_all(f"tick {tick_id}: {decision.get('summary', '')[:80]}")
        return summary

    def _do_submit(self, tick_id: str, sa: dict) -> dict:
        day = self.today_fn()
        cap = self.settings.max_auto_submits_per_day
        used = self.state.submits_today(day)
        verdict = decide_submit(sa.get("cv_score"), self.state.state.get("best_cv"), used, cap)
        if verdict.action != "submit":
            self._queue_pending(sa, verdict.reason)
            return {"action": "queue", "reason": verdict.reason}
        rc, out = self.kaggle.submit(self.settings.active_competition,
                                     sa["file"], sa.get("message", f"auto {tick_id}"))
        if rc != 0:
            self._queue_pending(sa, f"kaggle submit failed: {out[:200]}")
            return {"action": "queue", "reason": "submit_failed"}
        ops = [{"op": "increment_submit_counter", "idempotency_key": f"{tick_id}:submit:{day}",
                "data": {"date": day}}]
        if sa.get("cv_score") is not None:
            ops.append({"op": "set_best_cv", "idempotency_key": f"{tick_id}:bestcv:{sa['cv_score']}",
                        "data": {"score": sa["cv_score"]}})
        self.state.apply_patch({"tick_id": tick_id, "operations": ops})
        return {"action": "submitted", "cv_score": sa.get("cv_score")}

    def _queue_pending(self, sa: dict, reason: str) -> None:
        d = self.settings.competition_dir() / "submissions" / "pending"
        d.mkdir(parents=True, exist_ok=True)
        (d / "APPROVAL_NEEDED.md").write_text(
            f"# Pending submission\n\n- file: {sa.get('file')}\n- cv: {sa.get('cv_score')}\n- reason: {reason}\n",
            encoding="utf-8")

    # ---------- driver ----------
    def run_tick(self, tick_id: str, feedback: str = "", open_prs=None) -> dict:
        self.poll_in_flight(tick_id)
        ctx = self.gather_context(tick_id, feedback=feedback, open_prs=open_prs)
        decision = self.operator.run_tick(ctx)
        summary = self.apply_decision(decision)
        return {"decision": decision, "summary": summary}

    def run_forever(self, max_ticks: int | None = None, sleep_fn=time.sleep) -> None:  # pragma: no cover
        i = 0
        while max_ticks is None or i < max_ticks:
            i += 1
            self.run_tick(f"RUN-{i:06d}")
            sleep_fn(self.settings.poll_interval_s)

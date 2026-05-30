"""Operator toolkit CLI — the bridge the Claude Code operator drives each tick.

The OPERATOR is the Claude Code session (your subscription) — NOT an API key and
NOT a `claude -p` subprocess the Python spawns. Python here is a *toolkit*: it
gathers state and executes the operator's approved decision. A tick is:

    python -m orchestrator.tools context          # -> prints decision-context JSON
    # (the Claude Code operator reads it, decides, writes decision.json)
    python -m orchestrator.tools apply decision.json
    python -m orchestrator.tools status

`apply` validates the decision against operator_decision.schema.json, then runs
the mechanics (state patch, parallel Jules dispatch within cap+locks, GPU runs,
approved PR merges, budgeted submit, git commit).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from . import config
from .git_ops import GitOps
from .github_ops import GitHubOps
from .jules_client import JulesClient
from .kaggle_client import KaggleClient
from .locks import LockManager
from .loop import Orchestrator
from .state import StateStore
from .status import render, summarize

import os


def _repo_slug(source: str) -> str:
    # "sources/github/owner/repo" -> "owner/repo"
    parts = source.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else source


def build_orchestrator(settings: config.Settings | None = None) -> Orchestrator:
    s = settings or config.Settings.load()
    git = GitOps(config.REPO_ROOT)
    return Orchestrator(
        state=StateStore(active_competition=s.active_competition),
        locks=LockManager(cap=s.concurrency_cap),
        jules=JulesClient(api_key=os.environ.get("JULES_API_KEY", ""), source=s.jules_source),
        kaggle=KaggleClient(),
        operator=None,                      # the operator is the Claude Code session, not a subprocess
        git=git,
        github=GitHubOps(repo=_repo_slug(s.jules_source), git=git),
        settings=s,
    )


def _validator() -> Draft202012Validator:
    schema = json.loads((config.REPO_ROOT / "operator_decision.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


# ---- command logic (orchestrator injected, so tests run offline) ----
def cmd_context(orch: Orchestrator, tick_id: str, poll: bool = True) -> dict:
    if poll:
        orch.poll_in_flight(tick_id)
    ctx = orch.gather_context(tick_id)
    return ctx


def cmd_apply(orch: Orchestrator, decision: dict) -> dict:
    errors = sorted(_validator().iter_errors(decision), key=lambda e: list(e.path))
    if errors:
        raise ValueError("decision failed schema validation: " + "; ".join(e.message for e in errors[:5]))
    return orch.apply_decision(decision)


def cmd_status(orch: Orchestrator) -> dict:
    return summarize(orch.state.state, free_slots=orch.locks.free_slots())


def cmd_next(orch: Orchestrator) -> dict:
    """Role-select the next move from the ledger (like the SDLC router)."""
    from . import selector
    st = orch.state.state
    open_prs = len([s for s in st.get("sessions", {}).values() if s.get("pr_url")])
    prev = (st.get("cursors", {}) or {}).get("last_role")
    return selector.select(
        st, free_slots=orch.locks.free_slots(), open_prs=open_prs,
        previous_role=prev, concurrency_target=orch.settings.concurrency_cap,
    )


def cmd_dashboard(orch: Orchestrator):
    from . import dashboard
    return dashboard.build_dashboard(orch.state.state, dashboard.default_path())


def _parse_task_md(text: str, fallback_id: str) -> dict:
    import re
    rec = {"id": fallback_id, "status": "BACKLOG"}
    m = re.search(r"^#\s*(\S+)\s*[—-]\s*(.+)$", text, re.M)
    if m:
        rec["id"] = m.group(1).strip()
        rec["title"] = m.group(2).strip()
    for line in text.splitlines():
        fm = re.match(r"^-\s*([a-z_]+):\s*(.+)$", line.strip())
        if fm and fm.group(1) in ("status", "allowed_area", "hypothesis", "story", "actor", "gpu", "mode", "dependencies"):
            rec[fm.group(1)] = fm.group(2).strip()
    rec["status"] = "BACKLOG"  # ledger owns lifecycle from here
    return rec


def cmd_seed(orch: Orchestrator, tick: str = "SEED") -> dict:
    """Ingest competitions/<slug>/tasks/todo/*.md into ledger task rows (one-time)."""
    from pathlib import Path
    todo = orch.settings.competition_dir() / "tasks" / "todo"
    ops = []
    for f in sorted(Path(todo).glob("*.md")):
        rec = _parse_task_md(f.read_text(encoding="utf-8"), f.stem)
        rec["spec_path"] = str(f.relative_to(config.REPO_ROOT))
        ops.append({"op": "create_task", "idempotency_key": f"seed:{rec['id']}",
                    "data": rec, "summary": f"seed task {rec['id']}"})
    return orch.state.apply_patch({"tick_id": tick, "operations": ops})


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m orchestrator.tools {context|apply <file>|status} [--tick ID]")
        return 2
    cmd = argv[0]
    tick = "RUN-MANUAL"
    if "--tick" in argv:
        tick = argv[argv.index("--tick") + 1]
    orch = build_orchestrator()
    if cmd == "context":
        print(json.dumps(cmd_context(orch, tick), indent=2, default=str))
        return 0
    if cmd == "status":
        print(render(cmd_status(orch)))
        return 0
    if cmd == "next":
        print(json.dumps(cmd_next(orch), indent=2, default=str))
        return 0
    if cmd == "dashboard":
        p = cmd_dashboard(orch)
        print(f"dashboard written: {p}")
        return 0
    if cmd == "seed":
        print(json.dumps(cmd_seed(orch, tick), indent=2, default=str))
        return 0
    if cmd == "apply":
        if len(argv) < 2:
            print("apply needs a decision JSON file path")
            return 2
        decision = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        print(json.dumps(cmd_apply(orch, decision), indent=2, default=str))
        return 0
    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())

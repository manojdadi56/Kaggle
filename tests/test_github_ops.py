"""GitHub PR ops: list/diff (mock http) + merge via git (mock runner) + loop wiring."""
import json

from orchestrator.git_ops import GitOps
from orchestrator.github_ops import GitHubOps


class _Resp:
    def __init__(self, payload=None, text=""):
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


def test_list_open_prs_parses_api():
    def http(method, url, headers, accept="application/vnd.github+json"):
        assert "/pulls?state=open" in url
        return _Resp(payload=[
            {"number": 1, "title": "Feat A", "head": {"ref": "feat-a"},
             "body": "x", "html_url": "https://github.com/o/r/pull/1"},
            {"number": 2, "title": "Feat B", "head": {"ref": "feat-b"},
             "body": "y", "html_url": "https://github.com/o/r/pull/2"},
        ])
    gh = GitHubOps(repo="o/r", git=GitOps("."), http=http)
    prs = gh.list_open_prs()
    assert [p["number"] for p in prs] == [1, 2]
    assert prs[0]["branch"] == "feat-a"


def test_get_pr_diff_uses_diff_accept():
    seen = {}
    def http(method, url, headers, accept="application/vnd.github+json"):
        seen["accept"] = accept
        return _Resp(text="diff --git a/x b/x")
    gh = GitHubOps(repo="o/r", git=GitOps("."), http=http)
    assert gh.get_pr_diff(5).startswith("diff --git")
    assert seen["accept"] == "application/vnd.github.diff"


def test_merge_pr_runs_git_sequence():
    cmds = []
    def runner(cmd, cwd):
        cmds.append(cmd)
        return 0, "ok"
    gh = GitHubOps(repo="o/r", git=GitOps(".", runner=runner), http=lambda *a, **k: _Resp())
    rc, out = gh.merge_pr(7, message="looks good")
    assert rc == 0
    joined = [" ".join(c) for c in cmds]
    assert any("fetch origin pull/7/head:pr-7" in j for j in joined)
    assert any(j.startswith("git checkout main") for j in joined)
    assert any("merge" in j and "pr-7" in j for j in joined)
    assert any(j == "git push origin main" for j in joined)


def test_merge_pr_reports_conflict():
    def runner(cmd, cwd):
        if cmd[:2] == ["git", "merge"]:
            return 1, "CONFLICT"
        return 0, "ok"
    gh = GitHubOps(repo="o/r", git=GitOps(".", runner=runner), http=lambda *a, **k: _Resp())
    rc, out = gh.merge_pr(8)
    assert rc != 0 and "conflict" in out.lower()


def test_loop_executes_pr_merges():
    # minimal orchestrator wiring with a fake github
    from orchestrator.config import Settings
    from orchestrator.loop import Orchestrator
    from orchestrator.locks import LockManager
    from orchestrator.state import StateStore
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.mkdtemp())
    (tmp / "comp").mkdir()
    settings = Settings(active_competition="nemotron")
    settings.competition_dir = lambda slug=None: tmp / "comp"

    class FakeGitHub:
        def __init__(self): self.merged = []
        def merge_pr(self, number, message=None):
            self.merged.append(number); return 0, "Merged"

    class FakeGit:
        def commit_all(self, m): return 0, "ok"

    gh = FakeGitHub()
    orch = Orchestrator(
        state=StateStore(state_file=tmp / "s.json", events_file=tmp / "e.jsonl", active_competition="nemotron"),
        locks=LockManager(locks_file=tmp / "l.json", cap=15),
        jules=None, kaggle=None, operator=None, git=FakeGit(), github=gh, settings=settings)
    out = orch.apply_decision({
        "tick_id": "T1", "status": "complete", "summary": "merge approved PRs",
        "state_patch": {"operations": []},
        "pr_merges": [{"number": 1, "reason": "matches acceptance criteria"},
                      {"number": 2, "reason": "docs only"}],
    })
    assert gh.merged == [1, 2]
    assert all(m["ok"] for m in out["merged_prs"])

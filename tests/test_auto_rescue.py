import pytest
import subprocess
import tempfile
import pathlib
import os
import json
import re
import sys

from orchestrator.loop import Orchestrator
from orchestrator.state import StateStore
from orchestrator.locks import LockManager
from orchestrator.jules_client import JulesClient
from orchestrator.git_ops import GitOps
from orchestrator.github_ops import GitHubOps

class DummyJulesClient(JulesClient):
    def __init__(self, activities):
        super().__init__("fake-key")
        self._activities = activities
        self.owner = None
        self.sessions = {}

    def get_session(self, sid):
        return self.sessions.get(sid, {})

    def register_owner(self, sid, acc):
        self.owner = acc

    def list_activities(self, sid):
        return self._activities

@pytest.fixture
def temp_git_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    # Initialize a real git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    
    # Create an initial commit
    init_file = repo_dir / "main.py"
    init_file.write_text("def hello():\n    print('world')\n")
    subprocess.run(["git", "add", "main.py"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)
    
    # Ensure branch is main
    subprocess.run(["git", "branch", "-m", "main"], cwd=repo_dir, check=True)
    
    return repo_dir

@pytest.fixture
def setup_orchestrator(temp_git_repo, tmp_path, monkeypatch):
    state_file = tmp_path / "state.json"
    events_file = tmp_path / "events.jsonl"
    state = StateStore(state_file, events_file)
    locks = LockManager(tmp_path / "locks.json")
    
    # Add a session that is COMPLETED but has no pr_url
    sid = "sess-123"
    tid = "task-456"
    state.state["sessions"][sid] = {"session_id": sid, "task_id": tid, "state": "COMPLETED"}
    state.state["tasks"][tid] = {"task_id": tid, "status": "IN_PROGRESS"}
    
    jules = DummyJulesClient([])
    jules.sessions[sid] = {"state": "COMPLETED"}
    
    git = GitOps(temp_git_repo)
    github = GitHubOps("test/repo", git=git)
    
    orch = Orchestrator(
        state=state,
        locks=locks,
        jules=jules,
        kaggle=None,
        operator=None,
        git=git,
        github=github,
    )
    
    return orch, state, sid, jules, temp_git_repo

def test_auto_rescue_happy_path(setup_orchestrator, monkeypatch):
    orch, state, sid, jules, repo_dir = setup_orchestrator
    patch = """diff --git a/main.py b/main.py
index e69de29..7fbca62 100644
--- a/main.py
+++ b/main.py
@@ -1,2 +1,3 @@
 def hello():
     print('world')
+    print('rescued')
"""
    jules._activities = [{"sessionCompleted": {"artifact": {"changeSet": {"gitPatch": {"unidiffPatch": patch}}}}}]
    
    # Mock pytest to return 0
    import subprocess
    orig_run = subprocess.run
    class MockResult:
        returncode = 0
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: MockResult() if "pytest" in args[0] else orig_run(*args, **kwargs))
    
    changed = orch.poll_in_flight("tick-1")
    
    # Session state should be deleted
    assert sid not in state.state["sessions"]
    
    # The task should be DONE
    assert state.state["tasks"]["task-456"]["status"] == "DONE"
    
    # Repo should have the merged changes
    out = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=repo_dir).decode()
    assert f"rescue: task-456 from session {sid}" in out or "Merge" in out
    
    # Main branch should be updated
    content = (repo_dir / "main.py").read_text()
    assert "rescued" in content

def test_auto_rescue_pytest_fails(setup_orchestrator, monkeypatch):
    orch, state, sid, jules, repo_dir = setup_orchestrator
    patch = """diff --git a/main.py b/main.py
index e69de29..7fbca62 100644
--- a/main.py
+++ b/main.py
@@ -1,2 +1,3 @@
 def hello():
     print('world')
+    print('pytest fail')
"""
    jules._activities = [{"sessionCompleted": {"artifact": {"changeSet": {"gitPatch": {"unidiffPatch": patch}}}}}]
    
    # Mock pytest to return 1
    import subprocess
    orig_run = subprocess.run
    class MockResult:
        returncode = 1
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: MockResult() if "pytest" in args[0] else orig_run(*args, **kwargs))
    
    changed = orch.poll_in_flight("tick-2")
    
    # Session state should be FAILED
    assert state.state["sessions"][sid]["state"] == "FAILED"
    
    # Main branch should NOT have the changes
    content = (repo_dir / "main.py").read_text()
    assert "pytest fail" not in content
    
    # Check if a rescue branch exists
    branches = subprocess.check_output(["git", "branch"], cwd=repo_dir).decode()
    assert "operator-rescue" in branches

def test_auto_rescue_patch_fails(setup_orchestrator):
    orch, state, sid, jules, repo_dir = setup_orchestrator
    # Invalid patch (wrong context or file)
    patch = """diff --git a/nonexistent.py b/nonexistent.py
index e69de29..7fbca62 100644
--- a/nonexistent.py
+++ b/nonexistent.py
@@ -1,2 +1,3 @@
 def test():
     pass
+    print('fail')
"""
    jules._activities = [{"sessionCompleted": {"artifact": {"changeSet": {"gitPatch": {"unidiffPatch": patch}}}}}]
    
    changed = orch.poll_in_flight("tick-3")
    
    # Session state should be FAILED
    assert state.state["sessions"][sid]["state"] == "FAILED"
    
    # No new branches should be created or changes made
    branches = subprocess.check_output(["git", "branch"], cwd=repo_dir).decode()
    assert "operator-rescue" not in branches

def test_auto_rescue_no_artifact(setup_orchestrator):
    orch, state, sid, jules, repo_dir = setup_orchestrator
    # Empty activities (no unidiffPatch)
    jules._activities = []
    
    changed = orch.poll_in_flight("tick-4")
    
    assert state.state["sessions"][sid]["state"] == "FAILED"
    
    branches = subprocess.check_output(["git", "branch"], cwd=repo_dir).decode()
    assert "operator-rescue" not in branches

def test_auto_rescue_secret_leak(setup_orchestrator, monkeypatch):
    orch, state, sid, jules, repo_dir = setup_orchestrator
    patch = """diff --git a/main.py b/main.py
index e69de29..7fbca62 100644
--- a/main.py
+++ b/main.py
@@ -1,2 +1,3 @@
 def hello():
     print('world')
+    print('KGAT_123456789')
"""
    jules._activities = [{"sessionCompleted": {"artifact": {"changeSet": {"gitPatch": {"unidiffPatch": patch}}}}}]
    
    # Mock pytest to return 0
    import subprocess
    orig_run = subprocess.run
    class MockResult:
        returncode = 0
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: MockResult() if "pytest" in args[0] else orig_run(*args, **kwargs))
    
    changed = orch.poll_in_flight("tick-5")
    
    # Session state should be FAILED
    assert state.state["sessions"][sid]["state"] == "FAILED"
    
    # Main branch should NOT have the changes
    content = (repo_dir / "main.py").read_text()
    assert "KGAT_" not in content

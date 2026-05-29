"""Minimal git wrapper for the orchestrator's commit-after-tick state writes.

`runner(cmd, cwd) -> (returncode, stdout)` injected for offline tests.
Local operations only; the build never pushes.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

Runner = Callable[[list, object], tuple]


def _default_runner(cmd: list, cwd) -> tuple:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class GitOps:
    def __init__(self, repo_dir, runner: Runner = _default_runner):
        self.repo_dir = Path(repo_dir)
        self.runner = runner

    def _git(self, *args) -> tuple:
        return self.runner(["git", *args], self.repo_dir)

    def current_branch(self) -> str:
        _, out = self._git("rev-parse", "--abbrev-ref", "HEAD")
        return out.strip()

    def head_sha(self) -> str:
        _, out = self._git("rev-parse", "HEAD")
        return out.strip()

    def status_porcelain(self) -> str:
        _, out = self._git("status", "--porcelain")
        return out.strip()

    def list_branches(self) -> list[str]:
        _, out = self._git("branch", "--format=%(refname:short)")
        return [b.strip() for b in out.splitlines() if b.strip()]

    def add_all(self) -> int:
        rc, _ = self._git("add", "-A")
        return rc

    def commit_all(self, message: str) -> tuple:
        """Stage everything and commit. Returns (rc, stdout). No-op-safe."""
        self.add_all()
        if not self.status_porcelain():
            return 0, "nothing to commit"
        return self._git("commit", "-m", message)

    def checkout(self, branch: str, create: bool = False) -> tuple:
        return self._git("checkout", *(["-b"] if create else []), branch)

    def merge(self, branch: str, ff_only: bool = False) -> tuple:
        args = ["merge"] + (["--ff-only"] if ff_only else ["--no-edit"]) + [branch]
        return self._git(*args)

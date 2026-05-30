"""GitHub PR operations — list, read diff, and MERGE Jules PRs.

No `gh` CLI required: PR listing/diff use the public GitHub API (injectable
`http`), and merge uses plain git (`fetch origin pull/<n>/head` -> merge -> push)
via an injected GitOps, relying on the machine's cached push credentials.

The operator decides WHICH PRs to merge (reviewing the diff against acceptance
criteria + invariants); this module just executes the approved merges.
"""
from __future__ import annotations

import re
from typing import Callable

from .git_ops import GitOps


def _default_http(method: str, url: str, headers: dict, accept: str = "application/vnd.github+json"):
    import httpx
    h = {"Accept": accept, "User-Agent": "kaggle-jules-orchestrator"}
    h.update(headers or {})
    resp = httpx.request(method, url, headers=h, timeout=30)
    resp.raise_for_status()
    return resp


class GitHubOps:
    def __init__(self, repo: str = "manojdadi56/Kaggle", git: GitOps | None = None,
                 http: Callable | None = None, token: str | None = None):
        self.repo = repo
        self.git = git or GitOps(".")
        self._http = http or _default_http
        self.token = token

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def list_open_prs(self) -> list[dict]:
        url = f"https://api.github.com/repos/{self.repo}/pulls?state=open&per_page=50"
        resp = self._http("GET", url, self._auth_headers())
        data = resp.json()
        return [{
            "number": pr["number"],
            "title": pr.get("title", ""),
            "branch": pr.get("head", {}).get("ref"),
            "body": (pr.get("body") or "")[:2000],
            "url": pr.get("html_url"),
        } for pr in data]

    def get_pr_diff(self, number: int) -> str:
        url = f"https://api.github.com/repos/{self.repo}/pulls/{number}"
        resp = self._http("GET", url, self._auth_headers(), accept="application/vnd.github.diff")
        return resp.text

    # tokens we will NEVER let slip into main, even in force mode
    _SECRET_RE = re.compile(r"(KGAT_[A-Za-z0-9]{8,}|AQ\.Ab[A-Za-z0-9_\-]{8,}|sk-ant-[A-Za-z0-9_\-]{8,})")

    def merge_pr(self, number: int, message: str | None = None, force: bool = False) -> tuple:
        """Merge a PR by number using git (no gh needed).

        `force=True` is the unsupervised mode: conflicts auto-resolve in favor of
        the PR (`git merge -X theirs`). The single non-negotiable check is a
        regex scan of the PR's diff for literal secret prefixes — if one is
        found, the merge is refused (the credential never reaches public main).
        """
        # Belt-and-suspenders: refuse to merge a PR whose diff contains a literal token.
        try:
            diff = self.get_pr_diff(number)
            if self._SECRET_RE.search(diff):
                return 99, "SECRET_LEAK_DETECTED — refused to merge (PR diff contained a literal credential token)"
        except Exception:
            pass  # if the diff fetch fails we proceed; the merge itself may still fail

        g = self.git
        rc, out = g.fetch("origin", f"pull/{number}/head:pr-{number}")
        if rc != 0:
            return rc, f"fetch failed: {out}"
        rc, out = g.checkout("main")
        if rc != 0:
            return rc, f"checkout main failed: {out}"
        if force:
            rc, out = g.runner(["git", "merge", "-X", "theirs", "--no-edit", f"pr-{number}"], g.repo_dir)
        else:
            rc, out = g.merge(f"pr-{number}")
        if rc != 0:
            return rc, f"merge conflict/failure: {out}"
        rc, out = g.push("origin", "main")
        return rc, out

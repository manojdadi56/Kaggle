"""Jules REST client (worker trigger).

Verified contract (live): base `https://jules.googleapis.com/v1alpha`,
auth header `X-Goog-Api-Key`, source `sources/github/{owner}/{repo}`.
Create with AUTO_CREATE_PR + requirePlanApproval=false → fully autonomous.

The HTTP transport is injected (`http(method, url, headers, json) -> dict`)
so tests run offline. The default uses httpx (lazy-imported).
"""
from __future__ import annotations

from typing import Callable

# Session states (F-005)
QUEUED = "QUEUED"
PLANNING = "PLANNING"
AWAITING_PLAN_APPROVAL = "AWAITING_PLAN_APPROVAL"
AWAITING_USER_FEEDBACK = "AWAITING_USER_FEEDBACK"
IN_PROGRESS = "IN_PROGRESS"
PAUSED = "PAUSED"
FAILED = "FAILED"
COMPLETED = "COMPLETED"
TERMINAL_STATES = {COMPLETED, FAILED}


def _default_http(method: str, url: str, headers: dict, json: dict | None) -> dict:
    import httpx  # lazy: tests inject their own transport
    resp = httpx.request(method, url, headers=headers, json=json, timeout=60)
    resp.raise_for_status()
    return resp.json() if resp.content else {}


def session_id_of(name_or_id: str) -> str:
    """Normalize 'sessions/<id>' -> '<id>'."""
    return name_or_id.split("/", 1)[1] if name_or_id.startswith("sessions/") else name_or_id


class JulesClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://jules.googleapis.com/v1alpha",
        source: str = "sources/github/manojdadi56/Kaggle",
        http: Callable[..., dict] = _default_http,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.source = source
        self._http = http

    def _headers(self) -> dict:
        return {"X-Goog-Api-Key": self.api_key, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self._http(method, url, self._headers(), json)

    # ---- sources ----
    def list_sources(self) -> list[dict]:
        return self._request("GET", "sources").get("sources", [])

    # ---- sessions ----
    def create_session(
        self,
        prompt: str,
        title: str = "",
        starting_branch: str = "main",
        automation_mode: str = "AUTO_CREATE_PR",
        require_plan_approval: bool = False,
    ) -> dict:
        body = {
            "prompt": prompt,
            "title": title,
            "sourceContext": {
                "source": self.source,
                "githubRepoContext": {"startingBranch": starting_branch},
            },
            "automationMode": automation_mode,
            "requirePlanApproval": require_plan_approval,
        }
        return self._request("POST", "sessions", json=body)

    def get_session(self, session_id: str) -> dict:
        return self._request("GET", f"sessions/{session_id_of(session_id)}")

    def list_activities(self, session_id: str, created_after: str | None = None) -> list[dict]:
        path = f"sessions/{session_id_of(session_id)}/activities?pageSize=30"
        if created_after:
            path += f'&filter=createTime>"{created_after}"'
        return self._request("GET", path).get("activities", [])

    def send_message(self, session_id: str, prompt: str) -> dict:
        return self._request("POST", f"sessions/{session_id_of(session_id)}:sendMessage",
                             json={"prompt": prompt})

    def approve_plan(self, session_id: str) -> dict:
        return self._request("POST", f"sessions/{session_id_of(session_id)}:approvePlan", json={})

    # ---- helpers ----
    @staticmethod
    def state_of(session: dict) -> str:
        return session.get("state", QUEUED)

    @classmethod
    def is_terminal(cls, session: dict) -> bool:
        return cls.state_of(session) in TERMINAL_STATES

    @staticmethod
    def pr_url(session: dict) -> str | None:
        for out in session.get("outputs", []) or []:
            pr = out.get("pullRequest") or {}
            if pr.get("url"):
                return pr["url"]
        return None

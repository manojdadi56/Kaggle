"""Multi-account Jules worker pool (R-008).

Each Jules API key is a separate account with its own quota (15 concurrent /
100 day on Pro). The pool wraps multiple `JulesClient`s and:
 - round-robins `create_session` across the accounts (per-account quotas split
   the load),
 - records the originating account on each session,
 - routes `get_session` / `list_activities` / `send_message` / `approve_plan` to
   the correct account when polling/steering.

Backward compat: the pool exposes the same surface as a single `JulesClient` so
existing code (loop.poll_in_flight, dispatcher) keeps working.
"""
from __future__ import annotations

from .jules_client import JulesClient


class JulesPool:
    def __init__(self, clients: list[JulesClient]):
        if not clients:
            raise ValueError("JulesPool needs at least one JulesClient")
        self.clients = clients
        self._next = 0
        # session_id -> account_idx, set on create_session; used by polling
        self._owner: dict[str, int] = {}

    @property
    def source(self) -> str:
        return self.clients[0].source

    def __len__(self) -> int:
        return len(self.clients)

    def get(self, account_idx: int) -> JulesClient:
        return self.clients[int(account_idx) % len(self.clients)]

    def register_owner(self, session_id: str, account_idx: int) -> None:
        self._owner[session_id] = int(account_idx) % len(self.clients)

    def owner_of(self, session_id: str) -> int:
        # default to 0 if unknown (back-compat with pre-pool sessions)
        return self._owner.get(session_id, 0)

    # ---- pool-aware versions of JulesClient calls ----
    def create_session(self, prompt: str, title: str = "",
                       starting_branch: str = "main",
                       automation_mode: str = "AUTO_CREATE_PR",
                       require_plan_approval: bool = False,
                       account_idx: int | None = None) -> dict:
        """Pick an account (round-robin) and create a session on it."""
        idx = self._next % len(self.clients) if account_idx is None else int(account_idx) % len(self.clients)
        self._next += 1
        client = self.clients[idx]
        sess = client.create_session(prompt=prompt, title=title,
                                     starting_branch=starting_branch,
                                     automation_mode=automation_mode,
                                     require_plan_approval=require_plan_approval)
        sid = JulesClient_session_id(sess)
        if sid:
            self._owner[sid] = idx
        # surface the account so the dispatcher can persist it on the session record
        sess = dict(sess)
        sess["account_idx"] = idx
        return sess

    def get_session(self, session_id: str) -> dict:
        return self.get(self.owner_of(session_id)).get_session(session_id)

    def list_activities(self, session_id: str, created_after: str | None = None) -> list[dict]:
        return self.get(self.owner_of(session_id)).list_activities(session_id, created_after)

    def send_message(self, session_id: str, prompt: str) -> dict:
        return self.get(self.owner_of(session_id)).send_message(session_id, prompt)

    def approve_plan(self, session_id: str) -> dict:
        return self.get(self.owner_of(session_id)).approve_plan(session_id)


def JulesClient_session_id(sess: dict) -> str | None:
    sid = sess.get("id")
    if sid:
        return sid
    name = sess.get("name") or ""
    if name.startswith("sessions/"):
        return name.split("/", 1)[1]
    return None


def build_pool(api_keys: list[str], source: str,
               base_url: str = "https://jules.googleapis.com/v1alpha") -> JulesPool:
    clients = [JulesClient(api_key=k, base_url=base_url, source=source) for k in api_keys]
    return JulesPool(clients)

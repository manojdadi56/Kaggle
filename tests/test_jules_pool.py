"""JulesPool multi-account round-robin (R-008)."""
import pytest

from orchestrator.jules_client import JulesClient
from orchestrator.jules_pool import JulesPool, build_pool


class _RecordingClient(JulesClient):
    """JulesClient whose http transport records calls and returns canned data."""
    def __init__(self, key, label):
        super().__init__(api_key=key, http=self._fake)
        self.label = label
        self.calls = []

    def _fake(self, method, url, headers, json):
        self.calls.append({"label": self.label, "method": method, "url": url, "key": headers.get("X-Goog-Api-Key")})
        if method == "POST" and url.endswith("/sessions"):
            # session id is "<label>-<counter>"
            self._n = getattr(self, "_n", 0) + 1
            return {"name": f"sessions/{self.label}-{self._n}", "id": f"{self.label}-{self._n}"}
        if "/sessions/" in url and not url.endswith(":sendMessage"):
            sid = url.rsplit("/", 1)[-1]
            return {"name": f"sessions/{sid}", "state": "COMPLETED",
                    "outputs": [{"pullRequest": {"url": f"https://github.com/pr/{sid}"}}]}
        return {}


@pytest.fixture
def pool():
    a = _RecordingClient("KEY_A", "A")
    b = _RecordingClient("KEY_B", "B")
    return JulesPool([a, b])


def test_round_robin_create_session_alternates_accounts(pool):
    s1 = pool.create_session("p1", title="t1")
    s2 = pool.create_session("p2", title="t2")
    s3 = pool.create_session("p3", title="t3")
    s4 = pool.create_session("p4", title="t4")
    assert s1["account_idx"] == 0
    assert s2["account_idx"] == 1
    assert s3["account_idx"] == 0
    assert s4["account_idx"] == 1
    # 2 calls landed on each client
    assert sum(1 for c in pool.clients[0].calls if c["method"] == "POST") == 2
    assert sum(1 for c in pool.clients[1].calls if c["method"] == "POST") == 2


def test_owner_routing_for_get_session(pool):
    s1 = pool.create_session("p")
    sid = s1["id"]
    assert pool.owner_of(sid) == 0
    # polling routes back to account A
    pool.get_session(sid)
    last = pool.clients[0].calls[-1]
    assert last["method"] == "GET"
    assert last["key"] == "KEY_A"


def test_explicit_account_idx_overrides_round_robin(pool):
    s = pool.create_session("p", account_idx=1)
    assert s["account_idx"] == 1
    sid = s["id"]
    assert pool.owner_of(sid) == 1


def test_register_owner_for_externally_started_session(pool):
    pool.register_owner("ext-99", 1)
    assert pool.owner_of("ext-99") == 1


def test_owner_defaults_to_zero_for_unknown_session(pool):
    assert pool.owner_of("never-seen") == 0


def test_build_pool_helper_constructs_clients():
    p = build_pool(["k1", "k2", "k3"], source="sources/github/o/r")
    assert len(p) == 3
    assert p.source == "sources/github/o/r"
    assert p.clients[0].api_key == "k1"
    assert p.clients[2].api_key == "k3"


def test_pool_rejects_empty():
    with pytest.raises(ValueError):
        JulesPool([])

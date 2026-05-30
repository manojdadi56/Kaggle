"""Multi-account Kaggle pool helper — picks ACCT1 (sai1881) or ACCT2 (akhildadi).

When one account is exhausted (5/day submit cap, weekly GPU-hours, rate limit),
swap to the other. Both creds are read from .env (gitignored) and never logged.

Usage:
    from tools.kaggle_account_pool import for_account, list_accounts
    bearer = for_account(0)   # ACCT1 (sai1881) - primary
    bearer = for_account(1)   # ACCT2 (akhildadi) - fallback

    # Or auto-pick based on today's submit counts in state/state.json:
    idx, bearer, user = pick_account_with_headroom()
"""
from __future__ import annotations

import datetime as _dt
import json as _json
from pathlib import Path
from typing import Optional


REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"
STATE_PATH = REPO / "state" / "state.json"


def _load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def list_accounts() -> list[dict]:
    """Return all configured accounts: [{idx, username, has_token}, ...]."""
    env = _load_env()
    accounts: list[dict] = []
    for idx, (user_key, tok_key) in enumerate([
        ("KAGGLE_USERNAME", "KAGGLE_API_TOKEN"),
        ("KAGGLE_USERNAME_2", "KAGGLE_API_TOKEN_2"),
    ]):
        u = env.get(user_key)
        t = env.get(tok_key)
        if u and t:
            accounts.append({"idx": idx, "username": u, "has_token": True, "token_prefix": t[:14] + "..."})
    return accounts


def for_account(idx: int) -> tuple[str, str]:
    """Return (username, bearer_token) for account index 0 or 1."""
    env = _load_env()
    if idx == 0:
        u, t = env.get("KAGGLE_USERNAME"), env.get("KAGGLE_API_TOKEN")
    elif idx == 1:
        u, t = env.get("KAGGLE_USERNAME_2"), env.get("KAGGLE_API_TOKEN_2")
    else:
        raise ValueError(f"unknown account index {idx}; have 0 (sai1881) and 1 (akhildadi)")
    if not (u and t):
        raise RuntimeError(f"account {idx} not configured in {ENV_PATH}")
    return u, t


def _today_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).date().isoformat()


def _read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return _json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def submits_today(idx: int) -> int:
    """Read per-account daily submit count from state.

    Convention: state['submits_by_day_by_account'][YYYY-MM-DD][str(idx)] = int.
    """
    s = _read_state()
    return int(
        s.get("submits_by_day_by_account", {})
         .get(_today_iso(), {})
         .get(str(idx), 0)
    )


def pick_account_with_headroom(daily_cap: int = 5, reserve_finals: int = 2) -> tuple[int, str, str]:
    """Pick the first account whose today-submits < (daily_cap - reserve_finals).

    Returns (idx, username, bearer). Falls back to ACCT1 if both are exhausted.
    """
    threshold = daily_cap - reserve_finals  # default 3 auto-submits/day per account
    for idx in (0, 1):
        try:
            u, t = for_account(idx)
        except Exception:
            continue
        if submits_today(idx) < threshold:
            return idx, u, t
    # both exhausted: return ACCT1 anyway, caller decides
    u, t = for_account(0)
    return 0, u, t


if __name__ == "__main__":
    import json
    accts = list_accounts()
    print(json.dumps({"accounts": accts}, indent=2))
    if accts:
        idx, u, _ = pick_account_with_headroom()
        print(f"recommended_account: idx={idx} user={u} submits_today={submits_today(idx)}")

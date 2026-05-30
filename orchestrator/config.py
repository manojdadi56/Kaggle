"""Configuration: repo paths, settings, and a tiny .env loader (no extra deps)."""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = REPO_ROOT / "state"
PROMPTS_DIR = REPO_ROOT / "prompts"
COMPETITIONS_DIR = REPO_ROOT / "competitions"

STATE_FILE = STATE_DIR / "state.json"
EVENTS_FILE = STATE_DIR / "events.jsonl"
LOCKS_FILE = STATE_DIR / "locks.json"
RUN_LOG_FILE = STATE_DIR / "run_log.jsonl"


def load_env(path: Path | None = None) -> dict[str, str]:
    """Load KEY=VALUE lines from .env into os.environ (without overriding existing).

    Returns the parsed mapping. Lines starting with '#' or blank are ignored.
    Never raises if the file is missing.
    """
    path = path or (REPO_ROOT / ".env")
    parsed: dict[str, str] = {}
    if not path.exists():
        return parsed
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        parsed[key] = value
        os.environ.setdefault(key, value)
    return parsed


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    jules_base_url: str = "https://jules.googleapis.com/v1alpha"
    jules_source: str = "sources/github/manojdadi56/Kaggle"
    active_competition: str = "nvidia-nemotron-model-reasoning-challenge"
    poll_interval_s: int = 60
    heartbeat_s: int = 1800
    concurrency_cap: int = 3            # Jules free tier = 3 concurrent
    max_auto_submits_per_day: int = 3   # clamped to the live competition cap at runtime
    operator_model: str = "opus"
    operator_max_turns: int = 60
    starting_branch: str = "main"
    # R-007: unsupervised mode — every COMPLETED Jules PR auto-merges to main.
    # Set to "review" to restore acceptance-criteria review before merging.
    operator_auto_merge: str = "force"

    @classmethod
    def load(cls) -> "Settings":
        load_env()
        return cls(
            jules_base_url=os.environ.get("JULES_BASE_URL", cls.jules_base_url),
            jules_source=os.environ.get("JULES_SOURCE", cls.jules_source),
            active_competition=os.environ.get("ACTIVE_COMPETITION", cls.active_competition),
            poll_interval_s=_int_env("POLL_INTERVAL_S", cls.poll_interval_s),
            heartbeat_s=_int_env("HEARTBEAT_S", cls.heartbeat_s),
            concurrency_cap=_int_env("CONCURRENCY_CAP", cls.concurrency_cap),
            max_auto_submits_per_day=_int_env("MAX_AUTO_SUBMITS_PER_DAY", cls.max_auto_submits_per_day),
            operator_model=os.environ.get("OPERATOR_MODEL", cls.operator_model),
            starting_branch=os.environ.get("STARTING_BRANCH", cls.starting_branch),
            operator_auto_merge=os.environ.get("OPERATOR_AUTO_MERGE", cls.operator_auto_merge),
        )

    @staticmethod
    def jules_api_keys() -> list[str]:
        """All Jules API keys from .env, in account order (JULES_API_KEY, JULES_API_KEY_2, …).

        Each key is an independent account with its own quota; together they form the
        multi-account JulesPool (R-008).
        """
        keys = []
        primary = os.environ.get("JULES_API_KEY", "").strip()
        if primary:
            keys.append(primary)
        for i in range(2, 10):
            k = os.environ.get(f"JULES_API_KEY_{i}", "").strip()
            if k:
                keys.append(k)
        return keys

    def competition_dir(self, slug: str | None = None) -> Path:
        return COMPETITIONS_DIR / (slug or self.active_competition)

    def to_dict(self) -> dict:
        return asdict(self)

"""Scaffold sanity: package imports, key paths exist, settings load."""
from pathlib import Path

import orchestrator
from orchestrator import config


def test_package_version():
    assert orchestrator.__version__


def test_repo_paths_exist():
    assert config.REPO_ROOT.is_dir()
    assert config.STATE_DIR.is_dir()
    assert config.PROMPTS_DIR.is_dir()
    assert config.COMPETITIONS_DIR.is_dir()


def test_active_competition_folder_present():
    comp = config.COMPETITIONS_DIR / "nvidia-nemotron-model-reasoning-challenge"
    assert comp.is_dir()
    for sub in ("tasks/todo", "references", "experiments", "submissions/pending"):
        assert (comp / sub).is_dir(), sub


def test_settings_load_defaults():
    s = config.Settings.load()
    assert s.jules_base_url.endswith("/v1alpha")
    assert s.jules_source == "sources/github/manojdadi56/Kaggle"
    assert s.concurrency_cap >= 1
    assert s.max_auto_submits_per_day >= 1


def test_agents_md_has_invariants():
    text = (config.REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "rank ≤ 32" in text or "rank <= 32" in text
    assert "\\boxed" in text

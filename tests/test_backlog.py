"""The seeded backlog is well-formed and the parallel tasks are independent."""
import itertools
import re
from pathlib import Path

from orchestrator import config
from orchestrator.locks import areas_overlap

COMP = config.COMPETITIONS_DIR / "nvidia-nemotron-model-reasoning-challenge"
TODO = COMP / "tasks" / "todo"


def _fields(md: str) -> dict:
    out = {}
    for line in md.splitlines():
        m = re.match(r"^-\s*([a-z_]+):\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def test_plan_and_readme_present():
    assert (COMP / "plan.md").exists()
    assert (COMP / "README.md").exists()
    assert "baseline-first" in (COMP / "plan.md").read_text(encoding="utf-8").lower()


def test_all_user_stories_present():
    stories = {p.name.split("-")[0] + "-" + p.name.split("-")[1] for p in (COMP / "user-stories").glob("US-*.md")}
    assert {"US-1", "US-2", "US-3", "US-4", "US-5"} <= stories


def test_task_files_have_required_fields():
    files = list(TODO.glob("TASK-*.md"))
    assert len(files) >= 6
    for f in files:
        fields = _fields(f.read_text(encoding="utf-8"))
        for key in ("story", "actor", "status", "allowed_area", "gpu"):
            assert key in fields, f"{f.name} missing '{key}'"
        assert fields["actor"] in ("jules", "operator")
        assert fields["status"] == "todo"


def test_analysis_tasks_are_independent():
    areas = {}
    for tid in ("TASK-1.1", "TASK-1.2", "TASK-1.3"):
        f = next(TODO.glob(f"{tid}-*.md"))
        areas[tid] = _fields(f.read_text(encoding="utf-8"))["allowed_area"]
    # pairwise disjoint -> operator may dispatch them in parallel
    for a, b in itertools.combinations(areas.values(), 2):
        assert not areas_overlap(a, b), f"{a} overlaps {b}"

"""Concurrency cap + per-area path-prefix locks."""
import pytest

from orchestrator.locks import LockManager, areas_overlap


@pytest.mark.parametrize("a,b,expected", [
    ("competitions/c/references/winner.md", "competitions/c/references/winner.md", True),
    ("competitions/c/references", "competitions/c/references/winner.md", True),  # ancestor
    ("competitions/c/references/winner.md", "competitions/c/references/community.md", False),
    ("competitions/c/data", "competitions/c/references", False),
    ("competitions/c/**", "competitions/c/references", True),   # glob ancestor
    ("", "competitions/c/references", True),                     # root conflicts w/ all
])
def test_areas_overlap(a, b, expected):
    assert areas_overlap(a, b) is expected
    assert areas_overlap(b, a) is expected  # symmetric


@pytest.fixture
def lm(tmp_path):
    return LockManager(locks_file=tmp_path / "locks.json", cap=3)


def test_acquire_independent_areas_up_to_cap(lm):
    assert lm.acquire("s1", "competitions/c/references/winner.md")
    assert lm.acquire("s2", "competitions/c/references/community.md")
    assert lm.acquire("s3", "competitions/c/data")
    assert lm.active_count() == 3
    # cap reached
    ok, reason = lm.can_launch("s4", "competitions/c/eval")
    assert not ok and reason == "concurrency_cap_reached"


def test_area_conflict_blocks(lm):
    assert lm.acquire("s1", "competitions/c/references")
    ok, reason = lm.can_launch("s2", "competitions/c/references/winner.md")
    assert not ok and reason.startswith("area_conflict_with:s1")
    assert not lm.acquire("s2", "competitions/c/references/winner.md")


def test_release_frees_slot_and_area(lm):
    lm.acquire("s1", "competitions/c/references")
    assert lm.free_slots() == 2
    assert lm.release("s1")
    assert lm.free_slots() == 3
    # now the previously-conflicting area can be taken
    assert lm.acquire("s2", "competitions/c/references/winner.md")


def test_duplicate_holder_rejected(lm):
    assert lm.acquire("s1", "competitions/c/a")
    ok, reason = lm.can_launch("s1", "competitions/c/b")
    assert not ok and reason == "holder_already_active"


def test_persistence_roundtrip(tmp_path):
    f = tmp_path / "locks.json"
    lm1 = LockManager(locks_file=f, cap=2)
    lm1.acquire("s1", "competitions/c/x")
    lm2 = LockManager(locks_file=f, cap=2)
    assert lm2.active_count() == 1
    assert "s1" in lm2.data["holders"]

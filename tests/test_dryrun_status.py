"""The full mock dry-run passes, and status summarizes state."""
from orchestrator.dryrun import main as dryrun_main
from orchestrator.status import summarize


def test_dryrun_end_to_end_exits_zero():
    assert dryrun_main() == 0


def test_status_summarize_shapes():
    state = {
        "active_competition": "nemotron",
        "sessions": {"s1": {"state": "IN_PROGRESS"}},
        "gpu_runs": {"exp1": {"state": "COMPLETED"}},
        "best_cv": 0.71,
        "submit_counter": {"2026-05-30": 1},
        "tasks": {"TASK-1.1": {"status": "DONE"}},
    }
    s = summarize(state, free_slots=2)
    assert s["in_flight_sessions"] == 1
    assert s["in_flight_gpu_runs"] == 1
    assert s["best_cv"] == 0.71
    assert s["free_jules_slots"] == 2
    assert s["submits_by_day"]["2026-05-30"] == 1

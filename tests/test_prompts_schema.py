"""Prompts present + operator decision schema is valid and accepts a sample."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from orchestrator import config

ROOT = config.REPO_ROOT


def test_prompt_files_exist_with_surfaces():
    jw = (ROOT / "prompts" / "jules_worker.md").read_text(encoding="utf-8")
    assert "## Identity" in jw and "## Output contract" in jw and "NEEDS_INFO" in jw
    osys = (ROOT / "prompts" / "operator_system.md").read_text(encoding="utf-8")
    assert "Operator" in osys and "beat the current best" in osys.replace("\n", " ").lower() or "best local CV" in osys
    otick = (ROOT / "prompts" / "operator_tick.md").read_text(encoding="utf-8")
    assert "primary move" in otick.lower()


def test_decision_schema_is_valid():
    schema = json.loads((ROOT / "operator_decision.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)  # raises if the schema itself is invalid


def test_sample_decision_validates():
    schema = json.loads((ROOT / "operator_decision.schema.json").read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    sample = {
        "tick_id": "T1",
        "status": "complete",
        "summary": "Created analysis task and dispatched it.",
        "actions_taken": ["seeded backlog", "dispatched TASK-1.1"],
        "state_patch": {
            "tick_id": "T1",
            "operations": [
                {"op": "set_task_status", "idempotency_key": "T1:TASK-1.1:claim",
                 "data": {"task_id": "TASK-1.1", "status": "IN_PROGRESS",
                          "allowed_area": "competitions/x/references/analysis-winner.md"}}
            ],
        },
        "jules_dispatch": [
            {"task_id": "TASK-1.1", "title": "Analyze winner",
             "prompt": "Worker task...", "allowed_area": "competitions/x/references/analysis-winner.md",
             "starting_branch": "main"}
        ],
        "submit_action": {"action": "none", "reason": "no fresh adapter"},
    }
    assert list(v.iter_errors(sample)) == []


def test_bad_decision_is_rejected():
    schema = json.loads((ROOT / "operator_decision.schema.json").read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    bad = {"tick_id": "T1", "status": "explode", "summary": "x",
           "state_patch": {"operations": []}}  # invalid status enum
    assert list(v.iter_errors(bad))  # has errors

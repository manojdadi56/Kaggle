import pytest
import os
import pandas as pd

def test_master_roadmap_exists():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    assert os.path.exists(path), "master_roadmap.xlsx does not exist"

def test_master_roadmap_sheets():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    xls = pd.ExcelFile(path)
    expected_sheets = ["RankedExperiments", "NextWeekPlan", "CurrentNotebookGaps", "SubmissionStrategy"]
    for sheet in expected_sheets:
        assert sheet in xls.sheet_names, f"Missing sheet: {sheet}"

def test_master_roadmap_ranked_experiments_count():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    df = pd.read_excel(path, sheet_name="RankedExperiments")
    assert len(df) >= 15, f"Expected at least 15 ranked experiments, got {len(df)}"

def test_master_roadmap_next_week_plan_count():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    df = pd.read_excel(path, sheet_name="NextWeekPlan")
    assert len(df) >= 7, f"Expected at least 7 days in plan, got {len(df)}"
    assert 'day' in df.columns
    assert 'experiment' in df.columns
    assert 'who' in df.columns
    assert 'expected_outcome' in df.columns

def test_master_roadmap_gaps_count():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    df = pd.read_excel(path, sheet_name="CurrentNotebookGaps")
    assert len(df) >= 10, f"Expected at least 10 gap rows, got {len(df)}"

def test_master_roadmap_strategy_exists():
    path = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/master_roadmap.xlsx"
    df = pd.read_excel(path, sheet_name="SubmissionStrategy")
    assert len(df) > 0, "Submission strategy shouldn't be empty"

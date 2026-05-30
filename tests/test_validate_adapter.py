import os
import json
import subprocess
import pytest

SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "validate_adapter.py"))

def run_script(*args):
    cmd = ["python", SCRIPT_PATH] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_missing_files(tmp_path):
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()

    # Missing config entirely
    res = run_script("--adapter", str(adapter_dir), "--base", "dummy", "--mock")
    assert res.returncode == 1
    assert "CODE=MISSING_FILES" in res.stdout

    # Has config, missing model
    (adapter_dir / "adapter_config.json").write_text('{"r": 16}')
    res = run_script("--adapter", str(adapter_dir), "--base", "dummy", "--mock")
    assert res.returncode == 1
    assert "CODE=MISSING_FILES" in res.stdout

def test_rank_too_high(tmp_path):
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()

    (adapter_dir / "adapter_config.json").write_text('{"r": 64}')
    (adapter_dir / "adapter_model.safetensors").write_text('dummy')

    res = run_script("--adapter", str(adapter_dir), "--base", "dummy", "--mock")
    assert res.returncode == 1
    assert "CODE=RANK_TOO_HIGH" in res.stdout

def test_valid_mock(tmp_path, monkeypatch):
    # Change dir so validation_report.json goes to tmp_path
    monkeypatch.chdir(tmp_path)

    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()

    (adapter_dir / "adapter_config.json").write_text('{"r": 32}')
    (adapter_dir / "adapter_model.bin").write_text('dummy')

    res = run_script("--adapter", str(adapter_dir), "--base", "dummy", "--mock")
    assert res.returncode == 0
    assert "validation_report.json" in os.listdir(tmp_path)

    with open("validation_report.json") as f:
        report = json.load(f)

    assert report["ok"] is True
    assert report["rank"] == 32
    assert report["n_smoke"] == 5
    assert report["n_boxed_ok"] == 5

def test_check_boxed_logic():
    # We can test the parse logic by importing it
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))
    from validate_adapter import check_boxed

    assert check_boxed("The answer is \\boxed{42}") is True
    assert check_boxed("Nested \\boxed{42 + \\text{abc}}") is True
    assert check_boxed("Missing \\boxed{42") is False
    assert check_boxed("Wrong brace \\boxed(42)") is False
    assert check_boxed("Empty \\boxed{}") is True

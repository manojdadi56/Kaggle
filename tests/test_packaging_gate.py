"""Adapter packaging/validation + submit-gate logic."""
import json
import zipfile

import pytest

from orchestrator.packaging import package_submission, validate_adapter_config, MAX_LORA_RANK
from orchestrator.submit_gate import decide_submit


def _write_adapter(d, rank=16, with_weights=True):
    d.mkdir(parents=True, exist_ok=True)
    (d / "adapter_config.json").write_text(json.dumps({"r": rank, "base_model_name_or_path": "Nemotron"}), encoding="utf-8")
    if with_weights:
        (d / "adapter_model.safetensors").write_bytes(b"\x00\x01\x02")


def test_validate_ok(tmp_path):
    a = tmp_path / "adapter"; _write_adapter(a, rank=32)
    ok, reason = validate_adapter_config(a)
    assert ok and "rank=32" in reason


def test_validate_rejects_over_rank(tmp_path):
    a = tmp_path / "adapter"; _write_adapter(a, rank=MAX_LORA_RANK + 1)
    ok, reason = validate_adapter_config(a)
    assert not ok and "exceeds" in reason


def test_validate_missing_config(tmp_path):
    a = tmp_path / "adapter"; a.mkdir()
    ok, reason = validate_adapter_config(a)
    assert not ok and "missing" in reason


def test_package_builds_zip(tmp_path):
    a = tmp_path / "adapter"; _write_adapter(a, rank=8)
    z = package_submission(a, tmp_path / "out" / "submission.zip")
    assert z.exists()
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
    assert "adapter_config.json" in names
    assert "adapter_model.safetensors" in names


def test_package_refuses_over_rank(tmp_path):
    a = tmp_path / "adapter"; _write_adapter(a, rank=64)
    with pytest.raises(ValueError):
        package_submission(a, tmp_path / "submission.zip")


@pytest.mark.parametrize("cv,best,today,cap,expected", [
    (0.8, 0.7, 0, 3, "submit"),    # beats best, budget free
    (0.6, 0.7, 0, 3, "queue"),     # worse than best
    (0.9, None, 0, 3, "submit"),   # no best yet
    (0.9, 0.7, 3, 3, "queue"),     # cap reached
    (None, 0.7, 0, 3, "queue"),    # no cv
])
def test_decide_submit(cv, best, today, cap, expected):
    assert decide_submit(cv, best, today, cap).action == expected

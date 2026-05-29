"""Executor registry + backends (all offline via injected deps)."""
import json

import pytest

from orchestrator.executors import (
    COMPLETED, FAILED, NotConfigured, available_backends, build_executor,
)


def test_registry_lists_all_backends():
    assert set(available_backends()) == {"kaggle_gpu", "dev_local", "local_40g", "cloud_paid"}


def test_build_unknown_backend_raises():
    with pytest.raises(KeyError):
        build_executor("gpu_on_the_moon")


class FakeKernelApi:
    """Simulates kaggle kernels push/status/output without network."""
    def __init__(self, cv=0.62):
        self.cv = cv
        self._pushed = None

    def push(self, kernel_dir):
        self._pushed = str(kernel_dir)
        return "manojdadi56/nemotron-exp1"

    def status(self, slug):
        return "complete"

    def output(self, slug, dest):
        (dest / "adapter").mkdir(parents=True, exist_ok=True)
        (dest / "cv_score.json").write_text(json.dumps({"cv_score": self.cv}), encoding="utf-8")


def test_kaggle_gpu_submit_poll_fetch(tmp_path):
    ex = build_executor("kaggle_gpu", kernel_api=FakeKernelApi(cv=0.71))
    kdir = tmp_path / "kernel"; kdir.mkdir()
    h = ex.submit_run({"experiment_id": "exp1", "kernel_dir": kdir})
    assert h.native_id == "manojdadi56/nemotron-exp1"
    assert ex.poll(h) == COMPLETED
    res = ex.fetch(h, tmp_path / "out")
    assert res["cv_score"] == 0.71
    assert res["adapter_dir"] is not None


def test_kaggle_gpu_unconfigured_raises():
    ex = build_executor("kaggle_gpu")  # no kernel_api
    with pytest.raises(NotConfigured):
        ex.submit_run({"experiment_id": "x", "kernel_dir": "."})


def test_dev_local_success_and_failure(tmp_path):
    def good_runner(cmd, cwd):
        (tmp_path / "out").mkdir(parents=True, exist_ok=True)
        (tmp_path / "out" / "adapter").mkdir(parents=True, exist_ok=True)
        (tmp_path / "out" / "cv_score.json").write_text('{"cv_score": 0.3}', encoding="utf-8")
        return 0, "ok"

    ex = build_executor("dev_local", runner=good_runner)
    h = ex.submit_run({"experiment_id": "e", "train_cmd": ["python", "train.py"],
                       "out_dir": tmp_path / "out"})
    assert ex.poll(h) == COMPLETED
    assert ex.fetch(h, tmp_path / "out")["cv_score"] == 0.3

    ex2 = build_executor("dev_local", runner=lambda cmd, cwd: (1, "boom"))
    h2 = ex2.submit_run({"experiment_id": "e2", "train_cmd": ["x"], "out_dir": tmp_path / "o2"})
    assert ex2.poll(h2) == FAILED


@pytest.mark.parametrize("backend", ["local_40g", "cloud_paid"])
def test_stub_backends_not_configured(backend):
    ex = build_executor(backend)
    with pytest.raises(NotConfigured):
        ex.submit_run({"experiment_id": "x"})

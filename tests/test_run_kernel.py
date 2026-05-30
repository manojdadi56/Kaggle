import json
import subprocess
import sys
from pathlib import Path

def test_mock_happy_path(tmp_path):
    out_dir = tmp_path / "out"
    cmd = [
        sys.executable, "tools/run_kernel.py",
        "--kernel-dir", "dummy_dir",
        "--owner", "test_owner",
        "--slug", "test-slug",
        "--out-dir", str(out_dir),
        "--mock"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0

    output = json.loads(result.stdout)
    assert output["kernel_url"] == "https://www.kaggle.com/code/test_owner/test-slug"
    assert output["terminal_state"] == "complete"
    assert output["cv_aggregate"] == 0.50
    assert output["elapsed_secs"] == 10

from unittest.mock import patch

def test_timeout_simulation(tmp_path):
    out_dir = tmp_path / "out"

    with patch("tools.kaggle_lite.kernel_push") as mock_push, \
         patch("tools.kaggle_lite.kernel_status") as mock_status:

        mock_push.return_value = {"status": 200, "body": '{"ref": "test_owner/test-slug"}'}
        # Always return running so it times out
        mock_status.return_value = {"status": 200, "body": '{"status": "running"}'}

        # We need to run main directly so the patches apply
        from tools.run_kernel import main

        test_args = [
            "--kernel-dir", "dummy_dir",
            "--owner", "test_owner",
            "--slug", "test-slug",
            "--out-dir", str(out_dir),
            "--poll-secs", "0", # instant polling
            "--timeout-mins", "0" # immediate timeout
        ]

        # Override sys.argv
        old_argv = sys.argv
        sys.argv = ["run_kernel.py"] + test_args

        try:
            main()
        except SystemExit as e:
            assert e.code == 2
        finally:
            sys.argv = old_argv

def test_error_simulation(tmp_path):
    out_dir = tmp_path / "out"

    with patch("tools.kaggle_lite.kernel_push") as mock_push, \
         patch("tools.kaggle_lite.kernel_status") as mock_status:

        mock_push.return_value = {"status": 200, "body": '{"ref": "test_owner/test-slug"}'}
        mock_status.return_value = {"status": 200, "body": '{"status": "error"}'}

        from tools.run_kernel import main

        test_args = [
            "--kernel-dir", "dummy_dir",
            "--owner", "test_owner",
            "--slug", "test-slug",
            "--out-dir", str(out_dir),
            "--poll-secs", "0",
            "--timeout-mins", "10"
        ]

        old_argv = sys.argv
        sys.argv = ["run_kernel.py"] + test_args

        try:
            main()
        except SystemExit as e:
            assert e.code == 1
        finally:
            sys.argv = old_argv

def test_json_output_schema_complete(tmp_path, capsys):
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    # mock the output from kaggle
    (out_dir / "cv_score.json").write_text('{"cv_aggregate": 0.85}')

    with patch("tools.kaggle_lite.kernel_push") as mock_push, \
         patch("tools.kaggle_lite.kernel_status") as mock_status, \
         patch("tools.kaggle_lite.kernel_output") as mock_output:

        mock_push.return_value = {"status": 200, "body": '{"ref": "test_owner/test-slug"}'}
        mock_status.return_value = {"status": 200, "body": '{"status": "complete"}'}
        mock_output.return_value = {"status": 200}

        from tools.run_kernel import main

        test_args = [
            "--kernel-dir", "dummy_dir",
            "--owner", "test_owner",
            "--slug", "test-slug",
            "--out-dir", str(out_dir),
            "--poll-secs", "0",
            "--timeout-mins", "10"
        ]

        old_argv = sys.argv
        sys.argv = ["run_kernel.py"] + test_args

        try:
            main()
        except SystemExit as e:
            assert e.code == 0
        finally:
            sys.argv = old_argv

        captured = capsys.readouterr()
        # Find the JSON output, it should be the last thing printed to stdout
        lines = captured.out.strip().split('\n')
        out_json = json.loads(lines[-1])

        assert "kernel_url" in out_json
        assert "terminal_state" in out_json
        assert "cv_aggregate" in out_json
        assert "elapsed_secs" in out_json

        assert out_json["terminal_state"] == "complete"
        assert out_json["cv_aggregate"] == 0.85

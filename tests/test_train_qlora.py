import os
import sys
import json
import pytest
import importlib

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def get_run_training():
    # Use importlib since module name has hyphens
    # To import a module with hyphens correctly we have to build the path and load it
    import importlib.util
    train_path = os.path.join(os.path.dirname(__file__), "..", "competitions", "nvidia-nemotron-model-reasoning-challenge", "kernels", "train", "train.py")
    spec = importlib.util.spec_from_file_location("train_module", train_path)
    train_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train_module)
    return train_module.run_training

def test_qlora_rank_exceeds_max():
    run_training = get_run_training()
    with pytest.raises(ValueError, match="LoRA rank must be <= 32"):
        run_training(rank=64, smoke=True)

def test_qlora_valid_rank_writes_outputs(tmp_path, monkeypatch):
    run_training = get_run_training()
    # Change current working directory to a temporary path so files are written there
    monkeypatch.chdir(tmp_path)

    run_training(rank=32, smoke=True)

    # Check if adapter/adapter_config.json exists
    assert os.path.exists("adapter/adapter_config.json")
    with open("adapter/adapter_config.json") as f:
        config = json.load(f)
        assert config["r"] == 32
        assert config["base_model_name_or_path"] == "toy-model"

    # Check if cv_score.json exists
    assert os.path.exists("cv_score.json")
    with open("cv_score.json") as f:
        cv_score = json.load(f)
        assert "score" in cv_score

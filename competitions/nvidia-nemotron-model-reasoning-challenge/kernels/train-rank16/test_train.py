import pytest
import os
import sys

# Ensure evaluating modules can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eval')))
import cv

from train import run_training, LinearDecayLRSchedule, compute_loss, LORA_RANK, LORA_ALPHA

def test_hard_invariant_rank():
    # Attempting to run training with rank > 32 should throw ValueError
    with pytest.raises(ValueError, match="LoRA rank must be <= 32"):
        run_training(rank=33, smoke=True)

    # Check variables
    assert LORA_RANK == 16
    assert LORA_ALPHA == 32

def test_linear_decay_schedule():
    schedule = LinearDecayLRSchedule(2e-5, 1e-5)
    epochs = 1
    total_steps = 100

    # Beginning of training (step 0 => mult 1.0 => lr 2e-5)
    lr_start = schedule.get_lr(0, total_steps, 0, epochs)
    assert lr_start == 2e-05

    # End of training (step 100 => mult 0.0 => lr 1e-5)
    lr_end = schedule.get_lr(100, total_steps, 1, epochs)
    assert abs(lr_end - 1e-05) < 1e-10

def test_smoke_training_loop():
    # If run successfully, adapter dir and cv_score.json should be created
    if os.path.exists("adapter"):
        import shutil
        shutil.rmtree("adapter")
    if os.path.exists("cv_score.json"):
        os.remove("cv_score.json")

    run_training(rank=8, smoke=True)

def test_1_epoch_and_accum():
    # This implicitly validates standard code layout for 1 epoch logic in file
    with open('competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-rank16/train.py', 'r') as f:
        content = f.read()
    assert "epochs = 1" in content
    assert "gradient_accumulation_steps = 8 if not smoke else 1" in content

    assert os.path.exists("adapter")
    assert os.path.exists("adapter/adapter_config.json")
    assert os.path.exists("cv_score.json")

if __name__ == "__main__":
    pytest.main(["-v", "test_train.py"])

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
    assert LORA_RANK <= 32
    assert LORA_ALPHA == 64

def test_linear_decay_schedule():
    schedule = LinearDecayLRSchedule(2e-5, 1e-5)
    epochs = 2
    total_steps = 100

    # Beginning of training (epoch 0, epochs 2 => mult = 1 - 0/3 = 1.0 => 1e-5 + 1e-5*1.0 = 2e-5)
    lr_start = schedule.get_lr(0, total_steps, 0, epochs)
    assert lr_start == 2e-05

    # End of training (epoch 2 means end of epoch 1) (epoch 2, epochs 2 => mult = 1 - 2/3 = 0.3333333333 => 1e-5 + 1e-5*(1/3))
    lr_end = schedule.get_lr(100, total_steps, 2, epochs)
    assert abs(lr_end - (1e-5 + 1e-5 * (1.0 / 3.0))) < 1e-10

@pytest.fixture(autouse=True)
def cleanup():
    # Teardown to clean up adapter/ and cv_score.json after tests
    yield
    if os.path.exists("adapter"):
        import shutil
        shutil.rmtree("adapter")
    if os.path.exists("cv_score.json"):
        os.remove("cv_score.json")


def test_smoke_training_loop():
    # If run successfully, adapter dir and cv_score.json should be created
    if os.path.exists("adapter"):
        import shutil
        shutil.rmtree("adapter")
    if os.path.exists("cv_score.json"):
        os.remove("cv_score.json")

    run_training(rank=8, smoke=True)

def test_2_epoch_and_accum():
    # This implicitly validates standard code layout for 2 epoch logic in file
    with open('train.py', 'r') as f:
        content = f.read()
    assert "epochs = 2" in content
    assert "gradient_accumulation_steps = 8 if not smoke else 1" in content

if __name__ == "__main__":
    pytest.main(["-v", "test_train.py"])

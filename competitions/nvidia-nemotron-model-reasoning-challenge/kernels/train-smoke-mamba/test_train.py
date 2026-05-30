import os
import sys
import importlib.util

def test_train_config():
    # Construct absolute path to train.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    train_py_path = os.path.join(current_dir, "train.py")

    # Import train.py as a module
    spec = importlib.util.spec_from_file_location("train_module", train_py_path)
    train_module = importlib.util.module_from_spec(spec)
    sys.modules["train_module"] = train_module
    spec.loader.exec_module(train_module)

    # Assert parameters
    assert isinstance(train_module.LORA_TARGET_MODULES, list), "LORA_TARGET_MODULES should be a list"
    assert train_module.LORA_TARGET_MODULES == ['mixer.in_proj', 'mixer.out_proj', 'q_proj', 'k_proj', 'v_proj', 'o_proj'], "LORA_TARGET_MODULES does not match expected exact list"
    assert train_module.MAX_STEPS == 10, "MAX_STEPS should be 10"
    assert train_module.LORA_RANK == 32, "LORA_RANK should be 32"
    assert train_module.LORA_ALPHA == 64, "LORA_ALPHA should be 64"
    assert train_module.LOAD_IN_4BIT is True, "LOAD_IN_4BIT should be True"

    print("All tests passed.")

if __name__ == "__main__":
    test_train_config()

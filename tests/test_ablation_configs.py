import pytest
import sys
import os

# Add the experiments directory to the path so we can import ablation_configs
sys.path.append(os.path.join(os.path.dirname(__file__), '../competitions/nvidia-nemotron-model-reasoning-challenge/experiments'))

from ablation_configs import CONFIGS

def test_configs_exist():
    expected_keys = ['baseline', 'rank16', '2epoch', 'curriculum', 'select2reason', 'logprob_filter']
    for key in expected_keys:
        assert key in CONFIGS, f"Missing config key: {key}"
    assert len(CONFIGS) == 6, f"Expected 6 configs, found {len(CONFIGS)}"

def test_config_fields():
    required_fields = ['lora_rank', 'alpha', 'epochs', 'lr', 'target_modules', 'hypothesis', 'source']
    for name, config in CONFIGS.items():
        for field in required_fields:
            assert field in config, f"Config '{name}' missing field: '{field}'"

        assert isinstance(config['lora_rank'], int)
        assert isinstance(config['alpha'], (int, float))
        assert isinstance(config['epochs'], int)
        assert isinstance(config['lr'], float)
        assert isinstance(config['target_modules'], list)
        assert isinstance(config['hypothesis'], str)
        assert isinstance(config['source'], str)

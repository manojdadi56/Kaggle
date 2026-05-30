# Ablation Experiments

This directory contains configuration definitions and tools to test different training approaches systematically.

## Applying a configuration

To test one of the configs defined in `ablation_configs.py`, the operator should update the training notebook (or script) by substituting the tunables block.

For example, to test the `rank16` config:

1. Import `CONFIGS` from `ablation_configs.py`
2. Select the desired config: `cfg = CONFIGS['rank16']`
3. Update the training hyperparameters:
   - `LORA_RANK = cfg['lora_rank']`
   - `LORA_ALPHA = cfg['alpha']`
   - `EPOCHS = cfg['epochs']`
   - `LR = cfg['lr']`
   - `TARGET_MODULES = cfg['target_modules']`
4. For configs that require data changes (like `curriculum`, `select2reason`, `logprob_filter`), ensure the data pipeline applies the corresponding logic based on the selected config.

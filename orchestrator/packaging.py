"""Package + validate a LoRA adapter submission.

Hard invariant (F-022/F-023): the submission is a zip of the adapter +
`adapter_config.json` with LoRA rank ≤ 32. We validate BEFORE any submit so an
over-rank config never reaches Kaggle.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

MAX_LORA_RANK = 32
BASE_MODEL = "Nemotron-3-Nano-30B-A3B-BF16"


def validate_adapter_config(adapter_dir) -> tuple[bool, str]:
    cfg = Path(adapter_dir) / "adapter_config.json"
    if not cfg.exists():
        return False, "missing adapter_config.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"adapter_config.json not valid JSON: {e}"
    rank = data.get("r", data.get("rank"))
    if rank is None:
        return False, "adapter_config.json has no LoRA rank ('r')"
    try:
        rank = int(rank)
    except (TypeError, ValueError):
        return False, f"rank not an integer: {rank!r}"
    if rank > MAX_LORA_RANK:
        return False, f"LoRA rank {rank} exceeds max {MAX_LORA_RANK}"
    return True, f"ok (rank={rank})"


def package_submission(adapter_dir, out_zip) -> Path:
    """Validate then zip the adapter dir into out_zip. Raises ValueError if invalid."""
    ok, reason = validate_adapter_config(adapter_dir)
    if not ok:
        raise ValueError(f"refusing to package invalid adapter: {reason}")
    adapter_dir = Path(adapter_dir)
    out_zip = Path(out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(adapter_dir.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(adapter_dir))
    return out_zip

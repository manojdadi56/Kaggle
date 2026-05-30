"""Lint a Nemotron Kaggle kernel directory for the 7 required fixes.

Usage:
  python tools/check_kernel.py competitions/.../kernels/train-baseline-e002/

Exit codes:
  0 = all 7 fixes present
  1 = one or more fixes missing (lists which)
  2 = kernel dir or required files missing

See AGENTS.md "Nemotron kernel — 7 hard-learned fixes" for the why behind each.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def lint(kernel_dir: Path) -> tuple[int, list[str]]:
    """Return (exit_code, list_of_failures)."""
    if not kernel_dir.is_dir():
        return 2, [f"not a directory: {kernel_dir}"]
    meta_path = kernel_dir / "kernel-metadata.json"
    train_path = kernel_dir / "train.py"
    if not meta_path.exists():
        return 2, [f"missing kernel-metadata.json in {kernel_dir}"]
    if not train_path.exists():
        return 2, [f"missing train.py in {kernel_dir}"]

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    train = train_path.read_text(encoding="utf-8")

    failures: list[str] = []

    # 1. enable_internet: true (needed for pip-install of Mamba deps)
    if str(meta.get("enable_internet", "")).lower() not in ("true", "1"):
        failures.append("1. kernel-metadata.json must have enable_internet: true (needed for pip-install)")

    # 2. Real canonical Nemotron model slug (metric/, not daroai/ or others)
    model_sources = meta.get("model_sources", [])
    canonical = "metric/nemotron-3-nano-30b-a3b-bf16"
    if not any(canonical in src for src in model_sources):
        failures.append(
            f"2. kernel-metadata.json model_sources should include "
            f"'{canonical}/transformers/default/1' (got {model_sources})"
        )

    # 3. Inline cv + score modules
    if not ("_score_mod" in train and "_cv_mod" in train and "sys.modules['score']" in train):
        failures.append(
            "3. train.py must inline cv.py + score.py modules at top "
            "(script kernels upload only code_file). See train-baseline-e002 reference."
        )

    # 4. Mamba + bitsandbytes pip install
    deps = ("causal-conv1d", "mamba-ssm", "bitsandbytes")
    missing_deps = [d for d in deps if d not in train]
    if missing_deps or "pip" not in train:
        failures.append(
            f"4. train.py must pip-install Mamba deps inline. Missing: {missing_deps or '(no pip call found)'}"
        )

    # 5. Offline transformers
    if "TRANSFORMERS_OFFLINE" not in train or "local_files_only=True" not in train:
        failures.append(
            "5. train.py must set TRANSFORMERS_OFFLINE=1 and pass local_files_only=True to from_pretrained"
        )

    # 6. trust_remote_code
    if "trust_remote_code=True" not in train:
        failures.append(
            "6. train.py must pass trust_remote_code=True to AutoModelForCausalLM.from_pretrained "
            "AND AutoTokenizer.from_pretrained (Nemotron has custom Mamba modeling code)"
        )

    # 7. Auto-detect mount path
    if "os.walk" not in train or "config.json" not in train or "tokenizer.json" not in train:
        failures.append(
            "7. train.py must os.walk /kaggle/input looking for a dir with config.json + tokenizer.json "
            "(the Kaggle Models mount path varies)"
        )

    return (1 if failures else 0), failures


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python tools/check_kernel.py <kernel-dir>", file=sys.stderr)
        return 2
    kernel_dir = Path(argv[0]).resolve()
    rc, failures = lint(kernel_dir)
    if rc == 0:
        print(f"OK: {kernel_dir.name} has all 7 required fixes")
    else:
        print(f"FAIL: {kernel_dir.name} is missing {len(failures)} fixes:")
        for f in failures:
            print(f"  {f}")
        print("\nSee AGENTS.md 'Nemotron kernel — 7 hard-learned fixes' for details.")
        print("Reference implementation: train-baseline-e002/train.py")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

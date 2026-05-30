"""Lock in the verified-working E-002 baseline kernel.

The reference (train-baseline-e002) must pass all 7 fixes — regressions
fail this test. Other kernels are reported but not enforced (they're queued
for backport when the operator's ready to push them).

See AGENTS.md "Nemotron kernel — 7 hard-learned fixes" and tools/check_kernel.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_kernel import lint  # type: ignore[import-not-found]


REPO = Path(__file__).resolve().parents[1]
KERNELS = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "kernels"
REFERENCE = KERNELS / "train-baseline-e002"


def test_reference_kernel_has_all_7_fixes():
    """E-002 baseline is the verified-working reference; regressions block."""
    rc, failures = lint(REFERENCE)
    assert rc == 0, (
        f"REGRESSION: train-baseline-e002 lost a required fix:\n  "
        + "\n  ".join(failures)
    )


def test_report_other_kernel_status():
    """Diagnostic only — reports how many fixes each non-reference kernel has.

    Does NOT fail; the other kernels need a deliberate backport pass before they're
    pushed. This test exists to make the gap visible in `pytest -v` output.
    """
    if not KERNELS.is_dir():
        pytest.skip("kernels dir not present")

    rows = []
    for kd in sorted(KERNELS.iterdir()):
        if not kd.is_dir() or not (kd / "train.py").exists() or kd == REFERENCE:
            continue
        rc, failures = lint(kd)
        rows.append((kd.name, 7 - len(failures), len(failures)))

    if rows:
        print("\n=== Non-reference kernels (informational) ===")
        for name, passes, fails in rows:
            print(f"  {name}: {passes}/7 fixes present")
        n_ready = sum(1 for _, _, fails in rows if fails == 0)
        print(f"=== {n_ready}/{len(rows)} non-reference kernels ready to push ===")

"""One-shot seed for audit-2026-05-30: 5 missing critical-path tasks + 1 decision."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator.tools import build_orchestrator
from collections import Counter

orch = build_orchestrator()
tick = "AUDIT-20260530"

ops = [
    {"op": "create_task", "idempotency_key": f"{tick}:TASK-FIX-kernel-metadata", "data": {
        "id": "TASK-FIX-kernel-metadata",
        "title": "Replace TODO dataset_sources + model_sources in 8 kernel-metadata.json files",
        "status": "BLOCKED",
        "blocked_by": None,
        "allowed_area": "competitions/nvidia-nemotron-model-reasoning-challenge/kernels",
        "spec": ("Each kernel-metadata.json has dataset_sources=['TODO/REPLACE-WITH-CORPUS-DATASET-SLUG'] "
                 "and model_sources=['TODO/REPLACE-WITH-REAL-MODEL-VERSION-FROM-KAGGLE']. Replace with the "
                 "real Kaggle dataset slug owned by sai1881 holding corpus.jsonl v1 (built by TASK-E001), "
                 "and the real model-version slug for Nemotron-3-Nano-30B-A3B-BF16. Validate with "
                 "kaggle_lite kernel-push dry-run. Blocked on Q-018/Q-019."),
        "acceptance_criteria": "All 8 files have non-placeholder values; dry-run passes.",
        "definition_of_done": "One PR; tests green.",
        "size_hint": "~30 min",
        "mode": "deep",
        "story": "US-4",
        "actor": "jules",
    }, "summary": "audit-seed: kernel-metadata fix task"},

    {"op": "create_task", "idempotency_key": f"{tick}:TASK-E002-SMOKE-RUN", "data": {
        "id": "TASK-E002-SMOKE-RUN",
        "title": "Kaggle GPU smoke run: 5-min rank=4 max_steps=20 100-row preflight",
        "status": "BLOCKED",
        "blocked_by": "TASK-FIX-kernel-metadata",
        "allowed_area": "competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-smoke-mamba",
        "spec": ("Push smoke-mamba kernel with reduced hyperparams (rank=4, max_steps=20, 100 rows). "
                 "Validate full chain: kernel-push -> status=complete -> output-pull -> cv_score.json + "
                 "adapter_config.json present. Do NOT submit. Steelman counter-arg 8."),
        "acceptance_criteria": "Kernel completes; outputs pulled; runtime <10 min; metrics logged.",
        "definition_of_done": "Result under experiments/SMOKE-001/; cv recorded via update_gpu_run.",
        "size_hint": "~45 min",
        "mode": "deep",
        "story": "US-4",
        "actor": "jules",
    }, "summary": "audit-seed: smoke-run preflight task"},

    {"op": "create_task", "idempotency_key": f"{tick}:TASK-E002-push-and-train", "data": {
        "id": "TASK-E002-push-and-train",
        "title": "Push baseline E-002 (rank=32) kernel to Kaggle GPU and ingest cv_score",
        "status": "BLOCKED",
        "blocked_by": "TASK-E002-SMOKE-RUN",
        "allowed_area": "competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-baseline-e002",
        "spec": ("Once smoke run succeeds: emit gpu_dispatch for experiment_id=E-002-baseline-rank32, "
                 "backend=kaggle_gpu, slug=sai1881/train-baseline-e002. Poll until terminal; pull "
                 "adapter/ + cv_score.json into experiments/E-002-baseline-rank32/; record cv; "
                 "set experiments[E-002].cv_score + status=COMPLETED."),
        "acceptance_criteria": "state.gpu_runs entry for the slug; cv_score numeric; rank<=32.",
        "definition_of_done": "best_cv is non-null; submit-gate unlocked.",
        "size_hint": "GPU ~2-3hr; orchestrator ~15 min.",
        "mode": "deep",
        "story": "US-4",
        "actor": "operator",
    }, "summary": "audit-seed: E-002 push+train+ingest task"},

    {"op": "create_task", "idempotency_key": f"{tick}:TASK-E007-RESCOPE", "data": {
        "id": "TASK-E007-RESCOPE",
        "title": "Rescope or abort stuck E-007 cryptarithm-guess Jules session",
        "status": "BACKLOG",
        "allowed_area": ("competitions/nvidia-nemotron-model-reasoning-challenge/data/corpus/v1, "
                         "competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/cryptarithm, "
                         "competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-e007-cryptarithm"),
        "spec": ("Session 13107147469450254389 stuck in out-of-scope edit retry loop (~35min idle, "
                 "26 identical refused patches). See F-057. Decision: (a) sendmessage steer to ship "
                 "kernel-only + NEEDS_SPLIT, or (b) kill + re-dispatch with widened area. User decision needed."),
        "acceptance_criteria": "Session terminal (COMPLETED + PR or canceled); lock released.",
        "definition_of_done": "No stale lock; ledger reflects terminal state.",
        "size_hint": "~15 min",
        "mode": "deep",
        "story": "US-3",
        "actor": "operator",
    }, "summary": "audit-seed: unstick E-007"},

    {"op": "create_task", "idempotency_key": f"{tick}:TASK-OPS-cron-trigger", "data": {
        "id": "TASK-OPS-cron-trigger",
        "title": "Schedule the autonomous operator tick (cron / Task Scheduler) - user approval",
        "status": "BACKLOG",
        "allowed_area": "(scheduler only)",
        "spec": ("No cron exists (F-054). Pick: (a) /schedule @hourly running tools dispatch+status, "
                 "(b) Windows Task Scheduler + claude -p (CLAUDE_CODE_OAUTH_TOKEN), "
                 "(c) accept manual-tick mode. User decision."),
        "acceptance_criteria": "Scheduled trigger exists OR explicit manual-tick acceptance recorded.",
        "definition_of_done": "CronList/Task Scheduler shows entry; or feedback memory records decision.",
        "size_hint": "~10 min",
        "mode": "deep",
        "story": "US-meta",
        "actor": "operator",
    }, "summary": "audit-seed: schedule autonomous trigger"},

    {"op": "create_decision", "idempotency_key": f"{tick}:D-AUDIT-2026-05-30", "data": {
        "id": "D-AUDIT-2026-05-30",
        "entity": "project",
        "decision": "Pause new feature work; land the 6 audit-corrections + 5 seeded tasks before adding capability.",
        "rationale": ("Audit found 5 live defects (3 fixed mid-pass), 6 invalidated assumptions, 0 end-to-end runs. "
                      "Infrastructure-complete but execution-untriggered. Adding features now compounds cross-PR "
                      "invariant drift the audit identified."),
    }, "summary": "audit-seed: corrections-first decision"},
]

res = orch.state.apply_patch({"tick_id": tick, "operations": ops})
print(f"applied: {len(res['applied'])}; skipped: {len(res['skipped'])}")
print("Ledger task statuses (post-seed):",
      dict(Counter(t.get("status") for t in orch.state.state.get("tasks", {}).values())))
print("New tasks present:")
for tid in ("TASK-FIX-kernel-metadata", "TASK-E002-SMOKE-RUN", "TASK-E002-push-and-train",
            "TASK-E007-RESCOPE", "TASK-OPS-cron-trigger"):
    t = orch.state.state.get("tasks", {}).get(tid)
    print(f"  {tid}: {t.get('status') if t else 'MISSING'}")

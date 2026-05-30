"""Planner emitter for pipeline-completion tasks: training -> validation -> submission."""
import json

TICK = "RUN-20260530-114605c"
TS = "2026-05-30T12:00:00Z"

ops = []

# --- New hypothesis: H-GPU-DISPATCH ---
ops.append({"op":"create_hypothesis","idempotency_key":f"{TICK}:H-GPU-DISPATCH:create",
 "data":{"id":"H-GPU-DISPATCH",
  "title":"Wiring gpu_dispatch into the loop closes the SDLC training cycle end-to-end (Jules authors kernel -> operator pushes -> kernel runs on 2xT4 -> outputs ingested as cv_score)",
  "statement":("Today the loop stops at 'kernel authored by Jules and merged to main' - the actual "
               "Kaggle GPU run is a manual operator action. Adding a gpu_dispatch ledger op + a "
               "tools/run_kernel.py runner (kernel-push -> poll kernel-status -> kernel-output) "
               "lets the operator's owner-role automatically promote a merged experiment with "
               "status=READY_FOR_GPU into a live Kaggle kernel run and capture cv_score.json + "
               "adapter dir into the ledger, completing the train->validate loop."),
  "expected_effect":("Removes the only manual hand-off in the loop; enables the operator's "
                     "30-min cron to also drive Kaggle GPU runs autonomously; unlocks the full "
                     "E-002 -> E-003..E-009 ablation fanout to run end-to-end."),
  "how_to_test":("After E-002 baseline kernel PR merges, run a single tick - confirm gpu_dispatch "
                 "auto-fires, kernel-push returns a Kaggle kernel URL, kernel-status terminalizes, "
                 "kernel-output pulls cv_score.json + adapter/ into experiments/<exp-id>/, and the "
                 "operator's add_metric op records the new cv into best_cv if better."),
  "source_refs":["AGENTS.md kernel-experiment pattern","tools/kaggle_lite.py kernel-push/kernel-status/kernel-output",
                 "orchestrator/loop.py poll_in_flight"],
  "status":"PROPOSED","created_at":TS}})

# === TRAINING PHASE ===

# Task 1: run_kernel.py runner
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-OPS-run-kernel-runner:create",
 "data":{"id":"TASK-OPS-run-kernel-runner",
  "title":"Write tools/run_kernel.py end-to-end runner (kernel-push -> poll status -> pull outputs)",
  "spec":("Create tools/run_kernel.py with CLI: --kernel-dir <path> --owner <kaggle_user> --slug <kernel-slug> "
          "--out-dir <experiments/<exp-id>/> --poll-secs 30 --timeout-mins 240 [--mock]. Behavior: "
          "(1) Call tools.kaggle_lite.kernel-push for the directory; capture returned ref. "
          "(2) Loop kaggle_lite.kernel-status every poll-secs until terminal (complete/error/cancelled) "
          "or timeout. (3) On complete: call kaggle_lite.kernel-output to download into out-dir. "
          "(4) Parse out-dir/cv_score.json if present; print a one-line summary {kernel_url, terminal_state, "
          "cv_aggregate, elapsed_secs}. (5) --mock short-circuits to a deterministic fake "
          "(returns terminal_state='complete', cv_aggregate=0.50 fixture). (6) Exit 0 on terminal-complete, "
          "1 on terminal-error, 2 on timeout. Add tests/test_run_kernel.py covering --mock happy path "
          "+ timeout simulation + JSON-output schema."),
  "allowed_area":"tools/run_kernel.py, tests/test_run_kernel.py",
  "acceptance_criteria":("CLI works in --mock mode end-to-end; exit codes correct on each branch; "
                         "JSON summary contains kernel_url/terminal_state/cv_aggregate/elapsed_secs; "
                         "pytest -q green."),
  "definition_of_done":"One PR; tests green; PR body shows --mock CLI output sample; hypothesis_id=H-GPU-DISPATCH.",
  "hypothesis_id":"H-GPU-DISPATCH","priority":"P0","status":"BACKLOG","est_hours":1.0,
  "source_refs":["AGENTS.md kernel-experiment pattern","tools/kaggle_lite.py"],"created_at":TS}})

# Task 2: gpu_dispatch op wiring
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-OPS-gpu-dispatch-op:create",
 "data":{"id":"TASK-OPS-gpu-dispatch-op",
  "title":"Wire gpu_dispatch op into orchestrator/loop.py + state.py (auto-run merged kernels)",
  "spec":("Extend the orchestrator to dispatch merged kernel experiments to Kaggle GPU automatically. "
          "(1) state.py: add op 'gpu_dispatch' with data={experiment_id, kernel_dir, owner, slug, out_dir}; "
          "appends to state['gpu_runs'][slug] = {state:'QUEUED', experiment_id, started_at, kernel_url:None}. "
          "(2) loop.py.apply_decision: if decision contains gpu_dispatch ops, invoke tools.run_kernel.py "
          "(via subprocess.run with --mock=$RUN_KERNEL_MOCK) and update gpu_runs[slug] with terminal_state "
          "+ cv_aggregate. (3) loop.py.poll_in_flight: extend to also poll non-terminal gpu_runs and "
          "update their state. (4) Add tests/test_gpu_dispatch.py exercising the mock path. "
          "Acceptance: an experiment with status=READY_FOR_GPU + kernel_dir set, when included in a "
          "decision's gpu_dispatch list, ends up with gpu_runs[slug].state in {COMPLETE,ERROR,TIMEOUT} "
          "and (on complete) cv_aggregate captured. pytest -q green."),
  "allowed_area":"orchestrator/state.py, orchestrator/loop.py, tests/test_gpu_dispatch.py",
  "acceptance_criteria":("gpu_dispatch op accepted by state.py schema; loop.py invokes tools/run_kernel.py "
                         "with --mock honored via env; gpu_runs records state transitions; pytest -q green."),
  "definition_of_done":"One PR; tests green; PR body shows ledger ops list updated; hypothesis_id=H-GPU-DISPATCH.",
  "hypothesis_id":"H-GPU-DISPATCH","priority":"P0","status":"BLOCKED","blocked_by":"TASK-OPS-run-kernel-runner",
  "est_hours":1.5,"source_refs":["orchestrator/loop.py","orchestrator/state.py ALLOWED_OPS"],
  "created_at":TS}})

# === VALIDATION PHASE ===

# Task 3: CV fixture jsonl
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-EVAL-cv-fixture:create",
 "data":{"id":"TASK-EVAL-cv-fixture",
  "title":"Build held-out CV fixture (200 rows stratified across 9 categories) for vllm_eval.py",
  "spec":("Create competitions/nvidia-nemotron-model-reasoning-challenge/eval/build_cv_fixture.py "
          "+ produce eval/cv_fixture.jsonl. Behavior: "
          "(1) Loads train.csv from data/raw/ (fetched by tools/download_competition_data.py; if missing, "
          "the script must exit nonzero with a clear 'run download_competition_data.py first' message). "
          "(2) Classifies each row into one of the 9 host categories using the same classify.py logic "
          "that R28 merged (re-import; do NOT duplicate code). "
          "(3) Selects 200 rows stratified across categories (proportional or floor=15/cat — document choice). "
          "(4) Writes eval/cv_fixture.jsonl with {id, prompt, answer, category}. "
          "(5) The fixture itself is gitignored (it contains answers); only the builder script + a "
          "README explaining the build are committed. "
          "(6) Add tests/test_build_cv_fixture.py using a 50-row stub of train.csv (synthetic, no real data) "
          "to verify stratification + jsonl schema."),
  "allowed_area":("competitions/nvidia-nemotron-model-reasoning-challenge/eval/build_cv_fixture.py, "
                  "competitions/nvidia-nemotron-model-reasoning-challenge/eval/README.md, "
                  "tests/test_build_cv_fixture.py"),
  "acceptance_criteria":("Builder script works on a 50-row synthetic stub in the test; produces jsonl "
                         "with category stratification within ±2 rows of target; pytest -q green; "
                         "real fixture file is gitignored."),
  "definition_of_done":"One PR; tests green; README documents the 'why answers stay gitignored' rule; hypothesis_id=H-VLLM-EVAL.",
  "hypothesis_id":"H-VLLM-EVAL","priority":"P1","status":"BACKLOG","est_hours":0.75,
  "source_refs":["DATA.md","competitions/.../data/curation/classify.py (R28)"],"created_at":TS}})

# Task 4: cv_score ingest op
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-EVAL-cv-score-ingest:create",
 "data":{"id":"TASK-EVAL-cv-score-ingest",
  "title":"Add record_cv_score state op + auto best_cv update + apply_decision pickup from kernel-output",
  "spec":("(1) orchestrator/state.py: add op 'record_cv_score' with data={experiment_id, cv_aggregate, "
          "per_category, n_total, n_correct, n_boxed_missing, source_kernel:str|None}. Appends to "
          "state['metrics'][f'cv:{experiment_id}'] = data; if cv_aggregate > state.get('best_cv', -inf), "
          "set state['best_cv'] = cv_aggregate AND state['best_cv_source'] = experiment_id. "
          "(2) orchestrator/loop.py.apply_decision: after a gpu_dispatch completes successfully, "
          "automatically read out_dir/cv_score.json and emit a record_cv_score op into the patch. "
          "(3) tools/status.py: update the snapshot to show best_cv + best_cv_source. "
          "(4) Add tests/test_record_cv_score.py covering: new best_cv -> updates; lower cv -> recorded "
          "but best_cv unchanged; per_category serialized. Acceptance: pytest -q green; status snapshot "
          "shows best_cv after a mock gpu_dispatch run."),
  "allowed_area":("orchestrator/state.py, orchestrator/loop.py, orchestrator/status.py, "
                  "tests/test_record_cv_score.py"),
  "acceptance_criteria":("record_cv_score op accepted; best_cv auto-updates only when strictly better; "
                         "tests cover both branches; pytest -q green."),
  "definition_of_done":"One PR; tests green; PR body shows status snapshot before/after mock; hypothesis_id=H-VLLM-EVAL.",
  "hypothesis_id":"H-VLLM-EVAL","priority":"P1","status":"BLOCKED","blocked_by":"TASK-OPS-gpu-dispatch-op",
  "est_hours":1.0,"source_refs":["orchestrator/state.py ALLOWED_OPS","orchestrator/loop.py"],"created_at":TS}})

# === SUBMISSION PHASE ===

# Task 5: package_submission.py
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-SUBMIT-package-zip:create",
 "data":{"id":"TASK-SUBMIT-package-zip",
  "title":"Write tools/package_submission.py that builds submission.zip from an adapter dir (Kaggle format)",
  "spec":("Create tools/package_submission.py with CLI: --adapter <adapter_dir> --out <submission.zip> "
          "[--cv-score <path>] [--manifest <path>]. Behavior: "
          "(1) Validate adapter dir has adapter_config.json + adapter_model.{safetensors,bin}; "
          "validate rank <= 32 (same check as validate_adapter.py - import that function, don't duplicate). "
          "(2) Build submission.zip with the host-required layout (adapter_config.json at root, "
          "adapter_model.safetensors at root, tokenizer files passed through if present). "
          "(3) Write a manifest.json inside the zip containing {cv_score, adapter_sha256, packed_at, "
          "experiment_id_if_provided}. (4) Print zip path + bytes + cv_score on stdout as JSON. "
          "(5) Add tests/test_package_submission.py covering: valid adapter -> zip created; rank>32 "
          "-> nonzero; missing files -> nonzero; zip contents include manifest.json. "
          "Acceptance: pytest -q green; CLI roundtrip on a stub adapter dir."),
  "allowed_area":"tools/package_submission.py, tests/test_package_submission.py",
  "acceptance_criteria":("CLI builds a valid submission.zip from a stub adapter; rank>32 path errors; "
                         "manifest.json included; pytest -q green."),
  "definition_of_done":"One PR; tests green; PR body shows zip listing; hypothesis_id=H-SUBMIT-GATE.",
  "hypothesis_id":"H-SUBMIT-GATE","priority":"P1","status":"BLOCKED","blocked_by":"TASK-SUBMIT-validate-adapter",
  "est_hours":1.0,"source_refs":["AGENTS.md submission handoff"],"created_at":TS}})

# Task 6: submit gate decision
ops.append({"op":"create_task","idempotency_key":f"{TICK}:TASK-SUBMIT-gate-decision:create",
 "data":{"id":"TASK-SUBMIT-gate-decision",
  "title":"Add submit_decision step to orchestrator/loop.py (cv-beats-best + cap-headroom + ≤3/day gating)",
  "spec":("Add orchestrator/submit_gate.py module with function decide_submit(state, kaggle_lite) -> "
          "{action:'submit'|'skip', reason:str, candidate:{experiment_id, blob_token, cv_score} | None}. "
          "Behavior: "
          "(1) Find candidate experiments with status=READY_FOR_SUBMIT + recorded cv_score + blob_token. "
          "(2) Skip unless cv_score > state['best_cv'] by at least a configurable margin (default 0.0). "
          "(3) Skip unless today's auto-submit count < MAX_AUTO_SUBMITS_PER_DAY (env, default 3). "
          "(4) Skip unless live kaggle_lite.submissions(comp) cap-remaining >= 1 + 2 (reserve 2 finals). "
          "(5) Wire orchestrator/loop.py.apply_decision: when decide_submit returns submit, call "
          "tools.kaggle_lite.competition_submit and emit record_submission op + bump submits_by_day. "
          "(6) Add tests/test_submit_gate.py covering each skip branch + the happy submit path "
          "(mock kaggle_lite). Acceptance: pytest -q green; happy path emits submit decision + records; "
          "all 4 skip branches return correct reason strings."),
  "allowed_area":"orchestrator/submit_gate.py, orchestrator/loop.py, tests/test_submit_gate.py",
  "acceptance_criteria":("decide_submit covers all 4 skip branches and 1 happy path; loop.py integration "
                         "calls competition_submit only on happy path; pytest -q green."),
  "definition_of_done":"One PR; tests green; PR body lists all skip reasons; hypothesis_id=H-SUBMIT-GATE.",
  "hypothesis_id":"H-SUBMIT-GATE","priority":"P1","status":"BLOCKED","blocked_by":"TASK-SUBMIT-package-zip",
  "est_hours":1.5,"source_refs":["AGENTS.md submission gate","tools/kaggle_lite.py competition-submit"],
  "created_at":TS}})

decision = {
  "tick_id": TICK,
  "status": "complete",
  "summary": ("planner: pipeline-completion tasks toward train->validate->submit end-to-end. "
              "Added H-GPU-DISPATCH + 6 R-005-sized tasks (2 training-dispatch, 2 validation, 2 submission). "
              "Dependency chain: run-kernel -> gpu-dispatch-op -> cv-score-ingest; validate-adapter -> "
              "package-zip -> submit-gate-decision. CV fixture is independent and dispatches first."),
  "state_patch": {"tick_id": TICK, "operations": ops},
}
with open("decision_pipeline.json","w",encoding="utf-8") as f:
    json.dump(decision, f)
print("wrote decision_pipeline.json with", len(ops), "ops")

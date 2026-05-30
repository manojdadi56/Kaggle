"""Deploy 4 parallel Jules tasks closing gaps #2, #4, #7, #8 (the ones operator can't do alone)."""
import json
from pathlib import Path

TICK = "CAMP-GAPS-1"
TS = "2026-05-31T03:30:00Z"

XLSX_DIR = "competitions/nvidia-nemotron-model-reasoning-challenge/"

tasks = [
  {
    # Gap #2 + #4 — scale corpus + add remaining 5 categories
    "id": "TASK-CORPUS-scale-9cat",
    "title": "Scale CoT corpus to 3K+ rows across ALL 9 host categories (winner-grade volume)",
    "spec": (
      "Read existing data/corpus/v2/corpus.jsonl (398 rows, 4 cats) and references/analysis-winner.md + "
      "winner-reasoning.py.md + winner-augmentation.py.md + winner-corpus.py.md. Build "
      f"{XLSX_DIR}data/corpus/v4/corpus.jsonl with: "
      "(a) 9 categories covered: bit_manipulation, cipher, gravity, numeral, cryptarithm, cryptarithm_guess, "
      "equation_numeric, unit_conversion, select2reason. (b) >= 300 rows per category (3000+ total). "
      "(c) Use per-category deterministic Python solvers (NO LLM/API), mirror winner's reasoning.py logic. "
      "(d) Apply the 5 winner augmenters (paraphrase, perturbation, etc) per augmentation.py. "
      "(e) HARD verification: each row's completion must end with \\boxed{X} where X exactly equals "
      "or numerically matches the original answer; reject mismatched rows; do NOT mark verified=True falsely. "
      "(f) Write data/corpus/v4/quality_report.json with per-category {generated, verified, rejected, samples}. "
      "(g) Add tests/test_corpus_v4_quality.py asserting >= 3000 rows, >= 95% verified, all 9 cats present. "
      "Acceptance: pytest -q green; quality report shows >= 95% verified for every category."
    ),
    "allowed_area": f"{XLSX_DIR}data/corpus/v4/, tests/test_corpus_v4_quality.py",
    "priority": "P0", "est_hours": 2.0, "status": "BACKLOG",
  },
  {
    # Gap #7 — held-out CV fixture
    "id": "TASK-EVAL-cv-fixture-9cat",
    "title": "Build held-out CV fixture (300 rows stratified across all 9 host categories)",
    "spec": (
      "Read data/raw/train.csv (run tools/download_competition_data.py if missing) and "
      "data/curation/classify.py (the 9-category classifier from R28). Build "
      f"{XLSX_DIR}eval/cv_fixture_v2.jsonl with: "
      "(a) 300 rows total, stratified across 9 categories with floor(33/cat). "
      "(b) Schema per line: {id, category, prompt, answer}. "
      "(c) HARD requirement: rows MUST NOT appear in data/corpus/v4/corpus.jsonl (no train/eval leakage). "
      "(d) The fixture file itself is gitignored (contains answers); commit the builder script + README + "
      "  per-category count manifest at eval/cv_fixture_v2_manifest.json. "
      "(e) Add eval/build_cv_fixture_v2.py + tests/test_cv_fixture_v2.py asserting 300 rows, 9 cats, no overlap "
      "with corpus, schema valid. Acceptance: pytest -q green; manifest committed with counts."
    ),
    "allowed_area": f"{XLSX_DIR}eval/cv_fixture_v2_manifest.json, {XLSX_DIR}eval/build_cv_fixture_v2.py, {XLSX_DIR}eval/README.md, tests/test_cv_fixture_v2.py",
    "priority": "P0", "est_hours": 1.0, "status": "BACKLOG",
  },
  {
    # Gap #5 — host chat template parity test
    "id": "TASK-EVAL-host-chat-template",
    "title": "Capture exact Nemotron host chat template + reasoning_on system prompt for parity testing",
    "spec": (
      "Per references/analysis-winner-training-internals.md + the winner repo's notebook_tinker.py, the host "
      "uses a SPECIFIC chat template + reasoning_on system header. Our v23 notebook now calls "
      "tokenizer.apply_chat_template — but we need parity tests. Build: "
      f"(a) {XLSX_DIR}eval/host_template_spec.md documenting the exact template, system prompt text, "
      "  max_new_tokens, temperature, top_p, max_model_len that the host uses (extract from analyses + "
      "  any official references). "
      f"(b) {XLSX_DIR}eval/test_template_parity.py: load tokenizer from a local fake or skip if not "
      "  available; render 5 fixed prompts via apply_chat_template + reasoning_on; "
      "  assert byte-equality vs expected strings in host_template_spec.md. "
      "Acceptance: spec.md exists with concrete strings; parity test runs (xfail allowed if local tokenizer "
      "isn't accessible). Cite source line numbers in analyses + winner repo."
    ),
    "allowed_area": f"{XLSX_DIR}eval/host_template_spec.md, {XLSX_DIR}eval/test_template_parity.py",
    "priority": "P0", "est_hours": 0.75, "status": "BACKLOG",
  },
  {
    # Gap #8 prep — pre-build the 5 ablation configs as JSON
    "id": "TASK-ABLATION-configs",
    "title": "Pre-build 5 ablation config JSONs (rank16, 2epoch, curriculum, select2reason, logprob_filter)",
    "spec": (
      "Create a single Python module that yields 5 ablation configs as dicts (one per knob), each one "
      "compatible with our notebook's tunables (LORA_RANK, MAX_TRAIN, REASONING_ON, EPOCHS, etc). Place at "
      f"{XLSX_DIR}experiments/ablation_configs.py exposing CONFIGS = {{'baseline':..., 'rank16':..., "
      "'2epoch':..., 'curriculum':..., 'select2reason':..., 'logprob_filter':...}}. For each, include: "
      "(a) the parameter delta from baseline (e.g. rank=16 instead of 32), (b) one-line hypothesis, "
      "(c) source citation (winner repo file:line or discussion id). "
      "Also write experiments/README.md explaining how the operator applies one config to the notebook via "
      "save_notebook (search/replace the tunable block). "
      "Add tests/test_ablation_configs.py asserting all 6 keys exist and each has the required fields. "
      "Acceptance: 6 configs total (baseline + 5); each has rank, alpha, epochs, lr, target_modules, "
      "hypothesis, source; pytest -q green."
    ),
    "allowed_area": f"{XLSX_DIR}experiments/ablation_configs.py, {XLSX_DIR}experiments/README.md, tests/test_ablation_configs.py",
    "priority": "P1", "est_hours": 0.75, "status": "BACKLOG",
  },
]

ops = []
hyp_id = "H-FINAL-PREP-PARALLEL"
ops.append({"op":"create_hypothesis","idempotency_key":f"{TICK}:{hyp_id}",
  "data":{"id":hyp_id,
    "title":"Parallel close of all 10 gaps unblocks final-quality training within 24h",
    "statement":("4 Jules workers (corpus-scale 9cat, cv-fixture 9cat, host-template-parity, ablation-configs) "
                 "+ operator-side notebook v23 (chat template + reasoning_on + full corpus) + corpus-uploader "
                 "tool close all 10 gaps from the readiness audit in parallel; once landed, the operator can "
                 "run baseline + 5 ablations within 3 days."),
    "expected_effect":"From 'pipeline-validation' state to 'final-quality-runnable' state within 24h.",
    "how_to_test":"All 4 Jules ship within ~3h Jules wall-clock; v23 produces first real CV on next browser run; "
                  "ablation_configs.py exposes 6 dicts.",
    "source_refs":["readiness audit (10 gaps)","ROADMAP.md","references/analysis-winner-training-internals.md"],
    "status":"PROPOSED","created_at":TS}})

for t in tasks:
    ops.append({"op":"create_task","idempotency_key":f"{TICK}:{t['id']}",
      "data":{**t, "hypothesis_id":hyp_id, "created_at":TS}})

decision = {"tick_id":TICK,"status":"complete",
  "summary":"campaign GAPS-1: 4 parallel Jules tasks closing readiness gaps #2/#4/#5/#7/#8",
  "state_patch":{"tick_id":TICK,"operations":ops}}
Path("_gaps.json").write_text(json.dumps(decision), encoding="utf-8")
print(f"wrote {len(ops)} ops ({len(tasks)} tasks)")

"""Deploy 4 deep-analysis Jules tasks; each produces a standalone .xlsx workbook."""
import json
from pathlib import Path

TICK = "CAMP-EXCEL-1"
TS = "2026-05-31T01:30:00Z"

XLSX_DIR = "competitions/nvidia-nemotron-model-reasoning-challenge/analysis/"

tasks = [
  {
    # ----- 17 winner files: deep code-by-code analysis -----
    "id": "TASK-XLSX-winner-code-analysis",
    "title": "Excel: per-file deep analysis of all 17 winner-* code files",
    "spec": (
      "Read ALL 17 files matching competitions/nvidia-nemotron-model-reasoning-challenge/references/winner-*.md "
      "(135KB total: train_sft.py, reasoning.py, corpus.py, loss_config.py, lr_schedule.py, augmentation.py, "
      "generate_csv.py, train_common.py, upload_adapter.py, notebook_tinker.py, serve.sh, README.md, "
      "delete-tinker-checkpoint.sh, .mcp.json, CLAUDE.md, pyproject.toml, INDEX.md). "
      "Build ONE Excel workbook at "
      f"{XLSX_DIR}winner_code_analysis.xlsx with these sheets: "
      "(1) 'Overview' — one row per file: filename | role | LoC | key_functions | depends_on | criticality_1to5. "
      "(2) 'TechnicalDetails' — one row per significant function/class across all 17 files: "
      "file | symbol | purpose | input | output | algorithm_summary | hyperparams_used | gotchas. "
      "(3) 'KeyImprovements' — one row per technique we should adopt: "
      "technique | source_file | source_lines | current_state_in_our_notebook | expected_cv_delta | priority_1to5 | code_change_pseudocode. "
      "(4) 'CoreApproach' — narrative cells: 'data_pipeline', 'training_recipe', 'inference_pipeline', "
      "'evaluation_method', 'submission_packaging' — what the winner does end-to-end. "
      "(5) 'OpenQuestions' — things the code reveals about the winner's choices we don't yet understand. "
      "Use openpyxl. NO LLM/external API calls — pure file reading + parsing. "
      "Acceptance: xlsx exists with all 5 sheets populated; >= 17 rows on Overview; >= 30 rows on TechnicalDetails; "
      ">= 10 rows on KeyImprovements ranked by priority."
    ),
    "allowed_area": f"{XLSX_DIR}winner_code_analysis.xlsx, tests/test_winner_code_analysis.py",
    "priority": "P0", "est_hours": 1.5, "status": "BACKLOG",
  },
  {
    # ----- 217 discussions: chunked structured extraction -----
    "id": "TASK-XLSX-discussions-extract",
    "title": "Excel: structured extraction from all 217 discussion-*.md threads",
    "spec": (
      "Read ALL 217 files matching competitions/nvidia-nemotron-model-reasoning-challenge/references/discussion-*.md "
      "(1.08MB total). For each thread, extract structured rows. Build ONE Excel workbook at "
      f"{XLSX_DIR}discussions_extract.xlsx with these sheets: "
      "(1) 'Threads' — one row per thread: file | topic_id | title_inferred | category "
      "(TRAIN_TRICK / DATA_TRICK / EVAL_TRICK / GPU_TIP / GOTCHA / SUBMIT_TIP / META / RULES) "
      "| word_count | author_count_inferred | confidence_rating_1to5. "
      "(2) 'Insights' — one row PER extracted insight (multiple per thread allowed): "
      "thread_file | insight_text | category | applicability_to_our_notebook (YES/MAYBE/NO) | "
      "expected_cv_delta_qualitative (HIGH/MED/LOW) | concrete_code_change_if_applicable. "
      "(3) 'Top20Actionable' — the 20 highest-impact insights ranked by expected_cv_delta and "
      "applicability, with concrete code-change pseudocode for our notebook_fork_working.ipynb. "
      "(4) 'KnownGotchas' — every documented failure mode (P100, mamba-ssm versions, OOM, chat template, "
      "boxed extraction, submission format etc.) with the fix. "
      "Use openpyxl. Acceptance: xlsx with all 4 sheets; >=217 rows on Threads; >=100 rows on Insights; "
      "exactly 20 on Top20Actionable with code-change pseudocode."
    ),
    "allowed_area": f"{XLSX_DIR}discussions_extract.xlsx, tests/test_discussions_extract.py",
    "priority": "P0", "est_hours": 2.0, "status": "BACKLOG",  # >2h, may NEEDS_SPLIT
  },
  {
    # ----- All other refs: community sources + analyses + tab pages -----
    "id": "TASK-XLSX-community-and-tabs",
    "title": "Excel: community-sources + 6 analyses + 7 tab pages + technique-backlog into one workbook",
    "spec": (
      "Read these reference files: "
      "(a) competitions/.../references/community-sources.md (95KB, multi-section), "
      "(b) all 6 analysis-*.md files, "
      "(c) all 7 tab-*.md files (overview, rules, data, code, models, leaderboard, discussion-list), "
      "(d) technique-backlog.md + DIGEST-community.md + scraped-index.md. "
      "Build ONE Excel workbook at "
      f"{XLSX_DIR}community_and_tabs.xlsx with these sheets: "
      "(1) 'CommunityCode' — every code-snippet/repo/notebook referenced in community-sources.md: "
      "source_block | author | what_it_does | key_techniques | applicable_to_us. "
      "(2) 'CompetitionFacts' — extracted from tab-overview/rules/data: "
      "fact | source_tab | implication_for_us (eval metric, daily cap, accelerator grant, scoring formula etc.). "
      "(3) 'TechniqueBacklog' — every ranked technique from technique-backlog.md + DIGEST-community.md: "
      "rank | technique | source | effort_S/M/L | expected_gain | rationale | status (TODO/DONE/SUPERSEDED). "
      "(4) 'OurAnalysisSummary' — distill our own 6 analysis-*.md files into key conclusions per file. "
      "Use openpyxl. Acceptance: xlsx with all 4 sheets; >=30 community-code rows; >=20 facts; >=9 backlog rows."
    ),
    "allowed_area": f"{XLSX_DIR}community_and_tabs.xlsx, tests/test_community_and_tabs.py",
    "priority": "P1", "est_hours": 1.5, "status": "BACKLOG",
  },
  {
    # ----- The synthesis: SOURCE_OF_TRUTH for what to ship next -----
    "id": "TASK-XLSX-master-roadmap",
    "title": "Excel: master roadmap consolidating findings from the 3 other workbooks into a single shippable plan",
    "spec": (
      "This task RUNS AFTER the other 3 xlsx tasks land. Read the 3 workbooks: "
      f"{XLSX_DIR}winner_code_analysis.xlsx, "
      f"{XLSX_DIR}discussions_extract.xlsx, "
      f"{XLSX_DIR}community_and_tabs.xlsx. "
      "Synthesize them into ONE master workbook at "
      f"{XLSX_DIR}master_roadmap.xlsx with these sheets: "
      "(1) 'RankedExperiments' — every experiment we should run, ranked by (expected_cv_delta / effort): "
      "rank | name | hypothesis | source_evidence | expected_delta | effort_hours | depends_on | code_change_summary. "
      "(2) 'NextWeekPlan' — exactly which experiments to run in days 1-7 toward 0.85 LB; "
      "include a Gantt-style sheet: day | experiment | who (operator / Jules / GPU) | expected_outcome. "
      "(3) 'CurrentNotebookGaps' — line-by-line diff: what notebook_fork_working.ipynb does vs what winner does, "
      "with the exact change. (4) 'SubmissionStrategy' — when to submit, what cv-thresholds to gate on, "
      "how to use the 5/day cap intelligently across 15 days. "
      "Use openpyxl, read the input xlsx with openpyxl.load_workbook. "
      "BLOCKED until the other 3 xlsx tasks are DONE. "
      "Acceptance: xlsx with all 4 sheets; >=15 ranked experiments; 7-day plan; >=10 gap rows."
    ),
    "allowed_area": f"{XLSX_DIR}master_roadmap.xlsx, tests/test_master_roadmap.py",
    "priority": "P0", "est_hours": 1.5, "status": "BACKLOG",
    "blocked_by": "TASK-XLSX-winner-code-analysis",  # rough — will be unblocked when all 3 land
  },
]

ops = []
hyp_id = "H-DEEP-ANALYSIS-XLSX"
ops.append({"op":"create_hypothesis","idempotency_key":f"{TICK}:{hyp_id}",
  "data":{"id":hyp_id,
    "title":"Structured xlsx synthesis of every scraped source produces the highest-quality input for next code push",
    "statement":("Per-source markdown is hard to compare/rank. Structured Excel sheets with the same column "
                 "vocabulary across sources (winner code, 217 discussions, community, tabs) make the operator's "
                 "next-experiment decision provable: rank by (expected_cv_delta / effort), pick the top, push it."),
    "expected_effect":("Decision quality. Replaces 'operator skim 1MB of markdown' with 'operator reads 5-sheet xlsx "
                       "with ranked experiments + code-change pseudocode for each.'"),
    "how_to_test":"4 workbooks materialize within ~6h Jules-wall-clock; next code push cites a specific xlsx row.",
    "source_refs":["references/winner-*.md (17)","references/discussion-*.md (217)","references/community-sources.md","references/tab-*.md (7)"],
    "status":"PROPOSED","created_at":TS}})

for t in tasks:
    ops.append({"op":"create_task","idempotency_key":f"{TICK}:{t['id']}",
      "data":{**t, "hypothesis_id":hyp_id, "created_at":TS}})

decision = {"tick_id":TICK,"status":"complete",
  "summary":"campaign EXCEL-1: 4 deep-analysis xlsx tasks (winner-code, discussions, community/tabs, master-roadmap)",
  "state_patch":{"tick_id":TICK,"operations":ops}}
Path("_excel.json").write_text(json.dumps(decision), encoding="utf-8")
print(f"wrote {len(ops)} ops ({len(tasks)} xlsx tasks)")

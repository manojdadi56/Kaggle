#!/usr/bin/env python3
import argparse
from pathlib import Path
import shutil
from workbook_init import create_state_workbook, create_index_workbook


def write_if_missing(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def bootstrap(project_id, project_root, central_root, project_name=None, cadence="90m"):
    project_root = Path(project_root).resolve()
    central_root = Path(central_root).resolve()
    project_name = project_name or project_id
    sdlc_dir = project_root / ".sdlc"
    central_project = central_root / "projects" / project_id
    for p in [sdlc_dir, sdlc_dir / "progress_docs", sdlc_dir / "state_patches", sdlc_dir / "artifacts", sdlc_dir / "review_notes", sdlc_dir / "test_notes", sdlc_dir / "research_notes", sdlc_dir / "locks", central_project, central_project / "snapshots", central_project / "exports", central_project / "locks"]:
        p.mkdir(parents=True, exist_ok=True)
    state_workbook = central_project / "state.xlsx"
    index_workbook = central_root / "sdlc_index.xlsx"
    if not state_workbook.exists():
        create_state_workbook(str(state_workbook), project_id)
    if not index_workbook.exists():
        create_index_workbook(str(index_workbook))
    project_yaml = f"""project_id: {project_id}
project_name: {project_name}
project_root: {project_root}
central_root: {central_root}
state_workbook: {state_workbook}
cadence: {cadence}
owner_policy:
  max_parallel_owners: 1
  commit_when_coherent: true
  require_tests_or_reason: true
role_policy:
  prevent_adjacent_repeat: true
  reviewer_blocks_active_owner_task: true
  tester_requires_implementation: true
validation_policy:
  minor: 1
  small: 3
  medium: 5
  large: 7
  very_large: 9
"""
    write_if_missing(sdlc_dir / "project.yaml", project_yaml)
    write_if_missing(sdlc_dir / "USER_CONTEXT.md", "# USER_CONTEXT.md\n\nAdd user guidance here. Every SDLC run reads this file.\n")
    write_if_missing(sdlc_dir / "PROJECT_MEMORY.md", "# PROJECT_MEMORY.md\n\nDurable project facts only. Do not store full transcripts or hidden reasoning.\n")
    write_if_missing(project_root / "AGENTS.md", "# AGENTS.md\n\n## Repository expectations\n\n- Read `.sdlc/project.yaml` before SDLC automation work.\n- Only the SDLC Owner role may modify product code during scheduled runs.\n- Replace this file with project-specific build, test, and review instructions.\n")
    return {"project_root": str(project_root), "central_root": str(central_root), "state_workbook": str(state_workbook), "index_workbook": str(index_workbook)}


def main():
    parser = argparse.ArgumentParser(description="Bootstrap a project for the SDLC Skill Mesh.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-name")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--central-root", required=True)
    parser.add_argument("--cadence", default="90m")
    args = parser.parse_args()
    result = bootstrap(args.project_id, args.project_root, args.central_root, args.project_name, args.cadence)
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()

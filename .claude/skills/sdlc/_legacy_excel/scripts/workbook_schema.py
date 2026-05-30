SHEETS = {
    "Dashboard": ["field", "value", "notes"],
    "Events": ["event_id", "project_id", "run_id", "created_at", "event_type", "entity_type", "entity_id", "summary", "idempotency_key", "details_json"],
    "Runs_Attendance": ["run_id", "project_id", "triggered_at", "started_at", "ended_at", "status", "role_selected", "role_selection_reason", "roles_feasible", "roles_rejected", "work_item_id", "task_id", "phase_id", "story_id", "lock_ids", "started_state", "completed_state", "high_level_completed", "project_movement_long", "artifacts_created", "commits_created", "tests_run", "new_work_items_created", "next_recommended_role", "saturation_status", "errors"],
    "Locks": ["lock_id", "project_id", "lock_type", "scope_type", "scope_id", "holder_run_id", "holder_role", "created_at", "heartbeat_at", "expires_at", "status", "reclaim_reason"],
    "RoleHistory": ["run_id", "project_id", "created_at", "role_selected", "previous_role", "roles_feasible", "roles_rejected", "selection_reason", "work_item_id"],
    "Phases": ["phase_id", "project_id", "title", "goal", "status", "priority", "created_at", "updated_at", "version", "notes"],
    "UserStories": ["story_id", "phase_id", "project_id", "title", "user_story", "acceptance_summary", "status", "priority", "created_at", "updated_at", "version", "notes"],
    "Tasks": ["task_id", "story_id", "phase_id", "project_id", "title", "goal", "status", "priority", "role_owner", "acceptance_criteria", "definition_of_done", "dependencies", "allowed_area", "test_expectation", "risk_level", "estimated_size", "created_from", "created_by_run", "assigned_owner", "branch", "commit_sha", "created_at", "updated_at", "version", "notes"],
    "SupportWork": ["support_id", "project_id", "role", "source_id", "title", "goal", "status", "priority", "dependencies", "created_by_run", "created_at", "updated_at", "version", "notes"],
    "TaskProgressDocs": ["progress_doc_id", "project_id", "task_id", "run_id", "role", "path", "summary", "status", "sha256", "created_at"],
    "Suggestions": ["suggestion_id", "project_id", "source_role", "source_id", "title", "change_size", "expected_benefit", "risk", "status", "planner_triage", "validation_required", "validation_passes_required", "created_by_run", "created_at", "updated_at", "notes"],
    "Validations": ["validation_id", "project_id", "suggestion_id", "run_id", "validator_profile", "vote", "confidence", "rationale", "risk_notes", "implementation_notes", "test_implications", "ops_implications", "created_at"],
    "Decisions": ["decision_id", "project_id", "run_id", "entity_type", "entity_id", "decision", "rationale", "validation_summary", "tasks_created", "risks_accepted", "created_at"],
    "UserFeedback_Inbox": ["feedback_id", "project_id", "created_at", "user_name", "feedback_text", "priority_hint", "area_hint", "desired_outcome", "status", "planner_run_id", "converted_to", "planner_notes"],
    "UserContext": ["context_id", "project_id", "active", "scope", "instruction", "created_at", "updated_at", "notes"],
    "ProjectMemory_Index": ["memory_id", "project_id", "status", "scope", "fact", "source_run_id", "source_artifact_id", "created_at", "updated_at", "confidence", "notes"],
    "ArtifactRegistry": ["artifact_id", "project_id", "run_id", "task_id", "artifact_type", "path", "summary", "sha256", "commit_sha", "created_at", "created_by_role", "notes"],
    "InnovationLog": ["innovation_id", "project_id", "run_id", "source_type", "title", "authors_or_org", "published_or_updated_date", "retrieved_at", "source_ref", "summary", "techniques_observed", "architecture_patterns", "evaluation_methods", "implementation_details", "relevance_to_project", "risk_or_limitations", "suggested_actions", "confidence", "annotation"],
    "MaintainerFindings": ["finding_id", "project_id", "run_id", "area", "finding_type", "severity", "summary", "evidence", "suggestion_id", "created_at", "notes"],
    "ReviewFindings": ["review_id", "project_id", "run_id", "task_id", "finding_type", "severity", "summary", "evidence", "status", "followup_task_id", "created_at", "notes"],
    "TestFindings": ["test_id", "project_id", "run_id", "task_id", "test_command", "result", "summary", "failure_excerpt", "coverage_gap", "followup_task_id", "created_at", "notes"],
    "Metrics": ["metric_id", "project_id", "run_id", "metric_name", "metric_value", "unit", "period_start", "period_end", "created_at", "notes"]
}

STATUS_VALUES = [
    "NOT_STARTED", "READY", "CLAIMED", "IN_PROGRESS", "SATURATED", "BLOCKED",
    "READY_FOR_REVIEW", "CHANGES_REQUESTED", "READY_FOR_TEST", "DONE_PENDING_REVIEW",
    "DONE_PENDING_TEST", "DONE", "SUPERSEDED", "REJECTED", "VALIDATION_REQUIRED", "ACCEPTED"
]

ROLE_NAMES = ["planner", "owner", "reviewer", "tester", "maintainer", "innovator", "validator", "reporter"]

VALIDATION_COUNTS = {
    "minor": 1,
    "small": 3,
    "medium": 5,
    "large": 7,
    "very_large": 9
}

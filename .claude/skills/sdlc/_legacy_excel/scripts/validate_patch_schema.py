#!/usr/bin/env python3
"""Validate a StatePatch JSON file against the operation contract.

Usage:
  python3 validate_patch_schema.py --patch PATH

Exit 0 = valid. Exit 1 = invalid (errors printed as JSON).
"""
import argparse
import json
import sys
from pathlib import Path

ALLOWED_OPS = {
    "append_event",
    "append_row",
    "update_row_by_id",
    "update_status",
    "create_task",
    "create_support_work",
    "create_suggestion",
    "create_validation",
    "create_decision",
    "register_artifact",
    "add_metric",
    "add_memory_candidate",
    "start_attendance",
    "close_attendance",
}

REQUIRED_TOP = {"patch_id", "run_id", "project_id", "operations"}


def validate(patch):
    errors = []
    missing = REQUIRED_TOP - set(patch.keys())
    if missing:
        errors.append({"field": "<top>", "error": f"missing_fields: {sorted(missing)}"})
    ops = patch.get("operations", [])
    if not isinstance(ops, list) or not ops:
        errors.append({"field": "operations", "error": "must_be_non_empty_list"})
        return errors
    seen_keys = set()
    for i, op in enumerate(ops):
        prefix = f"operations[{i}]"
        if not isinstance(op, dict):
            errors.append({"field": prefix, "error": "not_an_object"})
            continue
        name = op.get("op")
        if name not in ALLOWED_OPS:
            errors.append({"field": f"{prefix}.op", "error": f"unknown_op: {name}"})
            continue
        if "idempotency_key" not in op or not op["idempotency_key"]:
            errors.append({"field": f"{prefix}.idempotency_key", "error": "required"})
        else:
            k = op["idempotency_key"]
            if k in seen_keys:
                errors.append({"field": f"{prefix}.idempotency_key", "error": f"duplicate_within_patch: {k}"})
            seen_keys.add(k)
        if name in {"update_row_by_id", "update_status"}:
            if "sheet" not in op:
                errors.append({"field": f"{prefix}.sheet", "error": "required_for_update"})
            if "entity_id" not in op:
                errors.append({"field": f"{prefix}.entity_id", "error": "required_for_update"})
            if name == "update_status":
                if "to_status" not in op:
                    errors.append({"field": f"{prefix}.to_status", "error": "required"})
        if name in {
            "append_event", "append_row", "create_task", "create_support_work",
            "create_suggestion", "create_validation", "create_decision",
            "register_artifact", "add_metric", "add_memory_candidate",
            "start_attendance", "close_attendance",
        }:
            if "data" in op and not isinstance(op["data"], dict):
                errors.append({"field": f"{prefix}.data", "error": "must_be_object"})
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--patch", required=True)
    args = p.parse_args()
    path = Path(args.patch)
    if not path.exists():
        print(json.dumps({"error": "patch_not_found", "path": str(path)}))
        sys.exit(1)
    try:
        patch = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "invalid_json", "detail": str(e)}))
        sys.exit(1)
    errs = validate(patch)
    if errs:
        print(json.dumps({"valid": False, "errors": errs}, indent=2))
        sys.exit(1)
    print(json.dumps({"valid": True, "operation_count": len(patch["operations"])}))
    sys.exit(0)


if __name__ == "__main__":
    main()

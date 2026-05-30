#!/usr/bin/env python3
"""Scan a RunResult / artifact / patch JSON file for audit-safety violations.

Detects rough proxies for hidden chain-of-thought leakage:
  - Long uninterrupted prose blocks in fields meant to be structured rationale.
  - Forbidden markers ("let me think", "i'll consider", "internal:", "scratchpad:", "<thinking>", etc).
  - Free-text reasoning > N chars in audit-critical fields.

Usage:
  python3 audit_check.py --result PATH [--max-rationale-chars 800]

Exit 0 = clean. Exit 1 = violations found (printed as JSON).
"""
import argparse
import json
import re
import sys
from pathlib import Path

FORBIDDEN_MARKERS = [
    r"\blet me think\b",
    r"\bi['']?ll consider\b",
    r"\bi['']?m thinking\b",
    r"\binternal[: ]",
    r"\bscratchpad[: ]",
    r"<thinking>",
    r"</thinking>",
    r"\bchain[- ]of[- ]thought\b",
    r"\bok,? so\b",
    r"\bhmm,?\b",
    r"\bwait,?\b",
    r"\blet's see\b",
    r"\bactually,?\b",
]

AUDIT_CRITICAL_FIELDS = {"rationale", "summary", "high_level_completed", "notes", "rationale_summary", "reason_summary", "role_selection_reason"}


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def check(data, max_rationale_chars=800):
    findings = []
    pattern = re.compile("|".join(FORBIDDEN_MARKERS), re.IGNORECASE)
    for path, value in walk(data):
        if not isinstance(value, str):
            continue
        m = pattern.search(value)
        if m:
            findings.append({
                "field": path,
                "violation": "forbidden_marker",
                "match": m.group(0),
                "context": value[:160] + ("..." if len(value) > 160 else ""),
            })
        leaf = path.split(".")[-1].split("[")[0]
        if leaf in AUDIT_CRITICAL_FIELDS and len(value) > max_rationale_chars:
            findings.append({
                "field": path,
                "violation": "rationale_too_long",
                "length": len(value),
                "limit": max_rationale_chars,
            })
    return findings


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--result", required=True, help="JSON file to audit (RunResult, patch, or any JSON artifact)")
    p.add_argument("--max-rationale-chars", type=int, default=800)
    args = p.parse_args()
    path = Path(args.result)
    if not path.exists():
        print(json.dumps({"error": "file_not_found", "path": str(path)}))
        sys.exit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "invalid_json", "detail": str(e)}))
        sys.exit(1)
    findings = check(data, max_rationale_chars=args.max_rationale_chars)
    if findings:
        print(json.dumps({"clean": False, "findings": findings}, indent=2))
        sys.exit(1)
    print(json.dumps({"clean": True}))
    sys.exit(0)


if __name__ == "__main__":
    main()

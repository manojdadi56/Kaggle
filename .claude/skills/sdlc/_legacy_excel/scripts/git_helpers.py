#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def run_git(repo, args):
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    return {"args": args, "returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}


def main():
    parser = argparse.ArgumentParser(description="Small Git helper for SDLC skill runs.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("cmd", choices=["status", "diff", "branch", "log", "commit"])
    parser.add_argument("--message")
    parser.add_argument("--paths", nargs="*")
    args = parser.parse_args()
    if args.cmd == "status":
        result = run_git(args.repo, ["status", "--short"])
    elif args.cmd == "diff":
        result = run_git(args.repo, ["diff", "--", *(args.paths or [])])
    elif args.cmd == "branch":
        result = run_git(args.repo, ["branch", "--show-current"])
    elif args.cmd == "log":
        result = run_git(args.repo, ["log", "-5", "--oneline"])
    else:
        if not args.message:
            raise SystemExit("--message required for commit")
        result = run_git(args.repo, ["add", *(args.paths or ["."])])
        if result["returncode"] == 0:
            result = run_git(args.repo, ["commit", "-m", args.message])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

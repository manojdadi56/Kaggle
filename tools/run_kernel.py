#!/usr/bin/env python3
import argparse
import json
import sys
import time
from pathlib import Path

# Insert current dir to sys.path to easily import tools.kaggle_lite
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools import kaggle_lite

def main():
    parser = argparse.ArgumentParser(description="End-to-end Kaggle kernel runner.")
    parser.add_argument("--kernel-dir", required=True, type=str, help="Directory containing the kernel to push")
    parser.add_argument("--owner", required=True, type=str, help="Kaggle user owner of the kernel")
    parser.add_argument("--slug", required=True, type=str, help="Kaggle kernel slug")
    parser.add_argument("--out-dir", required=True, type=str, help="Directory to download the kernel output to")
    parser.add_argument("--poll-secs", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--timeout-mins", type=int, default=240, help="Timeout in minutes")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")

    args = parser.parse_args()
    kernel_url = f"https://www.kaggle.com/code/{args.owner}/{args.slug}"

    if args.mock:
        summary = {
            "kernel_url": kernel_url,
            "terminal_state": "complete",
            "cv_aggregate": 0.50,
            "elapsed_secs": 10
        }
        print(json.dumps(summary))
        sys.exit(0)

    start_time = time.time()

    # 1. Call kaggle_lite.kernel_push
    push_res = kaggle_lite.kernel_push(Path(args.kernel_dir))
    if push_res.get("status") != 200:
        print(f"Error pushing kernel: {push_res}", file=sys.stderr)
        sys.exit(1)

    try:
        body = json.loads(push_res.get("body", "{}"))
        ref = body.get("ref", f"{args.owner}/{args.slug}")
    except json.JSONDecodeError:
        ref = f"{args.owner}/{args.slug}"

    print(f"Kernel pushed successfully. Ref: {ref}", file=sys.stderr)

    # 2. Polling loop
    timeout_secs = args.timeout_mins * 60
    terminal_state = None

    while True:
        elapsed_secs = int(time.time() - start_time)
        if elapsed_secs > timeout_secs:
            summary = {
                "kernel_url": kernel_url,
                "terminal_state": "timeout",
                "cv_aggregate": None,
                "elapsed_secs": elapsed_secs
            }
            print(json.dumps(summary))
            sys.exit(2)

        status_res = kaggle_lite.kernel_status(f"{args.owner}/{args.slug}")
        if status_res.get("status") != 200:
            print(f"Error fetching kernel status: {status_res}", file=sys.stderr)
            sys.exit(1)

        try:
            status_body = json.loads(status_res.get("body", "{}"))
            current_status = status_body.get("status", "unknown")
        except json.JSONDecodeError:
            current_status = "unknown"

        if current_status == "complete":
            terminal_state = "complete"
            break
        elif current_status in ("error", "cancel", "cancelled"):
            terminal_state = current_status
            summary = {
                "kernel_url": kernel_url,
                "terminal_state": terminal_state,
                "cv_aggregate": None,
                "elapsed_secs": elapsed_secs
            }
            print(json.dumps(summary))
            sys.exit(1)

        time.sleep(args.poll_secs)

    # 3. Output download and summary
    out_res = kaggle_lite.kernel_output(f"{args.owner}/{args.slug}", Path(args.out_dir))
    if out_res.get("status") != 200:
        print(f"Error downloading kernel output: {out_res}", file=sys.stderr)
        sys.exit(1)

    cv_aggregate = None
    cv_score_path = Path(args.out_dir) / "cv_score.json"
    if cv_score_path.exists():
        try:
            cv_data = json.loads(cv_score_path.read_text(encoding="utf-8"))
            cv_aggregate = cv_data.get("cv_aggregate")
        except Exception as e:
            print(f"Warning: could not parse cv_score.json: {e}", file=sys.stderr)

    elapsed_secs = int(time.time() - start_time)
    summary = {
        "kernel_url": kernel_url,
        "terminal_state": terminal_state,
        "cv_aggregate": cv_aggregate,
        "elapsed_secs": elapsed_secs
    }
    print(json.dumps(summary))
    sys.exit(0)

if __name__ == "__main__":
    main()

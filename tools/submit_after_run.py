"""Automate post-GPU-run submission.

Given a Kaggle notebook slug (default: sai1881/nvidia-nemotron-submission-demo), this:
  1. Polls get_notebook_session_status — bails if not COMPLETE
  2. download_notebook_output (the output dir contains adapter_config.json + adapter_model* + submission.zip)
  3. Reads cv_score.json to get the local CV
  4. Loads state.json best_cv; if new > best, decides to submit
  5. Calls submit_to_competition with the submission.zip
  6. Calls get_competition_leaderboard, captures our rank
  7. Updates state via record_cv_score op
  8. Appends a structured event to state/run_log.jsonl

This is the post-run automation that the campaign's been gated on. Run it after the
user clicks Save & Run All and the kernel terminalizes.

Usage:
    python tools/submit_after_run.py
    python tools/submit_after_run.py --slug sai1881/my-other-fork --account 0
    python tools/submit_after_run.py --dry-run  # don't actually submit
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV = REPO / ".env"
STATE = REPO / "state" / "state.json"
RUN_LOG = REPO / "state" / "run_log.jsonl"
COMP_SLUG = "nvidia-nemotron-model-reasoning-challenge"


def _env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV.exists():
        return out
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _mcp(tok: str, name: str, args: dict, timeout: int = 180) -> str:
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": name, "arguments": args}}
    req = urllib.request.Request(
        "https://www.kaggle.com/mcp",
        data=json.dumps(rpc).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "Accept": "application/json,text/event-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            d = json.loads(line[6:])
            return d.get("result", {}).get("content", [{}])[0].get("text", "")
    return body


def _today_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).date().isoformat()


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", default="sai1881/nvidia-nemotron-submission-demo",
                   help="notebook slug (user/slug)")
    p.add_argument("--account", type=int, default=0, help="0=sai1881 / 1=akhildadi")
    p.add_argument("--dry-run", action="store_true", help="don't actually submit")
    p.add_argument("--force-submit", action="store_true",
                   help="submit even if cv doesn't beat best_cv")
    p.add_argument("--message", default="auto-submit via tools/submit_after_run.py",
                   help="submission message")
    args = p.parse_args(argv)

    env = _env()
    if args.account == 0:
        user_env, tok_env = "KAGGLE_USERNAME", "KAGGLE_API_TOKEN"
    else:
        user_env, tok_env = "KAGGLE_USERNAME_2", "KAGGLE_API_TOKEN_2"
    user_name = env.get(user_env)
    tok = env.get(tok_env)
    if not (user_name and tok):
        print(f"ERROR: missing creds for account {args.account}", file=sys.stderr)
        return 2

    slug_user, slug_kernel = args.slug.split("/", 1)

    # === Step 1: poll status ===
    print(f"[1] polling status of {args.slug} ...")
    status_raw = _mcp(tok, "get_notebook_session_status",
                      {"request": {"userName": slug_user, "kernelSlug": slug_kernel}})
    try:
        status = json.loads(status_raw).get("status", "?")
    except Exception:
        status = status_raw[:200]
    print(f"    status: {status}")
    if "COMPLETE" not in str(status).upper():
        print(f"    not COMPLETE -- bailing. Re-run after Save & Run All terminalizes.")
        return 1

    # === Step 2: download output ===
    out_dir = Path(tempfile.mkdtemp(prefix="kaggle_out_"))
    print(f"[2] downloading outputs to {out_dir} ...")
    # MCP `download_notebook_output_zip` returns a zip blob — use the kaggle python API instead
    os.environ.setdefault("KAGGLE_USERNAME", user_name)
    os.environ.setdefault("KAGGLE_API_TOKEN", tok)
    try:
        import kaggle  # noqa
        api = kaggle.KaggleApi(); api.authenticate()
        api.kernels_output(args.slug, path=str(out_dir))
        print(f"    downloaded files: {[p.name for p in out_dir.iterdir()][:10]}")
    except Exception as e:
        print(f"    kernel output download err: {e}")
        return 3

    cv_path = out_dir / "cv_score.json"
    sub_zip = out_dir / "submission.zip"
    if not sub_zip.exists():
        print(f"    no submission.zip — adapter wasn't packaged. Check notebook cell 4.")
        return 4
    cv = None
    if cv_path.exists():
        try:
            cv = json.loads(cv_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"    cv_score.json parse err: {e}")
    print(f"    cv_score.json: {cv}")

    # === Step 3: compare to best_cv ===
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    best = state.get("best_cv")
    new_score = cv.get("score") if cv else None
    print(f"[3] best_cv: {best}  new: {new_score}")
    if not args.force_submit:
        if new_score is None:
            print("    no score available — bailing"); return 5
        if best is not None and new_score <= best:
            print("    new score does NOT beat best — skipping submit (use --force-submit to override)")
            return 0

    # === Step 4: daily submit cap check ===
    submits_today = state.get("submits_by_day_by_account", {}).get(_today_utc(), {}).get(str(args.account), 0)
    if submits_today >= 3 and not args.force_submit:
        print(f"    account {args.account} already used {submits_today}/3 auto-submits today — bailing")
        return 6

    # === Step 5: submit ===
    if args.dry_run:
        print(f"[5] DRY RUN: would call submit_to_competition with {sub_zip}")
    else:
        print(f"[5] uploading submission.zip ...")
        # Use the kaggle python API for the actual submit
        try:
            r = api.competition_submit(file_name=str(sub_zip), message=args.message,
                                       competition=COMP_SLUG, quiet=False)
            print(f"    submitted: {r}")
        except Exception as e:
            print(f"    submit err: {e}")
            return 7

        # === Step 6: leaderboard rank ===
        try:
            lb = api.competition_view_leaderboard(competition=COMP_SLUG)
            # find our entry
            for entry in lb[:50]:
                if hasattr(entry, "teamName") and entry.teamName and user_name in str(entry.teamName):
                    print(f"    LB rank: {getattr(entry, 'rank', '?')} | score: {getattr(entry, 'score', '?')}")
                    break
        except Exception as e:
            print(f"    leaderboard fetch err: {e}")

    # === Step 7: write event ===
    event = {
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "tool": "submit_after_run",
        "slug": args.slug,
        "account": args.account,
        "local_cv": new_score,
        "previous_best_cv": best,
        "submitted": not args.dry_run,
        "submission_message": args.message,
    }
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    print(f"[7] event logged.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

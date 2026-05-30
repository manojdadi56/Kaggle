"""End-to-end auto-submit: pull notebook output -> read cv_score -> validate -> submit -> leaderboard.

Use after a Kaggle notebook session reaches COMPLETE. Reads the kernel slug, downloads its
output zip, parses cv_score.json + the embedded submission.zip, records the CV into our
ledger, and (if cv > best_cv AND today's auto-submit count < cap) fires submit_to_competition
via the kaggle MCP, then reports the leaderboard rank.

Usage:
    python tools/auto_submit.py --slug nvidia-nemotron-submission-demo \
                                --competition nvidia-nemotron-model-reasoning-challenge \
                                [--force]   # bypass cv>best_cv check
                                [--dry-run] # everything except the actual submit_to_competition call

Honors guardrails: <=3 auto-submits/day, 2 finals reserved, never submits a worse CV.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import zipfile
import io
from pathlib import Path
from datetime import datetime, timezone


REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"
STATE_PATH = REPO / "state" / "state.json"
MAX_AUTO_SUBMITS_PER_DAY = 3  # operator default; respects 5/day real cap with 2 finals reserved


def _env() -> dict[str, str]:
    return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in ENV_PATH.read_text(encoding="utf-8").splitlines()
            if l and "=" in l and not l.startswith("#")}


def _mcp(name: str, arguments: dict, timeout: int = 120, raw: bool = False) -> str:
    """Call a kaggle MCP tool via JSON-RPC; return the text content (or raw body if raw=True)."""
    tok = _env()["KAGGLE_API_TOKEN"]
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": name, "arguments": arguments}}
    req = urllib.request.Request(
        "https://www.kaggle.com/mcp",
        data=json.dumps(rpc).encode(),
        headers={"Authorization": f"Bearer {tok}",
                 "Content-Type": "application/json",
                 "Accept": "application/json,text/event-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    if raw:
        return body
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result", {}).get("content", [{}])[0].get("text", "")
    return body


def get_session_status(slug: str, user: str) -> str:
    out = _mcp("get_notebook_session_status", {"request": {"userName": user, "kernelSlug": slug}})
    try:
        return json.loads(out).get("status", "?")
    except Exception:
        return out[:200]


def list_outputs(slug: str, user: str) -> dict:
    out = _mcp("list_notebook_session_output", {"request": {"userName": user, "kernelSlug": slug}})
    try:
        return json.loads(out)
    except Exception:
        return {"raw": out[:500]}


def fetch_output_file(slug: str, user: str, file_path: str) -> bytes:
    """download_notebook_output returns a download URL; fetch the bytes."""
    out = _mcp("download_notebook_output",
               {"request": {"ownerSlug": user, "kernelSlug": slug, "filePath": file_path}})
    # The MCP tool returns either bytes (b64) or a URL — parse accordingly
    try:
        obj = json.loads(out)
    except Exception:
        obj = {"raw": out}
    url = obj.get("url") or obj.get("download_url") or obj.get("signedUrl")
    if url:
        with urllib.request.urlopen(url, timeout=300) as r:
            return r.read()
    if "b64" in obj or "content_b64" in obj:
        import base64
        return base64.b64decode(obj.get("b64") or obj["content_b64"])
    raise RuntimeError(f"could not extract bytes from download_notebook_output: keys={list(obj.keys())[:5]}")


def submits_today(state: dict) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return state.get("submits_by_day", {}).get(today, 0)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slug", required=True, help="kernel slug, e.g. nvidia-nemotron-submission-demo")
    ap.add_argument("--user", default=None, help="kaggle username (default from $KAGGLE_USERNAME)")
    ap.add_argument("--competition", default="nvidia-nemotron-model-reasoning-challenge")
    ap.add_argument("--force", action="store_true", help="submit even if CV does not beat best_cv")
    ap.add_argument("--dry-run", action="store_true", help="do everything except the actual competition submit")
    ap.add_argument("--message", default=None, help="submission description")
    args = ap.parse_args(argv)

    env = _env()
    user = args.user or env.get("KAGGLE_USERNAME", "sai1881")

    # 1. Confirm session is terminal-complete
    status = get_session_status(args.slug, user)
    print(f"session status: {status}")
    if "COMPLETE" not in str(status).upper():
        print(f"REFUSE: session is not COMPLETE (status={status})", file=sys.stderr)
        return 2

    # 2. List output files, find submission.zip + cv_score.json
    outputs = list_outputs(args.slug, user)
    files = outputs.get("files", []) or outputs.get("output_files", [])
    if isinstance(files, list) and files:
        names = [f.get("name") or f.get("path") or str(f) for f in files]
    else:
        # Some versions of the API only return log; fall back to known paths
        names = ["submission.zip", "cv_score.json"]
    print(f"output files: {names[:10]}")

    sub_name = next((n for n in names if str(n).endswith("submission.zip")), "submission.zip")
    cv_name = next((n for n in names if str(n).endswith("cv_score.json")), "cv_score.json")

    # 3. Download submission.zip + cv_score.json bytes
    try:
        sub_bytes = fetch_output_file(args.slug, user, sub_name)
        print(f"submission.zip: {len(sub_bytes)} bytes")
    except Exception as e:
        print(f"submission.zip fetch failed: {e}", file=sys.stderr)
        return 3

    try:
        cv_bytes = fetch_output_file(args.slug, user, cv_name)
        cv_score = json.loads(cv_bytes.decode("utf-8"))
        print(f"cv_score: {cv_score}")
    except Exception as e:
        print(f"cv_score.json fetch failed: {e}; proceeding with cv=None", file=sys.stderr)
        cv_score = {"score": None}

    # 4. Save outputs locally for the ledger
    out_dir = REPO / "competitions" / "nvidia-nemotron-model-reasoning-challenge" / "experiments" / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "submission.zip").write_bytes(sub_bytes)
    (out_dir / "cv_score.json").write_text(json.dumps(cv_score, indent=2), encoding="utf-8")
    print(f"saved outputs to {out_dir}")

    # 5. Verify zip is non-empty and has adapter_config.json
    try:
        with zipfile.ZipFile(io.BytesIO(sub_bytes)) as zf:
            zip_names = zf.namelist()
            assert "adapter_config.json" in zip_names, f"submission.zip missing adapter_config.json (has {zip_names})"
            with zf.open("adapter_config.json") as af:
                cfg = json.load(af)
            assert cfg.get("r", 999) <= 32, f"adapter rank {cfg.get('r')} > 32 (host max)"
        print(f"submission.zip validated (rank={cfg.get('r')}, files={zip_names})")
    except Exception as e:
        print(f"submission.zip INVALID: {e}", file=sys.stderr)
        return 4

    # 6. Check submit gate: cv > best_cv, daily cap, headroom
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    best_cv = state.get("best_cv")
    cur_cv = cv_score.get("score")
    n_today = submits_today(state)

    if cur_cv is None and not args.force:
        print(f"REFUSE: cv_score is None and --force not set", file=sys.stderr)
        return 5
    if best_cv is not None and cur_cv is not None and cur_cv <= best_cv and not args.force:
        print(f"REFUSE: cv {cur_cv} does not beat best {best_cv}", file=sys.stderr)
        return 6
    if n_today >= MAX_AUTO_SUBMITS_PER_DAY and not args.force:
        print(f"REFUSE: {n_today} auto-submits already today (cap {MAX_AUTO_SUBMITS_PER_DAY})", file=sys.stderr)
        return 7

    # 7. Live submission-count check (real cap is 5/day)
    try:
        live = _mcp("search_competition_submissions",
                    {"request": {"competitionName": args.competition, "pageSize": 20}})
        live_obj = json.loads(live)
        today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        live_today = sum(1 for s in live_obj.get("submissions", [])
                         if str(s.get("submitted_at", "")).startswith(today_iso))
        print(f"live submissions today (kaggle): {live_today} / 5")
        if live_today >= 4 and not args.force:
            print(f"REFUSE: live cap headroom too low ({live_today}/5; reserving 2 finals)", file=sys.stderr)
            return 8
    except Exception as e:
        print(f"warning: could not check live submission count ({e}); proceeding")

    # 8. Submit (or dry-run)
    msg = args.message or f"{args.slug} cv={cur_cv}"
    if args.dry_run:
        print(f"DRY-RUN: would submit '{sub_name}' ({len(sub_bytes)} bytes) with message '{msg}'")
        return 0

    # Need to upload first to get a blob token, then submit_to_competition
    upload = _mcp("start_competition_submission_upload",
                  {"request": {"competitionName": args.competition,
                               "fileName": "submission.zip",
                               "contentLength": len(sub_bytes)}})
    try:
        u = json.loads(upload)
    except Exception:
        u = {}
    upload_url = u.get("createUrl") or u.get("uploadUrl") or u.get("url")
    blob_token = u.get("token") or u.get("blobFileToken")
    if upload_url:
        put = urllib.request.Request(upload_url, data=sub_bytes, method="PUT",
                                     headers={"Content-Type": "application/octet-stream",
                                              "x-goog-content-length-range": f"{len(sub_bytes)},{len(sub_bytes)}"})
        with urllib.request.urlopen(put, timeout=600) as r:
            print(f"upload PUT status: {r.status}")

    submit = _mcp("submit_to_competition",
                  {"request": {"competitionName": args.competition,
                               "blobFileTokens": blob_token,
                               "submissionDescription": msg}})
    print(f"submit result: {submit}")

    # 9. Leaderboard look-up
    try:
        lb = _mcp("get_competition_leaderboard",
                  {"request": {"competitionName": args.competition, "pageSize": 20}})
        print(f"leaderboard sample: {lb[:500]}")
    except Exception as e:
        print(f"leaderboard lookup err: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

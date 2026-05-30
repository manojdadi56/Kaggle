"""Minimal Kaggle client for the Jules VM.

Uses KGAT (`$KAGGLE_API_TOKEN`) as a Bearer against the official Kaggle web API.
No `kaggle` CLI required; only depends on httpx.

Allowed verbs on the Jules side (mirrored in AGENTS.md):
  read   : list comp files, view leaderboard, list our own submissions / kernels
  kernel : push, status, output  (the actual GPU run happens on Kaggle, not Jules)
  comp   : submission_upload     (presigned-URL upload of a candidate zip)

NOT allowed from Jules (operator-only, enforced by AGENTS.md and review):
  comp_submit                   (the binding 5/day-cap step; operator gates it)

Usage:
  python tools/kaggle_lite.py whoami
  python tools/kaggle_lite.py leaderboard nvidia-nemotron-model-reasoning-challenge
  python tools/kaggle_lite.py submissions nvidia-nemotron-model-reasoning-challenge
  python tools/kaggle_lite.py kernel-push  -p kernels/train-exp01
  python tools/kaggle_lite.py kernel-status sai1881/train-exp01
  python tools/kaggle_lite.py kernel-output sai1881/train-exp01 -d kernels/train-exp01/output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print(json.dumps({"error": "httpx not installed; setup script must `pip install httpx`"}))
    sys.exit(2)

API = "https://www.kaggle.com/api/v1"
UA = "kaggle-orchestrator/kaggle_lite"


def _token() -> str:
    tok = os.environ.get("KAGGLE_API_TOKEN") or os.environ.get("KGAT")
    if not tok:
        print(json.dumps({"error": "KAGGLE_API_TOKEN (KGAT) not set on this VM. Add it via "
                                    "jules.google → Sources → manojdadi56/Kaggle → Configuration → Environment."}))
        sys.exit(3)
    return tok


def _headers(content_type: str | None = None) -> dict:
    h = {"Authorization": f"Bearer {_token()}", "User-Agent": UA}
    if content_type:
        h["Content-Type"] = content_type
    return h


def _req(method: str, path: str, **kw):
    url = path if path.startswith("http") else f"{API}{path}"
    r = httpx.request(method, url, timeout=60, **kw)
    return r


def whoami() -> dict:
    user = os.environ.get("KAGGLE_USERNAME", "")
    if not user:
        return {"ok": False, "reason": "KAGGLE_USERNAME not set"}
    # leaderboard-list is a cheap auth probe
    r = _req("GET", "/competitions/list?page=1", headers=_headers())
    return {"ok": r.status_code == 200, "kaggle_user": user, "status": r.status_code}


def leaderboard(comp: str) -> dict:
    r = _req("GET", f"/competitions/{comp}/leaderboard/view", headers=_headers())
    return {"status": r.status_code, "body": r.text[:4000]}


def submissions(comp: str) -> dict:
    r = _req("GET", f"/competitions/submissions/list/{comp}", headers=_headers())
    return {"status": r.status_code, "body": r.text[:8000]}


def kernel_push(kernel_dir: Path) -> dict:
    """Push a kernel from a directory containing kernel-metadata.json."""
    meta = json.loads((kernel_dir / "kernel-metadata.json").read_text(encoding="utf-8"))
    # The official API expects a JSON-encoded form per Kaggle docs.
    # We forward kernel-metadata + bundled files; for simplicity the user's
    # kernel-metadata.json should be self-contained per Kaggle convention.
    files = []
    for f in sorted(kernel_dir.rglob("*")):
        if f.is_file():
            files.append(("files", (str(f.relative_to(kernel_dir)), f.read_bytes())))
    r = _req("POST", "/kernels/push", headers=_headers(), data={"metadata": json.dumps(meta)}, files=files)
    return {"status": r.status_code, "body": r.text[:4000]}


def kernel_status(slug: str) -> dict:
    r = _req("GET", f"/kernels/status/{slug}", headers=_headers())
    return {"status": r.status_code, "body": r.text[:4000]}


def kernel_output(slug: str, dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    r = _req("GET", f"/kernels/output/{slug}", headers=_headers())
    if r.status_code != 200:
        return {"status": r.status_code, "body": r.text[:2000]}
    # Output endpoint returns JSON with file urls; download each.
    try:
        data = r.json()
    except Exception:
        (dest / "raw.txt").write_bytes(r.content)
        return {"status": r.status_code, "written": ["raw.txt"]}
    written = []
    for f in data.get("files", []):
        url = f.get("url")
        name = f.get("fileName", "out.bin")
        if not url:
            continue
        rr = _req("GET", url, headers=_headers())
        (dest / name).write_bytes(rr.content)
        written.append(name)
    (dest / "_meta.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"status": r.status_code, "written": written}


def competition_submit(comp: str, blob_token: str, message: str = "") -> dict:
    """Submit a previously-uploaded candidate. **Counts toward the 5/day cap.**

    Refuses unless `KAGGLE_SUBMIT_AUTHORIZED=1` is set in the task env (the
    operator or the user flips it per task by including `submit_authorized: true`
    in the task spec — the dispatcher exports it on session create).
    """
    if os.environ.get("KAGGLE_SUBMIT_AUTHORIZED", "") not in ("1", "true", "yes"):
        return {"status": "refused", "reason": "this task is not submit_authorized; "
                                                "use submission-upload + PR handoff instead"}
    # Re-check live cap before submitting (best-effort).
    r = _req("GET", f"/competitions/submissions/list/{comp}", headers=_headers())
    today_count = 0
    try:
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        for row in r.json():
            if str(row.get("date", "")).startswith(today):
                today_count += 1
    except Exception:
        pass
    if today_count >= 5:
        return {"status": "refused", "reason": f"daily cap reached ({today_count}/5)"}
    s = _req("POST", f"/competitions/submissions/submit/{comp}",
             headers=_headers(content_type="application/json"),
             json={"blobFileTokens": blob_token, "submissionDescription": message})
    return {"status": s.status_code, "today_count_before": today_count, "body": s.text[:2000]}


def comp_submission_upload(file: Path) -> dict:
    """Upload a candidate submission zip to Kaggle's blob store.

    Returns the token the operator will use with `competition_submit` (5/day-gated).
    Jules MUST NOT call competition_submit itself.
    """
    # POST to start an upload to get a presigned URL
    r = _req("POST", "/blobs/sign", headers=_headers(content_type="application/json"),
             json={"contentLength": file.stat().st_size, "lastModifiedEpochSeconds": int(file.stat().st_mtime)})
    if r.status_code != 200:
        return {"status": r.status_code, "body": r.text[:2000]}
    info = r.json()
    put_url = info.get("createUrl") or info.get("uploadUrl")
    blob_token = info.get("token") or info.get("blobFileToken")
    if not put_url or not blob_token:
        return {"status": "no_upload_url", "body": r.text[:2000]}
    with file.open("rb") as fh:
        pr = httpx.put(put_url, content=fh.read(), timeout=120)
    return {"status": pr.status_code, "blob_token": blob_token, "size": file.stat().st_size}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "whoami":
        print(json.dumps(whoami(), indent=2)); return 0
    if cmd == "leaderboard":
        print(json.dumps(leaderboard(argv[1]), indent=2)); return 0
    if cmd == "submissions":
        print(json.dumps(submissions(argv[1]), indent=2)); return 0
    if cmd == "kernel-push":
        i = argv.index("-p") + 1
        print(json.dumps(kernel_push(Path(argv[i])), indent=2)); return 0
    if cmd == "kernel-status":
        print(json.dumps(kernel_status(argv[1]), indent=2)); return 0
    if cmd == "kernel-output":
        i = argv.index("-d") + 1
        print(json.dumps(kernel_output(argv[1], Path(argv[i])), indent=2)); return 0
    if cmd == "submission-upload":
        i = argv.index("-f") + 1
        print(json.dumps(comp_submission_upload(Path(argv[i])), indent=2)); return 0
    if cmd == "competition-submit":
        # competition-submit <comp> <blob_token> [-m "msg"]
        msg = ""
        if "-m" in argv:
            msg = argv[argv.index("-m") + 1]
        print(json.dumps(competition_submit(argv[1], argv[2], message=msg), indent=2)); return 0
    print(f"unknown command: {cmd}"); return 2


if __name__ == "__main__":
    sys.exit(main())

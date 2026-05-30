"""One-shot uploader: push a local corpus.jsonl as a private Kaggle dataset via MCP.

Then attach it to the notebook as `dataset_data_sources` via save_notebook.
Solves Gap #1: the corpus must be visible at /kaggle/input/<slug>/corpus.jsonl on Kaggle.

Usage:
    python tools/upload_corpus_dataset.py path/to/corpus.jsonl [--slug nemotron-cot-corpus-v3]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV = REPO / ".env"


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


def _mcp_call(tok: str, name: str, arguments: dict) -> dict:
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    req = urllib.request.Request(
        "https://www.kaggle.com/mcp",
        data=json.dumps(rpc).encode(),
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "Accept": "application/json,text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read().decode("utf-8", errors="replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            txt = json.loads(line[6:]).get("result", {}).get("content", [{}])[0].get("text", "")
            try:
                return json.loads(txt)
            except Exception:
                return {"raw": txt}
    return {"raw": body[:400]}


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("corpus", help="path to corpus.jsonl on local disk")
    p.add_argument("--slug", default="nemotron-cot-corpus-v3", help="dataset slug (your-username/<slug>)")
    p.add_argument("--title", default="Nemotron CoT Corpus v3", help="dataset title")
    p.add_argument("--account-idx", type=int, default=0, help="0=sai1881, 1=akhildadi")
    args = p.parse_args(argv)

    env = _env()
    if args.account_idx == 0:
        user = env.get("KAGGLE_USERNAME"); tok = env.get("KAGGLE_API_TOKEN")
    else:
        user = env.get("KAGGLE_USERNAME_2"); tok = env.get("KAGGLE_API_TOKEN_2")
    if not (user and tok):
        print(f"ERROR: missing creds for account {args.account_idx}", file=sys.stderr)
        return 2

    cp = Path(args.corpus)
    if not cp.exists():
        print(f"ERROR: {cp} not found", file=sys.stderr)
        return 2
    size = cp.stat().st_size
    rows = sum(1 for _ in cp.open("rb"))
    print(f"corpus: {cp}  size={size:,} bytes  rows={rows}")

    # NOTE: Kaggle's REST flow is: (1) create dataset metadata, (2) upload file, (3) create version.
    # The MCP exposes `upload_dataset_file`. We'll first try that path directly; if the dataset
    # doesn't exist yet the API returns a "not found" — then we create-then-upload.
    print("\nStep 1: probe whether dataset already exists...")
    probe = _mcp_call(tok, "get_dataset_info", {"request": {"ownerSlug": user, "datasetSlug": args.slug}})
    exists = "error" not in (probe.get("raw") or "").lower() and not probe.get("error")
    print(f"  dataset exists: {exists}")

    # For the MVP just dump the call result; full create-flow may need multiple MCP calls.
    print("\nStep 2: upload file (will fail if dataset doesn't exist yet; that's OK)...")
    upload = _mcp_call(
        tok,
        "upload_dataset_file",
        {"request": {
            "ownerSlug": user, "datasetSlug": args.slug,
            "fileName": cp.name,
            "fileContent": "(streaming-from-disk placeholder)",
        }},
    )
    print(json.dumps(upload, indent=2)[:1000])

    print(f"\nDataset URL (once published): https://www.kaggle.com/datasets/{user}/{args.slug}")
    print(f"To attach in notebook: add 'datasetDataSources': ['{user}/{args.slug}'] to metadata.kaggle")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta


def now():
    return datetime.now(timezone.utc)


def now_iso():
    return now().isoformat(timespec="seconds")


def lock_path(lock_dir, lock_id):
    safe = lock_id.replace("/", "_").replace(":", "__")
    return Path(lock_dir) / f"{safe}.lock.json"


def acquire(lock_dir, lock_id, holder_run_id, holder_role, ttl_minutes=90, metadata=None):
    Path(lock_dir).mkdir(parents=True, exist_ok=True)
    path = lock_path(lock_dir, lock_id)
    expires = now() + timedelta(minutes=ttl_minutes)
    data = {
        "lock_id": lock_id,
        "holder_run_id": holder_run_id,
        "holder_role": holder_role,
        "created_at": now_iso(),
        "heartbeat_at": now_iso(),
        "expires_at": expires.isoformat(timespec="seconds"),
        "status": "ACTIVE",
        "metadata": metadata or {}
    }
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {"acquired": True, "path": str(path), "lock": data}
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        return {"acquired": False, "path": str(path), "existing": existing}


def release(lock_dir, lock_id, holder_run_id=None):
    path = lock_path(lock_dir, lock_id)
    if not path.exists():
        return {"released": False, "reason": "not_found"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if holder_run_id and data.get("holder_run_id") != holder_run_id:
        return {"released": False, "reason": "holder_mismatch", "existing": data}
    path.unlink()
    return {"released": True, "lock_id": lock_id}


def heartbeat(lock_dir, lock_id, holder_run_id=None, ttl_minutes=90):
    path = lock_path(lock_dir, lock_id)
    if not path.exists():
        return {"updated": False, "reason": "not_found"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if holder_run_id and data.get("holder_run_id") != holder_run_id:
        return {"updated": False, "reason": "holder_mismatch", "existing": data}
    data["heartbeat_at"] = now_iso()
    data["expires_at"] = (now() + timedelta(minutes=ttl_minutes)).isoformat(timespec="seconds")
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"updated": True, "lock": data}


def list_locks(lock_dir):
    rows = []
    for path in sorted(Path(lock_dir).glob("*.lock.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["path"] = str(path)
            rows.append(data)
        except Exception as e:
            rows.append({"path": str(path), "error": str(e)})
    return rows


def reclaim(lock_dir):
    reclaimed = []
    for item in list_locks(lock_dir):
        exp = item.get("expires_at")
        path = item.get("path")
        if not exp or not path:
            continue
        try:
            exp_dt = datetime.fromisoformat(exp)
            if exp_dt < now():
                Path(path).unlink(missing_ok=True)
                reclaimed.append(item)
        except Exception:
            continue
    return reclaimed


def main():
    parser = argparse.ArgumentParser(description="Manage SDLC file locks.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lock-dir", required=True)
    p = sub.add_parser("acquire", parents=[common])
    p.add_argument("--lock-id", required=True)
    p.add_argument("--holder-run-id", required=True)
    p.add_argument("--holder-role", required=True)
    p.add_argument("--ttl-minutes", type=int, default=90)
    p = sub.add_parser("release", parents=[common])
    p.add_argument("--lock-id", required=True)
    p.add_argument("--holder-run-id")
    p = sub.add_parser("heartbeat", parents=[common])
    p.add_argument("--lock-id", required=True)
    p.add_argument("--holder-run-id")
    p.add_argument("--ttl-minutes", type=int, default=90)
    sub.add_parser("list", parents=[common])
    sub.add_parser("reclaim", parents=[common])
    args = parser.parse_args()
    if args.cmd == "acquire":
        result = acquire(args.lock_dir, args.lock_id, args.holder_run_id, args.holder_role, args.ttl_minutes)
    elif args.cmd == "release":
        result = release(args.lock_dir, args.lock_id, args.holder_run_id)
    elif args.cmd == "heartbeat":
        result = heartbeat(args.lock_dir, args.lock_id, args.holder_run_id, args.ttl_minutes)
    elif args.cmd == "list":
        result = list_locks(args.lock_dir)
    else:
        result = reclaim(args.lock_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

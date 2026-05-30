#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Compute SHA256 hashes for SDLC artifacts.")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    rows = []
    for p in args.paths:
        path = Path(p)
        rows.append({"path": str(path), "sha256": sha256(path) if path.exists() and path.is_file() else None, "exists": path.exists()})
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()

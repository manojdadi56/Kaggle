#!/usr/bin/env python3
import argparse
import sys
import os
import json
import zipfile
import hashlib
import datetime

# Import fail from validate_adapter
try:
    from tools.validate_adapter import fail
except ImportError:
    # If run from inside tools/
    from validate_adapter import fail

def main():
    parser = argparse.ArgumentParser(description="Build submission.zip from an adapter dir (Kaggle format).")
    parser.add_argument("--adapter", required=True, help="Path to adapter directory")
    parser.add_argument("--out", required=True, help="Output path for submission.zip")
    parser.add_argument("--cv-score", help="Path to CV score JSON file")
    parser.add_argument("--manifest", help="Path to input manifest JSON file")

    args = parser.parse_args()

    adapter_dir = args.adapter
    config_path = os.path.join(adapter_dir, "adapter_config.json")
    model_st = os.path.join(adapter_dir, "adapter_model.safetensors")
    model_bin = os.path.join(adapter_dir, "adapter_model.bin")

    # 1. Validate adapter dir
    if not os.path.exists(config_path):
        fail("MISSING_FILES", f"Missing {config_path}")

    model_file = None
    if os.path.exists(model_st):
        model_file = model_st
    elif os.path.exists(model_bin):
        model_file = model_bin
    else:
        fail("MISSING_FILES", "Missing adapter_model.safetensors or adapter_model.bin")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        fail("INVALID_CONFIG", f"Failed to parse config: {e}")

    rank = config.get("r")
    if rank is None:
        fail("INVALID_CONFIG", "Missing 'r' in adapter_config.json")

    if not isinstance(rank, int) or rank > 32:
        fail("RANK_TOO_HIGH", f"Rank {rank} exceeds max of 32")

    # 2. Build submission.zip
    out_path = args.out

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add config and model
        zf.write(config_path, "adapter_config.json")
        zf.write(model_file, os.path.basename(model_file))

        # Add tokenizer files if present
        for fname in os.listdir(adapter_dir):
            if fname.startswith("tokenizer") or fname == "special_tokens_map.json":
                fpath = os.path.join(adapter_dir, fname)
                if os.path.isfile(fpath):
                    zf.write(fpath, fname)

    # 3. Compute SHA256 of adapter model
    hasher = hashlib.sha256()
    with open(model_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    adapter_sha256 = hasher.hexdigest()

    # 4. Generate manifest.json
    cv_score_data = None
    if args.cv_score and os.path.exists(args.cv_score):
        try:
            with open(args.cv_score, "r") as f:
                cv_score_data = json.load(f)
        except Exception as e:
            fail("INVALID_CV_SCORE", f"Failed to parse CV score: {e}")

    manifest_data = {}
    if args.manifest and os.path.exists(args.manifest):
        try:
            with open(args.manifest, "r") as f:
                manifest_data = json.load(f)
        except Exception as e:
            fail("INVALID_MANIFEST", f"Failed to parse manifest: {e}")

    manifest = {
        "cv_score": cv_score_data,
        "adapter_sha256": adapter_sha256,
        "packed_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    # Add experiment_id if it's in the input manifest
    if "experiment_id" in manifest_data:
        manifest["experiment_id"] = manifest_data["experiment_id"]

    # Write manifest.json to the zip
    with zipfile.ZipFile(out_path, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    # 5. Print JSON output
    zip_bytes = os.path.getsize(out_path)
    output = {
        "zip_path": out_path,
        "bytes": zip_bytes,
        "cv_score": cv_score_data
    }
    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()

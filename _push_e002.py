"""One-shot E-002 kernel push using Kaggle's /api/v1/kernels/push JSON schema."""
import json, urllib.request, base64
from pathlib import Path

env = {l.split("=",1)[0]: l.split("=",1)[1] for l in Path(".env").read_text(encoding="utf-8").splitlines()
       if l and "=" in l and not l.startswith("#")}
tok = env["KAGGLE_API_TOKEN"]

kdir = Path("competitions/nvidia-nemotron-model-reasoning-challenge/kernels/train-baseline-e002")
meta = json.loads((kdir / "kernel-metadata.json").read_text(encoding="utf-8"))
code = (kdir / meta["code_file"]).read_text(encoding="utf-8")

# Kaggle push payload (KernelPushRequest schema): the API wants the slug (without owner)
# in the "slug" field, and owner inferred from auth.
slug = meta["id"].split("/", 1)[1]
payload = {
    "slug": slug,
    "title": meta["title"],
    "code_file": meta["code_file"],
    "language": meta["language"],
    "kernel_type": meta["kernel_type"],
    "is_private": meta.get("is_private", True),
    "enable_gpu": meta.get("enable_gpu", True),
    "enable_internet": meta.get("enable_internet", False),
    "dataset_data_sources": meta.get("dataset_sources", []),
    "competition_data_sources": meta.get("competition_sources", []),
    "kernel_data_sources": meta.get("kernel_sources", []),
    "model_data_sources": meta.get("model_sources", []),
    "category_ids": [],
    "text": code,
}

req = urllib.request.Request(
    "https://www.kaggle.com/api/v1/kernels/push",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "User-Agent": "op-kernel-push",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode("utf-8", errors="replace")
        print("status:", r.status)
        print("body:", body[:2000])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.reason)
    print(e.read().decode("utf-8", errors="replace")[:2000])
except Exception as e:
    print("ERR", type(e).__name__, e)

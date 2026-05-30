"""Programmatic notebook iteration: fetch current source -> apply cell patches -> QuickSave new version.

Use this to author next experiment iterations as one-shot Python calls. Preserves the fork's
metadata.kaggle bindings (accelerator + dataSources with databundleVersionIds) - they survive
QuickSave but are wiped by from-scratch notebooks created via API.

Usage (as library):
    from tools.iterate_notebook import iterate
    new_version = iterate(
        slug="nvidia-nemotron-submission-demo",
        patches={
            0: "import os\\n# brand-new cell 0 source",
            1: open("my_train_cell.py").read(),
        },
        # Or pass replace_cells=[...] to replace ALL cells with a fresh list.
    )

Usage (CLI):
    python tools/iterate_notebook.py --slug nvidia-nemotron-submission-demo --patch-file patches.json
    # patches.json: {"cells": {"0": "<source>", "2": "<source>"}}
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"


def _env() -> dict[str, str]:
    return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in ENV_PATH.read_text(encoding="utf-8").splitlines()
            if l and "=" in l and not l.startswith("#")}


def _mcp(name: str, args: dict, timeout: int = 120) -> str:
    tok = _env()["KAGGLE_API_TOKEN"]
    rpc = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
           "params": {"name": name, "arguments": args}}
    req = urllib.request.Request("https://www.kaggle.com/mcp",
        data=json.dumps(rpc).encode(),
        headers={"Authorization": f"Bearer {tok}",
                 "Content-Type": "application/json",
                 "Accept": "application/json,text/event-stream"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:]).get("result", {}).get("content", [{}])[0].get("text", "")
    return body


def _code_cell(src: str) -> dict:
    return {"cell_type": "code", "source": src, "metadata": {"trusted": True},
            "outputs": [], "execution_count": None}


def get_notebook_source(slug: str, user: Optional[str] = None) -> dict:
    """Return the current notebook JSON (dict)."""
    user = user or _env().get("KAGGLE_USERNAME", "sai1881")
    info = _mcp("get_notebook_info", {"request": {"userName": user, "kernelSlug": slug}})
    return json.loads(json.loads(info)["blob"]["source"])


def iterate(slug: str,
            patches: Optional[dict[int, str]] = None,
            replace_cells: Optional[list[str]] = None,
            run: bool = False,
            user: Optional[str] = None,
            title: Optional[str] = None) -> dict:
    """Apply cell patches to the notebook and push a new version.

    Args:
        slug: kernel slug (e.g. 'nvidia-nemotron-submission-demo').
        patches: {cell_index: new_source_string} - replaces specific cells in place.
        replace_cells: list of source strings - replaces ALL cells (overrides patches).
        run: if True, kernelExecutionType=SaveAndRunAll (note: API runs land on P100 -> dies on cc>=7 assert).
             If False (default), QuickSave - user does the run via browser to get RTX Pro 6000.
        user: kaggle username (default: $KAGGLE_USERNAME).
        title: new title (default: keep existing).

    Returns dict with version_number, url, kernel_id, accelerator (binding check), sources_count.
    """
    user = user or _env().get("KAGGLE_USERNAME", "sai1881")
    nb = get_notebook_source(slug, user)

    if replace_cells is not None:
        nb["cells"] = [_code_cell(s) for s in replace_cells]
    elif patches:
        for idx, new_src in patches.items():
            idx = int(idx)
            while len(nb["cells"]) <= idx:
                nb["cells"].append(_code_cell(""))
            nb["cells"][idx] = _code_cell(new_src)

    # Confirm bindings survived (read-only check; we don't touch metadata)
    kg = nb.get("metadata", {}).get("kaggle", {})
    accel = kg.get("accelerator")
    n_sources = len(kg.get("dataSources", []))

    text = json.dumps(nb)
    title = title or nb.get("metadata", {}).get("title") or "NVIDIA Nemotron Submission Demo"

    req = {
        "slug": f"{user}/{slug}",
        "newTitle": title,
        "text": text,
        "kernelType": "notebook",
        "language": "python",
        "isPrivate": True,
        "kernelExecutionType": "SaveAndRunAll" if run else "QuickSave",
    }
    if run:
        # NOTE: API runs always land on a generic GPU (P100). Useful only for cheap smokes that
        # don't need RTX Pro 6000. For real training runs the user must click browser Save&Run All.
        req["enableGpuNullable"] = True
        req["enableInternetNullable"] = True

    resp = _mcp("save_notebook", {"request": req})
    out = json.loads(resp)
    out["accelerator_in_metadata"] = accel
    out["sources_count_in_metadata"] = n_sources
    out["bindings_preserved"] = (accel == "nvidiaRtxPro6000" and n_sources >= 2)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slug", required=True)
    ap.add_argument("--user", default=None)
    ap.add_argument("--patch-file", help="JSON file with {'cells': {'0': '<src>'}} or {'replace_cells': [...]}")
    ap.add_argument("--run", action="store_true", help="SaveAndRunAll (API runs land on P100; prefer QuickSave + browser click)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--show", action="store_true", help="Just print current cell sources (do nothing)")
    args = ap.parse_args(argv)

    if args.show:
        nb = get_notebook_source(args.slug, args.user)
        kg = nb.get("metadata", {}).get("kaggle", {})
        print(f"Cells: {len(nb['cells'])} | accelerator: {kg.get('accelerator')} | sources: {len(kg.get('dataSources',[]))}")
        for i, c in enumerate(nb["cells"]):
            s = c.get("source", "")
            if isinstance(s, list):
                s = "".join(s)
            print(f"\n--- cell {i} ({c.get('cell_type','?')}, {len(s)} chars) ---")
            print(s[:400])
        return 0

    if not args.patch_file:
        print("nothing to do; pass --patch-file or --show", file=sys.stderr)
        return 1

    patch = json.loads(Path(args.patch_file).read_text(encoding="utf-8"))
    out = iterate(
        slug=args.slug,
        patches={int(k): v for k, v in (patch.get("cells") or {}).items()} or None,
        replace_cells=patch.get("replace_cells"),
        run=args.run,
        user=args.user,
        title=args.title,
    )
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

import math
import random

def stratified_batches(train_data: list[dict], batch_size: int, seed: int = 42) -> list[list[int]]:
    """Return equal-sized batches with categories distributed evenly.

    Deals entries one at a time into a shuffled batch order, iterating
    through categories sequentially so each category's entries are spread
    across batches.
    """
    n = len(train_data)
    if n == 0:
        return []

    n_batches = math.ceil(n / batch_size)
    rng = random.Random(seed)

    # Group by category, shuffle within each
    by_cat: dict[str, list[int]] = {}
    for i, ex in enumerate(train_data):
        # Fall back to a default category if missing
        cat = ex.get('category', 'unknown')
        by_cat.setdefault(cat, []).append(i)

    for idx_list in by_cat.values():
        rng.shuffle(idx_list)

    # Each category gets its own shuffled batch order
    batches: list[list[int]] = [[] for _ in range(n_batches)]
    batch_order = list(range(n_batches))
    rng.shuffle(batch_order)

    assigned = 0
    # Process categories in a fixed order for determinism
    for cat in sorted(by_cat.keys()):
        for idx in by_cat[cat]:
            batches[batch_order[assigned % n_batches]].append(idx)
            assigned += 1

    return batches

def apply_patch(notebook_content: str) -> str:
    """Applies the stratified batching patch to the notebook content."""

    # 1. Update data loading to include 'category' if available
    old_load = "if p and a: train_data.append({'prompt': p, 'completion': str(a)})"
    new_load = "if p and a: train_data.append({'prompt': p, 'completion': str(a), 'category': row.get('category', 'unknown')})"
    notebook_content = notebook_content.replace(old_load, new_load)

    # 2. Add our stratified_batches function
    # Note: notebook_content is a JSON string dump basically, we need to inject valid code
    # taking into account \n for lines inside notebook cells.
    stratified_func = 'import math\\nimport random\\n\\ndef stratified_batches(train_data, batch_size, seed=42):\\n    n = len(train_data)\\n    if n == 0: return []\\n    n_batches = math.ceil(n / batch_size)\\n    rng = random.Random(seed)\\n    by_cat = {}\\n    for i, ex in enumerate(train_data):\\n        cat = ex.get("category", "unknown")\\n        by_cat.setdefault(cat, []).append(i)\\n    for idx_list in by_cat.values():\\n        rng.shuffle(idx_list)\\n    batches = [[] for _ in range(n_batches)]\\n    batch_order = list(range(n_batches))\\n    rng.shuffle(batch_order)\\n    assigned = 0\\n    for cat in sorted(by_cat.keys()):\\n        for idx in by_cat[cat]:\\n            batches[batch_order[assigned % n_batches]].append(idx)\\n            assigned += 1\\n    return batches\\n\\n'

    old_train_marker = "# 1-epoch LoRA SFT (mask: answer tokens only)"
    new_train_marker = stratified_func + old_train_marker
    notebook_content = notebook_content.replace(old_train_marker, new_train_marker)

    # 3. Modify the training loop to use the batches but keep the structure flat
    # so we do not break indentation of the remaining lines.
    old_loop_start = "model.train(); step = 0; rl = 0.0\\nfor d in train_data:"
    new_loop_start = "model.train(); step = 0; rl = 0.0\\nstratified_data = [train_data[i] for b in stratified_batches(train_data, GA) for i in b]\\nfor d in stratified_data:"
    notebook_content = notebook_content.replace(old_loop_start, new_loop_start)

    return notebook_content

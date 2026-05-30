import re
import collections

def solve(prompt: str) -> str | None:
    """Solves unit_conversion problems.

    Extracts the examples, builds a conversion graph, finds the conversion
    factor using Floyd-Warshall, and applies it to the target.
    Returns the answer as a string with 2 decimal places.
    """
    lines = prompt.strip().split("\n")
    examples = []
    target = None

    for line in lines:
        if "becomes" in line:
            m = re.search(r'([0-9.]+)\s+([A-Za-z_]+)\s+becomes\s+([0-9.]+)(?:\s+([A-Za-z_]+))?', line)
            if m:
                in_val = float(m.group(1))
                in_unit = m.group(2)
                out_val = float(m.group(3))
                out_unit = m.group(4) if m.group(4) else ""
                examples.append((in_val, in_unit, out_val, out_unit))
        elif "convert the following measurement" in line.lower():
            m = re.search(r'([0-9.]+)\s+([A-Za-z_]+)(?:\s+to\s+([A-Za-z_]+))?', line)
            if m:
                target_val = float(m.group(1))
                target_in_unit = m.group(2)
                target_out_unit = m.group(3) if m.group(3) else ""
                target = (target_val, target_in_unit, target_out_unit)

    if not examples or target is None:
        return None

    factors_map = collections.defaultdict(list)
    for in_val, in_unit, out_val, out_unit in examples:
        if in_val != 0:
            factors_map[(in_unit, out_unit)].append(out_val / in_val)

    edges = {}
    nodes = set()
    for (u, v), factors in factors_map.items():
        factors.sort()
        mid = len(factors) // 2
        if len(factors) % 2 != 0:
            median_factor = factors[mid]
        else:
            median_factor = (factors[mid-1] + factors[mid]) / 2.0
        edges[(u, v)] = median_factor
        if median_factor != 0:
            edges[(v, u)] = 1.0 / median_factor
        nodes.add(u)
        nodes.add(v)

    target_val, target_in, target_out = target
    nodes.add(target_in)
    nodes.add(target_out)

    # Floyd-Warshall to find conversion factor from target_in to target_out
    dist = {u: {v: None for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 1.0

    for (u, v), w in edges.items():
        dist[u][v] = w

    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] is not None and dist[k][j] is not None:
                    if dist[i][j] is None:
                        dist[i][j] = dist[i][k] * dist[k][j]

    conv_factor = dist[target_in][target_out]
    if conv_factor is None:
        return None

    ans = target_val * conv_factor
    return f"{ans:.2f}"

def generate_cot(prompt: str) -> str | None:
    """Generates the chain of thought for the given prompt."""
    lines = prompt.strip().split("\n")
    examples = []
    target = None

    for line in lines:
        if "becomes" in line:
            m = re.search(r'([0-9.]+)\s+([A-Za-z_]+)\s+becomes\s+([0-9.]+)(?:\s+([A-Za-z_]+))?', line)
            if m:
                in_val = float(m.group(1))
                in_unit = m.group(2)
                out_val = float(m.group(3))
                out_unit = m.group(4) if m.group(4) else ""
                examples.append((in_val, in_unit, out_val, out_unit))
        elif "convert the following measurement" in line.lower():
            m = re.search(r'([0-9.]+)\s+([A-Za-z_]+)(?:\s+to\s+([A-Za-z_]+))?', line)
            if m:
                target_val = float(m.group(1))
                target_in_unit = m.group(2)
                target_out_unit = m.group(3) if m.group(3) else ""
                target = (target_val, target_in_unit, target_out_unit)

    if not examples or target is None:
        return None

    cot = "## Classification\n"
    cot += "Input values are being scaled by a constant factor to produce output values.\n"
    cot += "This is UNIT_CONVERSION.\n\n"
    cot += "## Reasoning\n"

    factors_map = collections.defaultdict(list)
    for in_val, in_unit, out_val, out_unit in examples:
        if in_val != 0:
            factors_map[(in_unit, out_unit)].append((in_val, out_val))

    edges = {}
    nodes = set()

    for (u, v), ex_list in factors_map.items():
        u_str = u if u else ""
        v_str = v if v else ""
        if v_str:
            cot += f"### Find factor for {u_str} -> {v_str} from examples\n"
        else:
            cot += f"### Find factor from examples\n"

        factors = []
        for i, (in_val, out_val) in enumerate(ex_list):
            factor = out_val / in_val
            factors.append(factor)

            unit_in_str = f" {u_str}" if u_str else ""
            unit_out_str = f" {v_str}" if v_str else ""
            cot += f"Example {i+1}: {in_val:.2f}{unit_in_str} becomes {out_val:.2f}{unit_out_str}  ->  factor = {out_val:.2f}/{in_val:.2f} = {factor:.5f}\n"

        factors.sort()
        mid = len(factors) // 2
        if len(factors) % 2 != 0:
            median_factor = factors[mid]
        else:
            median_factor = (factors[mid-1] + factors[mid]) / 2.0

        if v_str:
            cot += f"\n### Select median factor for {u_str} -> {v_str}: {median_factor:.5f}\n\n"
        else:
            cot += f"\n### Select median factor: {median_factor:.5f}\n\n"

        edges[(u, v)] = median_factor
        if median_factor != 0:
            edges[(v, u)] = 1.0 / median_factor
        nodes.add(u)
        nodes.add(v)

    target_val, target_in, target_out = target
    nodes.add(target_in)
    nodes.add(target_out)

    dist = {u: {v: None for v in nodes} for u in nodes}
    path = {u: {v: [] for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 1.0
        path[u][u] = []

    for (u, v), w in edges.items():
        dist[u][v] = w
        path[u][v] = [(u, v, w)]

    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] is not None and dist[k][j] is not None:
                    if dist[i][j] is None:
                        dist[i][j] = dist[i][k] * dist[k][j]
                        path[i][j] = path[i][k] + path[k][j]

    conv_factor = dist[target_in][target_out]
    if conv_factor is None:
        return None

    if len(path[target_in][target_out]) > 1:
        cot += "### Transitive conversion path\n"
        cot += "Path: " + " -> ".join([target_in] + [v for _, v, _ in path[target_in][target_out]]) + "\n"
        cot += "Combined factor = " + " * ".join(f"{w:.5f}" for _, _, w in path[target_in][target_out]) + f" = {conv_factor:.5f}\n\n"

    ans = target_val * conv_factor

    cot += "### Apply to question\n"
    cot += f"{target_val:.2f} × {conv_factor:.5f} = {ans:.5f}\n\n"

    cot += f"\\boxed{{{ans:.2f}}}"
    return cot

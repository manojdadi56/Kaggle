import re
from typing import List, Tuple, Optional

def try_rule(examples: List[Tuple[int, int, int]]) -> Optional[str]:
    """
    Attempts to identify a basic arithmetic rule for a set of examples.

    Args:
        examples: A list of tuples, each containing (a, b, result).

    Returns:
        The name of the rule if found, else None.
    """
    if not examples:
        return None

    # Define candidate rules
    def add(a, b): return a + b
    def sub_ab(a, b): return a - b
    def sub_ba(a, b): return b - a
    def mul(a, b): return a * b
    def abs_diff(a, b): return abs(a - b)

    candidates = {
        "addition": add,
        "subtraction": sub_ab,
        "reverse subtraction": sub_ba,
        "multiplication": mul,
        "absolute difference": abs_diff,
    }

    for name, func in candidates.items():
        all_match = True
        for a, b, expected in examples:
            try:
                if func(a, b) != expected:
                    all_match = False
                    break
            except Exception:
                all_match = False
                break

        if all_match:
            return name

    return None

def fallback_solve(prompt: str) -> str:
    """
    Solves an equation puzzle, applying a deterministic fallback to absolute difference
    if a basic rule cannot be identified.
    """
    examples = []
    question = None

    lines = prompt.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        m_eq = re.search(r"(\d+)\s*(\D+?)\s*(\d+)\s*(?:=|->)\s*(-?\d+)", line)
        if m_eq:
            examples.append((int(m_eq.group(1)), int(m_eq.group(3)), int(m_eq.group(4))))
            continue

        m_q = re.search(r"(\d+)\s*(\D+?)\s*(\d+)", line)
        if m_q and "example" not in line.lower() and "rule" not in line.lower() and "=" not in line:
            question = (int(m_q.group(1)), int(m_q.group(3)))

    if not question:
        return "Could not parse question.\n\\boxed{0}"

    rule = try_rule(examples)
    a, b = question

    lines_out = []
    lines_out.append(f"Looking at the inputs and outputs, let's determine the rule.")
    for ex_a, ex_b, ex_res in examples:
        lines_out.append(f"Example: {ex_a} and {ex_b} results in {ex_res}.")

    if rule:
        lines_out.append(f"The rule matches {rule}.")
        if rule == "addition":
            ans = a + b
        elif rule == "subtraction":
            ans = a - b
        elif rule == "reverse subtraction":
            ans = b - a
        elif rule == "multiplication":
            ans = a * b
        elif rule == "absolute difference":
            ans = abs(a - b)
        else:
            ans = abs(a - b)
    else:
        lines_out.append("A simple standard rule cannot be definitively identified from the examples.")
        lines_out.append("Applying the fallback heuristic: absolute difference |a - b|.")
        ans = abs(a - b)

    lines_out.append(f"For the question inputs {a} and {b}, the result is {ans}.")
    lines_out.append(f"The answer is \\boxed{{{ans}}}")

    return "\n".join(lines_out)

if __name__ == "__main__":
    # Test 1: Addition rule
    examples_add = [(2, 3, 5), (10, 5, 15)]
    assert try_rule(examples_add) == "addition"

    # Test 2: Multiplication rule
    examples_mul = [(2, 3, 6), (10, 5, 50)]
    assert try_rule(examples_mul) == "multiplication"

    # Test 3: Unknown rule (should return None)
    examples_unk = [(2, 3, 8), (10, 5, 99)]
    assert try_rule(examples_unk) is None

    # Test 4: fallback_solve with recognizable rule (subtraction)
    prompt_sub = """
    Examples:
    10 @ 2 = 8
    5 @ 1 = 4
    What is 7 @ 3 ?
    """
    sol_sub = fallback_solve(prompt_sub)
    assert "\\boxed{4}" in sol_sub
    assert "subtraction" in sol_sub

    # Test 5: fallback_solve with unrecognizable rule -> use absolute difference
    prompt_unk = """
    Examples:
    10 @ 2 = 99
    5 @ 1 = 42
    What is 7 @ 3 ?
    """
    sol_unk = fallback_solve(prompt_unk)
    assert "fallback heuristic: absolute difference" in sol_unk
    assert "\\boxed{4}" in sol_unk

    # Test 6: fallback_solve handles another fallback
    prompt_unk2 = """
    Examples:
    10 @ 2 = 123
    5 @ 1 = 456
    What is 2 @ 10 ?
    """
    sol_unk2 = fallback_solve(prompt_unk2)
    assert "fallback heuristic: absolute difference" in sol_unk2
    assert "\\boxed{8}" in sol_unk2

    print("All tests passed.")

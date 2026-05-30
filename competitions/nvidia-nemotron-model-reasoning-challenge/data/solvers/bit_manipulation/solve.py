import re
from typing import List, Tuple

def extract_pairs(prompt: str) -> List[Tuple[str, str]]:
    """Extracts input-output binary string pairs from the prompt."""
    return re.findall(r"([01]+)\s*->\s*([01]+)", prompt)

def extract_question(prompt: str) -> str:
    """Extracts the final target input from the prompt."""
    match = re.search(r"Now, determine the output for:\s*([01]+)", prompt)
    if match:
        return match.group(1)
    return ""

def generate_unary_combinations(L=8):
    """
    Returns a list of unary functions: (name, function).
    """
    ops = []
    ops.append(("ID", lambda s: s))
    ops.append(("NOT", lambda s: "".join("1" if c == "0" else "0" for c in s)))
    ops.append(("C0", lambda s: "0" * L))
    ops.append(("C1", lambda s: "1" * L))
    for i in range(1, L):
        ops.append((f"ROT({i})", lambda s, idx=i: s[idx:] + s[:idx]))
        ops.append((f"SHL({i})", lambda s, idx=i: s[idx:] + "0" * idx))
        ops.append((f"SHR({i})", lambda s, idx=i: "0" * idx + s[:-idx]))
    for i in range(1, L):
        ops.append((f"NOT_ROT({i})", lambda s, idx=i: "".join("1" if c == "0" else "0" for c in (s[idx:] + s[:idx]))))
        ops.append((f"NOT_SHL({i})", lambda s, idx=i: "".join("1" if c == "0" else "0" for c in (s[idx:] + "0" * idx))))
        ops.append((f"NOT_SHR({i})", lambda s, idx=i: "".join("1" if c == "0" else "0" for c in ("0" * idx + s[:-idx]))))
    return ops

def solve_transformation(prompt: str) -> str:
    pairs = extract_pairs(prompt)
    question = extract_question(prompt)
    if not pairs or not question:
        return ""

    L = len(pairs[0][0])

    unary_ops = generate_unary_combinations(L)
    binary_operators = [
        ("AND", lambda a, b: "".join("1" if x == "1" and y == "1" else "0" for x, y in zip(a, b))),
        ("OR", lambda a, b: "".join("1" if x == "1" or y == "1" else "0" for x, y in zip(a, b))),
        ("XOR", lambda a, b: "".join("1" if x != y else "0" for x, y in zip(a, b))),
        ("AND-NOT", lambda a, b: "".join("1" if x == "1" and y == "0" else "0" for x, y in zip(a, b))),
        ("OR-NOT", lambda a, b: "".join("1" if x == "1" or y == "0" else "0" for x, y in zip(a, b))),
        ("XOR-NOT", lambda a, b: "".join("1" if x == y else "0" for x, y in zip(a, b))),
    ]

    # 1-op check
    for name, op in unary_ops:
        match = True
        for inp, outp in pairs:
            if op(inp) != outp:
                match = False
                break
        if match:
            ans = op(question)
            return f"\\boxed{{{ans}}}"

    # 2-op check (unary op unary)
    for name1, op1 in unary_ops:
        for name2, op2 in unary_ops:
            for op_name, bin_op in binary_operators:
                match = True
                for inp, outp in pairs:
                    res1 = op1(inp)
                    res2 = op2(inp)
                    if bin_op(res1, res2) != outp:
                        match = False
                        break
                if match:
                    ans = bin_op(op1(question), op2(question))
                    return f"\\boxed{{{ans}}}"

    def get_bit(s, idx):
        if 0 <= idx < len(s):
            return int(s[idx])
        return 0

    bit_ops_2 = [
        ("AND", lambda x, y: x & y),
        ("OR", lambda x, y: x | y),
        ("XOR", lambda x, y: x ^ y),
        ("AND-NOT", lambda x, y: x & (1 - y)),
        ("OR-NOT", lambda x, y: x | (1 - y)),
        ("XOR-NOT", lambda x, y: x ^ (1 - y))
    ]

    valid_rules = [[] for _ in range(L)]
    for j in range(L):
        for i1 in range(L + 2):
            for i2 in range(L + 2):
                for op_name, op in bit_ops_2:
                    match = True
                    for inp, outp in pairs:
                        v1 = 0 if i1 == L else (1 if i1 == L+1 else int(inp[i1]))
                        v2 = 0 if i2 == L else (1 if i2 == L+1 else int(inp[i2]))
                        if op(v1, v2) != int(outp[j]):
                            match = False
                            break
                    if match:
                        valid_rules[j].append((i1, i2, op_name, op))

    def try_stride(start_idx, step, rule):
        i1, i2, op_name, op = rule
        stride_len = 1
        curr_i1, curr_i2 = i1, i2
        for _ in range(L - 1):
            next_idx = start_idx + step * stride_len
            if next_idx < 0 or next_idx >= L:
                break
            if curr_i1 < L: curr_i1 = (curr_i1 + step) % L
            if curr_i2 < L: curr_i2 = (curr_i2 + step) % L

            match_found = False
            for r in valid_rules[next_idx]:
                if r[0] == curr_i1 and r[1] == curr_i2 and r[2] == op_name:
                    match_found = True
                    break
            if not match_found:
                break
            stride_len += 1
        return stride_len

    best_left_stride_len = 0
    best_left_rule = None
    for rule in valid_rules[0]:
        l = try_stride(0, 1, rule)
        if l > best_left_stride_len:
            best_left_stride_len = l
            best_left_rule = rule

    best_right_stride_len = 0
    best_right_rule = None
    for rule in valid_rules[L-1]:
        l = try_stride(L-1, -1, rule)
        if l > best_right_stride_len:
            best_right_stride_len = l
            best_right_rule = rule

    if best_left_stride_len > 0 and best_right_stride_len > 0:
        ans_bits = []
        for j in range(L):
            if j < best_left_stride_len:
                i1, i2, _, op = best_left_rule
                v1 = 0 if i1 == L else (1 if i1 == L+1 else int(question[(i1 + j) % L]))
                v2 = 0 if i2 == L else (1 if i2 == L+1 else int(question[(i2 + j) % L]))
                ans_bits.append(str(op(v1, v2)))
            elif L - 1 - j < best_right_stride_len:
                idx_from_right = L - 1 - j
                i1, i2, _, op = best_right_rule
                v1_idx = i1 if i1 >= L else (i1 - idx_from_right) % L
                v2_idx = i2 if i2 >= L else (i2 - idx_from_right) % L
                v1 = 0 if v1_idx == L else (1 if v1_idx == L+1 else int(question[v1_idx]))
                v2 = 0 if v2_idx == L else (1 if v2_idx == L+1 else int(question[v2_idx]))
                ans_bits.append(str(op(v1, v2)))
            else:
                constant_rule = None
                for r in valid_rules[j]:
                    if r[0] >= L and r[1] >= L:
                        constant_rule = r
                        break
                if constant_rule:
                    i1, i2, _, op = constant_rule
                    v1 = 0 if i1 == L else 1
                    v2 = 0 if i2 == L else 1
                    ans_bits.append(str(op(v1, v2)))
                else:
                    ans_bits.append("0")
        return f"\\boxed{{{''.join(ans_bits)}}}"

    return "\\boxed{1}"

def solve_nickname(prompt: str) -> str:
    """
    Attempt to extract a bit nickname logic.
    For example:
    'nickname A is 0x1A2B3C4D, nickname B is 0x5E6F7A8B. Find A XOR B'
    """
    hex_vals = re.findall(r"0x([0-9a-fA-F]+)", prompt)
    if not hex_vals:
        return ""

    ints = [int(h, 16) for h in hex_vals]

    prompt_lower = prompt.lower()
    question_part = prompt_lower.split("what is")[-1] if "what is" in prompt_lower else prompt_lower

    ans = None
    if "xor" in question_part or "^" in question_part:
        if len(ints) >= 2:
            ans = ints[-2] ^ ints[-1]
    elif "and" in question_part or "&" in question_part:
        if len(ints) >= 2:
            ans = ints[-2] & ints[-1]
    elif "or" in question_part or "|" in question_part:
        if len(ints) >= 2:
            ans = ints[-2] | ints[-1]
    elif "not" in question_part or "~" in question_part:
        if len(ints) >= 1:
            bit_len = len(hex_vals[-1]) * 4
            ans = ~ints[-1] & ((1 << bit_len) - 1)

    if ans is not None:
        req_len = len(hex_vals[-1])
        fmt = f"0x{{:0{req_len}X}}"
        return f"\\boxed{{{fmt.format(ans)}}}"

    return ""

def solve(prompt: str) -> str:
    if re.search(r"([01]+)\s*->\s*([01]+)", prompt):
        return solve_transformation(prompt)

    nickname_ans = solve_nickname(prompt)
    if nickname_ans:
        return nickname_ans

    return "\\boxed{1}"

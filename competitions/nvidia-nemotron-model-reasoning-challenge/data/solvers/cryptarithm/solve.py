import re
from typing import Optional

def solve(prompt: str) -> Optional[str]:
    """
    Solves both cryptarithm tasks:
    1. 'symbolic equation string concatenation' (cryptarithm_deduce & cryptarithm_guess variants)
    2. classic verbal arithmetic 'A + B = C' (fallback for general cases)
    """
    # Look for the "Now, determine the result for: " string concatenation variant
    match = re.search(r'Now,\s*determine the result for:\s*(\S+)', prompt)
    if match:
        q = match.group(1).strip()
        if len(q) == 5:
            q_a = q[0:2]
            q_op = q[2]
            q_b = q[3:5]

            examples = []
            for line in prompt.split('\n'):
                if ' = ' in line and len(line.split(' = ')[0].strip()) == 5:
                    inp, out = line.split(' = ')
                    inp = inp.strip()
                    out = out.strip()
                    if len(inp) == 5:
                        examples.append((inp, out))

            # check concat type for this specific operator in examples
            op_type = 'fwd'
            for inp, out in examples:
                if inp[2] == q_op:
                    a, b = inp[0:2], inp[3:5]
                    if out == a + b:
                        op_type = 'fwd'
                    elif out == b + a:
                        op_type = 'rev'

            if op_type == 'fwd':
                return q_a + q_b
            else:
                return q_b + q_a

    # Look for classic verbal arithmetic (SEND + MORE = MONEY)
    match_classic = re.search(r'([A-Za-z]+)\s*\+\s*([A-Za-z]+)\s*=\s*([A-Za-z]+)', prompt)
    if match_classic:
        w1, w2, w3 = match_classic.group(1).upper(), match_classic.group(2).upper(), match_classic.group(3).upper()
        return _solve_z3(w1, w2, w3)

    return None

def _solve_z3(w1: str, w2: str, sum_w: str) -> Optional[str]:
    import z3
    s = z3.Solver()

    letters = list(set(w1 + w2 + sum_w))
    if len(letters) > 10:
        return None

    vars = {l: z3.Int(l) for l in letters}

    for v in vars.values():
        s.add(v >= 0, v <= 9)

    s.add(z3.Distinct(*list(vars.values())))

    if len(w1) > 1:
        s.add(vars[w1[0]] != 0)
    if len(w2) > 1:
        s.add(vars[w2[0]] != 0)
    if len(sum_w) > 1:
        s.add(vars[sum_w[0]] != 0)

    def word_to_expr(w):
        expr = 0
        for l in w:
            expr = expr * 10 + vars[l]
        return expr

    s.add(word_to_expr(w1) + word_to_expr(w2) == word_to_expr(sum_w))

    res = s.check()
    if res == z3.sat:
        m = s.model()
        solution = {l: m[vars[l]].as_long() for l in letters}

        # Check uniqueness
        block = []
        for l in letters:
            block.append(vars[l] != solution[l])
        s.add(z3.Or(block))

        if s.check() == z3.sat:
            # multiple solutions
            return None

        ans_sum = ''.join(str(solution[c]) for c in sum_w)
        return ans_sum
    return None

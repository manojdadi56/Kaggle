import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate import generate
from solve import solve

def test_numeral_solver():
    problems = generate(100)
    success = 0
    for p in problems:
        ans_trace = solve(p['prompt'])
        expected_box = f"\\boxed{{{p['answer']}}}"
        if expected_box in ans_trace:
            success += 1
        else:
            print(f"FAILED on prompt: {p['prompt']}")
            print(f"Expected answer: {p['answer']}")
            print(f"Trace returned: {ans_trace}")

    print(f"Passed {success}/100 tests.")
    assert success == 100, f"Failed {100 - success} tests."

if __name__ == "__main__":
    test_numeral_solver()

import json
import math
import re
from solve import solve, extract_answer

def test_gravity_solver():
    with open("sample.jsonl", "r") as f:
        lines = f.readlines()

    correct = 0
    total = len(lines)

    for i, line in enumerate(lines):
        data = json.loads(line)
        prompt = data["question"]
        expected_ans_str = data["answer"]

        # solve
        completion = solve(prompt)
        pred_ans_str = f"\\boxed{{{extract_answer(completion)}}}"

        if pred_ans_str == expected_ans_str:
            correct += 1
        else:
            print(f"Mismatch on problem {data['id']}: expected {expected_ans_str}, got {pred_ans_str}")
            print(f"Prompt:\n{prompt}")
            print(f"Completion:\n{completion}")

    print(f"Accuracy: {correct}/{total} ({(correct/total)*100:.2f}%)")
    assert correct == total, "Solver failed on some generated samples"

if __name__ == "__main__":
    test_gravity_solver()

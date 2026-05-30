import sys
import re

from generate import generate
from solve import solve

def extract_answer(reasoning_text: str) -> str:
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", reasoning_text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def main():
    print("Running 100-sample holdout validation for Cipher...")
    correct = 0
    total = 100

    for i in range(total):
        problem = generate()
        prompt = problem['prompt']
        expected_answer = problem['answer']

        cot = solve(prompt)
        extracted = extract_answer(cot)

        if extracted == expected_answer:
            correct += 1
        else:
            print(f"\n--- Failure on sample {i} ---")
            print(f"Prompt:\n{prompt}")
            print(f"Expected: {expected_answer}")
            print(f"Extracted: {extracted}")
            print(f"CoT:\n{cot}")
            break

    print(f"\nResult: {correct}/{total} ({correct/total*100:.1f}%)")
    if correct == total:
        print("PASS: 100% solve rate achieved.")
        sys.exit(0)
    else:
        print("FAIL: Did not achieve 100% solve rate.")
        sys.exit(1)

if __name__ == "__main__":
    main()

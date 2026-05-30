import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(__file__))
from solve import reasoning_equation_numeric
from parse import parse_equation_numeric

def extract_answer(reasoning_text: str) -> str:
    if not reasoning_text: return ""
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", reasoning_text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def run_test(path):
    correct_deduce = 0
    total_deduce = 0
    correct_guess = 0
    total_guess = 0
    failures = []

    with open(path, 'r') as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            prob = parse_equation_numeric(d['prompt'])
            res = reasoning_equation_numeric(prob)
            ans = extract_answer(res)

            is_correct = (ans == str(d['answer']))

            if d['category'] == 'equation_numeric_deduce':
                total_deduce += 1
                if is_correct: correct_deduce += 1
                else: failures.append(d)
            else:
                total_guess += 1
                if is_correct: correct_guess += 1
                else: failures.append(d)

    print(f"Deduce Accuracy: {correct_deduce}/{total_deduce}")
    print(f"Guess Accuracy: {correct_guess}/{total_guess}")
    print(f"Total Accuracy: {correct_deduce+correct_guess}/{total_deduce+total_guess}")

    if failures:
        print("\nFailure sample:")
        print(failures[0])

run_test('competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/equation_numeric/holdout.jsonl')

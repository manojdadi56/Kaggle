import json
import random
import os

random.seed(42)

def generate_deduce_problem(id_counter):
    # Let's pick an operator and an operation.
    # operators could be '+', '-', '*', '/'
    # transformations could be reverse operands, reverse result, or just simple

    ops = [
        # simple add
        (lambda a, b: a+b, '+', False, False),
        # absolute difference
        (lambda a, b: abs(a-b), '-', False, False),
        # reverse add (b+a)
        (lambda a, b: b+a, '+', False, False),
        # addition reversed result
        (lambda a, b: int(str(a+b)[::-1] if str(a+b) else "0"), '+', False, True)
    ]

    op_fn, op_char, rev_op, rev_res = random.choice(ops)

    examples = []
    for _ in range(4):
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        ans = op_fn(a, b)
        examples.append((a, b, ans))

    qa = random.randint(10, 99)
    qb = random.randint(10, 99)
    qans = op_fn(qa, qb)

    prompt = "Discover the transformation rule for the equation.\n"
    for a, b, ans in examples:
        prompt += f"{a}{op_char}{b} = {ans}\n"
    prompt += f"\nWhat is {qa}{op_char}{qb}?"

    return {
        "id": f"deduce_{id_counter}",
        "category": "equation_numeric_deduce",
        "prompt": prompt,
        "answer": str(qans)
    }

def generate_guess_problem(id_counter):
    # In guess, the operator in question doesn't appear in examples.
    # Typically absolute difference is guessed.

    # Let's say examples use '+', but question uses '-' (and the rule is abs diff)

    examples = []
    for _ in range(3):
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        ans = abs(a-b)
        examples.append((a, b, ans))

    qa = random.randint(10, 99)
    qb = random.randint(10, 99)
    qans = abs(qa-qb)

    prompt = "A secret rule is applied to equations. Guess the rule.\n"
    for a, b, ans in examples:
        prompt += f"{a}+{b} = {ans}\n"
    prompt += f"\nWhat is {qa}-{qb}?"

    return {
        "id": f"guess_{id_counter}",
        "category": "equation_numeric_guess",
        "prompt": prompt,
        "answer": str(qans)
    }

def generate_holdout(n_deduce=50, n_guess=30):
    data = []
    for i in range(n_deduce):
        data.append(generate_deduce_problem(i))
    for i in range(n_guess):
        data.append(generate_guess_problem(i))

    with open('competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/equation_numeric/holdout.jsonl', 'w') as f:
        for d in data:
            f.write(json.dumps(d) + '\n')

generate_holdout()
print("Generated holdout.jsonl")

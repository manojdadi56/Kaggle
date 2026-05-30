import json
import random
import math

def generate_gravity_problem(problem_id):
    """
    Generates a single synthetic gravity problem following the structure:
    For t = <t1>s, distance = <d1> m
    ...
    Now, determine the falling distance for t = <target_t>s given d = 0.5gt^2.
    """
    # 0.5g is our constant k
    # Choose a realistic-ish g, say between 1.0 and 20.0, so k is between 0.5 and 10.0
    k = round(random.uniform(0.5, 10.0), 4)

    num_examples = random.randint(3, 6)
    examples = []

    prompt = ""
    for _ in range(num_examples):
        t = round(random.uniform(1.0, 10.0), 2)
        d = round(k * (t**2), 2)
        examples.append((t, d))
        prompt += f"For t = {t}s, distance = {d} m\n"

    target_t = round(random.uniform(1.0, 10.0), 2)
    prompt += f"Now, determine the falling distance for t = {target_t}s given d = 0.5gt^2."

    # Calculate the exact expected answer to match the solver logic
    rates = []
    for (t, d) in examples:
        if t != 0:
            rates.append(d / (t**2))

    # The solver will compute the median rate
    rates.sort()
    n = len(rates)
    if n % 2 == 0:
        median_rate = (rates[n//2 - 1] + rates[n//2]) / 2.0
    else:
        median_rate = rates[n//2]

    result = median_rate * (target_t**2)
    trunc_result = math.trunc(result * 1000) / 1000.0
    answer = f"\\boxed{{{trunc_result:.3f}}}"

    return {
        "id": f"gravity_synth_{problem_id:04d}",
        "category": "gravity",
        "question": prompt,
        "answer": answer
    }

def main():
    random.seed(42) # For reproducibility
    problems = []
    for i in range(100):
        problems.append(generate_gravity_problem(i))

    with open("sample.jsonl", "w") as f:
        for p in problems:
            f.write(json.dumps(p) + "\n")

    print("Generated 100 gravity problems into sample.jsonl")

if __name__ == "__main__":
    main()

import random

def generate_problem(seed: int = None) -> tuple[str, str]:
    if seed is not None:
        random.seed(seed)

    num_examples = random.randint(3, 5)

    # Using a 2 decimal place factor to ensure precision doesn't drift too much
    factor = round(random.uniform(0.1, 10.0), 2)

    prompt = "In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:\n"

    # Store exact examples to compute the answer consistently with the solver
    examples = []
    for _ in range(num_examples):
        inp = round(random.uniform(5.0, 50.0), 2)
        outp = round(inp * factor, 2)
        examples.append((inp, outp))
        prompt += f"{inp:.2f} m becomes {outp:.2f}\n"

    target_val = round(random.uniform(5.0, 50.0), 2)
    prompt += f"Now, convert the following measurement: {target_val:.2f} m"

    # Calculate exactly like the solver to match
    factors = [outp / inp for inp, outp in examples if inp != 0]
    factors.sort()
    mid = len(factors) // 2
    if len(factors) % 2 != 0:
        median_factor = factors[mid]
    else:
        median_factor = (factors[mid-1] + factors[mid]) / 2.0

    ans = target_val * median_factor

    # Ensure answers are emitted inside \boxed{...} as per the Hard Invariants
    return prompt, f"\\boxed{{{ans:.2f}}}"

if __name__ == "__main__":
    p, a = generate_problem()
    print("Prompt:")
    print(p)
    print("Expected:", a)

import json
import random
import os
import sys

def generate_bit_manipulation_puzzle():
    """Generates a bit manipulation puzzle."""
    a = random.randint(0, 15)
    b = random.randint(0, 15)
    ops = ['AND', 'OR', 'XOR']
    op = random.choice(ops)

    if op == 'AND':
        ans = a & b
    elif op == 'OR':
        ans = a | b
    else:
        ans = a ^ b

    question = f"What is the result of the bitwise {op} operation between {a} and {b}?"
    answer = f"\\boxed{{{ans}}}"
    return {"question": question, "answer": answer, "metadata": {"type": "bit_manipulation", "a": a, "b": b, "op": op, "ans": ans}}

def generate_linear_algebra_puzzle():
    """Generates a simple linear algebra puzzle (dot product)."""
    v1 = [random.randint(1, 5), random.randint(1, 5)]
    v2 = [random.randint(1, 5), random.randint(1, 5)]

    ans = v1[0]*v2[0] + v1[1]*v2[1]

    question = f"What is the dot product of the vectors {v1} and {v2}?"
    answer = f"\\boxed{{{ans}}}"
    return {"question": question, "answer": answer, "metadata": {"type": "linear_algebra", "v1": v1, "v2": v2, "ans": ans}}

def generate_transformation_table_puzzle():
    """Generates a table transformation logic puzzle."""
    # simple rule: output = input * factor + offset
    factor = random.randint(2, 5)
    offset = random.randint(1, 10)

    inputs = random.sample(range(1, 16), 3)

    outputs = [i * factor + offset for i in inputs]

    target_input = random.randint(16, 20)
    target_output = target_input * factor + offset

    table = " | ".join([f"{i} -> {o}" for i, o in zip(inputs, outputs)])

    question = f"Given the transformation rules: {table}, what is the output for {target_input}?"
    answer = f"\\boxed{{{target_output}}}"
    return {"question": question, "answer": answer, "metadata": {"type": "transformation_table", "factor": factor, "offset": offset, "target_input": target_input, "target_output": target_output}}

def deduplicate_and_filter(puzzles):
    """Deduplicates puzzles based on exact question string matching."""
    seen = set()
    filtered = []
    for p in puzzles:
        if p["question"] not in seen:
            seen.add(p["question"])
            filtered.append(p)
    return filtered

def generate_dataset(num_samples=10):
    puzzles = []
    generators = [
        generate_bit_manipulation_puzzle,
        generate_linear_algebra_puzzle,
        generate_transformation_table_puzzle
    ]

    for _ in range(num_samples * 2): # generate extra to account for duplicates
        gen_func = random.choice(generators)
        puzzles.append(gen_func())

    filtered_puzzles = deduplicate_and_filter(puzzles)
    return filtered_puzzles[:num_samples]

if __name__ == "__main__":
    # Ensure seed for reproducibility during sample generation if needed
    random.seed(42)
    sample_data = generate_dataset(15)

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "sample.jsonl")

    with open(output_path, "w") as f:
        for item in sample_data:
            # strip metadata for the final output
            out_item = {"question": item["question"], "answer": item["answer"]}
            f.write(json.dumps(out_item) + "\n")

    print(f"Generated {len(sample_data)} puzzles in {output_path}")

import re
import math
import json
import argparse
import sys
from typing import Optional, Dict, Any

def extract_answer(reasoning_text: str) -> str:
    """Extract the answer from \\boxed{...}."""
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", reasoning_text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def compare_answer(stored_answer: str, predicted: str) -> bool:
    """Verify if the answer matches based on rules."""
    stored_answer = str(stored_answer).strip()
    predicted = str(predicted).strip()

    if re.fullmatch(r"[01]+", stored_answer):
        return predicted.lower() == stored_answer.lower()

    try:
        stored_num = float(stored_answer)
        predicted_num = float(predicted)
        return math.isclose(stored_num, predicted_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == stored_answer.lower()

def verify_and_format_cot(problem_id: str, category: str, prompt: str, expected_answer: str, reasoning_text: str) -> Optional[Dict[str, Any]]:
    """Validates the reasoning text against the expected answer and formats it if correct."""
    extracted_answer = extract_answer(reasoning_text)

    is_correct = compare_answer(expected_answer, extracted_answer)

    if not is_correct:
        return None

    completion = f"{reasoning_text}\n</think>\n\\boxed{{{extracted_answer}}}<|im_end|>"

    return {
        "problem_id": problem_id,
        "category": category,
        "prompt": prompt,
        "completion": completion,
        "expected_answer": str(expected_answer),
        "extracted_answer": extracted_answer,
        "is_correct": is_correct
    }

def main():
    parser = argparse.ArgumentParser(description="Generate verified CoT SFT examples.")
    parser.add_argument("--input", type=str, help="Path to input jsonl file containing problem data.")
    parser.add_argument("--output", type=str, help="Path to output jsonl file.")
    parser.add_argument("--mock", action="store_true", help="Run a mock generation")
    args = parser.parse_args()

    if args.mock:
        sample_prompt = "What is 2 + 2?"
        sample_expected = "4"
        sample_reasoning = "To find 2 + 2, we add 2 and 2.\n2 + 2 = 4.\nTherefore, the answer is \\boxed{4}."

        result = verify_and_format_cot(
            problem_id="mock-1",
            category="math",
            prompt=sample_prompt,
            expected_answer=sample_expected,
            reasoning_text=sample_reasoning
        )

        if result:
            print("Verified successfully:")
            print(json.dumps(result, indent=2))
        else:
            print("Verification failed.")
            sys.exit(1)
        return

    if not args.input or not args.output:
        print("Please provide both --input and --output paths, or use --mock.")
        sys.exit(1)

    generated = 0
    rejected = 0

    with open(args.input, 'r') as f_in, open(args.output, 'w') as f_out:
        for line in f_in:
            if not line.strip():
                continue

            data = json.loads(line)
            # Input format expected: {"id": "...", "category": "...", "prompt": "...", "answer": "...", "reasoning": "..."}

            result = verify_and_format_cot(
                problem_id=data.get("id", ""),
                category=data.get("category", ""),
                prompt=data.get("prompt", ""),
                expected_answer=data.get("answer", ""),
                reasoning_text=data.get("reasoning", "")
            )

            if result:
                f_out.write(json.dumps(result) + "\n")
                generated += 1
            else:
                rejected += 1

    print(f"Generated {generated} verified examples.")
    print(f"Rejected {rejected} examples due to verification failure.")

if __name__ == "__main__":
    main()

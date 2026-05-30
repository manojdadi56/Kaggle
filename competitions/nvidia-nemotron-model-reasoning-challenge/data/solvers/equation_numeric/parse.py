import re
from solve import Problem, Example

def parse_equation_numeric(prompt: str) -> Problem:
    """Parses a prompt into a Problem instance for equation_numeric solver."""
    examples = []
    question = ""

    lines = prompt.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line: continue

        m_eq = re.search(r"(\d+\s*\D\s*\d+)\s*(?:=|->)\s*(-?\d+)", line)
        if m_eq:
            inp = m_eq.group(1).replace(" ", "")
            examples.append(Example(input_value=inp, output_value=m_eq.group(2).strip()))
            continue

        m_q = re.search(r"(\d+\s*\D\s*\d+)", line)
        if m_q and "example" not in line.lower() and "rule" not in line.lower() and "=" not in line:
            question = m_q.group(1).replace(" ", "")

    return Problem(examples=examples, question=question)

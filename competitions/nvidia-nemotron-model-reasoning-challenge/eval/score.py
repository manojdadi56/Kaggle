def extract_boxed(text: str) -> str | None:
    if not text:
        return None
    idx = text.rfind(r"\boxed{")
    if idx == -1:
        return None
    start = idx + len(r"\boxed{")
    brace_count = 1
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
        if brace_count == 0:
            return text[start:i]
    return None


def score(predictions: list[str], gold: list[str]) -> float:
    if len(predictions) != len(gold):
        raise ValueError("Length mismatch between predictions and gold")
    if not predictions or not gold:
        return 0.0

    correct = 0
    for p, g in zip(predictions, gold):
        p_val = extract_boxed(p)
        if p_val is None:
            # Missing \boxed{} -> wrong
            continue

        g_val = extract_boxed(g)
        if g_val is None:
            # Gold doesn't have \boxed{} formatting? We'll assume the string is the value
            g_val = str(g).strip()
        else:
            g_val = g_val.strip()

        p_val = p_val.strip()

        # Exact string match
        if p_val == g_val:
            correct += 1
            continue

        # Numeric match within 1e-2 tolerance
        try:
            if abs(float(p_val) - float(g_val)) <= 1e-2:
                correct += 1
        except ValueError:
            pass

    return correct / len(predictions)

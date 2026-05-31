import re
import collections
from typing import Dict, Optional, List

WONDERLAND_WORDS = [
    "ALICE", "WONDERLAND", "RABBIT", "HATTER", "QUEEN", "CAT", "TEA",
    "TIME", "WATCH", "HOLE", "CHESHIRE", "MAD", "MARCH", "HARE",
    "DORMOUSE", "KING", "HEARTS", "WHITE", "DUCHESS", "TURTLE",
    "MOCK", "GRYPHON", "CATERPILLAR", "MUSHROOM", "PIG", "PEPPER",
    "GARDEN", "CROQUET", "FLAMINGO", "HEDGEHOG", "TART", "KNAVE",
    "JURY", "COURT", "WITNESS", "EVIDENCE", "DREAM", "SISTER",
    "BANK", "BOOK", "PICTURES", "CONVERSATION", "DAISY", "CHAIN",
    "SLEEPY", "STUPID", "WAISTCOAT", "POCKET", "HURRY", "NEVER",
    "BEFORE", "LOOKED", "STARTED", "FEET", "FLASHED", "ACROSS",
    "MIND", "SEEN", "EITHER", "TOOK", "BURNING", "CURIOSITY",
    "RAN", "FIELD", "AFTER", "FORTUNATELY", "JUST", "TIME",
    "SEE", "POP", "DOWN", "LARGE", "RABBIT", "HOLE", "UNDER", "HEDGE",
    "ANOTHER", "MOMENT", "WENT", "ALICE", "AFTER", "NEVER", "ONCE",
    "CONSIDERING", "HOW", "WORLD", "SHE", "WAS", "GET", "OUT", "AGAIN"
]
WONDERLAND_WORDS = sorted(list(set(WONDERLAND_WORDS)))

def get_word_pattern(word: str) -> tuple:
    """Returns a numeric pattern for a word to handle substitution ciphers."""
    char_to_num = {}
    pattern = []
    num = 0
    for char in word:
        if char not in char_to_num:
            char_to_num[char] = num
            num += 1
        pattern.append(char_to_num[char])
    return tuple(pattern)

def solve(prompt: str) -> str:
    """
    Decodes the substitution cipher based on the given prompt.
    Produces a deterministic Chain-of-Thought trace.
    """
    lines = [line.strip() for line in prompt.split('\n') if line.strip()]
    mapping_counts = collections.defaultdict(lambda: collections.defaultdict(int))

    question_line = None
    for line in lines:
        if ' -> ' in line:
            src, dst = line.split(' -> ')
            for s, d in zip(src, dst):
                if s.isalpha() and d.isalpha():
                    mapping_counts[s.upper()][d.upper()] += 1
        elif "Now, decrypt the following text:" in line:
            question_line = line.split("Now, decrypt the following text:")[1].strip()
        elif "Decrypt:" in line:
            question_line = line.split("Decrypt:")[1].strip()
        elif "Decrypt" in line:
            question_line = line.split("Decrypt")[1].strip()

    if not question_line:
        question_line = lines[-1]

    # Resolve conflicting character mappings using the most frequent one.
    mapping = {}
    for s, counts in mapping_counts.items():
        best_d = max(counts.items(), key=lambda x: (x[1], x[0]))[0]
        mapping[s] = best_d

    cot = "## Classification\n"
    cot += "Letters are consistently substituted across examples — the same ciphertext\n"
    cot += "letter always maps to the same plaintext letter. This is CIPHER.\n\n"
    cot += "## Reasoning\n"
    cot += "### Build mapping from examples\n"

    # Sort mapping for deterministic output
    for s in sorted(mapping.keys()):
        cot += f"{s} -> {mapping[s]}\n"

    cot += f"\n### Decrypt the question\n"

    words = question_line.split()
    words_to_resolve = []
    for word in words:
        clean_word = "".join(c for c in word if c.isalpha()).upper()
        if clean_word:
            words_to_resolve.append((word, clean_word))

    def get_candidates(word):
        word_pattern = get_word_pattern(word)
        word_len = len(word)
        candidates = []
        mapped_values = set(mapping.values())

        for w in WONDERLAND_WORDS:
            if len(w) == word_len and get_word_pattern(w) == word_pattern:
                valid = True
                for i, char in enumerate(word):
                    upper_char = char.upper()
                    mapped_char = mapping.get(upper_char)
                    if mapped_char and mapped_char != w[i].upper():
                        valid = False
                        break

                # Bijective mapping enforcement
                if valid:
                    for i, char in enumerate(word):
                        upper_char = char.upper()
                        if upper_char not in mapping and w[i].upper() in mapped_values:
                            valid = False
                            break
                if valid:
                    candidates.append(w)
        return candidates

    # Iteratively resolve unambiguous words
    changed = True
    while changed:
        changed = False
        for original_word, word in words_to_resolve:
            missing_chars = any(c.upper() not in mapping for c in word)
            if not missing_chars:
                continue

            candidates = get_candidates(word)
            if len(candidates) == 1:
                best_match = candidates[0]
                cot += f"Word '{word}' unambiguously decrypts to '{best_match}'.\n"
                for i, char in enumerate(word):
                    upper_char = char.upper()
                    if upper_char not in mapping:
                        mapping[upper_char] = best_match[i].upper()
                        cot += f"New mapping: {upper_char} -> {best_match[i].upper()}\n"
                changed = True

    # If there are still unresolved words, guess the first candidate
    changed = True
    while changed:
        changed = False
        for original_word, word in words_to_resolve:
            missing_chars = any(c.upper() not in mapping for c in word)
            if not missing_chars:
                continue

            candidates = get_candidates(word)
            if candidates:
                best_match = candidates[0]
                cot += f"Word '{word}' has multiple candidates: {candidates}. Guessing '{best_match}'.\n"
                for i, char in enumerate(word):
                    upper_char = char.upper()
                    if upper_char not in mapping:
                        mapping[upper_char] = best_match[i].upper()
                        cot += f"New mapping: {upper_char} -> {best_match[i].upper()}\n"
                changed = True

    # Apply final mapping
    final_ans = ""
    for c in question_line:
        if c.isalpha():
            is_upper = c.isupper()
            mapped = mapping.get(c.upper())
            if mapped:
                final_ans += mapped.upper() if is_upper else mapped.lower()
            else:
                final_ans += c
        else:
            final_ans += c

    cot += f"\nFull decryption of '{question_line}':\n{final_ans}\n"
    cot += f"\n\\boxed{{{final_ans}}}\n"

    return cot

def build_rows(prompts: List[str]) -> List[Dict[str, str]]:
    """Builds a list of dictionaries with prompt, response, and category."""
    rows = []
    for prompt in prompts:
        rows.append({
            "prompt": prompt,
            "response": solve(prompt),
            "category": "cipher"
        })
    return rows

def test_solve_basic():
    prompt = "A B C -> X Y Z\n\nDecrypt: A B C"
    result = solve(prompt)
    assert "\\boxed{X Y Z}" in result

def test_solve_lower_upper():
    prompt = "A b C -> X y Z\n\nDecrypt: A b c"
    result = solve(prompt)
    assert "\\boxed{X y z}" in result

def test_solve_words():
    prompt = "UCOOV -> QUEEN\nPWGTFYOQG -> DISCOVERS\n\nDecrypt: UCOOV PWGTFYOQG"
    result = solve(prompt)
    assert "\\boxed{QUEEN DISCOVERS}" in result

def test_solve_conflict_resolution():
    prompt = "A B C -> X Y Z\nA B C -> X W Z\nA B C -> X Y Z\n\nDecrypt: B"
    result = solve(prompt)
    assert "\\boxed{Y}" in result

def test_build_rows():
    prompts = ["A -> X\nDecrypt: A", "B -> Y\nDecrypt: B"]
    rows = build_rows(prompts)
    assert len(rows) == 2
    assert rows[0]["prompt"] == prompts[0]
    assert "\\boxed{X}" in rows[0]["response"]
    assert rows[0]["category"] == "cipher"
    assert rows[1]["prompt"] == prompts[1]
    assert "\\boxed{Y}" in rows[1]["response"]
    assert rows[1]["category"] == "cipher"

def test_solve_punctuation():
    prompt = "UCOOV, PWGTFYOQG! -> QUEEN, DISCOVERS!\n\nDecrypt: UCOOV, PWGTFYOQG!"
    result = solve(prompt)
    assert "\\boxed{QUEEN, DISCOVERS!}" in result

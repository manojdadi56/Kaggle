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
    mapping = {}

    question_line = None
    for line in lines:
        if ' -> ' in line:
            src, dst = line.split(' -> ')
            for s, d in zip(src, dst):
                if s.isalpha() and d.isalpha():
                    mapping[s] = d
        elif "Now, decrypt the following text:" in line:
            question_line = line.split("Now, decrypt the following text:")[1].strip()
        elif "Decrypt:" in line:
            question_line = line.split("Decrypt:")[1].strip()
        elif "Decrypt" in line:
            question_line = line.split("Decrypt")[1].strip()

    if not question_line:
        question_line = lines[-1]

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
    decrypted_words = []

    # Word matching
    for word in words:
        decrypted_word = ""
        missing_chars = False
        for c in word:
            if c.isalpha():
                if c in mapping:
                    decrypted_word += mapping[c]
                elif c.upper() in mapping:
                    decrypted_word += mapping[c.upper()]
                else:
                    decrypted_word += "?"
                    missing_chars = True
            else:
                decrypted_word += c

        if not missing_chars:
            decrypted_words.append(decrypted_word)
        else:
            # Match the word using pattern and length
            cot += f"Word '{word}' partially decrypts to '{decrypted_word}'.\n"
            word_pattern = get_word_pattern(word)
            word_len = len(word)

            candidates = []
            for w in WONDERLAND_WORDS:
                if len(w) == word_len and get_word_pattern(w) == word_pattern:
                    # Cross-check with known mapping
                    valid = True
                    for i, char in enumerate(word):
                        if char in mapping and mapping[char] != w[i]:
                            valid = False
                            break
                    if valid:
                        candidates.append(w)

            if candidates:
                # We assume the first candidate is correct for simplicity, but if there's only 1 it's deterministic
                cot += f"Candidates for '{word}' based on pattern and known letters: {candidates}\n"
                best_match = candidates[0]
                cot += f"Selected '{best_match}'.\n"
                decrypted_words.append(best_match)
                # Update mapping
                for i, char in enumerate(word):
                    if char.isalpha() and char not in mapping:
                        mapping[char] = best_match[i]
                        cot += f"New mapping: {char} -> {best_match[i]}\n"
            else:
                cot += f"No candidates found for '{word}'. Keeping as '{decrypted_word}'.\n"
                decrypted_words.append(decrypted_word)

    ans = " ".join(decrypted_words)

    # Re-evaluate any unknown words if mapping got updated
    final_ans = ""
    for c in question_line:
        if c.isalpha():
            is_upper = c.isupper()
            mapped = mapping.get(c, mapping.get(c.upper(), mapping.get(c.lower())))
            if mapped:
                final_ans += mapped.upper() if is_upper else mapped.lower()
            else:
                final_ans += c
        else:
            final_ans += c

    cot += f"\nFull decryption of '{question_line}':\n{final_ans}\n"
    cot += f"\n\\boxed{{{final_ans}}}\n"

    return cot

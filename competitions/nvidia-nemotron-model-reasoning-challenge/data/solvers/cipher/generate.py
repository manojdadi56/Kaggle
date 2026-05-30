import random
import string
import json
from typing import Dict, Any

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
# Remove duplicates
WONDERLAND_WORDS = list(set(WONDERLAND_WORDS))

def generate() -> Dict[str, Any]:
    """Generates a cipher problem."""
    # We want 3-5 examples of plaintext
    num_examples = random.randint(3, 5)

    # Each example is 2-4 words
    examples_pt = []
    for _ in range(num_examples):
        words_count = random.randint(2, 4)
        words = random.sample(WONDERLAND_WORDS, words_count)
        examples_pt.append(" ".join(words))

    # Question is 2-5 words
    question_words_count = random.randint(2, 5)
    question_words = random.sample(WONDERLAND_WORDS, question_words_count)
    question_pt = " ".join(question_words)

    # Generate cipher mapping
    alphabet = list(string.ascii_uppercase)
    shuffled = list(string.ascii_uppercase)
    random.shuffle(shuffled)
    mapping = dict(zip(alphabet, shuffled))

    def encrypt(text: str) -> str:
        return "".join(mapping.get(c, c) for c in text.upper())

    prompt = ""
    for pt in examples_pt:
        prompt += f"{encrypt(pt)} -> {pt}\n"

    prompt += f"\nDecrypt: {encrypt(question_pt)}"

    return {
        "prompt": prompt,
        "answer": question_pt,
        "category": "cipher"
    }

if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))

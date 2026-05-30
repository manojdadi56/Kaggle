import re
from typing import Literal

Category = Literal[
    "bit_manipulation",
    "cipher",
    "cryptarithm_deduce",
    "cryptarithm_guess",
    "equation_numeric_deduce",
    "equation_numeric_guess",
    "gravity",
    "numeral",
    "unit_conversion",
    "unknown"
]

def classify(prompt: str) -> Category:
    """Classifies a prompt into one of the 9 taxonomy categories.

    See data/taxonomy/taxonomy.md for details on each category.
    """
    if not isinstance(prompt, str):
        return 'unknown'

    p = prompt.lower()

    # 5. Bit Manipulation
    if re.search(r'bit.?manipul|binary|8.?bit|bitwise|bit.*transform', p):
        return 'bit_manipulation'

    # 1. Numeral Conversion
    elif re.search(r'numeral system|base[- ]?\d|number.*convert|radix|secret number|roman.*numeral|convert.*to an integer|convert.*to roman', p):
        return 'numeral'

    # 2. Gravity
    elif re.search(r'gravit|gravity|falling|free.?fall|acceleration due to', p):
        return 'gravity'

    # 3. Equation Transformation
    elif re.search(r'transformation rule|equation.*transform|secret.*rule.*equation|rule.*applied.*equation', p):
        if re.search(r'guess|assume|assumptions', p):
            return 'equation_numeric_guess'
        return 'equation_numeric_deduce'

    # 4. Cipher
    elif re.search(r'encrypt|cipher|decrypt|secret.*code.*letter|coded.*message|secret.*text', p):
        return 'cipher'

    # 6. Unit Conversion
    elif re.search(r'unit.?conver|measurement|becomes.*\d|secret.*conver.*measur', p):
        return 'unit_conversion'

    # 7. Cryptarithm (Verbal Arithmetic)
    elif re.search(r'cryptarithm|verbal arithmetic|verbal.*arithmetic|verbal.*puzzle', p):
        if re.search(r'guess|assume|assumptions', p):
            return 'cryptarithm_guess'
        return 'cryptarithm_deduce'

    return 'unknown'

def test_classify_numeral():
    prompt = "Convert 1893 to Roman numerals."
    assert classify(prompt) == 'numeral'
    prompt2 = "Convert CLXXVII to an integer."
    assert classify(prompt2) == 'numeral'
    prompt3 = "3439 -> MMMCDXXXIX\nConvert 1893 to Roman numerals."
    assert classify(prompt3) == 'numeral'
    prompt4 = "CLXXVII -> 177\nConvert MMMXCII to an integer."
    assert classify(prompt4) == 'numeral'

def test_classify_gravity():
    prompt = "Determine the acceleration due to gravity on planet Zorg if an object falls 10m in 2s."
    assert classify(prompt) == 'gravity'

def test_classify_equation_numeric():
    prompt = "Discover the transformation rule for the equation 64-65 = 201."
    assert classify(prompt) == 'equation_numeric_deduce'

    prompt2 = "Discover the secret rule applied to the equation 2+2=5, requiring assumptions about absolute difference."
    assert classify(prompt2) == 'equation_numeric_guess'

def test_classify_cipher():
    prompt = "Decrypt this secret code message using the substitution cipher."
    assert classify(prompt) == 'cipher'

def test_classify_bit_manipulation():
    prompt = "Apply a bitwise transformation rule to the 8-bit binary number 10101010."
    assert classify(prompt) == 'bit_manipulation'

def test_classify_unit_conversion():
    prompt = "Convert a measurement where 5 widgets becomes 20 gadgets."
    assert classify(prompt) == 'unit_conversion'

def test_classify_cryptarithm():
    prompt = "Solve the verbal arithmetic puzzle SEND + MORE = MONEY."
    assert classify(prompt) == 'cryptarithm_deduce'

    prompt2 = "Solve this cryptarithm puzzle, you must guess the unknown rule."
    assert classify(prompt2) == 'cryptarithm_guess'

    prompt3 = "Solve the verbal arithmetic puzzle where you must guess the operations."
    assert classify(prompt3) == 'cryptarithm_guess'

def test_classify_unknown():
    assert classify("What is the capital of France?") == 'unknown'
    assert classify(None) == 'unknown'

if __name__ == "__main__":
    # 1. Run Tests
    test_classify_numeral()
    test_classify_gravity()
    test_classify_equation_numeric()
    test_classify_cipher()
    test_classify_bit_manipulation()
    test_classify_unit_conversion()
    test_classify_cryptarithm()
    test_classify_unknown()
    print("All tests passed.")

    # 2. Report coverage on train.csv (if exists)
    import os
    import csv

    # Check if there is a train.csv
    train_csv_path = None

    # Look around for train.csv
    for root, dirs, files in os.walk("competitions/nvidia-nemotron-model-reasoning-challenge"):
        if "train.csv" in files:
            train_csv_path = os.path.join(root, "train.csv")
            break

    if train_csv_path:
        with open(train_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = 0
            unknowns = 0
            for row in reader:
                prompt = row.get("prompt", "")
                if prompt:
                    total += 1
                    if classify(prompt) == 'unknown':
                        unknowns += 1
        print(f"Train Coverage: {total - unknowns} / {total} ({(total - unknowns) / total * 100:.2f}%)")
    else:
        print("train.csv not found, skipping coverage report.")

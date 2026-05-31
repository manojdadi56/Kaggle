import re

def roman_to_int(s: str) -> int:
    roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    prev_value = 0
    for char in reversed(s):
        value = roman_values.get(char, 0)
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    return total

def int_to_roman(num: int) -> str:
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def base_to_dec(encoded: str, base: int, alphabet: list[str]) -> int:
    val = 0
    for char in encoded:
        val = val * base + alphabet.index(char)
    return val

def dec_to_base(n: int, base: int, alphabet: list[str]) -> str:
    if n == 0:
        return alphabet[0]
    res = ""
    while n > 0:
        res = alphabet[n % base] + res
        n //= base
    return res

def solve(prompt: str) -> str:
    lines = prompt.strip().split('\n')
    last_line = lines[-1].strip()

    # 1. Check for Roman numerals
    match_roman_to_int = re.search(r'Convert ([A-Z]+) to an integer', last_line)
    if match_roman_to_int:
        roman = match_roman_to_int.group(1)
        res = roman_to_int(roman)
        return (
            "We are asked to convert a Roman numeral into an integer.\n"
            f"The Roman numeral is {roman}.\n"
            f"We know the values are I=1, V=5, X=10, L=50, C=100, D=500, M=1000.\n"
            f"Converting {roman} step by step yields {res}.\n"
            f"\\boxed{{{res}}}"
        )

    match_int_to_roman = re.search(r'Convert (\d+) to Roman numerals', last_line)
    if not match_int_to_roman:
        match_int_to_roman = re.search(r'write the number (\d+) in the Wonderland numeral system', last_line)
    if match_int_to_roman:
        num = int(match_int_to_roman.group(1))
        res = int_to_roman(num)
        return (
            "We are asked to convert an integer into Roman numerals.\n"
            f"The integer is {num}.\n"
            f"Converting {num} step by step yields {res}.\n"
            f"\\boxed{{{res}}}"
        )

    # 2. Check for arbitrary base
    # "In a numeral system with base {base} and digits {digits_str}, ..."
    match_base = re.search(r'base (\d+) and digits (.*?),\s*(convert|calculate)(.*)', last_line)
    if match_base:
        base = int(match_base.group(1))
        digits_str = match_base.group(2)
        action_verb = match_base.group(3)
        action_rest = match_base.group(4)
        alphabet = digits_str.split(' ')

        # Action: base_to_dec
        if action_verb == "convert" and "to decimal" in action_rest:
            m_enc = re.search(r'([\S]+) to decimal', action_rest)
            if m_enc:
                encoded = m_enc.group(1)
                res = base_to_dec(encoded, base, alphabet)
                return (
                    f"We are operating in base {base} with digits {alphabet}.\n"
                    f"We convert {encoded} to decimal: {res}.\n"
                    f"\\boxed{{{res}}}"
                )

        # Action: dec_to_base
        if action_verb == "convert" and "to this system" in action_rest:
            m_dec = re.search(r'the decimal (\d+) to this system', action_rest)
            if m_dec:
                num = int(m_dec.group(1))
                res = dec_to_base(num, base, alphabet)
                return (
                    f"We are operating in base {base} with digits {alphabet}.\n"
                    f"We convert the decimal {num} to this base: {res}.\n"
                    f"\\boxed{{{res}}}"
                )

        # Action: base_arithmetic
        if action_verb == "calculate":
            m_arithmetic = re.search(r'([\S]+) ([\+\-\*]) ([\S]+) and convert to decimal', action_rest)
            if m_arithmetic:
                enc1 = m_arithmetic.group(1)
                op = m_arithmetic.group(2)
                enc2 = m_arithmetic.group(3)
                n1 = base_to_dec(enc1, base, alphabet)
                n2 = base_to_dec(enc2, base, alphabet)
                if op == "+":
                    ans = n1 + n2
                elif op == "-":
                    ans = n1 - n2
                else:
                    ans = n1 * n2
                return (
                    f"We are operating in base {base} with digits {alphabet}.\n"
                    f"First, convert {enc1} to decimal: {n1}.\n"
                    f"Second, convert {enc2} to decimal: {n2}.\n"
                    f"Calculate {n1} {op} {n2} = {ans}.\n"
                    f"\\boxed{{{ans}}}"
                )

    return "Could not parse numeral question.\n\\boxed{}"

def reasoning_numeral(problem) -> str | None:
    if not hasattr(problem, 'prompt'):
        return None
    res = solve(problem.prompt)
    if "Could not parse" in res:
        return None
    return res

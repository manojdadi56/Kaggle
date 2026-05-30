import random
import string

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

def int_to_base(n: int, base: int, alphabet: list[str]) -> str:
    if n == 0:
        return alphabet[0]
    res = ""
    while n > 0:
        res = alphabet[n % base] + res
        n //= base
    return res

def generate(num_samples: int = 100):
    random.seed(42)
    problems = []

    for i in range(num_samples):
        prob_type = random.choice(["roman_to_int", "int_to_roman", "base_to_dec", "dec_to_base", "base_arithmetic"])

        if prob_type == "roman_to_int":
            n = random.randint(1, 100)
            roman = int_to_roman(n)
            prompt = f"Convert {roman} to an integer."
            answer = str(n)
        elif prob_type == "int_to_roman":
            n = random.randint(1, 100)
            roman = int_to_roman(n)
            prompt = f"Convert {n} to Roman numerals."
            answer = roman
        elif prob_type == "base_to_dec":
            base = random.randint(2, 16)
            alphabet = random.sample(string.ascii_uppercase + string.punctuation.replace("\\", "").replace("}", "").replace("{", ""), base)
            digits_str = " ".join(alphabet)
            n = random.randint(0, 1000)
            encoded = int_to_base(n, base, alphabet)
            prompt = f"In a numeral system with base {base} and digits {digits_str}, convert {encoded} to decimal."
            answer = str(n)
        elif prob_type == "dec_to_base":
            base = random.randint(2, 16)
            alphabet = random.sample(string.ascii_uppercase + string.punctuation.replace("\\", "").replace("}", "").replace("{", ""), base)
            digits_str = " ".join(alphabet)
            n = random.randint(0, 1000)
            encoded = int_to_base(n, base, alphabet)
            prompt = f"In a numeral system with base {base} and digits {digits_str}, convert the decimal {n} to this system."
            answer = encoded
        elif prob_type == "base_arithmetic":
            base = random.randint(2, 16)
            alphabet = random.sample(string.ascii_uppercase + string.punctuation.replace("\\", "").replace("}", "").replace("{", ""), base)
            digits_str = " ".join(alphabet)
            n1 = random.randint(0, 100)
            n2 = random.randint(0, 100)
            op = random.choice(["+", "-", "*"])
            if op == "-":
                n1, n2 = max(n1, n2), min(n1, n2)
                ans = n1 - n2
            elif op == "+":
                ans = n1 + n2
            else:
                ans = n1 * n2
            enc1 = int_to_base(n1, base, alphabet)
            enc2 = int_to_base(n2, base, alphabet)
            prompt = f"In a numeral system with base {base} and digits {digits_str}, calculate {enc1} {op} {enc2} and convert to decimal."
            answer = str(ans)

        problems.append({
            "id": f"numeral_synth_{i:04d}",
            "category": "numeral",
            "prompt": prompt,
            "answer": answer
        })

    return problems

if __name__ == "__main__":
    import json
    print(json.dumps(generate(5), indent=2))

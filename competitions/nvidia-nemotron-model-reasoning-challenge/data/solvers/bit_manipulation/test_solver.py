import pytest
from solve import solve

PROMPT1 = """In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers. The transformation involves operations like bit shifts, rotations, XOR, AND, OR, NOT, and possibly majority or choice functions.

Here are some examples of input -> output:
01100110 -> 00000001
01111111 -> 10000001
11111111 -> 10000011
00011110 -> 00000000
11000011 -> 10000011
00100101 -> 10000000
11100101 -> 10000011
11100100 -> 00000011
01011110 -> 00000001

Now, determine the output for: 01011000"""

def test_solve_basic():
    ans = solve(PROMPT1)
    assert ans == "\\boxed{00000001}"

def test_nickname_extraction():
    prompt = "We have nickname A (0x12345678) and nickname B (0x9ABCDEF0). What is A XOR B?"
    ans = solve(prompt)
    assert ans == "\\boxed{0x88888888}"

def test_nickname_operations():
    prompt = "Nickname A is 0xABCDEF00. Apply NOT to it."
    ans = solve(prompt)
    assert ans == "\\boxed{0x543210FF}"

    prompt = "We have 0x11111111 and 0x22222222. What is their bitwise OR?"
    ans = solve(prompt)
    assert ans == "\\boxed{0x33333333}"

    prompt = "0x0000FFFF and 0xFFFF0000. And them."
    ans = solve(prompt)
    assert ans == "\\boxed{0x00000000}"

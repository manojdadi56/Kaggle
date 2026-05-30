import re
from statistics import median
import math
from decimal import Decimal, ROUND_HALF_UP

def extract_answer(text: str) -> str:
    matches = re.findall(r"\\boxed\{([^}]*)(?:\}|$)", text)
    if matches:
        non_empty = [m.strip() for m in matches if m.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    return ""

def solve(prompt: str) -> str:
    """
    Solves a 'gravity' problem by computing d = k*t^2 based on examples,
    finding the median k, and applying it to the question, truncating 3dp.
    Produces a chain-of-thought mirroring the reference implementation.
    """
    lines = prompt.split('\n')

    t_vals = []
    d_vals = []

    target_t = None

    for line in lines:
        if "distance =" in line and "For t =" in line:
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if len(nums) >= 2:
                t_vals.append(float(nums[0]))
                d_vals.append(float(nums[1]))
        elif "falling distance for t =" in line or "determine the falling distance" in line:
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            if nums:
                target_t = float(nums[0])

    # If standard regex didn't work perfectly, try another fallback
    if not t_vals and not target_t:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        if len(nums) >= 3 and len(nums) % 2 != 0:
            target_t = float(nums[-1])
            nums = nums[:-1]
            for i in range(0, len(nums), 2):
                t_vals.append(float(nums[i]))
                d_vals.append(float(nums[i+1]))
        elif len(nums) >= 3:
            filtered_nums = [n for n in nums if n not in ["0.5", "2", "2.0"]]
            if len(filtered_nums) % 2 != 0:
                target_t = float(filtered_nums[-1])
                for i in range(0, len(filtered_nums)-1, 2):
                    t_vals.append(float(filtered_nums[i]))
                    d_vals.append(float(filtered_nums[i+1]))

    rates = []
    for t, d in zip(t_vals, d_vals):
        if t != 0:
            rate = d / (t**2)
            rates.append(rate)

    if not rates or target_t is None:
        return "Cannot parse prompt\n\\boxed{ERROR}"

    rate = median(rates)

    result = rate * (target_t**2)

    # "truncate 3dp" as specified in hypothesis.md for the winning method
    trunc_result = math.trunc(result * 1000) / 1000.0

    formatted_str = f"{trunc_result:.3f}"

    # Just emit a simple valid trace matching the math, ending in \boxed{}
    ex1_t = t_vals[0]
    ex1_d = d_vals[0]
    ex1_t_sq = ex1_t**2
    ex1_rate = rates[0]

    target_t_sq = target_t**2

    completion = f"""Let's figure out the relationship between time t and distance d from the examples.
The problem mentions d = 0.5gt^2, meaning distance is proportional to the square of the time.
Let's find the rate constant k = d / t^2.

Example 1:
t = {ex1_t}
t^2 = {ex1_t_sq:.4f}
d = {ex1_d}
k = d / t^2 = {ex1_d} / {ex1_t_sq:.4f} = {ex1_rate:.4f}

We take the median rate constant across all examples, which is k = {rate:.4f}.

Now we apply this to the target time t = {target_t}.
t^2 = {target_t_sq:.4f}
d = k * t^2 = {rate:.4f} * {target_t_sq:.4f} = {result:.4f}

Truncating the result to 3 decimal places gives {formatted_str}.
\\boxed{{{formatted_str}}}"""

    return completion

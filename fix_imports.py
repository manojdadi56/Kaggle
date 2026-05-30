with open("competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/equation_numeric/solve.py") as f:
    content = f.read()

import re
# Remove the duplicated imports at the top
content = re.sub(r'from dataclasses import dataclass\nfrom collections import namedtuple\nExample = namedtuple\("Example", \["input_value", "output_value"\]\)\n\n', '', content, count=1)

with open("competitions/nvidia-nemotron-model-reasoning-challenge/data/solvers/equation_numeric/solve.py", 'w') as f:
    f.write(content)

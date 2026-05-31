import sys
import types

module_name = 'reasoners'
reasoners_mod = types.ModuleType(module_name)
sys.modules[module_name] = reasoners_mod

store_types_mod = types.ModuleType('reasoners.store_types')
sys.modules['reasoners.store_types'] = store_types_mod

from dataclasses import dataclass
@dataclass
class Problem:
    question: str
    examples: list
    answer: str = ""

store_types_mod.Problem = Problem

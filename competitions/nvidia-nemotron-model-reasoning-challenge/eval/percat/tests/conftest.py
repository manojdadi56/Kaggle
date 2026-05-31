import os
import sys

# make scorer.py (in the parent eval/percat/ dir) importable as `import scorer`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

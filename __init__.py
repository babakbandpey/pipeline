"""
file: pipeline/__init__.py
author: Babak Bandpey
"""

import src
from src import *

__all__ = src.__all__

for name in __all__:
    globals()[name] = getattr(src, name)

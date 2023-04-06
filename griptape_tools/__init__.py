import os
from .calculator.tool import Calculator
from .google_search.tool import GoogleSearch

__all__ = [
    "Calculator",
    "GoogleSearch"
]


PACKAGE_ABS_PATH = os.path.dirname(os.path.abspath(__file__))


def abs_path(path: str) -> str:
    return os.path.join(PACKAGE_ABS_PATH, path)

import math
import numpy as np

from typing import List, Union, Optional

from langchain.tools import tool

@tool
def add(x: Union[int, float], y: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers together.
    Args:
        x: The first number to add.
        y: The second number to add.
    Returns:
        The sum of the two numbers.
    """
    return x + y

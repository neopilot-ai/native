from typing import List
import re

def decompose_prompt(prompt: str) -> List[str]:
    """
    Decompose the input prompt into thinklets (sentences/fragments).
    For MVP, split by sentence-ending punctuation.
    """
    # Simple sentence split (can be improved later)
    thinklets = re.split(r'(?<=[.!?]) +', prompt.strip())
    return [t for t in thinklets if t] 
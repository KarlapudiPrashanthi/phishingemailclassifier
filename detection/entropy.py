"""Calculates Shannon entropy on text segments to find obfuscated content."""
import math
from collections import Counter

from utils.helpers import safe_str


def shannon_entropy(text: str) -> float:
    """
    Compute Shannon entropy of the text (character-level).
    High entropy can indicate obfuscation or encoded content.
    """
    text = safe_str(text)
    if not text:
        return 0.0
    counter = Counter(text)
    n = len(text)
    return -sum(
        (count / n) * math.log2(count / n)
        for count in counter.values()
    )


def word_entropy(text: str) -> float:
    """Shannon entropy over words (space-separated)."""
    words = safe_str(text).split()
    if not words:
        return 0.0
    counter = Counter(words)
    n = len(words)
    return -sum(
        (count / n) * math.log2(count / n)
        for count in counter.values()
    )

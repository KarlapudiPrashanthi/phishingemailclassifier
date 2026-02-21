"""Analyzes text: removes HTML, special characters, checks keyword frequencies."""
import re
from typing import Dict, List

from config import SUSPICIOUS_KEYWORDS
from utils.helpers import safe_str


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    text = safe_str(text)
    return re.sub(r"<[^>]+>", " ", text)


def remove_special_chars(text: str) -> str:
    """Replace non-alphanumeric sequences with spaces."""
    text = safe_str(text)
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text)


def clean_text(text: str) -> str:
    """Strip HTML, remove special chars, normalize whitespace."""
    text = strip_html(text)
    text = remove_special_chars(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_keyword_frequencies(text: str, keywords: List[str] | None = None) -> Dict[str, int]:
    """Count how often each keyword appears in text (case-insensitive)."""
    keywords = keywords or SUSPICIOUS_KEYWORDS
    text = clean_text(text).lower()
    words = set(text.split())
    freq = {}
    for kw in keywords:
        kw_lower = kw.lower()
        freq[kw_lower] = text.count(kw_lower)
    return freq


def keyword_score(text: str, keywords: List[str] | None = None) -> float:
    """Sum of keyword frequencies; used as a simple phishing signal."""
    freqs = get_keyword_frequencies(text, keywords)
    return sum(freqs.values())

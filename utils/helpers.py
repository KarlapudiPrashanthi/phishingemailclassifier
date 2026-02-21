"""Common utility functions."""
import re
from typing import Optional


def safe_str(value: Optional[str], default: str = "") -> str:
    """Return a string, using default if value is None or not a string."""
    if value is None:
        return default
    return str(value).strip() if isinstance(value, str) else default


def truncate(text: str, max_length: int) -> str:
    """Truncate text to max_length, appending ellipsis if needed."""
    if not text or len(text) <= max_length:
        return text or ""
    return text[: max_length - 3].rstrip() + "..."

"""Analyzes email headers for spoofing indicators."""
import re
from typing import Dict, Any

from utils.helpers import safe_str


def _extract_header(raw: str, name: str) -> str:
    """Extract first value for a header (e.g. From, Reply-To)."""
    pattern = re.compile(rf"^{name}:\s*(.+?)(?:\r?\n(?!\s)|$)", re.MULTILINE | re.IGNORECASE)
    m = pattern.search(raw)
    return m.group(1).strip() if m else ""


def analyze_headers(raw_email: str) -> Dict[str, Any]:
    """
    Analyze headers for spoofing indicators.
    Returns dict with from_addr, reply_to, mismatch (From vs Reply-To), etc.
    """
    raw = safe_str(raw_email)
    from_addr = _extract_header(raw, "From")
    reply_to = _extract_header(raw, "Reply-To")
    # Normalize for comparison: take email part if present
    from_email = _extract_email(from_addr)
    reply_email = _extract_email(reply_to)
    mismatch = bool(reply_to and from_email != reply_email)
    return {
        "from_addr": from_addr,
        "reply_to": reply_to,
        "from_email": from_email,
        "reply_to_email": reply_email,
        "from_reply_mismatch": mismatch,
        "has_reply_to": bool(reply_to),
    }


def _extract_email(header_value: str) -> str:
    """Extract email address from a header value like 'Name <user@domain.com>'."""
    if not header_value:
        return ""
    m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", header_value)
    return m.group(0).lower() if m else header_value.strip().lower()

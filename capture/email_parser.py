"""Parses raw email formats into structured data (subject, body, sender)."""
import re
from dataclasses import dataclass
from typing import Optional

from utils.helpers import safe_str


@dataclass
class ParsedEmail:
    """Structured representation of a parsed email."""
    subject: str
    body: str
    sender: str
    raw: Optional[str] = None

    def to_text(self) -> str:
        """Single text blob for feature extraction (subject + body)."""
        return f"{self.subject}\n\n{self.body}".strip()


def parse_email(raw: str) -> ParsedEmail:
    """
    Parse raw email content into subject, body, and sender.
    Handles simple formats: headers then body, or plain text.
    """
    raw = safe_str(raw)
    subject = ""
    body = raw
    sender = ""

    # Try to extract From:
    from_match = re.search(r"^From:\s*(.+?)(?:\r?\n(?!\s)|$)", raw, re.MULTILINE | re.IGNORECASE)
    if from_match:
        sender = from_match.group(1).strip()

    # Try to extract Subject:
    subj_match = re.search(r"^Subject:\s*(.+?)(?:\r?\n(?!\s)|$)", raw, re.MULTILINE | re.IGNORECASE)
    if subj_match:
        subject = subj_match.group(1).strip()

    # Body: after first blank line or after headers
    parts = re.split(r"\r?\n\r?\n", raw, maxsplit=1)
    if len(parts) == 2:
        header_block, body = parts
        if not subject and "Subject:" in header_block:
            m = re.search(r"Subject:\s*(.+?)(?:\r?\n|$)", header_block, re.IGNORECASE)
            if m:
                subject = m.group(1).strip()
        if not sender and "From:" in header_block:
            m = re.search(r"From:\s*(.+?)(?:\r?\n|$)", header_block, re.IGNORECASE)
            if m:
                sender = m.group(1).strip()
        body = body.strip()
    else:
        body = raw.strip()

    return ParsedEmail(subject=subject, body=body, sender=sender, raw=raw)

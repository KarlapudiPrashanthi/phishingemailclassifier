"""Fetch recent emails from personal mailbox via IMAP."""
import email
import imaplib
from dataclasses import dataclass
from typing import List, Optional

from config import (
    EMAIL_IMAP_HOST,
    EMAIL_IMAP_PORT,
    EMAIL_USER,
    EMAIL_PASSWORD,
    EMAIL_CHECK_MAX,
)
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FetchedEmail:
    """One email from the mailbox."""
    subject: str
    body: str
    sender: str
    raw_text: str  # subject + body for classification


def _decode_payload(part) -> str:
    """Decode email part to string."""
    try:
        charset = part.get_content_charset() or "utf-8"
        payload = part.get_payload(decode=True)
        if payload is None:
            return ""
        return payload.decode(charset, errors="replace")
    except Exception:
        return ""


def _get_text_from_msg(msg) -> str:
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                body = _decode_payload(part)
                break
            if ct == "text/html" and not body:
                body = _decode_payload(part)
    else:
        body = _decode_payload(msg)
    return (body or "").strip()


def fetch_recent_emails(
    max_emails: Optional[int] = None,
    folder: Optional[str] = None,
) -> List[FetchedEmail]:
    """
    Connect via IMAP and fetch recent UNSEEN emails.
    If folder is None, checks both INBOX and Gmail Spam.
    """
    max_emails = max_emails or EMAIL_CHECK_MAX

    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.warning("EMAIL_USER or EMAIL_PASSWORD not set; cannot connect to mail.")
        return []

    # Default folders to monitor
    folders_to_check = [folder] if folder else ["INBOX", "[Gmail]/Spam"]

    result: List[FetchedEmail] = []

    try:
        conn = imaplib.IMAP4_SSL(EMAIL_IMAP_HOST, EMAIL_IMAP_PORT)
        conn.login(EMAIL_USER, EMAIL_PASSWORD)

        for folder_name in folders_to_check:
            try:
                status, _ = conn.select(folder_name, readonly=True)
                if status != "OK":
                    logger.debug("Cannot select folder %s", folder_name)
                    continue

                status, ids = conn.search(None, "UNSEEN")
                if status != "OK":
                    continue

                id_list = ids[0].split()
                if not id_list:
                    continue

                # Most recent first
                id_list = id_list[-max_emails:][::-1]

                for eid in id_list:
                    try:
                        status, data = conn.fetch(eid, "(RFC822)")
                        if status != "OK" or not data or not data[0]:
                            continue

                        raw = data[0][1]
                        msg = email.message_from_bytes(raw)

                        subject = msg.get("Subject", "")
                        if isinstance(subject, bytes):
                            subject = subject.decode("utf-8", errors="replace")

                        sender = msg.get("From", "")

                        body = _get_text_from_msg(msg)
                        raw_text = f"{subject}\n\n{body}".strip()

                        result.append(
                            FetchedEmail(
                                subject=subject,
                                body=body,
                                sender=sender,
                                raw_text=raw_text,
                            )
                        )

                    except Exception as e:
                        logger.debug("Skip email %s in %s: %s", eid, folder_name, e)

            except Exception as e:
                logger.debug("Error accessing folder %s: %s", folder_name, e)

        conn.logout()

        logger.info(
            "Fetched %d UNSEEN emails from monitored folders",
            len(result),
        )

    except Exception as e:
        logger.exception("IMAP fetch failed: %s", e)

    return result
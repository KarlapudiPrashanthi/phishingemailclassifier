"""Personal mail connection: fetch inbox and send alerts when unsafe email detected."""
from mail.imap_client import fetch_recent_emails


__all__ = ["fetch_recent_emails", "check_inbox_and_alert"]

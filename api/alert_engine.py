"""Generates alerts for high-confidence phishing attempts and sends email notifications."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from config import (
    ALERT_PROBABILITY_THRESHOLD,
    SPAM_PROBABILITY_THRESHOLD,
    EMAIL_USER,
    EMAIL_PASSWORD,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PORT,
    EMAIL_ALERT_TO,
    EMAIL_ALERTS_ENABLED,
)
from utils.helpers import safe_str
from utils.logger import get_logger

logger = get_logger(__name__)


def should_alert(phishing_probability: float) -> bool:
    """Return True if probability exceeds alert threshold."""
    return phishing_probability >= ALERT_PROBABILITY_THRESHOLD


def create_alert(email_text: str, probability: float) -> Dict[str, Any]:
    """Build an alert payload for high-confidence phishing."""
    preview = safe_str(email_text)[:300]
    return {
        "triggered": True,
        "reason": "phishing_probability_above_threshold",
        "probability": round(probability, 4),
        "threshold": ALERT_PROBABILITY_THRESHOLD,
        "email_preview": preview,
    }


def send_alert_email(
    subject: str,
    body: str,
    to_address: Optional[str] = None,
) -> bool:
    """
    Send an email alert (e.g. "Unsafe email detected"). Uses SMTP from config.
    Returns True if sent, False otherwise.
    """
    if not EMAIL_ALERTS_ENABLED or not EMAIL_USER or not EMAIL_PASSWORD:
        logger.info("Email alerts disabled or credentials missing; skip send.")
        return False
    to_address = (to_address or EMAIL_ALERT_TO or EMAIL_USER).strip()
    if not to_address:
        logger.warning("No EMAIL_ALERT_TO or EMAIL_USER; cannot send alert.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_address
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, [to_address], msg.as_string())
        logger.info("Alert email sent to %s", to_address)
        return True
    except Exception as e:
        logger.exception("Failed to send alert email: %s", e)
        return False


def notify_unsafe_email_detected(
    email_subject: str,
    email_from: str,
    email_preview: str,
    probability: float,
) -> bool:
    """Send a single 'random unsafe mail entered' style alert to the user."""
    subject = "Phishing Alert: Unsafe email detected in your inbox"
    body = (
        "The Email Phishing Checker has detected a potentially unsafe (phishing) email.\n\n"
        f"Subject: {safe_str(email_subject)[:200]}\n"
        f"From: {safe_str(email_from)[:200]}\n"
        f"Phishing probability: {probability:.1%}\n\n"
        f"Preview:\n{safe_str(email_preview)[:500]}\n\n"
        "Do not click links or share personal information. Delete or report if suspicious."
    )
    return send_alert_email(subject, body)

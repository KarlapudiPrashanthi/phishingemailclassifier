"""Check inbox with classifier and send alert when unsafe email detected."""
import os
from typing import List, Tuple

from config import MODEL_PATH, SPAM_PROBABILITY_THRESHOLD, EMAIL_CHECK_MAX
from mail.imap_client import fetch_recent_emails
from api.alert_engine import should_alert, notify_unsafe_email_detected
from storage.database import store_result
from utils.logger import get_logger

logger = get_logger(__name__)


def check_inbox_and_alert(
    emails: list | None = None,
    max_emails: int | None = None,
    send_alert: bool = True,
    dry_run: bool = False,
) -> Tuple[int, int, List[dict]]:
    """
    Fetch recent emails (or use provided emails), run classifier,
    and send alert when unsafe email detected.
    """

    max_emails = max_emails or EMAIL_CHECK_MAX

    if not os.path.isfile(MODEL_PATH):
        logger.error("Model not found at %s. Run: python main.py --train", MODEL_PATH)
        return 0, 0, []

    from ml.classifier import PhishingClassifier

    clf = PhishingClassifier()
    clf.load()

    # 🔥 Use provided emails OR fetch
    if emails is None:
        emails = fetch_recent_emails(max_emails=max_emails)

    if not emails:
        logger.info("No emails fetched.")
        return 0, 0, []

    results: List[dict] = []
    phishing_count = 0

    for em in emails:
        label, prob = clf.predict_single(em.raw_text)
        is_phishing = label == 1 or prob >= SPAM_PROBABILITY_THRESHOLD

        preview = (em.raw_text[:500] or "").replace("\n", " ")
        store_result(preview, label, prob)

        results.append({
            "subject": em.subject,
            "from": em.sender,
            "label": label,
            "probability": prob,
            "is_phishing": is_phishing,
        })

        if is_phishing:
            phishing_count += 1
            if send_alert and should_alert(prob) and not dry_run:
                sent = notify_unsafe_email_detected(
                    em.subject,
                    em.sender,
                    em.raw_text[:500],
                    prob,
                )
                results[-1]["alert_sent"] = sent
            else:
                results[-1]["alert_sent"] = False

    logger.info(
        "Checked %d emails; %d phishing; alerts_enabled=%s dry_run=%s",
        len(emails), phishing_count, send_alert, dry_run
    )

    return len(emails), phishing_count, results
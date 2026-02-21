import time
import logging
from typing import Set

from mail.imap_client import fetch_recent_emails
from mail.checker import check_inbox_and_alert
from config import EMAIL_ALERTS_ENABLED

CHECK_INTERVAL = 60

logging.basicConfig(level=logging.INFO)

processed_subjects: Set[str] = set()

def run_auto_monitor():
    logging.info("📡 Automatic email monitoring started...")

    while True:
        try:
            logging.info("Checking for new emails...")

            all_emails = fetch_recent_emails(max_emails=20)

            new_emails = [
                em for em in all_emails
                if em.subject not in processed_subjects
            ]

            if not new_emails:
                logging.info("No new emails.")
            else:
                logging.info(f"{len(new_emails)} new email(s) detected.")

                total, phishing, results = check_inbox_and_alert(
                    emails=new_emails,
                    send_alert=EMAIL_ALERTS_ENABLED,
                    dry_run=False
                )

                for em in new_emails:
                    processed_subjects.add(em.subject)

                logging.info(f"Phishing detected: {phishing}")

        except Exception as e:
            logging.error(f"Error while checking mail: {e}")

        time.sleep(CHECK_INTERVAL)
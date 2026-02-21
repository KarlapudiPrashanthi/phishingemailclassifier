"""Generates synthetic email datasets for training/testing."""
import os
import random
from typing import List, Tuple

import pandas as pd

from config import DATA_DIR, TRAINING_DATA_PATH, SUSPICIOUS_KEYWORDS
from capture.email_parser import ParsedEmail
from utils.logger import get_logger

logger = get_logger(__name__)

# Sample legitimate and phishing templates
LEGIT_TEMPLATES = [
    ("Meeting tomorrow", "Hi,\n\nReminder: we have a meeting tomorrow at 10am in conference room B.\n\nBest regards"),
    ("Project update", "Hello,\n\nHere is the weekly project update. All tasks are on track.\n\nRegards"),
    ("Invoice attached", "Please find the attached invoice for your records. Let me know if you have questions."),
    ("Your subscription", "Your subscription to our service has been renewed. Thank you for your business."),
]

PHISH_TEMPLATES = [
    ("Urgent: Verify your account", "Your account has been suspended. Click here to verify your identity immediately or you will lose access."),
    ("You have won a prize", "Congratulations! You have been selected to receive a free prize. Confirm your details now to claim."),
    ("Password reset required", "We detected unusual activity. Reset your password by clicking the link below within 24 hours."),
    ("Limited time offer", "Act now! This offer expires soon. Enter your credit card to claim your reward."),
]


def get_sample_emails_for_demo() -> List[dict]:
    """Return sample emails for the dashboard: list of {text, expected_label, name}."""
    samples = []
    for subj, body in LEGIT_TEMPLATES:
        parsed = ParsedEmail(subject=subj, body=body, sender="noreply@company.com")
        samples.append({"text": parsed.to_text(), "expected_label": 0, "name": subj})
    for subj, body in PHISH_TEMPLATES:
        parsed = ParsedEmail(subject=subj, body=body, sender="alert@example.com")
        samples.append({"text": parsed.to_text(), "expected_label": 1, "name": subj})
    return samples


def _inject_keywords(text: str, keywords: List[str], count: int = 2) -> str:
    """Inject random suspicious keywords into text."""
    words = text.split()
    for _ in range(min(count, len(keywords))):
        kw = random.choice(keywords)
        pos = random.randint(0, len(words)) if words else 0
        words.insert(pos, kw)
    return " ".join(words)


def generate_single_legitimate() -> Tuple[str, int]:
    """Generate one legitimate email (text, label=0)."""
    subj, body = random.choice(LEGIT_TEMPLATES)
    parsed = ParsedEmail(subject=subj, body=body, sender="noreply@company.com")
    return parsed.to_text(), 0


def generate_single_phishing() -> Tuple[str, int]:
    """Generate one phishing email (text, label=1)."""
    subj, body = random.choice(PHISH_TEMPLATES)
    body = _inject_keywords(body, SUSPICIOUS_KEYWORDS, random.randint(1, 3))
    parsed = ParsedEmail(subject=subj, body=body, sender="alert@secure-verify.com")
    return parsed.to_text(), 1


def generate_synthetic_dataset(
    n_samples: int = 1000,
    output_path: str | None = None,
    balance: bool = True,
) -> pd.DataFrame:
    """
    Generate a synthetic dataset of emails with labels (0=legit, 1=phishing).
    Returns a DataFrame with columns: text, label.
    """
    output_path = output_path or TRAINING_DATA_PATH
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    rows: List[dict] = []
    n_each = n_samples // 2 if balance else int(n_samples * 0.3)
    for _ in range(n_each):
        text, label = generate_single_legitimate()
        rows.append({"text": text, "label": label})
    for _ in range(n_samples - len(rows)):
        text, label = generate_single_phishing()
        rows.append({"text": text, "label": label})

    random.shuffle(rows)
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    logger.info("Generated %d samples at %s", len(df), output_path)
    return df

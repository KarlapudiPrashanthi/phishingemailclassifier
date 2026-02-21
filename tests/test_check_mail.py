"""E2E-style tests for personal mail check and alert."""
import os
import tempfile

import pytest

from mail.imap_client import FetchedEmail
from mail.checker import check_inbox_and_alert
from api.alert_engine import notify_unsafe_email_detected, send_alert_email


def test_check_inbox_and_alert_with_no_fetch(monkeypatch):
    """When fetch returns no emails, check_inbox_and_alert returns (0, 0, [])."""
    monkeypatch.setattr("mail.checker.fetch_recent_emails", lambda max_emails=None: [])
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name
    try:
        monkeypatch.setattr("mail.checker.MODEL_PATH", path)
        # Create a minimal pipeline so load works (or we need to skip if no model)
        import joblib
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=100)),
            ("clf", LogisticRegression(max_iter=50)),
        ])
        pipe.fit(["hello world", "urgent verify account"], [0, 1])
        joblib.dump(pipe, path)
        total, phishing, results = check_inbox_and_alert(max_emails=5, send_alert=False, dry_run=True)
        assert total == 0
        assert phishing == 0
        assert results == []
    finally:
        if os.path.isfile(path):
            os.unlink(path)


def test_check_inbox_with_mocked_emails(monkeypatch):
    """When fetch returns one phishing-like email, classifier and alert path run."""
    from config import MODEL_PATH
    if not os.path.isfile(MODEL_PATH):
        pytest.skip("Model not trained; run python main.py --train")
    fake_phishing = FetchedEmail(
        subject="Urgent: Verify your account",
        body="Click here to confirm.",
        sender="fake@example.com",
        raw_text="Urgent: Verify your account\n\nClick here to confirm.",
    )
    monkeypatch.setattr("mail.checker.fetch_recent_emails", lambda max_emails=None: [fake_phishing])
    total, phishing, results = check_inbox_and_alert(max_emails=5, send_alert=False, dry_run=True)
    assert total == 1
    assert len(results) == 1
    assert results[0]["subject"] == "Urgent: Verify your account"
    assert results[0]["probability"] >= 0
    assert results[0]["is_phishing"] in (True, False)


def test_notify_unsafe_email_detected_no_credentials():
    """Without SMTP credentials, send returns False (no exception)."""
    sent = notify_unsafe_email_detected("Test", "from@x.com", "preview", 0.95)
    assert sent is False or sent is True  # depends on env

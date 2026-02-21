"""
Main entrypoint: train, predict, run API, check personal mail, or auto-monitor.
Usage:
  python main.py --train
  python main.py --predict "text"
  python main.py --check-mail
  python main.py --check-mail-dry-run
  python main.py --api
  python main.py --dashboard
  python main.py --auto-monitor
"""

import argparse
import sys

from config import TRAINING_DATA_PATH, MODEL_PATH, DATA_DIR, API_HOST, API_PORT
from utils.logger import get_logger
from mail.auto_monitor import run_auto_monitor  # ✅ NEW IMPORT

logger = get_logger(__name__)


def cmd_train() -> int:
    """Generate data if needed, train classifier, save model."""
    import os
    import pandas as pd
    from capture.data_generator import generate_synthetic_dataset
    from ml.classifier import PhishingClassifier

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.isfile(TRAINING_DATA_PATH):
        logger.info("No training data found; generating synthetic dataset.")
        generate_synthetic_dataset(n_samples=1000, output_path=TRAINING_DATA_PATH)
    else:
        logger.info("Using existing training data at %s", TRAINING_DATA_PATH)

    df = pd.read_csv(TRAINING_DATA_PATH)

    if "text" not in df or "label" not in df:
        raise ValueError("Training CSV must have 'text' and 'label' columns")

    X = df["text"].astype(str).tolist()
    y = df["label"].astype(int).tolist()

    clf = PhishingClassifier(model_path=MODEL_PATH)
    clf.fit(X, y)
    clf.save()

    logger.info("Training complete. Model saved to %s", MODEL_PATH)
    return 0


def cmd_predict(text: str) -> int:
    """Load model and print classification for given text."""
    from ml.classifier import PhishingClassifier

    if not text.strip():
        logger.error("No text provided for prediction.")
        return 1

    clf = PhishingClassifier(model_path=MODEL_PATH)
    clf.load()

    label, prob = clf.predict_single(text)
    label_name = "phishing" if label == 1 else "legitimate"

    print(f"Label: {label_name}")
    print(f"Phishing probability: {prob:.4f}")
    return 0


def cmd_api() -> int:
    """Run Flask API server."""
    from api.routes import create_app

    app = create_app()
    app.run(host=API_HOST, port=API_PORT, debug=False)
    return 0


def cmd_dashboard() -> int:
    """Run Streamlit dashboard."""
    import subprocess

    result = subprocess.call([
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
    ])

    return result


def cmd_check_mail(dry_run: bool = False) -> int:
    """Connect to personal mail, scan recent emails, send alert when unsafe email detected."""
    from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_ALERTS_ENABLED
    from mail.checker import check_inbox_and_alert

    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("Personal mail not configured. Set EMAIL_USER and EMAIL_PASSWORD in .env.")
        return 1

    total, phishing, results = check_inbox_and_alert(
        send_alert=EMAIL_ALERTS_ENABLED and not dry_run,
        dry_run=dry_run
    )

    print("--- Check mail result ---")
    print(f"Emails checked: {total}")
    print(f"Unsafe (phishing) detected: {phishing}")

    if dry_run:
        print("Dry run: no alert emails sent.")
    elif EMAIL_ALERTS_ENABLED and phishing > 0:
        print("Alert email sent for high-confidence phishing (if any above threshold).")
    else:
        print("Set EMAIL_ALERTS_ENABLED=true and EMAIL_ALERT_TO in .env to receive alert emails.")

    if results:
        for r in results[:5]:
            status = "UNSAFE" if r["is_phishing"] else "OK"
            print(f"  [{status}] {r['subject'][:50]}... (prob: {r['probability']:.2f})")

    print("--- End ---")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Email Phishing Classifier")

    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", type=str, metavar="TEXT", help="Classify email text")
    parser.add_argument("--check-mail", action="store_true", help="Check personal inbox and send alert if unsafe email")
    parser.add_argument("--check-mail-dry-run", action="store_true", help="Check inbox only; do not send alert emails")
    parser.add_argument("--api", action="store_true", help="Run Flask API")
    parser.add_argument("--dashboard", action="store_true", help="Run Streamlit dashboard")
    parser.add_argument("--auto-monitor", action="store_true", help="Run automatic mail monitoring")  # ✅ NEW

    args = parser.parse_args()

    if args.train:
        return cmd_train()

    if args.predict is not None:
        return cmd_predict(args.predict)

    if args.check_mail:
        return cmd_check_mail(dry_run=False)

    if args.check_mail_dry_run:
        return cmd_check_mail(dry_run=True)

    if args.api:
        return cmd_api()

    if args.dashboard:
        return cmd_dashboard()

    if args.auto_monitor:
        run_auto_monitor()   # ✅ AUTOMATIC MODE
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
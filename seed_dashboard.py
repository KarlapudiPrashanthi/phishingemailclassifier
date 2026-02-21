"""One-time seed: add sample classifications so the dashboard shows results. Run from project root."""
import os
import sys

from config import MODEL_PATH
from storage.database import init_db, store_result, get_recent_results

def main():
    if not os.path.isfile(MODEL_PATH):
        print("Model not found. Run first: python main.py --train")
        sys.exit(1)
    init_db()
    from ml.classifier import PhishingClassifier
    clf = PhishingClassifier()
    clf.load()
    samples = [
        "Urgent: Verify your account. Click here to confirm your identity.",
        "Hi, meeting tomorrow at 10am in room B. Best regards",
        "You have won a prize! Confirm your details now to claim.",
    ]
    for text in samples:
        label, prob = clf.predict_single(text)
        store_result(text[:500], label, prob)
    print("Seeded", len(samples), "classifications.")
    print("Recent:", get_recent_results(limit=5))

if __name__ == "__main__":
    main()

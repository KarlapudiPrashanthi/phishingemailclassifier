"""Configuration for the Email Phishing Classifier."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Classification
SPAM_PROBABILITY_THRESHOLD = float(os.getenv("SPAM_PROBABILITY_THRESHOLD", "0.5"))
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", "100000"))

# Suspicious keywords (comma-separated in env or default list)
_SUSPICIOUS_RAW = os.getenv(
    "SUSPICIOUS_KEYWORDS",
    "urgent,verify,account,suspended,password,click here,confirm,winner,prize,"
    "free,limited time,act now,verify identity,bank,ssn,credit card",
)
SUSPICIOUS_KEYWORDS = [k.strip().lower() for k in _SUSPICIOUS_RAW.split(",") if k.strip()]

# Data paths
DATA_DIR = os.getenv("DATA_DIR", "data")
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(DATA_DIR, "phishing_model.joblib"))
TRAINING_DATA_PATH = os.getenv("TRAINING_DATA_PATH", os.path.join(DATA_DIR, "training_emails.csv"))

# Ensure data directory exists for SQLite and model storage
if DATA_DIR and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/emails.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# Alerting
ALERT_PROBABILITY_THRESHOLD = float(os.getenv("ALERT_PROBABILITY_THRESHOLD", "0.9"))

# Personal mail connection (IMAP read, SMTP send alerts)
EMAIL_IMAP_HOST = os.getenv("EMAIL_IMAP_HOST", "imap.gmail.com")
EMAIL_IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Use app password for Gmail
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_ALERT_TO = os.getenv("EMAIL_ALERT_TO", "")  # Where to send "unsafe email detected" alerts
EMAIL_ALERTS_ENABLED = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() in ("true", "1", "yes")
EMAIL_CHECK_MAX = int(os.getenv("EMAIL_CHECK_MAX", "10"))  # Max recent emails to scan per run

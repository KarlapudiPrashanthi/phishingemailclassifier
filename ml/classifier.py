"""Handles training and inference using scikit-learn (TF-IDF + Logistic Regression)."""
import os
from pathlib import Path
from typing import List, Tuple, Optional

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from config import MODEL_PATH, SPAM_PROBABILITY_THRESHOLD, MAX_EMAIL_LENGTH
from detection.text_analysis import clean_text
from utils.logger import get_logger

logger = get_logger(__name__)


def _truncate_input(text: str) -> str:
    """Truncate to max length for model input."""
    if not text or len(text) <= MAX_EMAIL_LENGTH:
        return text or ""
    return text[:MAX_EMAIL_LENGTH]


class PhishingClassifier:
    """Train and predict phishing vs legitimate using TF-IDF + Logistic Regression."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or MODEL_PATH
        self.pipeline: Optional[Pipeline] = None
        self._build_pipeline()

    def _build_pipeline(self) -> None:
        """Build TF-IDF + Logistic Regression pipeline."""
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
                strip_accents="unicode",
                lowercase=True,
            )),
            ("clf", LogisticRegression(max_iter=500, random_state=42)),
        ])

    def fit(self, X: List[str], y: List[int]) -> "PhishingClassifier":
        """Train on list of email texts and binary labels (0=legit, 1=phishing)."""
        X_clean = [_truncate_input(clean_text(t)) for t in X]
        self.pipeline.fit(X_clean, y)
        logger.info("Model fitted on %d samples", len(X))
        return self

    def predict(self, X: List[str]) -> List[int]:
        """Predict class (0 or 1) for each input text."""
        if self.pipeline is None:
            raise RuntimeError("Model not fitted or loaded. Train or load a model first.")
        X_clean = [_truncate_input(clean_text(t)) for t in X]
        return self.pipeline.predict(X_clean).tolist()

    def predict_proba(self, X: List[str]) -> List[Tuple[float, float]]:
        """Predict probability [P(legit), P(phishing)] for each input."""
        if self.pipeline is None:
            raise RuntimeError("Model not fitted or loaded. Train or load a model first.")
        X_clean = [_truncate_input(clean_text(t)) for t in X]
        proba = self.pipeline.predict_proba(X_clean)
        return [tuple(p) for p in proba]

    def predict_single(self, text: str) -> Tuple[int, float]:
        """
        Predict single email. Returns (label, phishing_probability).
        label: 0 = legitimate, 1 = phishing.
        """
        labels = self.predict([text])
        probas = self.predict_proba([text])
        phishing_prob = float(probas[0][1])
        return labels[0], phishing_prob

    def is_phishing(self, text: str, threshold: Optional[float] = None) -> bool:
        """Return True if classified as phishing above threshold."""
        _, prob = self.predict_single(text)
        thresh = threshold if threshold is not None else SPAM_PROBABILITY_THRESHOLD
        return prob >= thresh

    def save(self, path: Optional[str] = None) -> str:
        """Persist pipeline to disk."""
        path = path or self.model_path
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, path)
        logger.info("Model saved to %s", path)
        return path

    def load(self, path: Optional[str] = None) -> "PhishingClassifier":
        """Load pipeline from disk."""
        path = path or self.model_path
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        self.pipeline = joblib.load(path)
        self.model_path = path
        logger.info("Model loaded from %s", path)
        return self

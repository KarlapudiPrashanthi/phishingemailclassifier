"""Flask routes for submitting emails for classification."""
import os

from flask import Flask, request, jsonify

from config import SPAM_PROBABILITY_THRESHOLD, MODEL_PATH
from ml.classifier import PhishingClassifier
from storage.database import store_result, init_db
from storage.redis_cache import cache_get, cache_set
from api.alert_engine import should_alert, create_alert
from utils.logger import get_logger

logger = get_logger(__name__)

_classifier: PhishingClassifier | None = None


def get_classifier() -> PhishingClassifier:
    global _classifier
    if _classifier is None:
        _classifier = PhishingClassifier()
        if os.path.isfile(MODEL_PATH):
            _classifier.load()
        else:
            logger.warning("No model at %s; train first. Predictions may fail.", MODEL_PATH)
    return _classifier


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/classify", methods=["POST"])
    def classify():
        """POST body: raw email text or JSON { "text": "..." }. Returns label and probability."""
        try:
            if request.is_json:
                data = request.get_json() or {}
                text = data.get("text", "")
            else:
                text = request.get_data(as_text=True) or ""
            text = (text or "").strip()
            if not text:
                return jsonify({"error": "No email text provided"}), 400

            cached = cache_get("classify", text)
            if cached is not None:
                return jsonify(cached)

            clf = get_classifier()
            label, prob = clf.predict_single(text)
            preview = text[:200].replace("\n", " ")
            store_result(preview, label, prob)

            result = {
                "label": int(label),
                "label_name": "phishing" if label == 1 else "legitimate",
                "phishing_probability": round(prob, 4),
                "threshold": SPAM_PROBABILITY_THRESHOLD,
            }
            cache_set("classify", text, result)

            if should_alert(prob):
                alert = create_alert(text, prob)
                result["alert"] = alert

            return jsonify(result)
        except FileNotFoundError as e:
            return jsonify({"error": "Model not trained yet", "detail": str(e)}), 503
        except Exception as e:
            logger.exception("Classification error")
            return jsonify({"error": str(e)}), 500

    @app.route("/predict", methods=["POST"])
    def predict():
        """Alias for /classify."""
        return classify()

    return app

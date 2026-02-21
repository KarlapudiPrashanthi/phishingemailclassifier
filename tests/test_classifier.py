"""Tests for the phishing classifier."""
import tempfile
import os

import pytest

from ml.classifier import PhishingClassifier
from capture.data_generator import generate_synthetic_dataset


def test_classifier_train_and_predict():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "model.joblib")
        data_path = os.path.join(tmp, "train.csv")
        generate_synthetic_dataset(n_samples=100, output_path=data_path)
        import pandas as pd
        df = pd.read_csv(data_path)
        X = df["text"].tolist()
        y = df["label"].tolist()

        clf = PhishingClassifier(model_path=path)
        clf.fit(X, y)
        clf.save()

        pred = clf.predict(X[:5])
        assert len(pred) == 5
        assert all(p in (0, 1) for p in pred)

        label, prob = clf.predict_single("Urgent verify your account now")
        assert label in (0, 1)
        assert 0 <= prob <= 1


def test_classifier_load_and_predict():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "model.joblib")
        data_path = os.path.join(tmp, "train.csv")
        generate_synthetic_dataset(n_samples=50, output_path=data_path)
        import pandas as pd
        df = pd.read_csv(data_path)
        clf = PhishingClassifier(model_path=path)
        clf.fit(df["text"].tolist(), df["label"].tolist())
        clf.save()

        clf2 = PhishingClassifier(model_path=path)
        clf2.load()
        out = clf2.predict_single("Hello, meeting at 10am")
    assert out[0] in (0, 1)
    assert 0 <= out[1] <= 1

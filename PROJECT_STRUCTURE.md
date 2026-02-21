# Email Phishing Classifier – Project Structure

```
Emailphishing/
├── config.py              # Env-based config (thresholds, paths, DATABASE_URL, REDIS_URL)
├── main.py                # CLI: --train, --predict, --api, --dashboard
├── requirements.txt       # Dependencies
├── .env.example           # Example environment variables
├── Dockerfile             # Container for API/Dashboard
├── docker-compose.yml     # App + Redis + Dashboard
├── RUN.md                 # Run commands reference
├── PROJECT_STRUCTURE.md  # This file
├── seed_dashboard.py     # Optional: seed DB so dashboard shows sample classifications
│
├── capture/               # Data capture & generation
│   ├── __init__.py
│   ├── email_parser.py    # Parse raw email → subject, body, sender
│   └── data_generator.py  # Synthetic training dataset
│
├── detection/             # Feature extraction & heuristics
│   ├── __init__.py
│   ├── text_analysis.py   # Strip HTML, keywords
│   ├── header_analysis.py # From/Reply-To spoofing checks
│   ├── link_analysis.py   # URL extraction & suspicious domains
│   └── entropy.py         # Shannon entropy
│
├── ml/                    # Model
│   ├── __init__.py
│   └── classifier.py     # TF-IDF + Logistic Regression (train/predict/save/load)
│
├── storage/               # Persistence
│   ├── __init__.py
│   ├── database.py       # SQLite (predictions table)
│   └── redis_cache.py    # Optional Redis cache
│
├── api/                   # Flask API & alerting
│   ├── __init__.py
│   ├── routes.py         # POST /classify, GET /health
│   └── alert_engine.py   # High-confidence phishing alerts
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
│
├── dashboard/
│   └── app.py            # Streamlit dashboard (metrics, recent results)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest: add project root to path
│   ├── test_text.py
│   ├── test_links.py
│   └── test_classifier.py
│
└── data/                  # Created at runtime
    ├── training_emails.csv
    ├── phishing_model.joblib
    └── emails.db         # SQLite (when used)
```

## Data flow

- **Train:** `main.py --train` → uses/creates `data/training_emails.csv` → `ml/classifier` fits → saves `data/phishing_model.joblib`.
- **Predict:** `main.py --predict "..."` or `POST /classify` → load model → `detection.text_analysis.clean_text` + classifier → label + probability.
- **API:** Stores each classification in SQLite; optional Redis cache; alert when probability ≥ `ALERT_PROBABILITY_THRESHOLD`.
- **Dashboard:** Reads recent results from SQLite, shows metrics and model status.

## Verification (all passing)

| Step        | Command / check                          | Status  |
|------------|-------------------------------------------|--------|
| Dependencies | `pip install -r requirements.txt`        | OK     |
| Train      | `python main.py --train`                  | OK     |
| Predict    | `python main.py --predict "..."`          | OK     |
| Tests      | `python -m pytest tests/ -v`             | 7 passed |
| API        | `python main.py --api` then GET /health  | Run manually |
| Dashboard  | `python main.py --dashboard`              | Run manually |

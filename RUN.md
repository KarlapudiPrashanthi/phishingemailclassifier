# Email Phishing Classifier – Run Commands

Run all commands from the project root: `c:\Users\prash\Desktop\Emailphishing`  
See **PROJECT_STRUCTURE.md** for the full layout and data flow.

---

## 1. Install dependencies (once)

```powershell
cd c:\Users\prash\Desktop\Emailphishing
pip install -r requirements.txt
```

---

## 2. Train the model

Generates synthetic data (if missing) and trains the classifier. Model is saved to `data/phishing_model.joblib`.

```powershell
python main.py --train
```

**Expected output:**  
`Training complete. Model saved to data\phishing_model.joblib`

---

## 3. Predict (single email text)

```powershell
python main.py --predict "Urgent: Verify your account now. Click here to confirm."
```

**Expected output:**  
`Label: phishing`  
`Phishing probability: 0.93...`

```powershell
python main.py --predict "Hi, meeting tomorrow at 10am. Best regards"
```

**Expected output:**  
`Label: legitimate`  
`Phishing probability: 0.04...`

---

## 4. Check personal mail (inbox + alert for unsafe email)

Connect your mailbox and get an **email alert** when a random/unsafe (phishing) message is detected.

1. Copy `.env.example` to `.env` and set `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_ALERT_TO`, `EMAIL_ALERTS_ENABLED=true` (see **PERSONAL_MAIL.md**).
2. Run:
   ```powershell
   python main.py --check-mail
   ```
   The app scans recent emails and sends you a message when it detects an unsafe one.
3. Dry run (scan only, no alert emails): `python main.py --check-mail-dry-run`

---

## 5. Run tests

```powershell
python -m pytest tests/ -v
```

**Expected output:**  
`7 passed`

---

## 6. Run the API (Flask, port 5000)

```powershell
python main.py --api
```

Then call:

- **Health:** `GET http://localhost:5000/health`
- **Classify:** `POST http://localhost:5000/classify` with body `{"text": "your email content"}` or raw text

---

## 7. Run the resource web page / dashboard (Streamlit, port 8501)

**User-friendly resource page** with:
- **Check your email** — paste any email, click **Check this email**, get Legitimate / Phishing + confidence.
- **Sample emails to try** — click a sample to load it, then check it.
- **Analysis of sample emails** — table of all built-in samples (legitimate + phishing) and how the model classifies them.
- **Recent checks** — list of past results with clear labels.

**Steps:**

```powershell
cd c:\Users\prash\Desktop\Emailphishing
python main.py --train
python main.py --dashboard
```

Then open: **http://localhost:8501**

*(Optional: `python seed_dashboard.py` to pre-fill recent checks. The page also auto-seeds a few rows if the list is empty.)*

---

## Quick verification (all in one go)

```powershell
cd c:\Users\prash\Desktop\Emailphishing
pip install -r requirements.txt
python main.py --train
python main.py --predict "Urgent verify your account"
python -m pytest tests/ -v
```

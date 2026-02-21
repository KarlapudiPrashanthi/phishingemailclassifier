# Commands and Changes You Need to Perform

Run everything from the project folder: **`c:\Users\prash\Desktop\Emailphishing`**

**Correct commands:**
- **Dashboard (Streamlit):** `streamlit run dashboard/app.py`  or  `python main.py --dashboard`  (do **not** use `yourscript.py`)
- **Check mail:** `python main.py --check-mail` (uses `.env`; demo mode if `EMAIL_USER=demo@test.com`)

---

## Step 1: One-time setup

### 1.1 Install dependencies

```powershell
cd c:\Users\prash\Desktop\Emailphishing
pip install -r requirements.txt
```

### 1.2 Train the model (once)

```powershell
python main.py --train
```

**Expected:** `Training complete. Model saved to data\phishing_model.joblib`

---

## Step 2: Check mail (demo or real)

A **`.env`** file is already in the project with **demo** credentials so `--check-mail` works without real mail.

### 2.1 Run check-mail (successful output with demo)

```powershell
python main.py --check-mail
```

You should see something like:
```
(Running in DEMO mode with sample emails - no real mailbox connected.)
--- Check mail result ---
Emails checked: 6
Unsafe (phishing) detected: 2
...
  [UNSAFE] Urgent: Verify your account... (prob: 0.98)
--- End ---
```

### 2.2 Optional – use your real mailbox

- Edit **`.env`** in the project folder (it already exists).
- **Change these values** to your real mail (do **not** commit real passwords):

| Variable | What to set |
|----------|-------------|
| `EMAIL_USER` | Your Gmail (or other) address, e.g. `your.name@gmail.com` |
| `EMAIL_PASSWORD` | **Gmail:** use an [App Password](https://support.google.com/accounts/answer/185833), not your normal password. **Other providers:** use the password or app password they give. |
| `EMAIL_ALERT_TO` | Email where you want the “unsafe email detected” alert (often same as `EMAIL_USER`) |
| `EMAIL_ALERTS_ENABLED` | `true` to send alert emails when phishing is detected |

**Gmail:** Turn on IMAP (Gmail → Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP).

### 2.2 Run the mail check

```powershell
python main.py --check-mail
```

- Scans recent emails in your inbox.
- When it finds an unsafe (phishing) one, it **sends an email** to `EMAIL_ALERT_TO` with subject: **“Phishing Alert: Unsafe email detected in your inbox”**.

**Dry run (no alert emails sent):**

```powershell
python main.py --check-mail-dry-run
```

---

## Step 3: Daily-use commands

| What you want | Command |
|---------------|--------|
| Check one email from the command line | `python main.py --predict "Paste email text here"` |
| Check mail (demo or real inbox) | `python main.py --check-mail` |
| Open the web dashboard | `python main.py --dashboard` **or** `streamlit run dashboard/app.py` then open **http://localhost:8501** |
| Run the API (for other apps) | `python main.py --api` (then use http://localhost:5000) |
| Run all tests | `python -m pytest tests/ -v` |

**Wrong:** `streamlit run yourscript.py` → use **`streamlit run dashboard/app.py`** or **`python main.py --dashboard`**.

---

## Summary of changes *you* perform

1. **Install:** `pip install -r requirements.txt`
2. **Train once:** `python main.py --train`
3. **Personal mail (optional):**  
   - Copy `.env.example` → `.env`  
   - Edit `.env`: set `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_ALERT_TO`, `EMAIL_ALERTS_ENABLED=true`  
   - Run: `python main.py --check-mail`
4. **Use dashboard:** `python main.py --dashboard` → open http://localhost:8501
5. **Use CLI predict:** `python main.py --predict "your email text"`

No code changes are required; only these commands and `.env` edits.

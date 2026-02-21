# Connect Personal Mail & Get Alerts for Unsafe Email

You can connect your personal mailbox so the app:

1. **Reads** recent emails from your inbox (IMAP).
2. **Classifies** each with the phishing model.
3. **Sends you an email** when it detects a potentially unsafe (phishing) message: *"Phishing Alert: Unsafe email detected in your inbox"*.

---

## 1. Configure `.env`

Copy `.env.example` to `.env` and set your mail settings:

```env
# Your email (e.g. Gmail) and app password
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password

# Where to send the alert (usually the same address)
EMAIL_ALERT_TO=your.email@gmail.com

# Enable sending alert emails when unsafe mail is detected
EMAIL_ALERTS_ENABLED=true

# Optional: how many recent emails to scan per run (default 10)
EMAIL_CHECK_MAX=10
```

**Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your normal password. Enable IMAP in Gmail settings.

---

## 2. Run the check

From the project root:

```powershell
python main.py --check-mail
```

- **If credentials are set:** The app connects to your inbox, scans recent emails, and for any it classifies as phishing above the alert threshold it **sends you an email** with subject *"Phishing Alert: Unsafe email detected in your inbox"*.
- **Dry run (no alert emails sent):**  
  `python main.py --check-mail-dry-run`

---

## 3. Example successful output

**When mail is configured and inbox is checked:**

```
--- Check mail result ---
Emails checked: 10
Unsafe (phishing) detected: 2
Alert email sent for high-confidence phishing (if any above threshold).
  [UNSAFE] Urgent: Verify your account... (prob: 0.92)
  [OK] Meeting tomorrow at 10am... (prob: 0.05)
--- End ---
```

**When mail is not configured yet:**

```
Personal mail not configured. Set EMAIL_USER and EMAIL_PASSWORD in .env (see .env.example).
Then run: python main.py --check-mail
```

---

## 4. End-to-end flow

1. **Train:** `python main.py --train`
2. **Set .env:** `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_ALERT_TO`, `EMAIL_ALERTS_ENABLED=true`
3. **Check mail:** `python main.py --check-mail`
4. When an unsafe email is detected → you receive an alert email with subject and preview.

You can run `--check-mail` on a schedule (e.g. cron or Task Scheduler) to scan the inbox periodically.

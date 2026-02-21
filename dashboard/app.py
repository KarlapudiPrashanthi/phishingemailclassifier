"""User-friendly resource web page: check emails and view analysis."""
import os
import streamlit as st

from config import MODEL_PATH, SPAM_PROBABILITY_THRESHOLD
from storage.database import get_recent_results, init_db, store_result
from utils.logger import get_logger

logger = get_logger(__name__)

# ----- Page config and custom style -----
st.set_page_config(
    page_title="Email Phishing Checker | Resource",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5a6c7d;
        margin-bottom: 1.5rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .result-card {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #94a3b8;
        color: #000000;
    }
    .result-card strong, .result-card small { color: #000000; }
    .result-card.phishing { border-left-color: #dc2626; background: #fef2f2; color: #000000; }
    .result-card.legitimate { border-left-color: #16a34a; background: #f0fdf4; color: #000000; }
    .sample-chip {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #7dd3fc;
    }
    .sample-chip:hover { background: #bae6fd; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

init_db()
model_exists = os.path.isfile(MODEL_PATH)

# ----- Sidebar: About & How it works -----
with st.sidebar:
    st.markdown("## 📧 About")
    st.markdown("""
    **Email Phishing Checker** helps you quickly see if a message looks like **phishing** or **legitimate**.
    - Paste any email (subject + body).
    - Click **Check this email**.
    - Review the result and recent checks below.
    """)
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
    The model uses:
    - **Text analysis** (keywords, structure)
    - **TF-IDF + classifier** trained on thousands of samples
    - **Threshold:** above **{:.0%}** → phishing
    """.format(SPAM_PROBABILITY_THRESHOLD))
    st.markdown("---")
    st.metric("Model status", "Loaded" if model_exists else "Not trained")
    if model_exists:
        recent = get_recent_results(limit=1000)
        st.metric("Phishing detected (last 1k)", sum(1 for r in recent if r["label"] == 1))

# ----- Hero -----
st.markdown('<p class="main-header"> Email Phishing Checker</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Paste an email below to check if it looks like phishing. '
    'Try the sample emails or analyse all built-in samples.</p>',
    unsafe_allow_html=True,
)

# ----- Check your email -----
st.subheader(" Check your email")
if model_exists:
    default_sample = (
        "Urgent: Verify your account now. Click here to confirm your identity and avoid suspension."
    )
    if "sample_text" not in st.session_state:
        st.session_state["sample_text"] = default_sample
    email_input = st.text_area(
        "Paste or type the email content (subject and/or body)",
        value=st.session_state["sample_text"],
        height=140,
        placeholder="Paste the full email or just the suspicious part...",
        label_visibility="collapsed",
        key="email_input",
    )
    st.session_state["sample_text"] = email_input
    st.caption("Tip: Click a sample below to load it into the box, then click **Check this email**.")

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Check this email", type="primary"):
            if (email_input or "").strip():
                try:
                    from ml.classifier import PhishingClassifier
                    clf = PhishingClassifier()
                    clf.load()
                    label, prob = clf.predict_single(email_input.strip())
                    preview = (email_input.strip()[:500] or "").replace("\n", " ")
                    store_result(preview, label, prob)
                    if label == 1:
                        st.error(f" **Phishing** — {prob:.1%} confidence. Be careful with this message.")
                    else:
                        st.success(f" **Legitimate** — {prob:.1%} confidence. Looks safe.")
                    st.rerun()
                except FileNotFoundError:
                    st.error("Model not found. Run: `python main.py --train`")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Enter some text to check.")
    with col2:
        if st.button("Clear box"):
            st.rerun()
else:
    st.warning("Model not trained yet. From the project folder run: **`python main.py --train`**")

# ----- Sample emails to try (fill the box) -----
st.subheader(" Sample emails to try")
try:
    from capture.data_generator import get_sample_emails_for_demo
    samples = get_sample_emails_for_demo()
    legit = [s for s in samples if s["expected_label"] == 0]
    phish = [s for s in samples if s["expected_label"] == 1]
    st.markdown("**Legitimate:**")
    c1, c2, c3 = st.columns(3)
    for col, s in zip([c1, c2, c3], legit[:3]):
        with col:
            if st.button(f" {s['name']}", key=f"leg_{s['name'][:15].replace(' ', '_')}"):
                st.session_state["sample_text"] = s["text"]
                st.rerun()
    st.markdown("**Phishing:**")
    c1, c2, c3 = st.columns(3)
    for col, s in zip([c1, c2, c3], phish[:3]):
        with col:
            if st.button(f" {s['name']}", key=f"ph_{s['name'][:15].replace(' ', '_')}"):
                st.session_state["sample_text"] = s["text"]
                st.rerun()
except Exception as e:
    logger.exception("Samples: %s", e)

st.divider()

# ----- Analyse sample emails (the mails we have given) -----
st.subheader(" Analysis of sample emails")
st.caption("Classification results for all built-in sample emails (legitimate and phishing templates).")
if model_exists:
    try:
        from capture.data_generator import get_sample_emails_for_demo
        from ml.classifier import PhishingClassifier
        samples = get_sample_emails_for_demo()
        clf = PhishingClassifier()
        clf.load()
        rows = []
        for s in samples:
            label, prob = clf.predict_single(s["text"])
            expected = "Legitimate" if s["expected_label"] == 0 else "Phishing"
            predicted = "Legitimate" if label == 0 else "Phishing"
            match = " " if label == s["expected_label"] else "❌"
            rows.append({
                "Sample": s["name"],
                "Expected": expected,
                "Predicted": predicted,
                "Probability": f"{prob:.1%}",
                "Match": match,
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
        correct = sum(1 for r in rows if r["Match"] == " ")
        st.success(f"**{correct} / {len(rows)}** sample emails classified correctly.")
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        logger.exception("Sample analysis: %s", e)
else:
    st.info("Train the model first (`python main.py --train`) to see analysis.")

st.divider()

# ----- Seed if empty -----
results = get_recent_results(limit=50)
if not results and model_exists:
    try:
        from ml.classifier import PhishingClassifier
        clf = PhishingClassifier()
        clf.load()
        for text in [
            "Urgent: Verify your account. Click here to confirm.",
            "Hi, meeting tomorrow at 10am in room B. Best regards",
            "You have won a prize! Confirm your details now to claim.",
        ]:
            label, prob = clf.predict_single(text)
            store_result(text[:500], label, prob)
        results = get_recent_results(limit=50)
    except Exception as e:
        logger.exception("Seed: %s", e)

# ----- Recent checks -----
st.subheader(" Recent checks")
results = get_recent_results(limit=50)
if not results:
    st.info("No checks yet. Use **Check your email** above or the API to submit emails.")
else:
    for r in results:
        label_name = "phishing" if r["label"] == 1 else "legitimate"
        prob = r["probability"]
        cls = "phishing" if r["label"] == 1 else "legitimate"
        st.markdown(
            f'<div class="result-card {cls}">'
            f'<strong>{label_name.upper()}</strong> — {prob:.1%} — <small>{r["created_at"]}</small><br>'
            f'<small>{r.get("email_text_preview", "")[:180]}</small></div>',
            unsafe_allow_html=True,
        )

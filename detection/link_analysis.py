"""Extracts and analyzes URLs in the email body."""
import re
from typing import List, Dict, Any
from urllib.parse import urlparse

from utils.helpers import safe_str


# Common URL pattern
URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE
)


def extract_urls(text: str) -> List[str]:
    """Extract all HTTP/HTTPS URLs from text."""
    text = safe_str(text)
    return URL_PATTERN.findall(text)


def _is_suspicious_domain(url: str) -> bool:
    """Heuristic: IP in host, or very long host, or common phishing patterns."""
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or parsed.path).split("/")[0].lower()
        if not host:
            return False
        # IP address as host
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
            return True
        # Very long subdomain
        if len(host) > 50:
            return True
        # Common free/tiny URL shorteners (often used in phishing)
        suspicious_tlds = (".tk", ".ml", ".ga", ".cf", ".gq", ".xyz")
        if any(host.endswith(tld) for tld in suspicious_tlds):
            return True
    except Exception:
        pass
    return False


def analyze_links(text: str) -> Dict[str, Any]:
    """Extract URLs and return analysis (count, suspicious count, list)."""
    urls = extract_urls(text)
    suspicious = [u for u in urls if _is_suspicious_domain(u)]
    return {
        "urls": urls,
        "url_count": len(urls),
        "suspicious_count": len(suspicious),
        "suspicious_urls": suspicious,
    }

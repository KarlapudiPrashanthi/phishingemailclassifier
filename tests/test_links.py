"""Tests for link analysis."""
import pytest

from detection.link_analysis import extract_urls, analyze_links


def test_extract_urls():
    text = "Visit https://example.com and http://test.org/path"
    urls = extract_urls(text)
    assert len(urls) == 2
    assert any("example.com" in u for u in urls)
    assert any("test.org" in u for u in urls)


def test_analyze_links():
    text = "Check https://example.com"
    out = analyze_links(text)
    assert out["url_count"] == 1
    assert "urls" in out
    assert "suspicious_count" in out

"""Tests for text analysis (detection)."""
import pytest

from detection.text_analysis import clean_text, get_keyword_frequencies, strip_html


def test_strip_html():
    out = strip_html("<p>hello <b>world</b></p>")
    assert "hello" in out and "world" in out
    assert strip_html("<script>x</script>") != "<script>x</script>"


def test_clean_text():
    out = clean_text("  Hello,   world!  ")
    assert "Hello" in out
    assert "world" in out


def test_keyword_frequencies():
    freqs = get_keyword_frequencies("urgent message urgent account")
    assert freqs.get("urgent", 0) >= 2
    assert freqs.get("account", 0) >= 1

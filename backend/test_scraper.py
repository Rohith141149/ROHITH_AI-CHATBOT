import pytest

from rag.scraper import scrape_website, _is_safe_url


def test_safe_url_accepts_https():
    assert _is_safe_url("https://example.com") is True


def test_safe_url_rejects_private_ip():
    assert _is_safe_url("http://192.168.1.1") is False
    assert _is_safe_url("http://10.0.0.1") is False
    assert _is_safe_url("http://127.0.0.1") is False


def test_safe_url_rejects_localhost():
    assert _is_safe_url("http://localhost") is False


def test_safe_url_rejects_file_scheme():
    assert _is_safe_url("file:///etc/passwd") is False


def test_scrape_rejects_unsafe_url():
    with pytest.raises(ValueError, match="URL is not allowed"):
        scrape_website("http://localhost/secret")


def test_scrape_website_returns_text():
    content = scrape_website("https://example.com")
    assert isinstance(content, str)
    assert len(content) > 0
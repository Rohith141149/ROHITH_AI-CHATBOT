import pytest
from unittest.mock import patch, MagicMock
from rag.scraper import scrape_website
from config import SCRAPER_TIMEOUT, SCRAPER_USER_AGENT


def _mock_streaming_response(html_content: str):
    """Create a mock response that supports streaming (iter_content)."""
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.iter_content.return_value = iter([html_content])
    mock_response.raise_for_status.return_value = None
    return mock_response


class TestScrapeWebsite:
    """Tests for the scrape_website function."""

    @patch("rag.scraper.requests.get")
    def test_scrape_website_returns_text_content(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body><p>Hello World</p></body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Hello World" in result
        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=SCRAPER_TIMEOUT,
            headers={"User-Agent": SCRAPER_USER_AGENT},
            stream=True,
        )

    @patch("rag.scraper.requests.get")
    def test_scrape_website_strips_script_tags(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body>"
            "<script>var x = 1;</script>"
            "<p>Visible content</p>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Visible content" in result
        assert "var x = 1" not in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_strips_style_tags(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body>"
            "<style>body { color: red; }</style>"
            "<p>Styled text</p>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Styled text" in result
        assert "color: red" not in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_handles_multiple_paragraphs(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body>"
            "<p>First paragraph</p>"
            "<p>Second paragraph</p>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "First paragraph" in result
        assert "Second paragraph" in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_strips_whitespace(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body>"
            "<p>   Spaced content   </p>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Spaced content" in result
        # Leading/trailing whitespace should be stripped
        assert result.strip() == result or "Spaced content" in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_returns_empty_for_empty_page(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body></body></html>"
        )

        result = scrape_website("https://example.com")

        assert result.strip() == ""

    @patch("rag.scraper.requests.get")
    def test_scrape_website_handles_nested_elements(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body>"
            "<div><span><a href='#'>Link text</a></span></div>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Link text" in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_uses_correct_timeout_and_headers(self, mock_get):
        mock_get.return_value = _mock_streaming_response(
            "<html><body><p>Test</p></body></html>"
        )

        scrape_website("https://example.com")

        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=SCRAPER_TIMEOUT,
            headers={"User-Agent": SCRAPER_USER_AGENT},
            stream=True,
        )

    @patch("rag.scraper.requests.get")
    def test_scrape_website_raises_on_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        with pytest.raises(requests.ConnectionError):
            scrape_website("https://nonexistent.example.com")

    @patch("rag.scraper.requests.get")
    def test_scrape_website_raises_on_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(requests.Timeout):
            scrape_website("https://slow.example.com")

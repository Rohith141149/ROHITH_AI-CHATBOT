import pytest
from unittest.mock import patch, MagicMock
from rag.scraper import scrape_website


def make_mock_response(html_content, content_length=None, status_code=200):
    """Create a mock response that supports streaming."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.headers = {}
    if content_length is not None:
        mock_response.headers["Content-Length"] = str(content_length)
    mock_response.raise_for_status = MagicMock()
    mock_response.iter_content = MagicMock(
        return_value=iter([html_content])
    )
    return mock_response


class TestScrapeWebsite:
    """Tests for the scrape_website function."""

    @patch("rag.scraper.requests.get")
    def test_scrape_website_returns_text_content(self, mock_get):
        mock_get.return_value = make_mock_response(
            "<html><body><p>Hello World</p></body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Hello World" in result
        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=15,
            headers={"User-Agent": "RohithAIChatbot/1.0"},
            stream=True,
        )

    @patch("rag.scraper.requests.get")
    def test_scrape_website_strips_script_tags(self, mock_get):
        mock_get.return_value = make_mock_response(
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
        mock_get.return_value = make_mock_response(
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
        mock_get.return_value = make_mock_response(
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
        mock_get.return_value = make_mock_response(
            "<html><body>"
            "<p>   Spaced content   </p>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Spaced content" in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_returns_empty_for_empty_page(self, mock_get):
        mock_get.return_value = make_mock_response(
            "<html><body></body></html>"
        )

        result = scrape_website("https://example.com")

        assert result.strip() == ""

    @patch("rag.scraper.requests.get")
    def test_scrape_website_handles_nested_elements(self, mock_get):
        mock_get.return_value = make_mock_response(
            "<html><body>"
            "<div><span><a href='#'>Link text</a></span></div>"
            "</body></html>"
        )

        result = scrape_website("https://example.com")

        assert "Link text" in result

    @patch("rag.scraper.requests.get")
    def test_scrape_website_uses_correct_timeout_and_headers(self, mock_get):
        mock_get.return_value = make_mock_response(
            "<html><body><p>Test</p></body></html>"
        )

        scrape_website("https://example.com")

        mock_get.assert_called_once_with(
            "https://example.com",
            timeout=15,
            headers={"User-Agent": "RohithAIChatbot/1.0"},
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

    @patch("rag.scraper.requests.get")
    def test_scrape_website_rejects_oversized_content_length(self, mock_get):
        mock_get.return_value = make_mock_response(
            "<html><body><p>Big</p></body></html>",
            content_length=10 * 1024 * 1024,  # 10 MB
        )

        with pytest.raises(ValueError, match="too large"):
            scrape_website("https://example.com")

    @patch("rag.scraper.requests.get")
    def test_scrape_website_rejects_oversized_stream(self, mock_get):
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.raise_for_status = MagicMock()
        # Simulate chunks that exceed max size
        mock_response.iter_content = MagicMock(
            return_value=iter(["x" * (3 * 1024 * 1024), "x" * (3 * 1024 * 1024)])
        )
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="too large"):
            scrape_website("https://example.com")

    @patch("rag.scraper.requests.get")
    def test_scrape_website_calls_raise_for_status(self, mock_get):
        import requests
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            scrape_website("https://example.com")

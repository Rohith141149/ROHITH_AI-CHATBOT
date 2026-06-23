import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB


class ScraperError(Exception):
    """Base exception for scraper errors."""


class ScraperNetworkError(ScraperError):
    """Raised when a network-level failure occurs during scraping."""


class ScraperHTTPError(ScraperError):
    """Raised when the target URL returns a non-2xx HTTP status."""


class ScraperContentError(ScraperError):
    """Raised when the scraped page yields no usable text content."""


class ScraperSizeError(ScraperError):
    """Raised when the response exceeds the maximum allowed size."""


def scrape_website(url: str) -> str:
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "RohithAIChatbot/1.0"},
            stream=True,
        )
    except requests.exceptions.Timeout:
        logger.error("Request timed out for URL: %s", url)
        raise ScraperNetworkError(
            f"Request timed out after 15 seconds: {url}"
        )
    except requests.exceptions.ConnectionError as exc:
        logger.error("Connection failed for URL %s: %s", url, exc)
        raise ScraperNetworkError(
            f"Could not connect to {url}. Verify the URL is correct and the site is reachable."
        ) from exc
    except requests.exceptions.InvalidURL as exc:
        logger.error("Invalid URL provided: %s", url)
        raise ScraperNetworkError(
            f"Invalid URL format: {url}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.error("Unexpected request error for URL %s: %s", url, exc)
        raise ScraperNetworkError(
            f"Failed to fetch {url}: {exc}"
        ) from exc

    if not response.ok:
        logger.warning(
            "HTTP %d response from %s", response.status_code, url
        )
        raise ScraperHTTPError(
            f"Received HTTP {response.status_code} from {url}"
        )

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_RESPONSE_SIZE:
        raise ScraperSizeError("Response too large to process.")

    chunks = []
    size = 0
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        size += len(chunk)
        if size > MAX_RESPONSE_SIZE:
            raise ScraperSizeError("Response too large to process.")
        chunks.append(chunk)

    html_content = "".join(chunks)

    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    if not text:
        logger.warning("No text content extracted from %s", url)
        raise ScraperContentError(
            f"No text content could be extracted from {url}"
        )

    return text

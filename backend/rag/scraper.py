import requests
from bs4 import BeautifulSoup

from config import (
    SCRAPER_MAX_RESPONSE_SIZE,
    SCRAPER_STRIP_TAGS,
    SCRAPER_TIMEOUT,
    SCRAPER_USER_AGENT,
)


def scrape_website(url: str) -> str:
    response = requests.get(
        url,
        timeout=SCRAPER_TIMEOUT,
        headers={"User-Agent": SCRAPER_USER_AGENT},
        stream=True,
    )
    response.raise_for_status()

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > SCRAPER_MAX_RESPONSE_SIZE:
        raise ValueError("Response too large to process.")

    chunks = []
    size = 0
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        size += len(chunk)
        if size > SCRAPER_MAX_RESPONSE_SIZE:
            raise ValueError("Response too large to process.")
        chunks.append(chunk)

    html_content = "".join(chunks)

    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(SCRAPER_STRIP_TAGS):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return text

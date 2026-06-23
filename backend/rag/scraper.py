import requests
from bs4 import BeautifulSoup

MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB


def scrape_website(url: str) -> str:
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "RohithAIChatbot/1.0"},
        stream=True,
    )
    response.raise_for_status()

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_RESPONSE_SIZE:
        raise ValueError("Response too large to process.")

    # Read up to max size
    chunks = []
    size = 0
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        size += len(chunk)
        if size > MAX_RESPONSE_SIZE:
            raise ValueError("Response too large to process.")
        chunks.append(chunk)

    html_content = "".join(chunks)

    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text
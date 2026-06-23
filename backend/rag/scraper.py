from urllib.parse import urlparse
import ipaddress

import requests
from bs4 import BeautifulSoup

ALLOWED_SCHEMES = {"http", "https"}


def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return False
    except ValueError:
        if hostname in ("localhost", "metadata.google.internal"):
            return False
    return True


def scrape_website(url: str) -> str:
    if not _is_safe_url(url):
        raise ValueError(
            f"URL is not allowed: {url}"
        )

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    return text
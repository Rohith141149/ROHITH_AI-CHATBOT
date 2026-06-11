import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    response = requests.get(url, timeout=20)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text
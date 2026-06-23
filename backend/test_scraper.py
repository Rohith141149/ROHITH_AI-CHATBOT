from rag.scraper import scrape_website, ScraperError
from utils import content_summary

url = "https://www.westernunion.com"

try:
    content = scrape_website(url)
except ScraperError as exc:
    print(f"\nScraper error: {exc}")
    raise SystemExit(1)
except Exception as exc:
    print(f"\nUnexpected error: {exc}")
    raise SystemExit(1)

summary = content_summary(content, preview_length=3000)

print("\nWebsite Content Preview:\n")
print(summary["preview"])

print("\n")
print("Total Characters:", summary["characters"])

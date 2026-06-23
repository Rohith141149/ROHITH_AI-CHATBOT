from rag.scraper import scrape_website, ScraperError

url = "https://www.westernunion.com"

try:
    content = scrape_website(url)
except ScraperError as exc:
    print(f"\nScraper error: {exc}")
    raise SystemExit(1)
except Exception as exc:
    print(f"\nUnexpected error: {exc}")
    raise SystemExit(1)

print("\nWebsite Content Preview:\n")
print(content[:3000])

print("\n")
print("Total Characters:", len(content))
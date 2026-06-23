from rag.scraper import scrape_website
from utils import content_summary

url = "https://www.westernunion.com"

content = scrape_website(url)
summary = content_summary(content, preview_length=3000)

print("\nWebsite Content Preview:\n")
print(summary["preview"])

print("\n")
print("Total Characters:", summary["characters"])

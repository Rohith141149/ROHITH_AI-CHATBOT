from rag.scraper import scrape_website

url = "https://www.westernunion.com"

content = scrape_website(url)

print("\nWebsite Content Preview:\n")
print(content[:3000])

print("\n")
print("Total Characters:", len(content))
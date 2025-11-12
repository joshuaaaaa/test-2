#!/usr/bin/env python3
"""Test script to fetch and parse CSFD news."""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def fetch_csfd_news():
    """Fetch and parse CSFD news."""
    url = "https://www.csfd.cz/novinky/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
        "Referer": "https://www.csfd.cz/",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")

                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    return

                html = await response.text()
                print(f"HTML length: {len(html)}")

                # Save HTML for inspection
                with open("/home/user/test-2/csfd_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("HTML saved to csfd_debug.html")

                # Parse HTML
                soup = BeautifulSoup(html, "html.parser")

                # Try different selectors
                print("\n=== Testing selectors ===")

                # Try article with class
                articles_with_class = soup.find_all("article", class_="article", limit=5)
                print(f"Articles with class 'article': {len(articles_with_class)}")

                # Try all articles
                all_articles = soup.find_all("article", limit=5)
                print(f"All <article> tags: {len(all_articles)}")

                # Try divs with news-related classes
                news_divs = soup.find_all("div", class_=lambda x: x and "news" in x.lower(), limit=5)
                print(f"Divs with 'news' in class: {len(news_divs)}")

                # Try to find any h3 or h2 with links
                headers = soup.find_all(["h2", "h3"], limit=10)
                print(f"Found {len(headers)} h2/h3 headers")

                headers_with_links = [h for h in headers if h.find("a")]
                print(f"Headers with links: {len(headers_with_links)}")

                if headers_with_links:
                    print("\nFirst few headers with links:")
                    for i, h in enumerate(headers_with_links[:3]):
                        link = h.find("a")
                        print(f"{i+1}. {h.name} - {link.get_text(strip=True)[:50]}")
                        print(f"   Link: {link.get('href', 'N/A')}")
                        print(f"   Parent classes: {h.parent.get('class', [])}")

                # Check for specific CSFD patterns
                print("\n=== Looking for CSFD-specific patterns ===")

                # Look for news items
                news_items = soup.find_all(class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['news', 'article', 'item', 'novinka']
                ), limit=5)
                print(f"Elements with news-related classes: {len(news_items)}")

                if news_items:
                    print("\nFirst news item structure:")
                    print(news_items[0].prettify()[:500])

        except aiohttp.ClientError as err:
            print(f"Client error: {err}")
        except Exception as err:
            print(f"Unexpected error: {err}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(fetch_csfd_news())

#!/usr/bin/env python3
"""Simple test script to fetch and parse CSFD news."""
import urllib.request
from bs4 import BeautifulSoup


def fetch_csfd_news():
    """Fetch and parse CSFD news."""
    url = "https://www.csfd.cz/novinky/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
        "Referer": "https://www.csfd.cz/",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")

            html = response.read().decode('utf-8')
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
                    print(f"   Parent tag: {h.parent.name}")
                    print(f"   Parent classes: {h.parent.get('class', [])}")

            # Look for news-like structures
            print("\n=== Looking for news structures ===")

            # Check main content area
            main = soup.find("main") or soup.find("div", id="main")
            if main:
                print(f"Found main content area: {main.name}")
                articles_in_main = main.find_all("article", limit=5)
                print(f"Articles in main: {len(articles_in_main)}")

            # Look for divs that might contain news
            news_containers = soup.find_all("div", class_=lambda x: x and any(
                kw in str(x).lower() for kw in ['news', 'article', 'box']
            ), limit=10)
            print(f"Potential news containers: {len(news_containers)}")

            if news_containers:
                print("\nFirst container structure (first 300 chars):")
                print(str(news_containers[0])[:300])

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as err:
        print(f"Unexpected error: {err}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_csfd_news()

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import logging
from datetime import date, timedelta
from scraper.newsonair_scraper import NewsOnAirScraper, CATEGORIES

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test():
    scraper = NewsOnAirScraper(delay=0.1)
    
    print("Listing categories:", list(CATEGORIES.keys()))
    
    # Let's collect links for sports category
    print("\nCollecting links for category 'sports'...")
    try:
        links = scraper._collect_category_links('sports', max_pages=1)
        print(f"Found {len(links)} links:")
        for url in links[:5]:
            print(f"- {url}")
            
        if not links:
            print("No links found! The HTML structure of the category page might have changed.")
            return
            
        print("\nParsing first link...")
        url = links[0]
        soup = scraper._fetch(url)
        
        # Test title extraction
        title_tag = soup.select_one("h1, .entry-title, .post-title")
        if title_tag:
            print(f"Parsed Title tag content: '{title_tag.get_text(strip=True)}'")
        else:
            print("Title tag not found!")
            
        # Test date extraction
        published_at = scraper._extract_published_at(soup)
        print(f"Parsed published_at raw string: '{published_at}'")
        published_date = scraper._published_date(published_at)
        print(f"Parsed published_date ISO format: '{published_date}'")
        
        # Test body extraction
        if title_tag:
            body = scraper._extract_body(soup, title_tag)
            print(f"Parsed Body character length: {len(body)}")
            print(f"Parsed Body snippet: '{body[:200]}...'")
            
        # Run scraper.scrape with large date range
        print("\nRunning scrape for 'sports' category with wide date range (no date filter)...")
        articles = scraper.scrape(['sports'], limit_per_category=2, max_pages=1)
        print(f"Scraped {len(articles)} articles successfully:")
        for idx, art in enumerate(articles):
            print(f"Article {idx+1}:")
            print(f"  Title: {art.title}")
            print(f"  Date: {art.published_date} ({art.published_at})")
            print(f"  URL: {art.url}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Add backend to python path
    import os
    sys.path.append(os.path.abspath("backend"))
    test()

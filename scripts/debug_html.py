import requests
from bs4 import BeautifulSoup
import os
import sys

sys.path.append(os.path.abspath("backend"))
from scraper.newsonair_scraper import HEADERS

url = "https://newsonair.gov.in/fih-womens-nations-cup-india-beat-uruguay-3-2-to-top-pool-a/"

res = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(res.text, "html.parser")

print("--- Printing all h1 elements ---")
for idx, tag in enumerate(soup.find_all("h1")):
    print(f"h1 [{idx}]: class={tag.get('class')}, text='{tag.get_text(strip=True)}'")
    
print("\n--- Printing all h2 elements ---")
for idx, tag in enumerate(soup.find_all("h2")[:5]):
    print(f"h2 [{idx}]: class={tag.get('class')}, text='{tag.get_text(strip=True)}'")

print("\n--- Printing potential title divs/sections ---")
# Let's search for tags that might contain the main title
for tag in soup.select("div.title, div.entry-title, .post-title, .news-title, .single-title"):
    print(f"Tag: {tag.name}, class={tag.get('class')}, text='{tag.get_text(strip=True)}'")

# Let's search for the text 'FIH Women's Nations Cup' or 'Uruguay' in the document
for tag in soup.find_all(text=True):
    if "uruguay" in tag.lower() and len(tag.strip()) > 10:
        print(f"Found text block: Parent={tag.parent.name}, Class={tag.parent.get('class')}, Text='{tag.strip()}'")

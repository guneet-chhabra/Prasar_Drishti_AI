import requests
from bs4 import BeautifulSoup

url = "https://newsonair.gov.in/west-indies-to-face-scotland-in-icc-womens-t20-world-cup-match-at-headingley-today/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def inspect():
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    print("=== Title Tags ===")
    for h in soup.find_all(["h1", "h2", "h3"]):
        print(f"Tag: {h.name}, Classes: {h.get('class')}, Text: '{h.get_text(strip=True)[:60]}'")
        
    print("\n=== Main Content Containers ===")
    # Let's search for tags that might contain the article content
    # Look for divs containing paragraphs
    for div in soup.find_all("div"):
        classes = div.get("class", [])
        # Check if div has some common article body classes or if it has p tags inside
        if any(c in ["entry-content", "post-content", "content", "story"] for c in classes):
            print(f"Div tag: {div.name}, Classes: {classes}")
            p_tags = div.find_all("p", recursive=False)
            print(f"  Recursive=False p-tags count: {len(p_tags)}")
            for p in p_tags[:3]:
                print(f"    p text: '{p.get_text(strip=True)[:100]}'")
                
    print("\n=== Divs near the main title ===")
    title_tag = soup.select_one("h2.text-capitalize")
    if title_tag:
        print(f"Found title tag: {title_tag.name}, text: '{title_tag.get_text(strip=True)}'")
        parent = title_tag.parent
        print(f"Parent tag: {parent.name}, Classes: {parent.get('class')}")
        
        # Let's check grandparent
        grandparent = parent.parent
        print(f"Grandparent tag: {grandparent.name}, Classes: {grandparent.get('class')}")
        
    print("\n=== Inspecting entry-content ===")
    entry_content = soup.select_one("div.entry-content")
    if entry_content:
        print("Found entry-content container!")
        print("Raw text snippet:")
        print(entry_content.get_text()[:300])
        print("\nDirect children:")
        for idx, child in enumerate(entry_content.children):
            name = child.name if child.name else "TextNode"
            text_val = child.get_text(strip=True) if child.name else child.strip()
            if text_val:
                print(f"Child {idx}: type={name}, text snippet='{text_val[:100]}'")
    else:
        print("entry-content container not found!")

if __name__ == "__main__":
    inspect()

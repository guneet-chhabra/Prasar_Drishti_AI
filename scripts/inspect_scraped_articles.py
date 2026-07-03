import json
import os

path = r"backend\data\raw\archive_articles.json"

def inspect():
    if not os.path.exists(path):
        print(f"Error: {path} does not exist.")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Total archive articles: {len(data)}")
    for idx, art in enumerate(data[:1]):
        print(f"\n--- Article {idx+1} ---")
        print(f"Title: {art.get('title')}")
        print(f"Category: {art.get('category')}")
        print(f"URL: {art.get('url')}")
        body = art.get('body', '')
        print(f"Body:\n'{body}'")
        print(f"Body length: {len(body)}")
        
if __name__ == "__main__":
    inspect()

import json
import os
import csv

archive_json_path = r"backend\data\raw\archive_articles.json"
archive_csv_path = r"backend\data\raw\archive_articles.csv"

def clean_body(text):
    if not text:
        return ""
        
    cleaned = text.strip()
    
    # 1. Strip sidebar text
    sidebar_indicators = ["most read", "about us", "what's new", "related sites", "copyright", "last updated:"]
    for term in sidebar_indicators:
        idx = cleaned.lower().find(term)
        if idx != -1:
            cleaned = cleaned[:idx].strip()
            
    # 2. Detect and remove paragraph duplication
    n = len(cleaned)
    half_len = n // 2
    # Check split points around the middle
    for offset in range(-50, 50):
        mid = half_len + offset
        if 20 < mid < n - 20:
            part1 = cleaned[:mid].strip()
            part2 = cleaned[mid:].strip()
            # If the two parts are identical or highly similar (overlap first 50 chars and last 50 chars)
            if part1 == part2:
                cleaned = part1
                break
            elif len(part1) > 100 and len(part2) > 100:
                if part1[:50] == part2[:50] and part1[-50:] == part2[-50:]:
                    cleaned = part1
                    break
                    
    return cleaned

def clean_archive():
    if not os.path.exists(archive_json_path):
        print(f"Archive JSON not found at {archive_json_path}")
        return
        
    print("Loading archive articles...")
    with open(archive_json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    print(f"Loaded {len(articles)} articles. Cleaning bodies...")
    cleaned_count = 0
    duplicate_removed_count = 0
    
    for art in articles:
        old_body = art.get("body", "")
        new_body = clean_body(old_body)
        
        # Check if changed
        if len(new_body) < len(old_body):
            cleaned_count += 1
            if "most read" in old_body.lower() or "about us" in old_body.lower():
                pass # sidebar removed
            if len(new_body) <= len(old_body) // 2 + 10:
                duplicate_removed_count += 1
                
            art["body"] = new_body
            art["summary"] = new_body[:260] + "..." if len(new_body) > 260 else new_body
            art["word_count"] = len(new_body.split())
            
    # Save back to JSON
    with open(archive_json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"Saved cleaned JSON. Cleaned {cleaned_count} articles (detected duplicates in {duplicate_removed_count} articles).")
    
    # Save back to CSV
    fieldnames = [
        "title",
        "url",
        "category",
        "published_at",
        "published_date",
        "summary",
        "body",
        "word_count",
        "is_government_related",
        "scraped_at",
    ]
    with open(archive_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(articles)
    print("Saved cleaned CSV.")

if __name__ == "__main__":
    clean_archive()

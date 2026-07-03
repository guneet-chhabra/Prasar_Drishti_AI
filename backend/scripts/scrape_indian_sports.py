"""Scrape and compile articles related to Indian sports participation.

This script fetches articles from the NewsOnAir sports category, filters them for 
Indian athletes, teams, and tournaments, and saves them to indian_sports_articles.json/csv.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from scraper.newsonair_scraper import NewsOnAirScraper, Article, save_articles, read_articles

logger = logging.getLogger(__name__)

INDIA_ROOT_KEYWORDS = [
    "india", "indian", "indians", "team india", "men in blue", "women in blue",
    "bcci", "hockey india", "wfi", "sports authority of india", "sai", "pro kabaddi",
    "delhi", "mumbai", "bengaluru", "chennai", "kolkata", "hyderabad", "ahmedabad",
    "pune", "lucknow", "chandigarh", "jaipur"
]

INDIAN_ATHLETES_AND_TEAMS = [
    "ipl", "kohli", "rohit", "dhoni", "bumrah", "pant", "shami", "gill", 
    "jaiswal", "siraj", "pandya", "kl rahul", "ravindra jadeja", "ashwin", "chahal",
    "sindhu", "saina", "nehwal", "sen", "lakshya", "satwik", "chirag", 
    "satwiksairaj", "rankireddy", "prannoy", "srikanth",
    "neeraj", "chopra", "sable", "avinash", "toor", "shreeshankar", 
    "hima das", "dutee chand",
    "phogat", "vinesh", "bajrang", "punia", "singh", "nikhat", "zareen", 
    "lovlina", "borgohain", "mary kom", "amit panghal",
    "praggnanandhaa", "pragg", "gukesh", "harikrishna", "vidit", "humpy", "harika",
    "harmanpreet", "sreejesh", "savita", "dilpreet", "manpreet",
    "deepika kumari", "manu bhaker", "abhinav bindra", "gagan narang"
]

GENERAL_SPORTS_KEYWORDS = [
    "cricket", "badminton", "athletics", "wrestler", "wrestling", "boxing", "boxer",
    "chess", "hockey", "kabaddi", "olympics", "olympic", "cwg", "commonwealth", 
    "asian games", "paralympic", "paralympics", "archery", "archer", "shooting", "shooter",
    "javelin"
]

def is_indian_sports_article(article: dict | Article) -> bool:
    title = (article.title if isinstance(article, Article) else article.get("title", "")).lower()
    body = (article.body if isinstance(article, Article) else article.get("body", "")).lower()
    category = (article.category if isinstance(article, Article) else article.get("category", "")).lower()
    
    # We only care about sports articles
    if category != "sports":
        return False
        
    full_text = f"{title} {body}"
    
    # Check if matches any explicit Indian athlete or team name
    if any(kw in full_text for kw in INDIAN_ATHLETES_AND_TEAMS):
        return True
        
    # Check if matches generic sports words and contains explicit Indian terms
    has_general_sport = any(kw in full_text for kw in GENERAL_SPORTS_KEYWORDS)
    has_india_term = any(kw in full_text for kw in INDIA_ROOT_KEYWORDS)
    
    if has_general_sport and has_india_term:
        return True
        
    # Check if it just contains direct India references in general sports context
    if has_india_term and ("sport" in full_text or "gold" in full_text or "medal" in full_text or "championship" in full_text):
        return True
        
    return False

def compile_sports_dataset(max_pages: int = 15):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print(f"=== Compiling Indian Sports Participation Dataset ===")
    
    compiled_articles = []
    
    # 1. Seed from existing archive articles
    archive_path = Path(Config.RAW_DIR) / "archive_articles.json"
    if archive_path.exists():
        print(f"Loading existing articles from archive: {archive_path}")
        try:
            with open(archive_path, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
            
            existing_sports = [art for art in archive_data if is_indian_sports_article(art)]
            compiled_articles.extend(existing_sports)
            print(f"Found {len(existing_sports)} relevant sports articles in archive.")
        except Exception as e:
            print(f"Error reading archive: {e}")
            
    # 2. Seed from today's files
    for p in Path(Config.RAW_DIR).glob("today_*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                today_data = json.load(f)
            today_sports = [art for art in today_data if is_indian_sports_article(art)]
            compiled_articles.extend(today_sports)
            print(f"Found {len(today_sports)} relevant sports articles in {p.name}.")
        except Exception as e:
            print(f"Error reading {p.name}: {e}")

    # 3. Scrape fresh sports articles from NewsOnAir
    print(f"\nScraping sports category from NewsOnAir (up to {max_pages} pages)...")
    try:
        scraper = NewsOnAirScraper(delay=0.4)
        # Scrape category 'sports' only
        fresh_articles = scraper.scrape(
            categories=["sports"],
            limit_per_category=max_pages * 10,
            max_pages=max_pages,
            government_only=False
        )
        
        filtered_fresh = [art for art in fresh_articles if is_indian_sports_article(art)]
        print(f"Scraped {len(fresh_articles)} fresh sports articles. {len(filtered_fresh)} are India-related.")
        
        # Convert Article dataclass to dict
        for art in filtered_fresh:
            compiled_articles.append(art)
            
    except Exception as e:
        print(f"Scrape failed/interrupted: {e}. Proceeding with compiled archive data...")
        
    # 4. Deduplicate and Save
    if not compiled_articles:
        print("No articles compiled. Exiting.")
        return
        
    # Deduplicate by URL
    seen_urls = set()
    unique_articles = []
    for art in compiled_articles:
        url = art.url if isinstance(art, Article) else art.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        unique_articles.append(art)
        
    print(f"\nTotal unique India-related sports articles compiled: {len(unique_articles)}")
    
    # Save using standard helpers
    paths = save_articles(unique_articles, stem="indian_sports_articles", merge_existing=True)
    print(f"Saved dataset:")
    print(f"  JSON: {paths['json']}")
    print(f"  CSV: {paths['csv']}")
    
    # Show stats
    show_stats(unique_articles)

def show_stats(articles: list):
    sports_categories = {
        "Cricket": ["cricket", "ipl", "bcci", "kohli", "rohit", "dhoni"],
        "Badminton": ["badminton", "sindhu", "saina", "sen", "lakshya", "satwik", "chirag"],
        "Hockey": ["hockey", "asia cup hockey"],
        "Wrestling & Boxing": ["wrestler", "wrestling", "phogat", "vinesh", "bajrang", "punia", "boxing", "boxer", "nikhat", "zareen"],
        "Chess": ["chess", "praggnanandhaa", "gukesh"],
        "Athletics": ["athletics", "neeraj", "chopra", "javelin", "javelin throw"]
    }
    
    stats = {k: 0 for k in sports_categories}
    stats["Other/General"] = 0
    
    for art in articles:
        title = (art.title if isinstance(art, Article) else art.get("title", "")).lower()
        body = (art.body if isinstance(art, Article) else art.get("body", "")).lower()
        text = f"{title} {body}"
        
        matched = False
        for sport, keywords in sports_categories.items():
            if any(kw in text for kw in keywords):
                stats[sport] += 1
                matched = True
                break
        if not matched:
            stats["Other/General"] += 1
            
    print("\nSport Type Breakdown:")
    for sport, count in stats.items():
        print(f"  - {sport}: {count} articles")

if __name__ == "__main__":
    pages = 15
    if len(sys.argv) > 1:
        try:
            pages = int(sys.argv[1])
        except ValueError:
            pass
    compile_sports_dataset(max_pages=pages)

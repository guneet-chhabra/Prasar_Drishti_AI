"""NewsOnAir scraper and file storage helpers."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import Config

logger = logging.getLogger(__name__)

CATEGORIES = {
    "national": "https://newsonair.gov.in/category/national/",
    "international": "https://newsonair.gov.in/category/international/",
    "business": "https://newsonair.gov.in/category/business/",
    "sports": "https://newsonair.gov.in/category/sports/",
    "miscellaneous": "https://newsonair.gov.in/category/miscellaneous/",
}

GOVERNMENT_KEYWORDS = [
    "government",
    "govt",
    "centre",
    "central government",
    "union minister",
    "prime minister",
    "pm modi",
    "cabinet",
    "ministry",
    "minister",
    "parliament",
    "lok sabha",
    "rajya sabha",
    "policy",
    "scheme",
    "yojana",
    "niti aayog",
    "supreme court",
    "election commission",
    "president",
    "chief minister",
    "state government",
    "governance",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class Article:
    title: str
    url: str
    category: str
    published_at: str
    published_date: str
    summary: str
    body: str
    word_count: int
    is_government_related: bool
    scraped_at: str


class NewsOnAirScraper:
    def __init__(self, delay: float | None = None, timeout: int = 20) -> None:
        self.delay = Config.SCRAPE_DELAY if delay is None else delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        Path(Config.RAW_DIR).mkdir(parents=True, exist_ok=True)

    def scrape(
        self,
        categories: Iterable[str],
        limit_per_category: int = 20,
        max_pages: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
        government_only: bool = False,
    ) -> list[Article]:
        articles: list[Article] = []
        end_date = end_date or date.today()

        for category in categories:
            if category not in CATEGORIES:
                raise ValueError(f"Unknown category '{category}'. Choose from: {', '.join(CATEGORIES)}")

            logger.info("Scraping %s", category)
            links = self._collect_category_links(category, max_pages=max_pages)

            for url in links:
                if len([item for item in articles if item.category == category]) >= limit_per_category:
                    break

                try:
                    article = self._parse_article(url, category)
                except Exception as exc:
                    logger.warning("Skipping %s because parsing failed: %s", url, exc)
                    continue

                if not article:
                    continue
                if start_date and article.published_date and article.published_date < start_date.isoformat():
                    continue
                if article.published_date and article.published_date > end_date.isoformat():
                    continue
                if government_only and not article.is_government_related:
                    continue

                articles.append(article)
                time.sleep(self.delay)

        return dedupe_articles(articles)

    def save(
        self,
        articles: list[Article],
        stem: str = "newsonair_articles",
        merge_existing: bool = True,
    ) -> dict[str, str]:
        return save_articles(articles, stem=stem, merge_existing=merge_existing)

    def _collect_category_links(self, category: str, max_pages: int) -> list[str]:
        links: list[str] = []
        base_url = CATEGORIES[category]

        for page in range(1, max_pages + 1):
            page_url = base_url if page == 1 else urljoin(base_url, f"page/{page}/")
            soup = self._fetch(page_url)
            page_links = self._extract_listing_links(soup, category)

            if not page_links:
                break

            for url in page_links:
                if url not in links:
                    links.append(url)

            time.sleep(self.delay)

        return links

    def _fetch(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _extract_listing_links(self, soup: BeautifulSoup, category: str) -> list[str]:
        links: list[str] = []
        category_url = CATEGORIES[category]

        for heading in soup.select("h3 a[href], h2 a[href], article a[href]"):
            href = heading.get("href", "")
            title = heading.get_text(" ", strip=True)
            full_url = urljoin(category_url, href)

            if not title or not self._looks_like_article_url(full_url):
                continue
            if full_url not in links:
                links.append(full_url)

        return links

    def _parse_article(self, url: str, category: str) -> Article | None:
        soup = self._fetch(url)

        # Try specific headline selectors first, including h2.text-capitalize used by NewsOnAir
        title_selectors = [
            "h2.text-capitalize",
            "h1.text-capitalize",
            "h1.entry-title",
            "h1",
            ".entry-title",
            ".post-title",
            "h2"
        ]
        
        title_tag = None
        title = ""
        for selector in title_selectors:
            tag = soup.select_one(selector)
            if tag:
                parsed_title = self._clean_text(tag.get_text(" ", strip=True))
                # Ensure it is a valid non-empty headline
                if parsed_title and len(parsed_title) >= 10:
                    title = parsed_title
                    title_tag = tag
                    break
                    
        if not title_tag:
            return None

        published_at = self._extract_published_at(soup)
        published_date = self._published_date(published_at)
        body = self._extract_body(soup, title_tag)
        summary = self._summarize(body)
        joined_text = f"{title} {summary} {body}".lower()

        if len(title) < 8 or len(body) < 40:
            return None

        return Article(
            title=title,
            url=url,
            category=category,
            published_at=published_at,
            published_date=published_date,
            summary=summary,
            body=body,
            word_count=len(body.split()),
            is_government_related=any(keyword in joined_text for keyword in GOVERNMENT_KEYWORDS),
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )

    def _extract_published_at(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(" ", strip=True)
        match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s+(AM|PM)",
            text,
        )
        return match.group(0) if match else ""

    def _published_date(self, published_at: str) -> str:
        if not published_at:
            return ""
        try:
            return parsedate_to_datetime(published_at).date().isoformat()
        except (TypeError, ValueError):
            try:
                return datetime.strptime(published_at, "%B %d, %Y %I:%M %p").date().isoformat()
            except ValueError:
                return ""

    def _extract_body(self, soup: BeautifulSoup, title_tag) -> str:
        paragraphs: list[str] = []
        
        # 1. Target the known article content container if it exists
        content_container = soup.select_one("div.entry-content")
        if content_container:
            # Look at its direct children to avoid nested text duplication
            for child in content_container.children:
                if child.name in ["p", "div"]:
                    text = self._clean_text(child.get_text(" ", strip=True))
                    if text and len(text.split()) >= 5:
                        lower_text = text.lower()
                        if any(term in lower_text for term in ["most read", "about us", "what's new", "related sites", "copyright", "last updated:"]):
                            break
                        if text not in paragraphs:
                            paragraphs.append(text)
                elif not child.name:  # Text node directly in container
                    text = self._clean_text(child.strip())
                    if text and len(text.split()) >= 5:
                        if text not in paragraphs:
                            paragraphs.append(text)
            
            # If we successfully extracted paragraphs from the container, return them
            if paragraphs:
                return " ".join(paragraphs)
                
            # If no children matched, fallback to getting container text as a whole,
            # but ensure we don't bleed into sidebars.
            text = self._clean_text(content_container.get_text(" ", strip=True))
            if text:
                # Truncate if sidebar indicators somehow ended up inside
                for term in ["most read", "about us", "what's new", "related sites", "copyright", "last updated:"]:
                    idx = text.lower().find(term)
                    if idx != -1:
                        text = text[:idx].strip()
                return text

        # 2. Fallback to title-tag traversal if entry-content is not found
        # We start traversing from title_tag's parent to avoid capturing parent of title_tag
        start_element = title_tag.parent if title_tag.parent else title_tag
        
        for tag in start_element.find_all_next(["p", "div"]):
            text = self._clean_text(tag.get_text(" ", strip=True))
            if not text:
                continue
            lower_text = text.lower()
            if any(term in lower_text for term in ["most read", "about us", "what's new", "related sites", "copyright", "last updated:"]):
                break
            
            # To avoid adding parent container text and then child element texts (duplication):
            # check if this tag contains other p or div tags. If it does, we skip it and wait for its children.
            if tag.find(["p", "div"]):
                continue
                
            if len(text.split()) >= 5 and text not in paragraphs:
                paragraphs.append(text)
            if len(paragraphs) >= 10:
                break

        return " ".join(paragraphs)

    def _summarize(self, body: str, max_chars: int = 260) -> str:
        if len(body) <= max_chars:
            return body
        return body[:max_chars].rsplit(" ", 1)[0] + "..."

    def _looks_like_article_url(self, url: str) -> bool:
        blocked = ["/category/", "/tag/", "/author/", "/page/", "#", "facebook", "twitter", "instagram"]
        return url.startswith("https://newsonair.gov.in/") and not any(part in url for part in blocked)

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()


def read_articles(stem: str) -> list[dict]:
    path = Path(Config.RAW_DIR) / f"{stem}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_articles(
    articles: list[Article] | list[dict],
    stem: str,
    merge_existing: bool = True,
) -> dict[str, str]:
    output_dir = Path(Config.RAW_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"

    incoming = [asdict(article) if isinstance(article, Article) else article for article in articles]
    existing = read_articles(stem) if merge_existing else []
    payload = dedupe_dict_articles(existing + incoming)
    payload.sort(key=lambda item: item.get("published_at", ""), reverse=True)

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

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
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(payload)

    return {"json": str(json_path), "csv": str(csv_path)}


def dedupe_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    unique: list[Article] = []

    for article in articles:
        if article.url in seen:
            continue
        seen.add(article.url)
        unique.append(article)

    return unique


def dedupe_dict_articles(articles: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []

    for article in articles:
        url = article.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        unique.append(article)

    return unique


def archive_today(today: date | None = None) -> dict[str, str] | None:
    today = today or date.today()
    today_stem = f"today_{today.isoformat()}"
    today_articles = read_articles(today_stem)
    if not today_articles:
        return None
    return save_articles(today_articles, stem="archive_articles", merge_existing=True)


def scrape_today(government_only: bool = True) -> list[Article]:
    scraper = NewsOnAirScraper(delay=0.3)
    return scraper.scrape(
        categories=["national", "international", "business", "sports", "miscellaneous"],
        limit_per_category=40,
        max_pages=3,
        start_date=date.today(),
        end_date=date.today(),
        government_only=government_only,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape articles from NewsOnAir.")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["national", "international", "business", "sports", "miscellaneous"],
        choices=sorted(CATEGORIES),
    )
    parser.add_argument("--limit", type=int, default=20, help="Articles per category.")
    parser.add_argument("--pages", type=int, default=5, help="Category listing pages to scan.")
    parser.add_argument("--days", type=int, default=1, help="How many days back to include.")
    parser.add_argument("--stem", default="newsonair_articles", help="Output filename without extension.")
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between requests.")
    parser.add_argument("--government-only", action="store_true", help="Keep only government-related articles.")
    parser.add_argument("--today", action="store_true", help="Save into today_YYYY-MM-DD files.")
    parser.add_argument("--archive-today", action="store_true", help="Merge today's file into archive_articles.")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args()

    if args.archive_today:
        paths = archive_today()
        print("Archived today's articles" if paths else "No today's articles to archive")
        return

    end_date = date.today()
    start_date = end_date - timedelta(days=max(args.days - 1, 0))
    stem = f"today_{end_date.isoformat()}" if args.today else args.stem

    scraper = NewsOnAirScraper(delay=args.delay)
    articles = scraper.scrape(
        args.categories,
        limit_per_category=args.limit,
        max_pages=args.pages,
        start_date=start_date,
        end_date=end_date,
        government_only=args.government_only,
    )
    paths = scraper.save(articles, stem=stem, merge_existing=True)

    print(f"Scraped {len(articles)} articles")
    print(f"JSON: {paths['json']}")
    print(f"CSV: {paths['csv']}")


if __name__ == "__main__":
    main()

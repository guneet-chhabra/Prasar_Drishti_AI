"""The Hindu scraper and file storage helpers."""

from __future__ import annotations

import argparse
import logging
import re
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import Config
from scraper.newsonair_scraper import Article, save_articles, read_articles, dedupe_articles, dedupe_dict_articles

logger = logging.getLogger(__name__)

CATEGORIES = {
    "national": "https://www.thehindu.com/news/national/",
    "international": "https://www.thehindu.com/news/international/",
    "business": "https://www.thehindu.com/business/",
    "sports": "https://www.thehindu.com/sport/",
    "miscellaneous": "https://www.thehindu.com/news/",
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


class TheHinduScraper:
    def __init__(self, delay: float | None = None, timeout: int = 20) -> None:
        self.delay = Config.SCRAPE_DELAY if delay is None else delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        Path(Config.RAW_DIR).mkdir(parents=True, exist_ok=True)

    def scrape(
        self,
        categories: Iterable[str],
        limit_per_category: int = 10,
        max_pages: int = 3,
        start_date: date | None = None,
        end_date: date | None = None,
        government_only: bool = False,
    ) -> list[Article]:
        articles: list[Article] = []
        end_date = end_date or date.today()

        for category in categories:
            if category not in CATEGORIES:
                raise ValueError(f"Unknown category '{category}'. Choose from: {', '.join(CATEGORIES)}")

            logger.info("Scraping The Hindu: %s", category)
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
        stem: str = "thehindu_articles",
        merge_existing: bool = True,
    ) -> dict[str, str]:
        return save_articles(articles, stem=stem, merge_existing=merge_existing)

    def _collect_category_links(self, category: str, max_pages: int) -> list[str]:
        links: list[str] = []
        base_url = CATEGORIES[category]

        for page in range(1, max_pages + 1):
            page_url = base_url if page == 1 else f"{base_url}?page={page}"
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
        base_domain = "https://www.thehindu.com"

        for a in soup.select("a[href]"):
            href = a.get("href", "")
            full_url = urljoin(base_domain, href)

            if not self._looks_like_article_url(full_url):
                continue
            if full_url not in links:
                links.append(full_url)

        return links

    def _looks_like_article_url(self, url: str) -> bool:
        # The Hindu article URLs end with /article\d+\.ece
        return bool(re.search(r"article\d+\.ece$", url))

    def _parse_article(self, url: str, category: str) -> Article | None:
        soup = self._fetch(url)

        # Title: Extract from meta tag or h1
        title_meta = soup.find("meta", property="og:title")
        if title_meta and title_meta.get("content"):
            title = title_meta.get("content").strip()
        else:
            h1 = soup.find("h1")
            title = h1.get_text(" ", strip=True) if h1 else ""

        # Strip " - The Hindu" suffix if present
        if title.endswith(" - The Hindu"):
            title = title[:-12].strip()

        if not title or len(title) < 10:
            return None

        # Published time: Extract from meta datePublished or article:published_time
        published_at_raw = ""
        for prop in ["article:published_time", "publish-date", "datePublished"]:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop}) or soup.find("meta", itemprop=prop)
            if meta and meta.get("content"):
                published_at_raw = meta.get("content").strip()
                break

        # Parse date and format published_at
        published_date = ""
        published_at = ""
        if published_at_raw:
            try:
                # E.g. "2026-07-09T13:48:58.000+05:30" or "2026-07-09T13:48:58+05:30"
                # Strip fractional seconds if present for standard datetime parsing
                dt_str = re.sub(r"\.\d+", "", published_at_raw)
                dt = datetime.fromisoformat(dt_str)
                published_date = dt.date().isoformat()
                published_at = dt.strftime("%B %d, %Y %I:%M %p")
            except Exception:
                # Fallback to simple regex/split
                match = re.search(r"\d{4}-\d{2}-\d{2}", published_at_raw)
                if match:
                    published_date = match.group(0)
                    published_at = published_at_raw

        if not published_date:
            published_date = date.today().isoformat()
            published_at = datetime.now().strftime("%B %d, %Y %I:%M %p")

        # Body: find content-body-xxxxx element or fallback
        body = ""
        body_elem = None
        for elem in soup.find_all(id=True):
            if elem.get("id", "").startswith("content-body-"):
                body_elem = elem
                break
        
        if not body_elem:
            body_elem = soup.select_one(".articlebodycontent, .article-body, .articlebodycontainer")

        if body_elem:
            paragraphs = []
            for p in body_elem.find_all("p"):
                txt = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
                # Skip paragraphs that look like subscription prompts or are too short
                lower_txt = txt.lower()
                if not txt or len(txt.split()) < 5:
                    continue
                if any(term in lower_txt for term in ["subscription", "subscribe", "subscribers", "sign in", "e-paper", "logged in", "loading..."]):
                    continue
                paragraphs.append(txt)
            body = " ".join(paragraphs)

        if not body or len(body) < 40:
            return None

        # Summary: Extract from meta description or fallback to first 260 chars of body
        summary = ""
        desc_meta = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if desc_meta and desc_meta.get("content"):
            summary = desc_meta.get("content").strip()
        
        if not summary or len(summary) < 20:
            if len(body) <= 260:
                summary = body
            else:
                summary = body[:260].rsplit(" ", 1)[0] + "..."

        joined_text = f"{title} {summary} {body}".lower()

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape articles from The Hindu.")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["national", "international", "business", "sports", "miscellaneous"],
        choices=sorted(CATEGORIES),
    )
    parser.add_argument("--limit", type=int, default=10, help="Articles per category.")
    parser.add_argument("--pages", type=int, default=3, help="Category listing pages to scan.")
    parser.add_argument("--days", type=int, default=1, help="How many days back to include.")
    parser.add_argument("--stem", default="thehindu_articles", help="Output filename without extension.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests.")
    parser.add_argument("--government-only", action="store_true", help="Keep only government-related articles.")
    parser.add_argument("--today", action="store_true", help="Save into today_thehindu_YYYY-MM-DD files.")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args()

    end_date = date.today()
    start_date = end_date - timedelta(days=max(args.days - 1, 0))
    stem = f"today_thehindu_{end_date.isoformat()}" if args.today else args.stem

    scraper = TheHinduScraper(delay=args.delay)
    articles = scraper.scrape(
        args.categories,
        limit_per_category=args.limit,
        max_pages=args.pages,
        start_date=start_date,
        end_date=end_date,
        government_only=args.government_only,
    )
    paths = scraper.save(articles, stem=stem, merge_existing=True)

    print(f"Scraped {len(articles)} articles from The Hindu")
    print(f"JSON: {paths['json']}")
    print(f"CSV: {paths['csv']}")


if __name__ == "__main__":
    main()

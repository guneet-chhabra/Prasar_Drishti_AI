"""Run the NewsOnAir monitor loop.

Use this in a separate terminal while the project is running. It updates today's
dataset every 30 minutes and archives the previous day when the date changes.
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scraper.newsonair_scraper import NewsOnAirScraper, archive_today

INTERVAL_SECONDS = 30 * 60


def update_today() -> int:
    today = date.today()
    scraper = NewsOnAirScraper(delay=0.3)
    articles = scraper.scrape(
        categories=["national", "international", "business", "sports", "miscellaneous"],
        limit_per_category=40,
        max_pages=3,
        start_date=today,
        end_date=today,
        government_only=False,
    )
    scraper.save(articles, stem=f"today_{today.isoformat()}", merge_existing=True)
    return len(articles)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    active_day = date.today()

    while True:
        current_day = date.today()
        if current_day != active_day:
            logging.info("Date changed. Archiving %s", active_day.isoformat())
            archive_today(active_day)
            active_day = current_day

        count = update_today()
        logging.info("Today's update complete. Newly fetched batch size: %s", count)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

"""Fetch OLX listings and print how many match the current .env filters,
without sending anything to Telegram. Useful for tuning filters."""
import asyncio
import sys

from bot.filters import matches, parse_ad
from bot.formatter import format_message
from bot.scraper import fetch_listings
from config import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


async def main():
    ads = await fetch_listings(config.city_slug, config.pages_to_scan)
    print(f"Знайдено оголошень на сторінках: {len(ads)}")

    matched = [parse_ad(raw) for raw in ads]
    matched = [p for p in matched if matches(p, config)]
    print(f"Проходять поточні фільтри: {len(matched)}")

    for parsed in matched[:3]:
        print("=" * 40)
        print(format_message(parsed))
        print(f"photos: {len(parsed.photos)}  url: {parsed.url}")


asyncio.run(main())

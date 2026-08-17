"""Fetch OLX listings for every configured feed and print how many match
its filters, without sending anything to Telegram. Useful for tuning filters."""
import asyncio
import sys

from bot.currency import fetch_usd_rate
from bot.filters import matches, parse_ad
from bot.formatter import format_message
from bot.scraper import fetch_listings
from config import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


async def main():
    for feed in config.feeds:
        print("#" * 50)
        print(f"feed={feed.key} enabled={feed.enabled} chat_id={feed.chat_id or '(not set)'}")

        ads = await fetch_listings(config.city_slug, feed.category_path, config.pages_to_scan)
        print(f"Знайдено оголошень на сторінках: {len(ads)}")

        parsed_list = [parse_ad(raw) for raw in ads]
        matched = [p for p in parsed_list if matches(p, feed)]
        print(f"Проходять поточні фільтри: {len(matched)}")

        usd_rate = await fetch_usd_rate() if feed.currency == "USD" else None
        show_pets = feed.key == "rental"
        for parsed in matched[:2]:
            price_usd = parsed.price_value / usd_rate if usd_rate and parsed.price_value else None
            print("=" * 40)
            print(format_message(parsed, title_label=feed.title_label, show_pets=show_pets, price_usd=price_usd))
            print(f"photos: {len(parsed.photos)}  url: {parsed.url}")


asyncio.run(main())

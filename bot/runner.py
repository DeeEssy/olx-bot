import asyncio
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from bot.currency import fetch_usd_rate
from bot.db import Database
from bot.filters import ParsedAd, matches, parse_ad
from bot.formatter import format_message
from bot.scraper import fetch_listings
from config import Config, FeedConfig

logger = logging.getLogger("olx-bot")

MAX_ALBUM_PHOTOS = 10


async def send_ad(
    bot: Bot,
    chat_id: str,
    parsed: ParsedAd,
    title_label: str,
    show_pets: bool,
    price_usd: float | None,
) -> None:
    photos = parsed.photos[:MAX_ALBUM_PHOTOS]

    if photos:
        media = [InputMediaPhoto(media=url) for url in photos]
        try:
            await bot.send_media_group(chat_id=chat_id, media=media)
        except Exception:
            logger.exception("Failed to send media group for ad %s", parsed.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Відкрити оголошення", url=parsed.url)]]
    )

    await bot.send_message(
        chat_id=chat_id,
        text=format_message(parsed, title_label=title_label, show_pets=show_pets, price_usd=price_usd),
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def run_feed(bot: Bot, db: Database, feed: FeedConfig, city_slug: str, pages_to_scan: int) -> int:
    if not feed.enabled:
        logger.info("Feed '%s' has no chat_id configured, skipping", feed.key)
        return 0

    logger.info("Scanning OLX feed=%s city=%s pages=%s", feed.key, city_slug, pages_to_scan)
    ads = await fetch_listings(city_slug, feed.category_path, pages_to_scan)
    logger.info("[%s] Fetched %d ads", feed.key, len(ads))

    usd_rate: float | None = None
    if feed.currency == "USD":
        usd_rate = await fetch_usd_rate()
        if usd_rate is None:
            logger.warning("[%s] Could not fetch USD rate, falling back to UAH prices", feed.key)

    show_pets = feed.key == "rental"
    sent = 0
    for raw_ad in ads:
        if db.is_notified(feed.key, raw_ad["id"]):
            continue

        parsed = parse_ad(raw_ad)

        if not matches(parsed, feed):
            continue

        price_usd = parsed.price_value / usd_rate if usd_rate and parsed.price_value else None
        await send_ad(bot, feed.chat_id, parsed, feed.title_label, show_pets, price_usd)
        db.mark_notified(feed.key, parsed.id)
        sent += 1
        await asyncio.sleep(1.5)  # avoid hitting Telegram rate limits

    logger.info("[%s] Sent %d new matching ads", feed.key, sent)
    return sent


async def run_cycle(bot: Bot, db: Database, config: Config) -> int:
    total = 0
    for feed in config.feeds:
        total += await run_feed(bot, db, feed, config.city_slug, config.pages_to_scan)
    return total

import asyncio
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from bot.db import Database
from bot.filters import ParsedAd, matches, parse_ad
from bot.formatter import format_message
from bot.scraper import fetch_listings
from config import Config

logger = logging.getLogger("olx-bot")

MAX_ALBUM_PHOTOS = 10


async def send_ad(bot: Bot, chat_id: str, parsed: ParsedAd) -> None:
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
        text=format_message(parsed),
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def run_cycle(bot: Bot, db: Database, config: Config) -> int:
    logger.info("Scanning OLX: city=%s pages=%s", config.city_slug, config.pages_to_scan)
    ads = await fetch_listings(config.city_slug, config.pages_to_scan)
    logger.info("Fetched %d ads", len(ads))

    sent = 0
    for raw_ad in ads:
        if db.is_notified(raw_ad["id"]):
            continue

        parsed = parse_ad(raw_ad)

        if not matches(parsed, config):
            continue

        if not config.chat_id:
            logger.warning("TELEGRAM_CHAT_ID is not set, skipping send for ad %s", parsed.id)
            continue

        await send_ad(bot, config.chat_id, parsed)
        db.mark_notified(parsed.id)
        sent += 1
        await asyncio.sleep(1.5)  # avoid hitting Telegram rate limits

    logger.info("Sent %d new matching ads", sent)
    return sent

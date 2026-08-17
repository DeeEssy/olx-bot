"""Run a single poll cycle and exit. Used by the GitHub Actions workflow,
which triggers this on a schedule instead of keeping a process alive."""
import asyncio
import logging
import sys

from aiogram import Bot

from bot.db import Database
from bot.runner import run_cycle
from config import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


async def main() -> None:
    if not config.bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
    if not config.chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID is not set")

    bot = Bot(token=config.bot_token)
    db = Database(config.db_path)
    try:
        await run_cycle(bot, db, config)
    finally:
        await bot.session.close()
        db.close()


asyncio.run(main())

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.db import Database
from bot.runner import run_cycle
from config import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olx-bot")


async def poll_loop(bot: Bot, db: Database) -> None:
    while True:
        try:
            await run_cycle(bot, db, config)
        except Exception:
            logger.exception("Error during poll cycle")

        await asyncio.sleep(config.poll_interval_seconds)


async def main() -> None:
    if not config.bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set in .env")

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        await message.answer(f"Привіт! Твій chat_id: {message.chat.id}")

    @dp.message()
    async def on_any_message(message: Message) -> None:
        await message.answer(f"Твій chat_id: {message.chat.id}")

    db = Database(config.db_path)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(poll_loop(bot, db))
        tg.create_task(dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())

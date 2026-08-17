import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _int_or_none(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    return int(value)


def _int_list(value: str | None) -> list[int]:
    if value is None or value.strip() == "":
        return []
    return [int(v.strip()) for v in value.split(",") if v.strip()]


def _bool(value: str | None) -> bool:
    return (value or "").strip().lower() in ("1", "true", "yes", "y")


@dataclass
class Config:
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    city_slug: str = os.getenv("CITY_SLUG", "kiev")
    city_name: str = os.getenv("CITY_NAME", "")

    price_min: int | None = field(default_factory=lambda: _int_or_none(os.getenv("PRICE_MIN")))
    price_max: int | None = field(default_factory=lambda: _int_or_none(os.getenv("PRICE_MAX")))
    rooms: list[int] = field(default_factory=lambda: _int_list(os.getenv("ROOMS")))
    pets_only: bool = field(default_factory=lambda: _bool(os.getenv("PETS_ONLY")))
    owner_type: str = os.getenv("OWNER_TYPE", "any")  # any / agency / private

    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
    pages_to_scan: int = int(os.getenv("PAGES_TO_SCAN", "3"))

    db_path: str = os.getenv("DB_PATH", "data/olx_bot.db")


config = Config()

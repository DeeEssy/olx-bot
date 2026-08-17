import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _str_or_default(value: str | None, default: str) -> str:
    if value is None or value.strip() == "":
        return default
    return value


def _int_or_default(value: str | None, default: int) -> int:
    if value is None or value.strip() == "":
        return default
    return int(value)


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


def _max_age_days(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return 3
    parsed = int(value)
    return parsed if parsed > 0 else None


@dataclass
class Config:
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    city_slug: str = field(default_factory=lambda: _str_or_default(os.getenv("CITY_SLUG"), "kiev"))
    city_name: str = os.getenv("CITY_NAME", "")

    price_min: int | None = field(default_factory=lambda: _int_or_none(os.getenv("PRICE_MIN")))
    price_max: int | None = field(default_factory=lambda: _int_or_none(os.getenv("PRICE_MAX")))
    rooms: list[int] = field(default_factory=lambda: _int_list(os.getenv("ROOMS")))
    pets_only: bool = field(default_factory=lambda: _bool(os.getenv("PETS_ONLY")))
    owner_type: str = field(default_factory=lambda: _str_or_default(os.getenv("OWNER_TYPE"), "any"))  # any / agency / private

    poll_interval_seconds: int = field(default_factory=lambda: _int_or_default(os.getenv("POLL_INTERVAL_SECONDS"), 300))
    pages_to_scan: int = field(default_factory=lambda: _int_or_default(os.getenv("PAGES_TO_SCAN"), 3))

    # Only notify about ads created within this many days (OLX sellers can
    # "bump" old ads to the top of search results without a fresh createdTime).
    # Set MAX_AGE_DAYS=0 to disable this filter entirely.
    max_age_days: int | None = field(default_factory=lambda: _max_age_days(os.getenv("MAX_AGE_DAYS")))

    db_path: str = field(default_factory=lambda: _str_or_default(os.getenv("DB_PATH"), "data/olx_bot.db"))


config = Config()

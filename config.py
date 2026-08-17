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
class FeedConfig:
    key: str  # dedup namespace, e.g. "rental" / "sale"
    category_path: str  # OLX URL segment, e.g. "dolgosrochnaya-arenda-kvartir"
    title_label: str  # message header word, e.g. "Оренда" / "Продаж"
    chat_id: str
    price_min: int | None = None
    price_max: int | None = None
    rooms: list[int] = field(default_factory=list)
    pets_only: bool = False
    owner_type: str = "any"  # any / agency / private
    max_age_days: int | None = 3

    @property
    def enabled(self) -> bool:
        return bool(self.chat_id)


def _rental_feed() -> FeedConfig:
    return FeedConfig(
        key="rental",
        category_path="dolgosrochnaya-arenda-kvartir",
        title_label="Оренда",
        chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        price_min=_int_or_none(os.getenv("PRICE_MIN")),
        price_max=_int_or_none(os.getenv("PRICE_MAX")),
        rooms=_int_list(os.getenv("ROOMS")),
        pets_only=_bool(os.getenv("PETS_ONLY")),
        owner_type=_str_or_default(os.getenv("OWNER_TYPE"), "any"),
        max_age_days=_max_age_days(os.getenv("MAX_AGE_DAYS")),
    )


def _sale_feed() -> FeedConfig:
    return FeedConfig(
        key="sale",
        category_path="prodazha-kvartir",
        title_label="Продаж",
        chat_id=os.getenv("TELEGRAM_CHAT_ID_SALE", ""),
        price_min=_int_or_none(os.getenv("SALE_PRICE_MIN")),
        price_max=_int_or_none(os.getenv("SALE_PRICE_MAX")),
        rooms=_int_list(os.getenv("SALE_ROOMS")),
        pets_only=False,
        owner_type=_str_or_default(os.getenv("SALE_OWNER_TYPE"), "any"),
        max_age_days=_max_age_days(os.getenv("SALE_MAX_AGE_DAYS")),
    )


@dataclass
class Config:
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    city_slug: str = field(default_factory=lambda: _str_or_default(os.getenv("CITY_SLUG"), "kiev"))
    city_name: str = os.getenv("CITY_NAME", "")

    poll_interval_seconds: int = field(default_factory=lambda: _int_or_default(os.getenv("POLL_INTERVAL_SECONDS"), 300))
    pages_to_scan: int = field(default_factory=lambda: _int_or_default(os.getenv("PAGES_TO_SCAN"), 3))

    db_path: str = field(default_factory=lambda: _str_or_default(os.getenv("DB_PATH"), "data/olx_bot.db"))

    feeds: list[FeedConfig] = field(default_factory=lambda: [_rental_feed(), _sale_feed()])


config = Config()

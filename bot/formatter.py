import re
from datetime import datetime

from bot.filters import ParsedAd

_TAG_RE = re.compile(r"<[^>]+>")
_BLANK_LINES_RE = re.compile(r"\n{3,}")

DEPOSIT_KEYWORDS = [
    "завдат",
    "задат",
    "застав",
    "депозит",
    "комісі",
    "комисси",
    "передоплат",
    "предоплат",
]

DESCRIPTION_LIMIT = 500


def _format_date(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return iso_str
    return dt.strftime("%d.%m.%Y %H:%M")


def _deposit_guess(description: str) -> str:
    low = description.lower()
    if any(kw in low for kw in DEPOSIT_KEYWORDS):
        return "ймовірно так"
    return "ймовірно немає"


def _pets_line(parsed: ParsedAd) -> str:
    if parsed.pets_allowed is None:
        return "не вказано — треба уточнити"
    if parsed.pets_allowed:
        return f"так ({parsed.pets_value})"
    return "не дозволено"


def _owner_line(parsed: ParsedAd) -> str:
    return "агентство" if parsed.is_agency else "власник"


def _floor_line(parsed: ParsedAd) -> str:
    if parsed.floor and parsed.total_floors:
        return f"{parsed.floor}/{parsed.total_floors}"
    if parsed.floor:
        return parsed.floor
    return "не вказано"


def _title_line(parsed: ParsedAd, title_label: str) -> str:
    if parsed.rooms:
        return f"🏠 {title_label} {parsed.rooms}кімнатної квартири"
    return f"🏠 {parsed.title}"


def _clean_description(description: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", description)
    text = _TAG_RE.sub("", text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def format_message(parsed: ParsedAd, title_label: str = "Оренда", show_pets: bool = True) -> str:
    description = _clean_description(parsed.description)
    if len(description) > DESCRIPTION_LIMIT:
        description = description[:DESCRIPTION_LIMIT].rstrip() + "..."

    lines = [
        _title_line(parsed, title_label),
        f"💰 {parsed.price_display}",
        f"📍 Район: {parsed.district or 'не вказано'}",
        f"🏢 Поверх: {_floor_line(parsed)}",
    ]
    if show_pets:
        lines.append(f"🐾 Тварини: {_pets_line(parsed)}")
    lines += [
        f"👤 Хазяїн: {_owner_line(parsed)}",
        f"🕒 Додано: {_format_date(parsed.created_time)}",
        f"⚠️ Доплата: {_deposit_guess(parsed.description)}",
        "",
        description,
    ]
    return "\n".join(lines)

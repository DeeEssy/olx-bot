import re
from dataclasses import dataclass

from config import Config


def _get_param(ad: dict, key: str) -> dict | None:
    for p in ad.get("params", []):
        if p.get("key") == key:
            return p
    return None


@dataclass
class ParsedAd:
    id: int
    title: str
    description: str
    url: str
    price_value: int | None
    price_display: str
    rooms: int | None
    floor: str | None
    total_floors: str | None
    pets_value: str | None
    pets_allowed: bool | None
    is_agency: bool
    district: str | None
    created_time: str
    photos: list[str]


def parse_ad(ad: dict) -> ParsedAd:
    price = ad.get("price") or {}
    regular = price.get("regularPrice") or {}

    rooms_param = _get_param(ad, "number_of_rooms_string")
    rooms = None
    if rooms_param and rooms_param.get("value"):
        m = re.search(r"\d+", rooms_param["value"])
        if m:
            rooms = int(m.group())

    floor_param = _get_param(ad, "floor")
    total_floors_param = _get_param(ad, "total_floors")

    pets_param = _get_param(ad, "pets")
    pets_value = pets_param.get("value") if pets_param else None
    pets_allowed = None
    if pets_param:
        normalized = pets_param.get("normalizedValue") or []
        pets_allowed = any(str(v).startswith("yes_") for v in normalized)

    location = ad.get("location") or {}

    return ParsedAd(
        id=ad["id"],
        title=ad.get("title", ""),
        description=ad.get("description", "") or "",
        url=ad.get("url", ""),
        price_value=regular.get("value"),
        price_display=price.get("displayValue", "Не вказано"),
        rooms=rooms,
        floor=floor_param.get("value") if floor_param else None,
        total_floors=total_floors_param.get("value") if total_floors_param else None,
        pets_value=pets_value,
        pets_allowed=pets_allowed,
        is_agency=bool(ad.get("isBusiness")),
        district=location.get("districtName"),
        created_time=ad.get("createdTime", ""),
        photos=ad.get("photos", []) or [],
    )


def matches(parsed: ParsedAd, config: Config) -> bool:
    if config.price_min is not None:
        if parsed.price_value is None or parsed.price_value < config.price_min:
            return False

    if config.price_max is not None:
        if parsed.price_value is None or parsed.price_value > config.price_max:
            return False

    if config.rooms:
        if parsed.rooms is None or parsed.rooms not in config.rooms:
            return False

    if config.pets_only:
        if not parsed.pets_allowed:
            return False

    if config.owner_type == "agency" and not parsed.is_agency:
        return False
    if config.owner_type == "private" and parsed.is_agency:
        return False

    return True

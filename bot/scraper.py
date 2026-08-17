import asyncio
import json
import logging
import re

from curl_cffi import requests as curl_requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.olx.ua/uk/nedvizhimost/kvartiry/{category}/{city}/"

# OLX sits behind a CloudFront bot-protection layer that fingerprints the TLS
# handshake (JA3/JA4-style). Plain Python HTTP clients (requests, aiohttp,
# httpx) and even plain `curl` get a blanket 403 - verified on both Windows
# and a real Linux (GitHub Actions) runner. curl_cffi, which impersonates a
# real Chrome TLS fingerprint, gets through with a 200 on both platforms, so
# it's used here instead of anything relying on the host's own TLS stack.
IMPERSONATE = "chrome124"

HEADERS = {
    "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7",
}

# Matches a well-formed JS string literal (respects \" and \\ escapes) so it
# stops at the real closing quote instead of over- or under-matching.
STATE_RE = re.compile(r'window\.__PRERENDERED_STATE__\s*=\s*"((?:[^"\\]|\\.)*)"')


def _get_sync(url: str) -> str | None:
    try:
        resp = curl_requests.get(url, headers=HEADERS, impersonate=IMPERSONATE, timeout=30)
    except Exception:
        logger.exception("curl_cffi request failed for %s", url)
        return None

    if resp.status_code != 200:
        logger.warning("OLX returned status %s for %s", resp.status_code, url)
        return None

    return resp.text


async def _curl_get(url: str) -> str | None:
    return await asyncio.to_thread(_get_sync, url)


def _extract_ads(html: str) -> list[dict]:
    match = STATE_RE.search(html)
    if not match:
        logger.warning("PRERENDERED_STATE not found on page")
        return []

    try:
        raw = json.loads('"' + match.group(1) + '"')
        state = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        logger.exception("Failed to parse PRERENDERED_STATE")
        return []

    listing = state.get("listing")
    if not listing or not listing.get("listing"):
        return []

    return listing["listing"].get("ads", [])


async def fetch_page(city_slug: str, category_path: str, page: int) -> list[dict]:
    url = BASE_URL.format(category=category_path, city=city_slug)
    if page > 1:
        url = f"{url}?page={page}"

    html = await _curl_get(url)
    if html is None:
        return []

    return _extract_ads(html)


async def fetch_listings(city_slug: str, category_path: str, pages: int) -> list[dict]:
    ads: list[dict] = []
    seen_ids: set[int] = set()

    for page in range(1, pages + 1):
        page_ads = await fetch_page(city_slug, category_path, page)
        if not page_ads:
            break
        for ad in page_ads:
            if ad["id"] not in seen_ids:
                seen_ids.add(ad["id"])
                ads.append(ad)

    return ads

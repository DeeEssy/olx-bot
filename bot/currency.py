import asyncio
import logging

from curl_cffi import requests as curl_requests

logger = logging.getLogger("olx-bot")

NBU_USD_RATE_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"


def _fetch_usd_rate_sync() -> float | None:
    try:
        resp = curl_requests.get(NBU_USD_RATE_URL, timeout=15)
        data = resp.json()
        return float(data[0]["rate"])
    except Exception:
        logger.exception("Failed to fetch USD/UAH rate from NBU")
        return None


async def fetch_usd_rate() -> float | None:
    return await asyncio.to_thread(_fetch_usd_rate_sync)

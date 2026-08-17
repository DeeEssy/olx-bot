import os
import sqlite3
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notified_ads (
    ad_id INTEGER PRIMARY KEY,
    notified_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def is_notified(self, ad_id: int) -> bool:
        cur = self._conn.execute("SELECT 1 FROM notified_ads WHERE ad_id = ?", (ad_id,))
        return cur.fetchone() is not None

    def mark_notified(self, ad_id: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO notified_ads (ad_id, notified_at) VALUES (?, ?)",
            (ad_id, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

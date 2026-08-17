import os
import sqlite3
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notified_ads (
    feed_key TEXT NOT NULL,
    ad_id INTEGER NOT NULL,
    notified_at TEXT NOT NULL,
    PRIMARY KEY (feed_key, ad_id)
);
"""


class Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._migrate()
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def _migrate(self) -> None:
        cur = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='notified_ads'"
        )
        if cur.fetchone() is None:
            return  # fresh DB, _SCHEMA will create the current layout

        columns = {row[1] for row in self._conn.execute("PRAGMA table_info(notified_ads)")}
        if "feed_key" in columns:
            return  # already current

        # Pre-multi-feed DB: every existing row was from the original
        # rental-only bot, so backfill feed_key='rental' during migration.
        self._conn.execute("ALTER TABLE notified_ads RENAME TO notified_ads_old")
        self._conn.execute(_SCHEMA)
        self._conn.execute(
            "INSERT INTO notified_ads (feed_key, ad_id, notified_at) "
            "SELECT 'rental', ad_id, notified_at FROM notified_ads_old"
        )
        self._conn.execute("DROP TABLE notified_ads_old")
        self._conn.commit()

    def is_notified(self, feed_key: str, ad_id: int) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM notified_ads WHERE feed_key = ? AND ad_id = ?", (feed_key, ad_id)
        )
        return cur.fetchone() is not None

    def mark_notified(self, feed_key: str, ad_id: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO notified_ads (feed_key, ad_id, notified_at) VALUES (?, ?, ?)",
            (feed_key, ad_id, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

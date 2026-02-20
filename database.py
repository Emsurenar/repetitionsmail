"""
SQLite database for tracking sent topics.
Prevents repetition and enables progressive deepening.
"""

import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
import config

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sent_topics (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    category   TEXT    NOT NULL,   -- 'math', 'philosophy', 'society'
    topic      TEXT    NOT NULL,   -- e.g. "Spektralsatsen"
    sent_at    TEXT    NOT NULL    -- ISO-8601
);

CREATE INDEX IF NOT EXISTS idx_category ON sent_topics(category);
CREATE INDEX IF NOT EXISTS idx_sent_at  ON sent_topics(sent_at);
"""


class TopicDatabase:
    def __init__(self, db_path: Path = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)
        logger.info(f"Database ready at {self.db_path}")

    def get_recent_topics(self, category: str, days: int = 60) -> List[str]:
        """Return topics used in the last `days` days for a given category."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT topic FROM sent_topics WHERE category = ? AND sent_at >= ? ORDER BY sent_at DESC",
                (category, cutoff)
            ).fetchall()
        topics = [row['topic'] for row in rows]
        logger.info(f"[{category}] {len(topics)} recent topics in last {days} days")
        return topics

    def log_topic(self, category: str, topic: str):
        """Record that a topic was used today."""
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sent_topics (category, topic, sent_at) VALUES (?, ?, ?)",
                (category, topic, now)
            )
        logger.info(f"[{category}] Logged topic: {topic!r}")

    def get_all(self, category: Optional[str] = None) -> List[dict]:
        """Fetch all records, optionally filtered by category."""
        with self._connect() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM sent_topics WHERE category = ? ORDER BY sent_at DESC", (category,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM sent_topics ORDER BY sent_at DESC"
                ).fetchall()
        return [dict(r) for r in rows]


if __name__ == '__main__':
    import json
    db = TopicDatabase()
    # Self-test
    db.log_topic('math', 'Spektralsatsen – Test')
    db.log_topic('philosophy', 'Gödels ofullständighetssats – Test')
    db.log_topic('society', 'Nash-jämvikt – Test')
    print("All records:")
    print(json.dumps(db.get_all(), indent=2, ensure_ascii=False))
    print("Recent math topics:", db.get_recent_topics('math'))

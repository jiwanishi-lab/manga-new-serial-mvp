import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("manga_watch.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = connect()
    con.execute("""
    CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        platform TEXT NOT NULL,
        url TEXT,
        source TEXT,
        detected_at TEXT NOT NULL,
        UNIQUE(title, platform)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS weekly_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id INTEGER NOT NULL,
        week_start TEXT NOT NULL,
        mention_count INTEGER DEFAULT 0,
        buzz_score REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        UNIQUE(work_id, week_start),
        FOREIGN KEY(work_id) REFERENCES works(id)
    )
    """)
    con.commit()
    con.close()

def upsert_work(title: str, platform: str, url: str | None, source: str):
    now = datetime.now(timezone.utc).isoformat()
    con = connect()
    con.execute("""
    INSERT OR IGNORE INTO works(title, platform, url, source, detected_at)
    VALUES (?, ?, ?, ?, ?)
    """, (title, platform, url, source, now))
    con.commit()
    con.close()

def list_recent_works(limit: int = 20):
    con = connect()
    rows = con.execute("""
    SELECT * FROM works
    ORDER BY detected_at DESC
    LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return rows

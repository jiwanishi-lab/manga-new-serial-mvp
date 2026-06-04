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
        start_date TEXT,
        detected_at TEXT NOT NULL,
        UNIQUE(title, platform)
    )
    """)

    # 古いDB向け：start_date列がなければ追加
    try:
        con.execute("ALTER TABLE works ADD COLUMN start_date TEXT")
    except sqlite3.OperationalError:
        pass

    con.commit()
    con.close()

def upsert_work(title, platform, url, source, start_date=None):
    now = datetime.now(timezone.utc).isoformat()
    con = connect()

    con.execute("""
    INSERT INTO works(title, platform, url, source, start_date, detected_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(title, platform) DO UPDATE SET
        url = excluded.url,
        source = excluded.source,
        start_date = excluded.start_date
    """, (title, platform, url, source, start_date, now))

    con.commit()
    con.close()

def list_recent_works(limit=20):
    con = connect()
    rows = con.execute("""
    SELECT * FROM works
    ORDER BY detected_at DESC
    LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return rows

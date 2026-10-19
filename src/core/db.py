import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lang TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    hint TEXT DEFAULT '',
    audio TEXT DEFAULT '',
    image TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    ease REAL DEFAULT 2.5,
    interval INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    due TEXT DEFAULT '',
    last_reviewed TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT NOT NULL,
    deck_id INTEGER,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    cards_reviewed INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS daily_stats (
    date TEXT NOT NULL,
    lang TEXT NOT NULL,
    minutes REAL DEFAULT 0,
    cards INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    PRIMARY KEY (date, lang)
);
"""


def connect(db_path):
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

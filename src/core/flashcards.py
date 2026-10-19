import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Card:
    id: Optional[int]
    deck_id: int
    front: str
    back: str
    hint: str = ""
    audio: str = ""
    image: str = ""
    tags: str = ""
    ease: float = 2.5
    interval: int = 0
    repetitions: int = 0
    due: str = ""
    last_reviewed: str = ""


def _today():
    return datetime.date.today().isoformat()


def _add_days(days):
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()


class FlashCardEngine:
    def __init__(self, conn):
        self.conn = conn

    def create_deck(self, name, lang, description=""):
        cur = self.conn.execute(
            "INSERT INTO decks (name, lang, description, created_at) VALUES (?,?,?,?)",
            (name, lang, description, datetime.datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_decks(self, lang=None):
        if lang is None:
            rows = self.conn.execute("SELECT * FROM decks ORDER BY id").fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM decks WHERE lang=? ORDER BY id", (lang,)).fetchall()
        return [dict(r) for r in rows]

    def delete_deck(self, deck_id):
        self.conn.execute("DELETE FROM decks WHERE id=?", (deck_id,))
        self.conn.commit()

    def add_card(self, deck_id, front, back, hint="", audio="", image="", tags=""):
        cur = self.conn.execute(
            """INSERT INTO cards (deck_id, front, back, hint, audio, image, tags, due, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (deck_id, front, back, hint, audio, image, tags, _today(), datetime.datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_card(self, card_id):
        r = self.conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        return dict(r) if r else None

    def list_cards(self, deck_id):
        rows = self.conn.execute("SELECT * FROM cards WHERE deck_id=? ORDER BY id", (deck_id,)).fetchall()
        return [dict(r) for r in rows]

    def delete_card(self, card_id):
        self.conn.execute("DELETE FROM cards WHERE id=?", (card_id,))
        self.conn.commit()

    def due_cards(self, deck_id, limit=50):
        rows = self.conn.execute(
            "SELECT * FROM cards WHERE deck_id=? AND (due='' OR due<=?) ORDER BY due, id LIMIT ?",
            (deck_id, _today(), limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def review(self, card_id, quality):
        if quality < 0 or quality > 5:
            raise ValueError("quality must be 0..5")
        row = self.conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        if row is None:
            raise KeyError(f"card {card_id} not found")
        ease = float(row["ease"])
        interval = int(row["interval"])
        reps = int(row["repetitions"])
        if quality < 3:
            reps = 0
            interval = 1
        else:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = max(1, round(interval * ease))
            reps += 1
        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ease < 1.3:
            ease = 1.3
        due = _add_days(interval)
        now = datetime.datetime.now().isoformat()
        self.conn.execute(
            """UPDATE cards SET ease=?, interval=?, repetitions=?, due=?, last_reviewed=? WHERE id=?""",
            (ease, interval, reps, due, now, card_id),
        )
        self.conn.commit()
        return {"ease": ease, "interval": interval, "repetitions": reps, "due": due}

    def cards_count(self, deck_id):
        r = self.conn.execute("SELECT COUNT(*) AS c FROM cards WHERE deck_id=?", (deck_id,)).fetchone()
        return int(r["c"])

    def mastered_count(self, deck_id, min_interval=21):
        r = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE deck_id=? AND interval>=?", (deck_id, min_interval)
        ).fetchone()
        return int(r["c"])

import datetime
from typing import Optional


class ProgressTracker:
    def __init__(self, conn):
        self.conn = conn

    def start_session(self, lang, deck_id=None):
        cur = self.conn.execute(
            "INSERT INTO sessions (lang, deck_id, started_at) VALUES (?,?,?)",
            (lang, deck_id, datetime.datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def end_session(self, session_id, cards_reviewed=0, correct_count=0):
        self.conn.execute(
            "UPDATE sessions SET ended_at=?, cards_reviewed=?, correct_count=? WHERE id=?",
            (datetime.datetime.now().isoformat(), cards_reviewed, correct_count, session_id),
        )
        self.conn.commit()

    def record_review(self, lang, correct, minutes=0.0):
        today = datetime.date.today().isoformat()
        row = self.conn.execute(
            "SELECT * FROM daily_stats WHERE date=? AND lang=?", (today, lang)
        ).fetchone()
        if row is None:
            self.conn.execute(
                "INSERT INTO daily_stats (date, lang, minutes, cards, correct) VALUES (?,?,?,?,?)",
                (today, lang, minutes, 1, 1 if correct else 0),
            )
        else:
            self.conn.execute(
                """UPDATE daily_stats SET minutes=minutes+?, cards=cards+1,
                   correct=correct+? WHERE date=? AND lang=?""",
                (minutes, 1 if correct else 0, today, lang),
            )
        self.conn.commit()

    def daily(self, lang=None, days=30):
        cutoff = (datetime.date.today() - datetime.timedelta(days=days - 1)).isoformat()
        if lang is None:
            rows = self.conn.execute(
                "SELECT * FROM daily_stats WHERE date>=? ORDER BY date", (cutoff,)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM daily_stats WHERE lang=? AND date>=? ORDER BY date", (lang, cutoff)
            ).fetchall()
        return [dict(r) for r in rows]

    def total_cards(self, lang=None):
        if lang is None:
            r = self.conn.execute("SELECT COALESCE(SUM(cards),0) AS c FROM daily_stats").fetchone()
        else:
            r = self.conn.execute(
                "SELECT COALESCE(SUM(cards),0) AS c FROM daily_stats WHERE lang=?", (lang,)
            ).fetchone()
        return int(r["c"])

    def streak(self, lang=None):
        rows = self.daily(lang=lang, days=365)
        dates = sorted({r["date"] for r in rows if r["cards"] > 0})
        if not dates:
            return 0
        today = datetime.date.today()
        streak = 0
        cur = today
        date_set = set(dates)
        while cur.isoformat() in date_set:
            streak += 1
            cur = cur - datetime.timedelta(days=1)
        return streak

    def mastery(self, engine, deck_id):
        total = engine.cards_count(deck_id)
        mastered = engine.mastered_count(deck_id)
        pct = (mastered / total * 100.0) if total else 0.0
        return {"total": total, "mastered": mastered, "percent": round(pct, 1)}

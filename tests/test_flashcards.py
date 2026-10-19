import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from core.db import connect
from core.flashcards import FlashCardEngine
from core.progress import ProgressTracker
from core.seed import load_deck_from_json


def test_deck_and_cards():
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(db)
    conn = connect(db)
    eng = FlashCardEngine(conn)
    did = eng.create_deck("Hiragana", "ja")
    cid = eng.add_card(did, "あ", "a")
    assert eng.cards_count(did) == 1
    assert eng.get_card(cid)["front"] == "あ"
    conn.close()
    os.remove(db)


def test_sm2_review():
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(db)
    conn = connect(db)
    eng = FlashCardEngine(conn)
    did = eng.create_deck("Hiragana", "ja")
    cid = eng.add_card(did, "あ", "a")
    r = eng.review(cid, 5)
    assert r["repetitions"] == 1
    assert r["interval"] == 1
    r2 = eng.review(cid, 5)
    assert r2["repetitions"] == 2
    assert r2["interval"] == 6
    conn.close()
    os.remove(db)


def test_due_cards_and_mastery():
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(db)
    conn = connect(db)
    eng = FlashCardEngine(conn)
    load_deck_from_json(eng, "ja", os.path.join(ROOT, "lang", "ja", "hiragana.json"))
    deck_id = eng.list_decks("ja")[0]["id"]
    assert eng.cards_count(deck_id) == 46
    due = eng.due_cards(deck_id)
    assert len(due) == 46
    conn.close()
    os.remove(db)


def test_progress_streak():
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(db)
    conn = connect(db)
    pt = ProgressTracker(conn)
    pt.record_review("ja", True)
    pt.record_review("ja", False)
    assert pt.total_cards("ja") == 2
    assert pt.streak("ja") == 1
    conn.close()
    os.remove(db)

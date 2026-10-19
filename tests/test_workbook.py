import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from core.db import connect
from core.flashcards import FlashCardEngine
from core.seed import load_deck_from_json
from core.workbook import WorkbookEngine


def test_workbook_drill():
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(db)
    conn = connect(db)
    eng = FlashCardEngine(conn)
    load_deck_from_json(eng, "ja", os.path.join(ROOT, "lang", "ja", "hiragana.json"))
    deck_id = eng.list_decks("ja")[0]["id"]
    wb = WorkbookEngine(eng)
    drill = wb.make_drill(deck_id, count=5)
    assert len(drill) == 5
    assert wb.check(drill[0]["answer"], drill[0]["answer"]) is True
    assert wb.check("wrong", drill[0]["answer"]) is False
    s = wb.score([True, False, True])
    assert s["correct"] == 2 and s["total"] == 3
    conn.close()
    os.remove(db)

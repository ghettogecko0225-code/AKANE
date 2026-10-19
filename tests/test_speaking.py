import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from core.speaking import normalize_japanese, score_pronunciation, levenshtein


def test_normalize():
    assert normalize_japanese("こんにちは、世界！") == "こんにちは世界"


def test_score_perfect():
    r = score_pronunciation("こんにちは", "こんにちは")
    assert r["accuracy"] == 100.0


def test_score_partial():
    r = score_pronunciation("こんにちは", "こんにちわ")
    assert r["accuracy"] < 100.0 and r["accuracy"] > 0


def test_levenshtein():
    assert levenshtein("abc", "abc") == 0
    assert levenshtein("abc", "axc") == 1

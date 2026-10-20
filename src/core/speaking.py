import json
import os

_reading_maps = {}


def build_reading_map(root):
    """Map kanji words to their hiragana reading using the bundled JLPT data.

    Lets us compare a target written in kanji against speech recognised
    in hiragana (or vice versa) fairly.
    """
    key = str(root)
    if key in _reading_maps:
        return _reading_maps[key]
    mapping = {}
    base = os.path.join(str(root), "assets", "jlpt", "vocab")
    for level in ("n5", "n4", "n3", "n2", "n1"):
        path = os.path.join(base, f"{level}.json")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for entry in data:
            word = entry.get("word") or ""
            reading = entry.get("reading") or ""
            if word and reading and word != reading:
                mapping[word] = reading
    _reading_maps[key] = mapping
    return mapping


def to_kana(text, mapping):
    """Replace known kanji words with their readings (longest match first)."""
    if not text or not mapping:
        return text
    keys = sorted(mapping.keys(), key=len, reverse=True)
    out = text
    for word in keys:
        if word in out:
            out = out.replace(word, mapping[word])
    return out


def normalize_japanese(text):
    if not text:
        return ""
    out = []
    for ch in text:
        if ch.isspace():
            continue
        if ch in "、。！？・「」『』（）()":
            continue
        out.append(ch)
    return "".join(out)

def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


def score_pronunciation(target, heard, reading_map=None):
    t = normalize_japanese(target)
    h = normalize_japanese(heard)
    if reading_map:
        t = normalize_japanese(to_kana(t, reading_map))
        h = normalize_japanese(to_kana(h, reading_map))
    if not t:
        return {"accuracy": 0.0, "distance": 0, "target": t, "heard": h}
    dist = levenshtein(t, h)
    acc = max(0.0, (1 - dist / max(len(t), len(h), 1)) * 100.0)
    return {"accuracy": round(acc, 1), "distance": dist, "target": t, "heard": h}

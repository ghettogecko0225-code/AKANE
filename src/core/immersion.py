import json
import os
import random


def load_passages(root):
    path = os.path.join(root, "assets", "immersion", "passages.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _vocab_dir(root):
    packaged = os.path.join(root, "assets", "jlpt", "vocab")
    if os.path.isdir(packaged):
        return packaged
    return os.path.join(root, "assets", "openjlpt", "data", "json", "vocab")


def listening_items(root, level=None, count=10):
    base = _vocab_dir(root)
    items = []
    levels = [level.lower()] if level else ["n5", "n4", "n3", "n2", "n1"]
    for lvl in levels:
        path = os.path.join(base, f"{lvl}.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for w in data:
            for ex in (w.get("examples") or []):
                ja = (ex.get("ja") or "").strip()
                en = (ex.get("en") or "").strip()
                if ja and en:
                    items.append({"ja": ja, "en": en, "level": lvl.upper()})
    if not items:
        return []
    random.shuffle(items)
    return items[:count]

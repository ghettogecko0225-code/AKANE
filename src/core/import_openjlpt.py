import json
import os


LEVELS = ["n5", "n4", "n3", "n2", "n1"]


def _data_dir(root):
    return os.path.join(root, "assets", "openjlpt", "data", "json")


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def import_level(engine, root, level):
    base = _data_dir(root)
    lvl = level.lower()
    existing = {d["name"] for d in engine.list_decks()}
    created = []

    vocab_path = os.path.join(base, "vocab", f"{lvl}.json")
    if os.path.exists(vocab_path):
        name = f"Vocab {level.upper()}"
        if name not in existing:
            did = engine.create_deck(name, "ja", f"OpenJLPT {level.upper()} vocabulary")
            for w in _load_json(vocab_path):
                front = w["word"]
                back = f"{w['reading']}  —  " + ", ".join(w.get("meanings", []))
                hint = ""
                ex = (w.get("examples") or [])
                if ex:
                    e = ex[0]
                    hint = f"{e.get('ja','')}  =>  {e.get('en','')}"
                engine.add_card(did, front, back, hint=hint, tags=",".join(w.get("pos", [])))
            created.append(name)

    kanji_path = os.path.join(base, "kanji", f"{lvl}.json")
    if os.path.exists(kanji_path):
        name = f"Kanji {level.upper()}"
        if name not in existing:
            did = engine.create_deck(name, "ja", f"OpenJLPT {level.upper()} kanji")
            for k in _load_json(kanji_path):
                front = k["character"]
                meanings = ", ".join(k.get("meanings", []))
                ony = ", ".join(k.get("onyomi", []))
                kuny = ", ".join(k.get("kunyomi", []))
                back = f"{meanings}  |  on: {ony}  kun: {kuny}"
                engine.add_card(did, front, back, hint=f"strokes: {k.get('strokes','')}")
            created.append(name)

    grammar_path = os.path.join(base, "grammar", f"{lvl}.json")
    if os.path.exists(grammar_path):
        name = f"Grammar {level.upper()}"
        if name not in existing:
            did = engine.create_deck(name, "ja", f"OpenJLPT {level.upper()} grammar")
            for g in _load_json(grammar_path):
                front = g["pattern"]
                back = f"{g.get('meaning','')}  |  {g.get('formation','')}"
                hint = ""
                ex = (g.get("examples") or [])
                if ex:
                    e = ex[0]
                    hint = f"{e.get('ja','')}  =>  {e.get('en','')}"
                engine.add_card(did, front, back, hint=hint, tags=",".join(g.get("tags", [])))
            created.append(name)

    return created


def import_all(engine, root):
    out = []
    for lvl in LEVELS:
        out.extend(import_level(engine, root, lvl))
    return out

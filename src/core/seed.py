import json
import os


def load_deck_from_json(engine, lang, path, deck_name=None):
    with open(path, encoding="utf-8") as f:
        cards = json.load(f)
    name = deck_name or os.path.splitext(os.path.basename(path))[0]
    deck_id = engine.create_deck(name, lang, f"Seed deck from {os.path.basename(path)}")
    for c in cards:
        engine.add_card(deck_id, c["front"], c["back"], hint=c.get("hint", ""), tags=c.get("tags", ""))
    return deck_id

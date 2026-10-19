import random


class WorkbookEngine:
    def __init__(self, engine):
        self.engine = engine

    def make_drill(self, deck_id, count=10):
        cards = self.engine.list_cards(deck_id)
        if not cards:
            return []
        pool = list(cards)
        random.shuffle(pool)
        chosen = pool[: min(count, len(pool))]
        return [{"card_id": c["id"], "prompt": c["front"], "answer": c["back"]} for c in chosen]

    @staticmethod
    def check(user_answer, correct):
        u = (user_answer or "").strip().lower()
        c = (correct or "").strip().lower()
        return u == c

    @staticmethod
    def score(results):
        total = len(results)
        correct = sum(1 for r in results if r)
        pct = (correct / total * 100.0) if total else 0.0
        return {"total": total, "correct": correct, "percent": round(pct, 1)}

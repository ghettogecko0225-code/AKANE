import datetime


class StudyConfig:
    def __init__(self, new_per_day=20, review_per_day=100):
        self.new_per_day = new_per_day
        self.review_per_day = review_per_day


class Scheduler:
    def __init__(self, engine, config=None):
        self.engine = engine
        self.config = config or StudyConfig()

    def due_today(self, deck_id, limit=None):
        limit = limit if limit is not None else self.config.review_per_day
        return self.engine.due_cards(deck_id, limit=limit)

    def forecast(self, deck_id, days=7):
        # count cards due on each of the next `days` days
        result = []
        cards = self.engine.list_cards(deck_id)
        today = datetime.date.today()
        for i in range(days):
            d = (today + datetime.timedelta(days=i)).isoformat()
            cnt = 0
            for c in cards:
                due = c.get("due") or ""
                if due and due <= d and (i == 0 or due > (today + datetime.timedelta(days=i - 1)).isoformat()):
                    # approximate: count cards whose due date falls on this day
                    pass
            # simpler: count by exact due date
            cnt = sum(1 for c in cards if (c.get("due") or "") == d or (i == 0 and (not c.get("due") or c.get("due") <= d)))
            # refine: for day 0 include overdue
            if i == 0:
                cnt = sum(1 for c in cards if not c.get("due") or c.get("due") <= d)
            else:
                cnt = sum(1 for c in cards if c.get("due") == d)
            result.append({"date": d, "count": cnt})
        return result

    def new_cards(self, deck_id, limit=None):
        limit = limit if limit is not None else self.new_per_day
        cards = self.engine.list_cards(deck_id)
        new = [c for c in cards if (c.get("repetitions") or 0) == 0]
        return new[:limit]

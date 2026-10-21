"""Daily study plan.

Turns the decks + the spaced repetition state into "what to do today":
how many cards are due, how many new ones to introduce, and a ready-to-run
session of cards mixed from the active decks.
"""
import datetime

from core.settings import load


def active_decks(engine, root, lang=None):
    """Deck ids the user studies. Empty selection means every deck."""
    settings = load(root)
    chosen = settings.get("active_decks") or []
    decks = engine.list_decks(lang)
    if not chosen:
        return [d["id"] for d in decks]
    names = set(chosen)
    return [d["id"] for d in decks if d["name"] in names or str(d["id"]) in names]


def counts(engine, root, deck_ids=None, lang=None):
    """Due / new / total card counts for the active decks."""
    if deck_ids is None:
        deck_ids = active_decks(engine, root, lang)
    today = datetime.date.today().isoformat()
    due = 0
    new = 0
    total = 0
    for deck_id in deck_ids:
        for card in engine.list_cards(deck_id):
            total += 1
            reps = card.get("repetitions") or 0
            if reps == 0:
                new += 1
            else:
                due_date = card.get("due") or ""
                if not due_date or due_date <= today:
                    due += 1
    return {"due": due, "new": new, "total": total, "decks": len(deck_ids)}


def plan(engine, root, deck_ids=None, lang=None):
    """The plan for today, respecting the user's daily limits."""
    settings = load(root)
    c = counts(engine, root, deck_ids, lang)
    new_limit = int(settings.get("new_per_day", 15) or 0)
    review_limit = int(settings.get("review_per_day", 100) or 0)
    goal = int(settings.get("daily_goal", 30) or 0)
    new_cards = min(c["new"], new_limit)
    reviews = min(c["due"], review_limit)
    planned = new_cards + reviews
    if goal:
        planned = min(planned, goal)
    return {
        "due": c["due"],
        "new": c["new"],
        "total": c["total"],
        "decks": c["decks"],
        "new_today": new_cards,
        "reviews_today": reviews,
        "planned": planned,
        "goal": goal,
        "done_today": reviewed_today(engine, root, lang),
    }


def reviewed_today(engine, root, lang=None):
    today = datetime.date.today().isoformat()
    rows = engine.conn.execute(
        "SELECT COALESCE(SUM(cards), 0) FROM daily_stats WHERE date=?", (today,)
    ).fetchone()
    return int(rows[0] or 0)


def build_session(engine, root, deck_ids=None, lang=None, limit=None):
    """Cards to study now: new cards first, then the ones that are due."""
    if deck_ids is None:
        deck_ids = active_decks(engine, root, lang)
    settings = load(root)
    new_limit = int(settings.get("new_per_day", 15) or 0)
    review_limit = int(settings.get("review_per_day", 100) or 0)
    today = datetime.date.today().isoformat()

    fresh = []
    due = []
    for deck_id in deck_ids:
        for card in engine.list_cards(deck_id):
            reps = card.get("repetitions") or 0
            if reps == 0:
                fresh.append(card)
            else:
                due_date = card.get("due") or ""
                if not due_date or due_date <= today:
                    due.append(card)

    fresh = fresh[:new_limit]
    due = due[:review_limit]
    session = fresh + due
    if limit:
        session = session[:limit]
    return session


def next_level_hint(engine, root, lang=None):
    """A friendly pointer: which level has the most unmastered cards."""
    best = None
    for deck in engine.list_decks(lang):
        if not deck["name"].startswith("Vocab"):
            continue
        count = engine.cards_count(deck["id"])
        if count and (best is None or count < best[1]):
            best = (deck["name"], count)
    if not best:
        return ""
    return f"Start with {best[0]} ({best[1]} cards)"

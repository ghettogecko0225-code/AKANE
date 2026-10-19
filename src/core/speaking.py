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


def score_pronunciation(target, heard):
    t = normalize_japanese(target)
    h = normalize_japanese(heard)
    if not t:
        return {"accuracy": 0.0, "distance": 0, "target": t, "heard": h}
    dist = levenshtein(t, h)
    acc = max(0.0, (1 - dist / max(len(t), len(h), 1)) * 100.0)
    return {"accuracy": round(acc, 1), "distance": dist, "target": t, "heard": h}

"""User settings shared by the desktop and phone apps.

Stored as JSON next to the app data so it survives app updates.
"""
import json
import os
from pathlib import Path

DEFAULTS = {
    "daily_goal": 30,
    "new_per_day": 15,
    "review_per_day": 100,
    "theme": "dark",
    "auto_speak": True,
    "show_hints": True,
    "active_decks": [],
    "daily_start_hour": 0,
}

_cache = {}


def settings_path(root):
    return Path(root) / "data" / "settings.json"


def load(root):
    key = str(root)
    if key in _cache:
        return _cache[key]
    values = dict(DEFAULTS)
    path = settings_path(root)
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                for k, v in stored.items():
                    if k in DEFAULTS:
                        values[k] = v
    except Exception:
        pass
    _cache[key] = values
    return values


def save(root, values):
    key = str(root)
    current = dict(DEFAULTS)
    try:
        current.update(load(root))
    except Exception:
        pass
    for k, v in (values or {}).items():
        if k in DEFAULTS:
            current[k] = v
    _cache[key] = current
    path = settings_path(root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception:
        pass
    return current


def get(root, name, fallback=None):
    values = load(root)
    if name in values:
        return values[name]
    return DEFAULTS.get(name, fallback)


def set_value(root, name, value):
    return save(root, {name: value})

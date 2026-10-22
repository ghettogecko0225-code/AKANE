import os
import sys
from pathlib import Path


def is_frozen():
    return getattr(sys, "frozen", False)


def resource_root():
    """Read-only root for bundled data (lang/, assets/, config.yaml).

    Frozen: PyInstaller puts them in the _internal folder next to the exe.
    Source: the project root.
    """
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def data_root():
    """Writable root for the database and user data.

    Frozen: the folder containing the exe, so the app can write next to
    itself (install folder) instead of inside the temp extraction dir.
    Source: the project root.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def models_root():
    """Root for heavyweight model files (piper voices, translation models)."""
    env = os.environ.get("AKANE_MODELS") or os.environ.get("SENSEI_MODELS")
    if env:
        return Path(env)
    if is_frozen():
        return data_root() / "models"
    studio = Path(r"C:\Users\Universe\Desktop\Hive Pulse Interactive\VIKI\Studio")
    return studio / "models"

"""Offline audio pack playback.

The pack is pre-rendered Japanese audio (see tools/build_audio_pack.py) so
the app can speak correct Japanese on any device, even when the phone has
no Japanese TTS voice installed.

Backend:
  Android -> android.media.MediaPlayer via pyjnius
  Desktop  -> soundfile + sounddevice
"""
import json
import os
import threading
from pathlib import Path


def manifest_path(root):
    return Path(root) / "assets" / "audio" / "manifest.json"


def load_manifest(root):
    path = manifest_path(root)
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def find(root, text):
    manifest = load_manifest(root)
    if not manifest:
        return None
    key = (text or "").strip()
    if not key:
        return None
    if key in manifest:
        return manifest[key]
    normalized = "".join(ch for ch in key if not ch.isspace())
    for text_key, path in manifest.items():
        if "".join(ch for ch in text_key if not ch.isspace()) == normalized:
            return path
    return None


def clip_path(root, rel_path):
    return Path(root) / "assets" / rel_path


class AudioPlayer:
    """Thread-safe one-shot player. Never blocks the UI."""

    def __init__(self, root):
        self.root = str(root)
        self._lock = threading.Lock()
        self._playing = False
        self._android = None
        self._stop = threading.Event()
        try:
            from jnius import autoclass
            self._android = autoclass
        except Exception:
            self._android = None

    @property
    def playing(self):
        return self._playing

    def play(self, text):
        rel = find(self.root, text)
        if not rel:
            return False
        path = clip_path(self.root, rel)
        if not path.exists():
            return False
        with self._lock:
            if self._playing:
                return False
            self._playing = True
        threading.Thread(target=self._worker, args=(str(path),), daemon=True).start()
        return True

    def _worker(self, path):
        try:
            if self._android is not None:
                self._play_android(path)
            else:
                self._play_desktop(path)
        except Exception:
            pass
        finally:
            with self._lock:
                self._playing = False

    def _play_android(self, path):
        import time

        from jnius import autoclass
        MediaPlayer = autoclass("android.media.MediaPlayer")
        player = MediaPlayer()
        player.setDataSource(path)
        player.prepare()
        player.start()
        try:
            while player.isPlaying():
                time.sleep(0.05)
        finally:
            player.release()

    def _play_desktop(self, path):
        import numpy as np
        import soundfile as sf
        import sounddevice as sd
        data, rate = sf.read(path, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        sd.play(data, rate)
        sd.wait()

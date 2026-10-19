import threading
import tempfile
import time
import pathlib

from PyQt6.QtCore import QObject, pyqtSignal

from core.voice import synthesize_to_wav, play_wav


class Speaker(QObject):
    started = pyqtSignal()
    done = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.playing = False
        self._stop = threading.Event()
        self._lock = threading.Lock()

    def say(self, text):
        text = (text or "").strip()
        if not text or self.playing:
            return
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def stop(self):
        self._stop.set()

    def _worker(self, text):
        with self._lock:
            if self.playing:
                return
            self.playing = True
        self._stop.clear()
        self.started.emit()
        try:
            d = pathlib.Path(tempfile.gettempdir()) / "sensei_tts"
            d.mkdir(exist_ok=True)
            out = d / f"utt_{int(time.time() * 1000)}.wav"
            synthesize_to_wav(text, out)
            play_wav(str(out))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.playing = False
            self.done.emit()

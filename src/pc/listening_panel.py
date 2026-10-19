import os
import tempfile
import threading

import numpy as np
import sounddevice as sd
import wave

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QTextEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal

from core.voice import synthesize_to_wav
from core.immersion import listening_items


class PlayThread(QThread):
    done = pyqtSignal()

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            with wave.open(self.path, "rb") as wf:
                rate = wf.getframerate()
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            stream = sd.OutputStream(samplerate=rate, channels=1, dtype="int16")
            stream.start()
            for i in range(0, len(data), 4096):
                stream.write(data[i:i + 4096].reshape(-1, 1))
            stream.stop()
            stream.close()
        except Exception:
            pass
        self.done.emit()


class ListeningPanel(QWidget):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.items = []
        self.current = None
        self.wav_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Listening Drill (type what you hear)"))

        row = QHBoxLayout()
        self.level_combo = QComboBox()
        for lvl in ["N5", "N4", "N3", "N2", "N1"]:
            self.level_combo.addItem(lvl)
        row.addWidget(self.level_combo)
        self.new_btn = QPushButton("New Sentence")
        self.new_btn.clicked.connect(self.new_sentence)
        row.addWidget(self.new_btn)
        layout.addLayout(row)

        self.play_btn = QPushButton("Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.play)
        layout.addWidget(self.play_btn)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type what you heard...")
        layout.addWidget(self.input)

        self.check_btn = QPushButton("Check")
        self.check_btn.clicked.connect(self.check)
        layout.addWidget(self.check_btn)

        self.result = QLabel("")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

        self.answer_reveal = QTextEdit()
        self.answer_reveal.setReadOnly(True)
        self.answer_reveal.hide()
        layout.addWidget(self.answer_reveal)

        self._play_thread = None
        self.new_sentence()

    def new_sentence(self):
        lvl = self.level_combo.currentText()
        self.items = listening_items(str(self.root), lvl, count=20)
        if not self.items:
            self.result.setText("No sentences available")
            return
        import random
        self.current = random.choice(self.items)
        self.input.clear()
        self.result.setText("Press Play, then type what you hear.")
        self.answer_reveal.hide()
        self.answer_reveal.clear()
        try:
            d = tempfile.mkdtemp()
            self.wav_path = os.path.join(d, "listen.wav")
            synthesize_to_wav(self.current["ja"], self.wav_path)
            self.play_btn.setEnabled(True)
        except Exception as e:
            self.result.setText(f"TTS error: {e}")
            self.play_btn.setEnabled(False)

    def play(self):
        if not self.wav_path or not os.path.exists(self.wav_path):
            return
        self.play_btn.setEnabled(False)
        self._play_thread = PlayThread(self.wav_path)
        self._play_thread.done.connect(lambda: self.play_btn.setEnabled(True))
        self._play_thread.start()

    def check(self):
        if self.current is None:
            return
        u = self.input.text().strip()
        c = self.current["ja"].strip()
        # loose compare: remove spaces/punctuation
        def norm(s):
            return "".join(ch for ch in s if ch not in " 　、。！？")
        ok = norm(u) == norm(c)
        self.result.setText("Correct!" if ok else "Not quite.")
        self.answer_reveal.setPlainText(f"Original: {c}\nMeaning: {self.current['en']}")
        self.answer_reveal.show()

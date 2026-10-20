import os
import tempfile

import numpy as np
import sounddevice as sd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QLineEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal

from core.voice import transcribe_samples
from core.immersion import listening_items
from core.speaking import score_pronunciation, build_reading_map


class RecordThread(QThread):
    result = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, seconds=5.0):
        super().__init__()
        self.seconds = seconds

    def run(self):
        try:
            rate = 16000
            rec = sd.rec(int(self.seconds * rate), samplerate=rate, channels=1, dtype="float32")
            sd.wait()
            samples = rec[:, 0]
            text = transcribe_samples(samples, self.root)
            self.result.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class SpeakingPanel(QWidget):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.current = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Speaking Practice (pronunciation scoring)"))

        row = QHBoxLayout()
        self.level_combo = QComboBox()
        for lvl in ["N5", "N4", "N3", "N2", "N1"]:
            self.level_combo.addItem(lvl)
        row.addWidget(self.level_combo)
        self.new_btn = QPushButton("New Sentence")
        self.new_btn.clicked.connect(self.new_sentence)
        row.addWidget(self.new_btn)
        layout.addLayout(row)

        self.target_label = QLabel("Press New Sentence")
        self.target_label.setStyleSheet("font-size: 24px;")
        self.target_label.setWordWrap(True)
        layout.addWidget(self.target_label)

        self.meaning_label = QLabel("")
        self.meaning_label.setWordWrap(True)
        layout.addWidget(self.meaning_label)

        self.record_btn = QPushButton("Record (5s)")
        self.record_btn.setEnabled(False)
        self.record_btn.clicked.connect(self.record)
        layout.addWidget(self.record_btn)

        self.heard_label = QLabel("You said: (none)")
        self.heard_label.setWordWrap(True)
        layout.addWidget(self.heard_label)

        self.score_label = QLabel("")
        layout.addWidget(self.score_label)

        self._thread = None
        self.new_sentence()

    def new_sentence(self):
        lvl = self.level_combo.currentText()
        items = listening_items(str(self.root), lvl, count=20)
        if not items:
            self.target_label.setText("No sentences available")
            return
        import random
        self.current = random.choice(items)
        self.target_label.setText(self.current["ja"])
        self.meaning_label.setText(self.current["en"])
        self.heard_label.setText("You said: (none)")
        self.score_label.setText("")
        self.record_btn.setEnabled(True)

    def record(self):
        self.record_btn.setEnabled(False)
        self.score_label.setText("Recording...")
        self._thread = RecordThread(5.0)
        self._thread.result.connect(self.on_result)
        self._thread.error.connect(self.on_error)
        self._thread.finished.connect(lambda: self.record_btn.setEnabled(True))
        self._thread.start()

    def on_result(self, text):
        self.heard_label.setText(f"You said: {text}")
        if self.current is None:
            return
            r = score_pronunciation(self.current["ja"], text, build_reading_map(self.root))
        self.score_label.setText(f"Accuracy: {r['accuracy']}%  (distance {r['distance']})")

    def on_error(self, err):
        self.score_label.setText(f"Error: {err}")

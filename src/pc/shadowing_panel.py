import json
import os
import tempfile

import numpy as np
import sounddevice as sd
import wave

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal

from core.voice import synthesize_to_wav
from core.audio_pack import find, clip_path, play_file


class PlayThread(QThread):
    done = pyqtSignal()

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            play_file(self.path)
        except Exception:
            pass
        self.done.emit()


class ShadowingPanel(QWidget):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        path = os.path.join(str(root), "assets", "immersion", "dialogues.json")
        with open(path, encoding="utf-8") as f:
            self.dialogues = json.load(f)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Shadowing (listen & repeat)"))

        row = QHBoxLayout()
        self.level_combo = QComboBox()
        for lvl in ["All", "N5", "N4", "N3", "N2", "N1"]:
            self.level_combo.addItem(lvl)
        row.addWidget(self.level_combo)
        self.next_btn = QPushButton("New Line")
        self.next_btn.clicked.connect(self.new_line)
        row.addWidget(self.next_btn)
        layout.addLayout(row)

        self.speaker_label = QLabel("")
        self.speaker_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.speaker_label)

        self.line_label = QLabel("")
        self.line_label.setStyleSheet("font-size: 22px;")
        self.line_label.setWordWrap(True)
        layout.addWidget(self.line_label)

        self.translation_label = QLabel("")
        self.translation_label.setWordWrap(True)
        layout.addWidget(self.translation_label)

        self.play_btn = QPushButton("Play (TTS)")
        self.play_btn.clicked.connect(self.play)
        layout.addWidget(self.play_btn)

        self.wav_path = None
        self._thread = None
        self.new_line()

    def filtered(self):
        lvl = self.level_combo.currentText()
        if lvl == "All":
            return self.dialogues
        return [d for d in self.dialogues if d["level"] == lvl]

    def new_line(self):
        import random
        pool = self.filtered()
        if not pool:
            return
        self.current = random.choice(pool)
        self.speaker_label.setText(self.current["speaker"])
        self.line_label.setText(self.current["line"])
        self.translation_label.setText(self.current["translation"])
        try:
            rel = find(self.root, self.current["line"])
            if rel:
                self.wav_path = str(clip_path(self.root, rel))
            else:
                d = tempfile.mkdtemp()
                self.wav_path = os.path.join(d, "shadow.wav")
                synthesize_to_wav(self.current["line"], self.wav_path)
        except Exception as e:
            self.line_label.setText(f"TTS error: {e}")
            self.wav_path = None

    def play(self):
        if not self.wav_path or not os.path.exists(self.wav_path):
            return
        self.play_btn.setEnabled(False)
        self._thread = PlayThread(self.wav_path)
        self._thread.done.connect(lambda: self.play_btn.setEnabled(True))
        self._thread.start()

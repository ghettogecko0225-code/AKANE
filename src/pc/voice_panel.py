import numpy as np
import sounddevice as sd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from pc.voice_qt import Speaker
from core.voice import transcribe_samples


class ListenThread(QThread):
    result = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, seconds=4.0):
        super().__init__()
        self.seconds = seconds

    def run(self):
        try:
            rate = 16000
            rec = sd.rec(int(self.seconds * rate), samplerate=rate, channels=1, dtype="float32")
            sd.wait()
            samples = rec[:, 0]
            text = transcribe_samples(samples)
            self.result.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class VoicePanel(QWidget):
    def __init__(self, parent=None, root=None):
        super().__init__(parent)
        self.speaker = Speaker(root)
        self.speaker.error.connect(lambda e: self.status.setText(f"TTS error: {e}"))
        self.speaker.done.connect(lambda: self.status.setText("Done speaking"))

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Voice (Japanese)"))

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type Japanese or English to speak...")
        layout.addWidget(self.text_input)

        row = QHBoxLayout()
        self.speak_btn = QPushButton("Speak")
        self.speak_btn.clicked.connect(self.speak)
        row.addWidget(self.speak_btn)
        self.listen_btn = QPushButton("Listen (4s)")
        self.listen_btn.clicked.connect(self.listen)
        row.addWidget(self.listen_btn)
        layout.addLayout(row)

        self.heard_label = QLabel("Heard: (none)")
        self.heard_label.setWordWrap(True)
        layout.addWidget(self.heard_label)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        self._listen_thread = None

    def speak(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        self.status.setText("Speaking...")
        self.speaker.say(text)

    def listen(self):
        self.status.setText("Listening...")
        self.listen_btn.setEnabled(False)
        self._listen_thread = ListenThread(4.0)
        self._listen_thread.result.connect(self._on_heard)
        self._listen_thread.error.connect(self._on_listen_error)
        self._listen_thread.finished.connect(lambda: self.listen_btn.setEnabled(True))
        self._listen_thread.start()

    def _on_heard(self, text):
        self.heard_label.setText(f"Heard: {text}")
        self.status.setText("Heard text ready")
        if text:
            self.text_input.setPlainText(text)

    def _on_listen_error(self, err):
        self.status.setText(f"Listen error: {err}")

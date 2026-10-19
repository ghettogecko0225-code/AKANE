from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox,
)

from core.translator import translate


class TranslatePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Translator (Japanese <-> English)"))

        self.input = QTextEdit()
        self.input.setPlaceholderText("Type text to translate...")
        layout.addWidget(self.input)

        row = QHBoxLayout()
        self.dir_combo = QComboBox()
        self.dir_combo.addItem("Auto", "auto")
        self.dir_combo.addItem("Japanese -> English", "ja-en")
        self.dir_combo.addItem("English -> Japanese", "en-ja")
        row.addWidget(self.dir_combo)
        self.btn = QPushButton("Translate")
        self.btn.clicked.connect(self.do_translate)
        row.addWidget(self.btn)
        layout.addLayout(row)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

    def do_translate(self):
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.status.setText("Translating...")
        d = self.dir_combo.currentData()
        direction = None if d == "auto" else d
        try:
            out = translate(text, direction)
            self.output.setPlainText(out)
            self.status.setText("Done")
        except Exception as e:
            self.status.setText(f"Error: {e}")

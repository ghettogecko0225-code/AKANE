from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QProgressBar,
)
from PyQt6.QtCore import Qt

from core.flashcards import FlashCardEngine
from core.workbook import WorkbookEngine


class WorkbookPanel(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.wb = WorkbookEngine(engine)
        self.drill = []
        self.index = 0
        self.results = []

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Workbook (type the answer)"))

        row = QHBoxLayout()
        self.deck_combo = QComboBox()
        row.addWidget(self.deck_combo)
        self.start_btn = QPushButton("Start Drill")
        self.start_btn.clicked.connect(self.start)
        row.addWidget(self.start_btn)
        layout.addLayout(row)

        self.prompt_label = QLabel("Press Start Drill")
        self.prompt_label.setStyleSheet("font-size: 36px;")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.prompt_label)

        self.answer_input = QLineEdit()
        self.answer_input.returnPressed.connect(self.submit)
        layout.addWidget(self.answer_input)

        self.feedback = QLabel("")
        layout.addWidget(self.feedback)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit)
        layout.addWidget(self.submit_btn)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.score_label = QLabel("")
        layout.addWidget(self.score_label)

        self.refresh_decks()

    def refresh_decks(self):
        self.deck_combo.clear()
        for d in self.engine.list_decks():
            self.deck_combo.addItem(f"{d['name']} ({d['lang']})", d["id"])

    def start(self):
        deck_id = self.deck_combo.currentData()
        if deck_id is None:
            return
        self.drill = self.wb.make_drill(deck_id, count=10)
        if not self.drill:
            self.prompt_label.setText("No cards in deck")
            return
        self.index = 0
        self.results = []
        self.progress.setMaximum(len(self.drill))
        self.progress.setValue(0)
        self.score_label.setText("")
        self.show_current()

    def show_current(self):
        if self.index >= len(self.drill):
            s = self.wb.score(self.results)
            self.prompt_label.setText("Drill complete")
            self.score_label.setText(f"Score: {s['correct']}/{s['total']} ({s['percent']}%)")
            self.answer_input.setEnabled(False)
            self.submit_btn.setEnabled(False)
            return
        self.answer_input.setEnabled(True)
        self.submit_btn.setEnabled(True)
        self.answer_input.clear()
        self.feedback.setText("")
        self.prompt_label.setText(self.drill[self.index]["prompt"])

    def submit(self):
        if self.index >= len(self.drill):
            return
        d = self.drill[self.index]
        ok = self.wb.check(self.answer_input.text(), d["answer"])
        self.results.append(ok)
        self.feedback.setText("Correct!" if ok else f"Wrong. Answer: {d['answer']}")
        self.index += 1
        self.progress.setValue(self.index)
        self.show_current()

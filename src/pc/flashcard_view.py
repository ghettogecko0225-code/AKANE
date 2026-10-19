from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt


class FlashCardView(QWidget):
    def __init__(self, engine, progress, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.progress = progress
        self.deck_id = None
        self.current = None
        self.flipped = False
        self.session_id = None
        self.reviewed = 0
        self.correct = 0

        layout = QVBoxLayout(self)
        self.status = QLabel("No deck loaded")
        layout.addWidget(self.status)

        self.card_frame = QFrame()
        self.card_frame.setFrameShape(QFrame.Shape.Box)
        self.card_frame.setMinimumHeight(200)
        cf = QVBoxLayout(self.card_frame)
        self.front_label = QLabel("")
        self.front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.front_label.setStyleSheet("font-size: 48px;")
        self.back_label = QLabel("")
        self.back_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_label.setStyleSheet("font-size: 24px;")
        self.back_label.hide()
        self.hint_label = QLabel("")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 14px; color: #aaa;")
        self.hint_label.setWordWrap(True)
        self.hint_label.hide()
        cf.addWidget(self.front_label)
        cf.addWidget(self.back_label)
        cf.addWidget(self.hint_label)
        layout.addWidget(self.card_frame)

        btns = QHBoxLayout()
        self.flip_btn = QPushButton("Show Answer")
        self.flip_btn.clicked.connect(self.flip)
        btns.addWidget(self.flip_btn)
        layout.addLayout(btns)

        qrow = QHBoxLayout()
        self.q_buttons = []
        for q in range(6):
            b = QPushButton(str(q))
            b.clicked.connect(lambda checked, qq=q: self.rate(qq))
            b.setEnabled(False)
            qrow.addWidget(b)
            self.q_buttons.append(b)
        layout.addLayout(qrow)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_card)
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)

    def load_deck(self, deck_id):
        self.deck_id = deck_id
        self.reviewed = 0
        self.correct = 0
        self.session_id = self.progress.start_session("ja", deck_id)
        self.next_card()

    def next_card(self):
        self.flipped = False
        self.back_label.hide()
        self.hint_label.hide()
        self.flip_btn.setEnabled(True)
        for b in self.q_buttons:
            b.setEnabled(False)
        self.next_btn.setEnabled(False)
        due = self.engine.due_cards(self.deck_id, limit=1)
        if not due:
            self.current = None
            self.front_label.setText("No cards due. Great job!")
            self.back_label.setText("")
            self.status.setText(f"Session: {self.reviewed} reviewed")
            if self.session_id is not None:
                self.progress.end_session(self.session_id, self.reviewed, self.correct)
                self.session_id = None
            return
        self.current = due[0]
        self.front_label.setText(self.current["front"])
        self.back_label.setText(self.current["back"])
        self.hint_label.setText(self.current.get("hint", "") or "")
        remaining = len(self.engine.due_cards(self.deck_id))
        self.status.setText(f"Due: {remaining}  |  Reviewed: {self.reviewed}")

    def flip(self):
        if self.current is None:
            return
        self.flipped = True
        self.back_label.show()
        if self.hint_label.text():
            self.hint_label.show()
        self.flip_btn.setEnabled(False)
        for b in self.q_buttons:
            b.setEnabled(True)

    def rate(self, quality):
        if self.current is None:
            return
        self.engine.review(self.current["id"], quality)
        self.progress.record_review("ja", quality >= 3)
        self.reviewed += 1
        if quality >= 3:
            self.correct += 1
        for b in self.q_buttons:
            b.setEnabled(False)
        self.next_btn.setEnabled(True)
        self.status.setText(f"Rated {quality}. Press Next.")

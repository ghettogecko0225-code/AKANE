import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QRadioButton, QButtonGroup,
)

from core.immersion import load_passages


class ReadingPanel(QWidget):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.passages = load_passages(str(root))
        self.current = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reading Comprehension"))

        row = QHBoxLayout()
        self.level_combo = QComboBox()
        for lvl in ["All", "N5", "N4", "N3", "N2", "N1"]:
            self.level_combo.addItem(lvl)
        row.addWidget(self.level_combo)
        self.next_btn = QPushButton("New Passage")
        self.next_btn.clicked.connect(self.new_passage)
        row.addWidget(self.next_btn)
        layout.addLayout(row)

        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.toggle_btn = QPushButton("Show Translation")
        self.toggle_btn.clicked.connect(self.toggle_translation)
        layout.addWidget(self.toggle_btn)

        self.showing_translation = False
        self.original_text = ""

        self.questions_box = QVBoxLayout()
        layout.addLayout(self.questions_box)

        self.score_label = QLabel("")
        layout.addWidget(self.score_label)

        self.new_passage()

    def filtered(self):
        lvl = self.level_combo.currentText()
        if lvl == "All":
            return self.passages
        return [p for p in self.passages if p["level"] == lvl]

    def new_passage(self):
        pool = self.filtered()
        if not pool:
            self.title_label.setText("No passages")
            return
        import random
        self.current = random.choice(pool)
        self.original_text = self.current["text"]
        self.showing_translation = False
        self.title_label.setText(f"{self.current['title']} ({self.current['level']})")
        self.text_area.setPlainText(self.original_text)
        self.toggle_btn.setText("Show Translation")
        self.build_questions()

    def toggle_translation(self):
        if self.current is None:
            return
        if self.showing_translation:
            self.text_area.setPlainText(self.original_text)
            self.toggle_btn.setText("Show Translation")
            self.showing_translation = False
        else:
            self.text_area.setPlainText(self.original_text + "\n\n---\n" + self.current["translation"])
            self.toggle_btn.setText("Hide Translation")
            self.showing_translation = True

    def build_questions(self):
        for i in reversed(range(self.questions_box.count())):
            w = self.questions_box.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.q_buttons = []
        self.q_group = []
        for qi, q in enumerate(self.current.get("questions", [])):
            lbl = QLabel(f"Q{qi+1}: {q['q']}")
            self.questions_box.addWidget(lbl)
            grp = QButtonGroup(self)
            opts = []
            for oi, opt in enumerate(q["options"]):
                rb = QRadioButton(opt)
                grp.addButton(rb, oi)
                self.questions_box.addWidget(rb)
                opts.append(rb)
            self.q_group.append((grp, q["answer"]))
        check_btn = QPushButton("Check Answers")
        check_btn.clicked.connect(self.check)
        self.questions_box.addWidget(check_btn)

    def check(self):
        correct = 0
        total = len(self.q_group)
        for grp, ans in self.q_group:
            if grp.checkedId() == ans:
                correct += 1
        self.score_label.setText(f"Score: {correct}/{total}")

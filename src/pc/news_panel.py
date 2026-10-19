import json
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QListWidget,
)


class NewsPanel(QWidget):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        path = os.path.join(str(root), "assets", "immersion", "articles.json")
        with open(path, encoding="utf-8") as f:
            self.articles = json.load(f)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("News Reader (Immersion)"))

        row = QHBoxLayout()
        self.level_combo = QComboBox()
        for lvl in ["All", "N5", "N4", "N3", "N2", "N1"]:
            self.level_combo.addItem(lvl)
        row.addWidget(self.level_combo)
        self.next_btn = QPushButton("New Article")
        self.next_btn.clicked.connect(self.new_article)
        row.addWidget(self.next_btn)
        layout.addLayout(row)

        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.toggle_btn = QPushButton("Show Translation")
        self.toggle_btn.clicked.connect(self.toggle)
        layout.addWidget(self.toggle_btn)

        layout.addWidget(QLabel("Key Vocabulary"))
        self.vocab_list = QListWidget()
        layout.addWidget(self.vocab_list)

        self.showing = False
        self.current = None
        self.new_article()

    def filtered(self):
        lvl = self.level_combo.currentText()
        if lvl == "All":
            return self.articles
        return [a for a in self.articles if a["level"] == lvl]

    def new_article(self):
        import random
        pool = self.filtered()
        if not pool:
            return
        self.current = random.choice(pool)
        self.showing = False
        self.title_label.setText(f"{self.current['title']} ({self.current['level']})")
        self.text_area.setPlainText(self.current["text"])
        self.toggle_btn.setText("Show Translation")
        self.vocab_list.clear()
        for v in self.current.get("vocab", []):
            self.vocab_list.addItem(v)

    def toggle(self):
        if self.current is None:
            return
        if self.showing:
            self.text_area.setPlainText(self.current["text"])
            self.toggle_btn.setText("Show Translation")
            self.showing = False
        else:
            self.text_area.setPlainText(self.current["text"] + "\n\n---\n" + self.current["translation"])
            self.toggle_btn.setText("Hide Translation")
            self.showing = True

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from core.progress import ProgressTracker
import datetime

from core.scheduler import Scheduler, StudyConfig


class BarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.labels = []
        self.setMinimumHeight(160)

    def set_data(self, labels, values):
        self.labels = labels
        self.data = values
        self.update()

    def paintEvent(self, event):
        if not self.data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        margin = 30
        chart_w = w - 2 * margin
        chart_h = h - 2 * margin
        maxv = max(self.data) if self.data else 1
        if maxv == 0:
            maxv = 1
        n = len(self.data)
        bar_w = chart_w / max(n, 1)
        for i, v in enumerate(self.data):
            x = margin + i * bar_w + 2
            bh = int(chart_h * v / maxv)
            y = margin + chart_h - bh
            p.setBrush(QColor(70, 130, 180))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(int(x), int(y), int(bar_w - 4), int(bh))
            if i % 5 == 0 or i == n - 1:
                p.setPen(QPen(QColor(200, 200, 200)))
                p.setFont(QFont("Consolas", 8))
                p.drawText(int(x), h - 5, self.labels[i] if i < len(self.labels) else "")
        # axis
        p.setPen(QPen(QColor(150, 150, 150)))
        p.drawLine(margin, margin, margin, margin + chart_h)
        p.drawLine(margin, margin + chart_h, margin + chart_w, margin + chart_h)


class ProgressPanel(QWidget):
    def __init__(self, engine, progress, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.progress = progress
        self.scheduler = Scheduler(engine)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Progress & Schedule"))

        row = QHBoxLayout()
        row.addWidget(QLabel("Deck"))
        self.deck_combo = QComboBox()
        row.addWidget(self.deck_combo)
        layout.addLayout(row)

        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)

        layout.addWidget(QLabel("Last 30 days (cards reviewed)"))
        self.chart = BarChart()
        layout.addWidget(self.chart)

        layout.addWidget(QLabel("Forecast (next 7 days due)"))
        self.forecast_table = QTableWidget(7, 2)
        self.forecast_table.setHorizontalHeaderLabels(["Date", "Due"])
        layout.addWidget(self.forecast_table)

        cfg_row = QHBoxLayout()
        cfg_row.addWidget(QLabel("New cards/day"))
        self.new_spin = QSpinBox()
        self.new_spin.setRange(0, 200)
        self.new_spin.setValue(20)
        cfg_row.addWidget(self.new_spin)
        cfg_row.addWidget(QLabel("Reviews/day"))
        self.rev_spin = QSpinBox()
        self.rev_spin.setRange(0, 500)
        self.rev_spin.setValue(100)
        cfg_row.addWidget(self.rev_spin)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_config)
        cfg_row.addWidget(apply_btn)
        layout.addLayout(cfg_row)

        self.refresh_decks()
        self.refresh()

    def refresh_decks(self):
        self.deck_combo.clear()
        for d in self.engine.list_decks():
            self.deck_combo.addItem(f"{d['name']} ({d['lang']})", d["id"])
        self.deck_combo.currentIndexChanged.connect(self.refresh)

    def apply_config(self):
        self.scheduler.config.new_per_day = self.new_spin.value()
        self.scheduler.config.review_per_day = self.rev_spin.value()
        self.refresh()

    def refresh(self):
        deck_id = self.deck_combo.currentData()
        if deck_id is None:
            return
        lang = None
        for d in self.engine.list_decks():
            if d["id"] == deck_id:
                lang = d["lang"]
        streak = self.progress.streak(lang)
        total = self.progress.total_cards(lang)
        mastery = self.progress.mastery(self.engine, deck_id)
        self.stats_label.setText(
            f"Streak: {streak} days   Reviewed: {total}   "
            f"Mastery: {mastery['mastered']}/{mastery['total']} ({mastery['percent']}%)"
        )

        daily = self.progress.daily(lang=lang, days=30)
        # build 30-day series
        by_date = {r["date"]: r["cards"] for r in daily}
        today = datetime.date.today()
        labels = []
        vals = []
        for i in range(29, -1, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            labels.append(d[5:])
            vals.append(by_date.get(d, 0))
        self.chart.set_data(labels, vals)

        fc = self.scheduler.forecast(deck_id, days=7)
        for i, f in enumerate(fc):
            self.forecast_table.setItem(i, 0, QTableWidgetItem(f["date"]))
            self.forecast_table.setItem(i, 1, QTableWidgetItem(str(f["count"])))

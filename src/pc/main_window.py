import os
import threading
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QComboBox, QTabWidget, QApplication,
)
from PyQt6.QtCore import Qt

from core.db import connect
from core.brand import APP_NAME
from core.flashcards import FlashCardEngine
from core.progress import ProgressTracker
from core.seed import load_deck_from_json
from core.import_openjlpt import import_all as import_openjlpt_all
from core import study
from core.theme import qt_stylesheet
from pc.flashcard_view import FlashCardView
from pc.voice_panel import VoicePanel
from pc.translate_panel import TranslatePanel
from pc.workbook_panel import WorkbookPanel
from pc.reading_panel import ReadingPanel
from pc.listening_panel import ListeningPanel
from pc.speaking_panel import SpeakingPanel
from pc.progress_panel import ProgressPanel
from pc.news_panel import NewsPanel
from pc.shadowing_panel import ShadowingPanel


class MainWindow(QMainWindow):
    def __init__(self, root, data_dir=None):
        super().__init__()
        self.root = Path(root)
        self.data_dir = Path(data_dir) if data_dir else self.root
        self.setWindowTitle(APP_NAME)
        self.resize(900, 600)

        db_path = self.data_dir / "data" / "benkyo.db"
        self.conn = connect(str(db_path))
        self.engine = FlashCardEngine(self.conn)
        self.progress = ProgressTracker(self.conn)

        hives = self._load_hives()
        existing = {d["name"] for d in self.engine.list_decks()}
        seed_map = [("Hiragana", "hiragana.json"), ("Katakana", "katakana.json"), ("Kanji Starter", "kanji_n5.json")]
        for name, fname in seed_map:
            if name not in existing:
                load_deck_from_json(self.engine, "ja", self.root / "lang" / "ja" / fname, name)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        sidebar = QVBoxLayout()
        self.today_label = QLabel("")
        self.today_label.setWordWrap(True)
        sidebar.addWidget(self.today_label)
        today_btn = QPushButton("Study today's plan")
        today_btn.clicked.connect(self.start_today)
        sidebar.addWidget(today_btn)

        sidebar.addWidget(QLabel("Hive"))
        self.hive_combo = QComboBox()
        for h in hives:
            self.hive_combo.addItem(h["name"], h["code"])
        sidebar.addWidget(self.hive_combo)

        sidebar.addWidget(QLabel("Decks"))
        self.deck_list = QListWidget()
        sidebar.addWidget(self.deck_list)
        self.refresh_decks()

        load_btn = QPushButton("Load Deck")
        load_btn.clicked.connect(self.load_selected_deck)
        sidebar.addWidget(load_btn)

        self.import_btn = QPushButton("Import OpenJLPT")
        self.import_btn.clicked.connect(self.import_content)
        sidebar.addWidget(self.import_btn)

        about_btn = QPushButton("About & Credits")
        about_btn.clicked.connect(self.show_credits)
        sidebar.addWidget(about_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        sidebar.addWidget(settings_btn)

        self.stats_label = QLabel("")
        sidebar.addWidget(self.stats_label)
        layout.addLayout(sidebar, 1)

        tabs = QTabWidget()
        self.tabs = tabs
        self.view = FlashCardView(self.engine, self.progress)
        tabs.addTab(self.view, "Flashcards")
        self.voice_panel = VoicePanel(root=self.root)
        tabs.addTab(self.voice_panel, "Voice")
        self.translate_panel = TranslatePanel()
        tabs.addTab(self.translate_panel, "Translate")
        self.workbook_panel = WorkbookPanel(self.engine)
        tabs.addTab(self.workbook_panel, "Workbook")
        self.reading_panel = ReadingPanel(self.root)
        tabs.addTab(self.reading_panel, "Reading")
        self.listening_panel = ListeningPanel(self.root)
        tabs.addTab(self.listening_panel, "Listening")
        self.speaking_panel = SpeakingPanel(self.root)
        tabs.addTab(self.speaking_panel, "Speaking")
        self.progress_panel = ProgressPanel(self.engine, self.progress)
        tabs.addTab(self.progress_panel, "Progress")
        self.news_panel = NewsPanel(self.root)
        tabs.addTab(self.news_panel, "News")
        self.shadowing_panel = ShadowingPanel(self.root)
        tabs.addTab(self.shadowing_panel, "Shadowing")
        layout.addWidget(tabs, 3)

        self.deck_list.itemDoubleClicked.connect(lambda _: self.load_selected_deck())
        self.refresh_stats()
        self.refresh_today()
        app = QApplication.instance()
        if app is not None:
            from core.settings import load as load_settings
            app.setStyleSheet(qt_stylesheet(load_settings(str(self.root)).get("theme", "dark")))
        self.refresh_decks()

        has_content = (self.root / "assets" / "jlpt").exists() or (
            self.root / "assets" / "openjlpt" / "data" / "json"
        ).exists()
        if has_content and "Vocab N5" not in {d["name"] for d in self.engine.list_decks()}:
            self.import_content(background=True)

    def _load_hives(self):
        try:
            import yaml
            with open(self.root / "config.yaml", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            return cfg.get("hives", [{"code": "ja", "name": "Japanese"}])
        except Exception:
            return [{"code": "ja", "name": "Japanese"}]

    def refresh_decks(self):
        self.deck_list.clear()
        lang = self.hive_combo.currentData() or "ja"
        for d in self.engine.list_decks(lang):
            item = QListWidgetItem(f"{d['name']} ({self.engine.cards_count(d['id'])})")
            item.setData(Qt.ItemDataRole.UserRole, d["id"])
            self.deck_list.addItem(item)

    def load_selected_deck(self):
        item = self.deck_list.currentItem()
        if item is None:
            if self.deck_list.count() > 0:
                item = self.deck_list.item(0)
            else:
                return
        deck_id = item.data(Qt.ItemDataRole.UserRole)
        self.view.load_deck(deck_id)
        self.refresh_stats()

    def refresh_stats(self):
        lang = self.hive_combo.currentData() or "ja"
        streak = self.progress.streak(lang)
        total = self.progress.total_cards(lang)
        self.stats_label.setText(f"Streak: {streak} days\nCards reviewed: {total}")

    def refresh_today(self):
        p = study.plan(self.engine, str(self.root), lang="ja")
        remaining = max(p["planned"] - p["done_today"], 0)
        self.today_label.setText(
            f"Today: {remaining} to go\n"
            f"due {p['due']} | new {p['new']} | done {p['done_today']}"
        )

    def start_today(self):
        cards = study.build_session(self.engine, str(self.root), lang="ja")
        if not cards:
            self.today_label.setText("Nothing to study in the selected decks")
            return
        self.view.start_session(cards)
        self.tabs.setCurrentIndex(0)
        self.refresh_today()

    def show_settings(self):
        from PyQt6.QtWidgets import (
            QCheckBox, QDialog, QDialogButtonBox, QSpinBox, QFormLayout,
        )
        from core import settings as app_settings
        from core.theme import palette, qt_stylesheet

        current = app_settings.load(str(self.root))
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        form = QFormLayout(dialog)
        goal = QSpinBox()
        goal.setRange(5, 500)
        goal.setValue(int(current.get("daily_goal", 30)))
        new_per = QSpinBox()
        new_per.setRange(0, 100)
        new_per.setValue(int(current.get("new_per_day", 15)))
        rev_per = QSpinBox()
        rev_per.setRange(10, 500)
        rev_per.setValue(int(current.get("review_per_day", 100)))
        form.addRow("Daily goal (cards)", goal)
        form.addRow("New cards per day", new_per)
        form.addRow("Reviews per day", rev_per)
        boxes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(boxes)
        boxes.accepted.connect(dialog.accept)
        boxes.rejected.connect(dialog.reject)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            app_settings.save(str(self.root), {
                "daily_goal": goal.value(),
                "new_per_day": new_per.value(),
                "review_per_day": rev_per.value(),
            })
            self.refresh_today()

    def show_credits(self):
        from PyQt6.QtWidgets import QMessageBox
        from core.credits import credits_text
        from core.brand import SOURCE_URL, DATA_LICENSE_URL
        box = QMessageBox(self)
        box.setWindowTitle("About & Credits")
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.setText(credits_text(SOURCE_URL, DATA_LICENSE_URL))
        box.exec()

    def import_content(self, background=False):
        # assets/jlpt is the packaged copy and is what ships in the exe and
        # the APK; assets/openjlpt is the upstream repo used when running
        # from source.
        data_dir = self.root / "assets" / "jlpt"
        if not data_dir.exists():
            data_dir = self.root / "assets" / "openjlpt" / "data" / "json"
        if not data_dir.exists():
            self.stats_label.setText("JLPT data not found")
            return

        def worker():
            try:
                self.stats_label.setText("Importing content...")
                created = import_openjlpt_all(self.engine, str(self.root))
                self.refresh_decks()
                self.stats_label.setText(f"Imported {len(created)} decks")
            except Exception as e:
                self.stats_label.setText(f"Import error: {e}")

        if background:
            threading.Thread(target=worker, daemon=True).start()
        else:
            worker()

    def closeEvent(self, event):
        try:
            self.conn.close()
        except Exception:
            pass
        super().closeEvent(event)

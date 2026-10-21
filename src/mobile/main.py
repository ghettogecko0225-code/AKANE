import os
import sys
import threading
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

try:
    import onnxruntime  # noqa
except Exception:
    pass
try:
    import faster_whisper  # noqa
except Exception:
    pass

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock

try:
    LabelBase.register(
        name="Roboto", fn_regular=str(ROOT / "assets" / "fonts" / "msgothic.ttc")
    )
except Exception:
    pass

from core.db import connect
from core.flashcards import FlashCardEngine
from core.progress import ProgressTracker
from core.seed import load_deck_from_json
from core.import_openjlpt import import_all as import_openjlpt_all
from core.translator import translate
from core.immersion import load_passages, listening_items
from core.speaking import score_pronunciation, build_reading_map
from core.workbook import WorkbookEngine
from core.scheduler import Scheduler

from core import android_speech
from core.audio_pack import AudioPlayer
from core import asr
from core import settings
from core import study
from core.theme import palette

ANDROID = android_speech.is_available()

TTS = android_speech.AndroidTTS("ja") if ANDROID else None
AUDIO = None


def _audio_pack():
    global AUDIO
    if AUDIO is None:
        try:
            AUDIO = AudioPlayer(ROOT)
        except Exception:
            AUDIO = False
    return AUDIO or None


def _speak(text):
    """Speak Japanese: pre-rendered audio first, device TTS as fallback."""
    player = _audio_pack()
    if player is not None and player.play(text):
        return True
    if TTS is not None:
        try:
            return TTS.speak(text)
        except Exception:
            return False
    return False


def _spinner(values):
    from kivy.uix.spinner import Spinner
    return Spinner(text=str(values[0]), values=[str(v) for v in values], size_hint=(1, 0.08))


def _check(label):
    from kivy.uix.checkbox import CheckBox
    return CheckBox(size_hint=(None, 0.05))


def card_bg(widget, color, radius=14):
    """Give a Kivy widget a rounded background."""
    from kivy.graphics import Color, RoundedRectangle

    def _paint(*_args):
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(*color)
            RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])

    widget.bind(pos=_paint, size=_paint)
    _paint()
    return widget


def apply_theme(theme_name="dark"):
    """Apply the shared colour palette to the whole app."""
    c = palette(theme_name)
    try:
        Window.clearcolor = c["bg"]
    except Exception:
        pass
    try:
        root = App.get_running_app().root
    except Exception:
        return
    for item in root.walk():
        try:
            if isinstance(item, Label):
                item.color = c["text"]
            elif isinstance(item, Button):
                item.background_color = c["panel"]
                item.color = c["text"]
            elif isinstance(item, TextInput):
                item.background_color = c["panel"]
                item.foreground_color = c["text"]
                item.cursor_color = c["accent"]
        except Exception:
            pass


def _tts_error():
    if TTS is None:
        return "no audio available"
    return getattr(TTS, "last_error", "") or "audio unavailable"


def _ui(fn):
    """Run a UI update on the Kivy main thread.

    Speech and translation run on background threads; touching widgets
    from there crashes Kivy.
    """
    def wrapped(*args, **kwargs):
        Clock.schedule_once(lambda dt: fn(*args, **kwargs), 0)
    return wrapped


def _recognize_offline(on_text, on_error, seconds=5.0):
    """Offline Japanese recognition with the bundled sherpa-onnx model."""
    if not asr.is_available(ROOT):
        on_error("offline model not available")
        return False

    def done(text, info):
        if text:
            on_text(text)
        else:
            raw_peak = info.get("raw_peak", 0)
            if not info.get("bytes"):
                on_error("microphone captured nothing - check the headset mic")
            elif raw_peak < 30:
                on_error(
                    "microphone is silent - plug in the headset or speak into the phone"
                )
            elif raw_peak < 600:
                on_error("microphone is very quiet - speak closer or louder")
            else:
                on_error(
                    "heard audio but no Japanese - say the sentence in Japanese"
                )

    asr.listen(ROOT, seconds, done)
    return True


def _recognize_device(on_text, on_error):
    """Android SpeechRecognizer with a language fallback chain."""
    if not ANDROID:
        on_error("speech recognition is Android-only")
        return False

    def on_result(text):
        on_text(text)

    def on_error_code(code):
        if int(code) in (7, 8, 9, 12, 15):
            on_error(
                "no Japanese voice model on this phone - add Japanese in "
                "Settings > Google voice typing"
            )
        else:
            on_error(f"listen error ({code})")

    try:
        stt = android_speech.AndroidSTT("ja", fallbacks=("ja-JP", "en-US"))
        stt.listen(_ui(on_result), _ui(on_error_code))
        return True
    except Exception as e:
        on_error(f"listen error: {e}")
        return False


def _start_listening(on_text, on_error):
    """Prefer the bundled offline model; fall back to the device engine."""
    if _recognize_offline(on_text, on_error, seconds=6.0):
        return
    _recognize_device(on_text, on_error)


class BaseScreen(Screen):
    def __init__(self, app_ref, title, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.box = BoxLayout(orientation="vertical", padding=16, spacing=8)
        self.title_label = Label(text=title, font_size=20, size_hint=(1, 0.08))
        self.box.add_widget(self.title_label)
        self.add_widget(self.box)

    def add_home_button(self):
        btn = Button(text="Home", size_hint=(1, 0.09))
        btn.bind(on_press=lambda x: self.app_ref.go("Home"))
        self.box.add_widget(btn)


class HomeScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Japanese Sensei AI", **kwargs)
        self.deck_items = []
        self.spinner = Spinner(text="Choose deck", values=self.deck_items, size_hint=(1, 0.09))
        self.spinner.bind(text=self.on_deck)
        self.box.add_widget(self.spinner)
        for name in ["Today", "Flashcards", "Voice", "Translate", "Workbook", "Reading",
                     "Listening", "Speaking", "News", "Shadowing", "Model",
                     "Progress", "Settings", "About"]:
            btn = Button(text=name, size_hint=(1, 0.075))
            btn.bind(on_press=lambda x, n=name: self.app_ref.go(n))
            self.box.add_widget(btn)
        self.status = Label(text="", size_hint=(1, 0.07))
        self.box.add_widget(self.status)
        self.refresh_decks()

    def refresh_decks(self):
        self.deck_items = []
        for d in self.app_ref.engine.list_decks():
            count = self.app_ref.engine.cards_count(d["id"])
            self.deck_items.append(f"{d['name']} ({count})")
        if self.deck_items:
            self.spinner.values = self.deck_items
            if not self.spinner.text or self.spinner.text not in self.deck_items:
                self.spinner.text = self.deck_items[0]
                self.on_deck(self.spinner.text)

    def on_deck(self, *a):
        text = a[-1] if a else ""
        for d in self.app_ref.engine.list_decks():
            if text.startswith(d["name"]):
                self.app_ref.deck_id = d["id"]
                return


class FlashcardScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Flashcards", **kwargs)
        self.current = None
        self.status = Label(text="", size_hint=(1, 0.08))
        self.box.add_widget(self.status)
        self.card = Label(text="", font_size=52, size_hint=(1, 0.32))
        card_bg(self.card, palette(settings.get(ROOT, "theme", "dark"))["card"])
        self.box.add_widget(self.card)
        self.back = Label(text="", font_size=22, size_hint=(1, 0.16))
        self.box.add_widget(self.back)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        self.flip_btn = Button(text="Show Answer")
        self.flip_btn.bind(on_press=self.flip)
        row.add_widget(self.flip_btn)
        self.next_btn = Button(text="Next")
        self.next_btn.bind(on_press=self.next_card)
        row.add_widget(self.next_btn)
        self.box.add_widget(row)
        rate_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=2)
        for q in range(6):
            b = Button(text=str(q))
            b.bind(on_press=lambda x, qq=q: self.rate(qq))
            rate_row.add_widget(b)
        self.box.add_widget(rate_row)
        self.add_home_button()

    def on_enter(self):
        self.next_card()

    def next_card(self, *a):
        deck_id = self.app_ref.deck_id
        if deck_id is None:
            self.card.text = "No deck"
            return
        self.back.text = ""
        due = self.app_ref.engine.due_cards(deck_id, limit=1)
        if not due:
            self.current = None
            self.card.text = "No cards due!"
            self.status.text = f"Reviewed: {self.app_ref.session_count}"
            return
        self.current = due[0]
        self.card.text = self.current["front"]
        remaining = len(self.app_ref.engine.due_cards(deck_id))
        self.status.text = f"Due: {remaining}"

    def flip(self, *a):
        if self.current is None:
            return
        self.back.text = self.current["back"]
        hint = self.current.get("hint") or ""
        if hint:
            self.back.text += "\n" + hint

    def rate(self, q):
        if self.current is None:
            return
        self.app_ref.engine.review(self.current["id"], q)
        self.app_ref.progress.record_review(self.app_ref.lang, q >= 3)
        self.app_ref.session_count += 1
        self.next_card()


class VoiceScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Voice (Japanese)", **kwargs)
        self.input = TextInput(size_hint=(1, 0.3), multiline=True)
        self.box.add_widget(self.input)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        speak_btn = Button(text="Speak")
        speak_btn.bind(on_press=self.speak)
        row.add_widget(speak_btn)
        listen_btn = Button(text="Listen")
        listen_btn.bind(on_press=self.listen)
        row.add_widget(listen_btn)
        self.box.add_widget(row)
        self.heard = Label(text="", size_hint=(1, 0.12))
        self.box.add_widget(self.heard)
        self.status = Label(text="", size_hint=(1, 0.1))
        self.box.add_widget(self.status)
        self.add_home_button()

    def speak(self, *a):
        text = self.input.text.strip()
        if not text:
            return
        player = _audio_pack()
        if player is not None and player.play(text):
            self.status.text = "Playing recorded Japanese audio"
            return
        if _speak(text):
            lang_res = getattr(TTS, "language_result", -1) if TTS else -1
            if lang_res is not None and int(lang_res) < 0:
                self.status.text = (
                    "Spoke, but no Japanese voice on device. "
                    "Settings > Google TTS > Languages > install Japanese."
                )
            else:
                self.status.text = "Speaking..."
        else:
            self.status.text = f"Audio error: {_tts_error()}"

    def listen(self, *a):
        self.status.text = "Listening..."

        def on_text(text):
            self.heard.text = f"You said: {text}"
            self.status.text = "Heard"
            self.input.text = text

        def on_error(msg):
            self.status.text = msg

        _start_listening(_ui(on_text), _ui(on_error))


class TranslateScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Translator", **kwargs)
        self.input = TextInput(size_hint=(1, 0.28), multiline=True)
        self.box.add_widget(self.input)
        self.spinner = Spinner(text="Auto", values=["Auto", "Japanese -> English", "English -> Japanese"])
        self.spinner.size_hint = (1, 0.09)
        self.box.add_widget(self.spinner)
        btn = Button(text="Translate", size_hint=(1, 0.1))
        btn.bind(on_press=self.do_translate)
        self.box.add_widget(btn)
        self.output = TextInput(size_hint=(1, 0.28), multiline=True, readonly=True)
        self.box.add_widget(self.output)
        self.status = Label(text="", size_hint=(1, 0.08))
        self.box.add_widget(self.status)
        self.add_home_button()

    def do_translate(self, *a):
        text = self.input.text.strip()
        if not text:
            return
        choice = self.spinner.text
        direction = None
        if choice.startswith("Japanese"):
            direction = "ja-en"
        elif choice.startswith("English"):
            direction = "en-ja"
        self.status.text = "Translating..."

        def worker():
            try:
                out = translate(text, direction)
            except Exception as e:
                msg = str(e) or type(e).__name__

                def show_error(dt):
                    self.output.text = ""
                    self.status.text = msg[:80]

                Clock.schedule_once(show_error, 0)
                return

            def show_result(dt):
                self.output.text = out
                self.status.text = "Done"

            Clock.schedule_once(show_result, 0)

        threading.Thread(target=worker, daemon=True).start()


class WorkbookScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Workbook", **kwargs)
        self.drill = []
        self.index = 0
        self.results = []
        self.prompt = Label(text="Press Start", font_size=34, size_hint=(1, 0.25))
        self.box.add_widget(self.prompt)
        self.answer = TextInput(size_hint=(1, 0.12), multiline=False)
        self.box.add_widget(self.answer)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        start_btn = Button(text="Start")
        start_btn.bind(on_press=self.start)
        row.add_widget(start_btn)
        submit_btn = Button(text="Submit")
        submit_btn.bind(on_press=self.submit)
        row.add_widget(submit_btn)
        self.box.add_widget(row)
        self.feedback = Label(text="", size_hint=(1, 0.1))
        self.box.add_widget(self.feedback)
        self.score = Label(text="", size_hint=(1, 0.1))
        self.box.add_widget(self.score)
        self.add_home_button()

    def start(self, *a):
        deck_id = self.app_ref.deck_id
        if deck_id is None:
            return
        wb = WorkbookEngine(self.app_ref.engine)
        self.drill = wb.make_drill(deck_id, count=10)
        if not self.drill:
            self.prompt.text = "No cards"
            return
        self.index = 0
        self.results = []
        self.show_current()

    def show_current(self):
        if self.index >= len(self.drill):
            s = WorkbookEngine.score(self.results)
            self.prompt.text = "Done"
            self.score.text = f"Score: {s['correct']}/{s['total']} ({s['percent']}%)"
            return
        self.prompt.text = self.drill[self.index]["prompt"]
        self.answer.text = ""
        self.feedback.text = ""

    def submit(self, *a):
        if self.index >= len(self.drill):
            return
        d = self.drill[self.index]
        ok = WorkbookEngine.check(self.answer.text, d["answer"])
        self.results.append(ok)
        self.feedback.text = "Correct!" if ok else f"Wrong: {d['answer']}"
        self.index += 1
        self.show_current()


class ReadingScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Reading", **kwargs)
        self.passages = load_passages(str(app_ref.root_path))
        self.current = None
        self.showing = False
        self.text_area = Label(text="", size_hint=(1, 0.45))
        self.text_area.text_size = (Window.width - 40, None)
        self.box.add_widget(self.text_area)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        new_btn = Button(text="New")
        new_btn.bind(on_press=self.new_passage)
        row.add_widget(new_btn)
        tog_btn = Button(text="Translation")
        tog_btn.bind(on_press=self.toggle)
        row.add_widget(tog_btn)
        self.box.add_widget(row)
        self.q_label = Label(text="", size_hint=(1, 0.2))
        self.box.add_widget(self.q_label)
        self.add_home_button()
        self.new_passage()

    def new_passage(self, *a):
        import random
        if not self.passages:
            self.title_label.text = "No passages"
            return
        self.current = random.choice(self.passages)
        self.showing = False
        self.title_label.text = f"{self.current['title']} ({self.current['level']})"
        self.text_area.text = self.current["text"]
        qs = self.current.get("questions", [])
        if qs:
            q = qs[0]
            self.q_label.text = q["q"] + "\n" + "  ".join(q["options"])

    def toggle(self, *a):
        if self.current is None:
            return
        if self.showing:
            self.text_area.text = self.current["text"]
            self.showing = False
        else:
            self.text_area.text = self.current["text"] + "\n\n" + self.current["translation"]
            self.showing = True


class ListeningScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Listening (type what you hear)", **kwargs)
        self.current = None
        self.play_btn = Button(text="Play", size_hint=(1, 0.1))
        self.play_btn.bind(on_press=self.play)
        self.box.add_widget(self.play_btn)
        self.input = TextInput(size_hint=(1, 0.12), multiline=False)
        self.box.add_widget(self.input)
        btn = Button(text="Check", size_hint=(1, 0.1))
        btn.bind(on_press=self.check)
        self.box.add_widget(btn)
        self.result = Label(text="", size_hint=(1, 0.16))
        self.box.add_widget(self.result)
        self.status = Label(text="", size_hint=(1, 0.09))
        self.box.add_widget(self.status)
        self.add_home_button()
        self.new_sentence()

    def new_sentence(self, *a):
        items = listening_items(str(self.app_ref.root_path), "n5", count=20)
        if not items:
            items = listening_items(str(self.app_ref.root_path), None, count=20)
        if not items:
            self.status.text = "No sentences available"
            return
        import random
        self.current = random.choice(items)
        self.input.text = ""
        self.result.text = ""
        self.status.text = "Press Play, then type what you hear"

    def play(self, *a):
        if self.current is None:
            return
        if _speak(self.current["ja"]):
            self.status.text = "Playing..."
        else:
            self.status.text = f"TTS error: {_tts_error()}"

    def check(self, *a):
        if self.current is None:
            return
        u = self.input.text.strip()
        c = self.current["ja"].strip()

        def norm(s):
            return "".join(ch for ch in s if ch not in " 、。！？")

        if norm(u) == norm(c):
            self.result.text = "Correct!"
        else:
            self.result.text = f"Not quite. Original: {c}"
        self.status.text = self.current["en"]


class SpeakingScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Speaking (say the sentence)", **kwargs)
        self.current = None
        self.target = Label(text="", font_size=28, size_hint=(1, 0.2))
        self.box.add_widget(self.target)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        new_btn = Button(text="New")
        new_btn.bind(on_press=self.new_sentence)
        row.add_widget(new_btn)
        rec_btn = Button(text="Record")
        rec_btn.bind(on_press=self.record)
        row.add_widget(rec_btn)
        self.box.add_widget(row)
        self.heard = Label(text="", size_hint=(1, 0.14))
        self.box.add_widget(self.heard)
        self.result = Label(text="", size_hint=(1, 0.12))
        self.box.add_widget(self.result)
        self.status = Label(text="", size_hint=(1, 0.09))
        self.box.add_widget(self.status)
        self.add_home_button()
        self.new_sentence()

    def new_sentence(self, *a):
        items = listening_items(str(self.app_ref.root_path), "n5", count=20)
        if not items:
            items = listening_items(str(self.app_ref.root_path), None, count=20)
        if not items:
            self.status.text = "No sentences available"
            return
        import random
        self.current = random.choice(items)
        self.target.text = self.current["ja"]
        self.heard.text = ""
        self.result.text = ""
        self.status.text = ""

    def record(self, *a):
        if self.current is None:
            return
        self.status.text = "Listening (offline Japanese model)..."

        def on_text(text):
            self.heard.text = f"You said: {text}"
            r = score_pronunciation(
                self.current["ja"], text, build_reading_map(ROOT)
            )
            self.result.text = f"Accuracy: {r['accuracy']}%"
            self.status.text = ""

        def on_error(msg):
            self.status.text = msg

        _start_listening(_ui(on_text), _ui(on_error))


class NewsScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "News", **kwargs)
        import json
        path = os.path.join(str(app_ref.root_path), "assets", "immersion", "articles.json")
        with open(path, encoding="utf-8") as f:
            self.articles = json.load(f)
        self.current = None
        self.showing = False
        self.text_area = Label(text="", size_hint=(1, 0.42))
        self.text_area.text_size = (Window.width - 40, None)
        self.box.add_widget(self.text_area)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        new_btn = Button(text="New")
        new_btn.bind(on_press=self.new_article)
        row.add_widget(new_btn)
        tog_btn = Button(text="Translation")
        tog_btn.bind(on_press=self.toggle)
        row.add_widget(tog_btn)
        self.box.add_widget(row)
        self.vocab = Label(text="", size_hint=(1, 0.2))
        self.box.add_widget(self.vocab)
        self.add_home_button()
        self.new_article()

    def new_article(self, *a):
        import random
        if not self.articles:
            return
        self.current = random.choice(self.articles)
        self.showing = False
        self.title_label.text = f"{self.current['title']} ({self.current['level']})"
        self.text_area.text = self.current["text"]
        self.vocab.text = "\n".join(self.current.get("vocab", []))

    def toggle(self, *a):
        if self.current is None:
            return
        if self.showing:
            self.text_area.text = self.current["text"]
            self.showing = False
        else:
            self.text_area.text = self.current["text"] + "\n\n" + self.current["translation"]
            self.showing = True


class ShadowingScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Shadowing (listen & repeat)", **kwargs)
        import json
        path = os.path.join(str(app_ref.root_path), "assets", "immersion", "dialogues.json")
        with open(path, encoding="utf-8") as f:
            self.dialogues = json.load(f)
        self.current = None
        self.line = Label(text="", font_size=26, size_hint=(1, 0.2))
        self.box.add_widget(self.line)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        new_btn = Button(text="New")
        new_btn.bind(on_press=self.new_line)
        row.add_widget(new_btn)
        play_btn = Button(text="Play")
        play_btn.bind(on_press=self.play)
        row.add_widget(play_btn)
        self.box.add_widget(row)
        self.translation = Label(text="", size_hint=(1, 0.14))
        self.box.add_widget(self.translation)
        self.status = Label(text="", size_hint=(1, 0.09))
        self.box.add_widget(self.status)
        self.add_home_button()
        self.new_line()

    def new_line(self, *a):
        import random
        if not self.dialogues:
            return
        self.current = random.choice(self.dialogues)
        self.title_label.text = f"Speaker {self.current['speaker']}"
        self.line.text = self.current["line"]
        self.translation.text = self.current["translation"]

    def play(self, *a):
        if self.current is None:
            return
        if _speak(self.current["line"]):
            self.status.text = "Playing..."
        else:
            self.status.text = f"TTS error: {_tts_error()}"


class ProgressScreen(BaseScreen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Progress", **kwargs)
        self.stats = Label(text="", size_hint=(1, 0.16))
        self.box.add_widget(self.stats)
        self.chart = Label(text="", size_hint=(1, 0.4))
        self.box.add_widget(self.chart)
        self.forecast = Label(text="", size_hint=(1, 0.2))
        self.box.add_widget(self.forecast)
        self.add_home_button()

    def on_enter(self):
        self.refresh()

    def refresh(self):
        lang = self.app_ref.lang
        streak = self.app_ref.progress.streak(lang)
        total = self.app_ref.progress.total_cards(lang)
        mastery = self.app_ref.progress.mastery(self.app_ref.engine, self.app_ref.deck_id) if self.app_ref.deck_id else {"mastered": 0, "total": 0, "percent": 0}
        self.stats.text = f"Streak: {streak} days\nReviewed: {total}\nMastery: {mastery['mastered']}/{mastery['total']} ({mastery['percent']}%)"
        daily = self.app_ref.progress.daily(lang=lang, days=14)
        by_date = {r["date"]: r["cards"] for r in daily}
        import datetime
        today = datetime.date.today()
        bars = []
        for i in range(13, -1, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            n = by_date.get(d, 0)
            bars.append("▇" * min(n, 20))
        self.chart.text = "Last 14 days\n" + "\n".join(bars)
        if self.app_ref.deck_id:
            sched = Scheduler(self.app_ref.engine)
            fc = sched.forecast(self.app_ref.deck_id, days=5)
            self.forecast.text = "Due next 5 days\n" + "\n".join(f"{f['date']}: {f['count']}" for f in fc)


class ModelScreen(BaseScreen):
    """Shows the offline voice engine that is in use."""

    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Voice Engine", **kwargs)
        self.info = Label(text="", size_hint=(1, 0.24))
        self.box.add_widget(self.info)
        self.status = Label(text="", size_hint=(1, 0.1))
        self.box.add_widget(self.status)
        self.add_home_button()
        self.refresh()

    def on_enter(self):
        self.refresh()

    def refresh(self):
        info = asr.model_info(ROOT)
        free_mb = asr.available_ram_mb()
        mem = f"\nFree RAM: {free_mb} MB" if free_mb else ""
        self.info.text = (
            f"Engine: {info.get('name', 'none')}\n{info.get('detail', '')}{mem}"
        )
        self.status.text = "Everything runs on this device - no internet needed."


class AboutScreen(BaseScreen):
    """Credits and licences - required because the app ships CC BY-SA data."""

    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "About & Credits", **kwargs)
        from core.credits import CREDITS
        from kivy.uix.scrollview import ScrollView

        self.text = Label(
            text=CREDITS,
            size_hint=(1, None),
            halign="left",
            valign="top",
            markup=False,
        )
        self.text.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            height=lambda inst, val: setattr(inst, "height", max(val, 1)),
        )
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.text)
        self.box.add_widget(scroll)
        self.add_home_button()


class TodayScreen(BaseScreen):
    """What to learn today, and a session that runs it."""

    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Today", **kwargs)
        self.session = []
        self.index = 0
        self.reviewed = 0
        self.plan_box = BoxLayout(orientation="vertical", size_hint=(1, None))
        self.box.add_widget(self.plan_box)
        self.big = Label(text="", font_size=30, size_hint=(1, 0.12))
        self.plan_box.add_widget(self.big)
        self.detail = Label(text="", size_hint=(1, 0.12))
        self.plan_box.add_widget(self.detail)
        self.hint = Label(text="", size_hint=(1, 0.1))
        self.plan_box.add_widget(self.hint)
        self.start_btn = Button(text="Start today's session", size_hint=(1, 0.11))
        self.start_btn.bind(on_press=self.start_session)
        self.plan_box.add_widget(self.start_btn)

        self.card_area = BoxLayout(orientation="vertical", size_hint=(1, None))
        self.box.add_widget(self.card_area)
        self.progress = Label(text="", size_hint=(1, 0.08))
        self.card_area.add_widget(self.progress)
        self.prompt = Label(text="", font_size=44, size_hint=(1, 0.24))
        card_bg(self.prompt, palette(settings.get(ROOT, "theme", "dark"))["card"])
        self.card_area.add_widget(self.prompt)
        self.answer = Label(text="", font_size=20, size_hint=(1, 0.16))
        self.card_area.add_widget(self.answer)
        row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=4)
        self.flip_btn = Button(text="Show answer")
        self.flip_btn.bind(on_press=self.flip)
        row.add_widget(self.flip_btn)
        self.card_area.add_widget(row)
        rate_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=2)
        for q in range(6):
            b = Button(text=str(q))
            b.bind(on_press=lambda x, qq=q: self.rate(qq))
            rate_row.add_widget(b)
        self.card_area.add_widget(rate_row)
        self.add_home_button()
        self.show_plan()

    def show_plan(self):
        p = study.plan(self.app_ref.engine, ROOT, lang=self.app_ref.lang)
        self.plan_box.opacity = 1
        self.card_area.opacity = 0
        self.card_area.disabled = True
        remaining = max(p["planned"] - p["done_today"], 0)
        self.big.text = f"{remaining} cards to go today"
        self.detail.text = (
            f"Due: {p['due']}    New: {p['new']}    Done today: {p['done_today']}\n"
            f"Goal {p['goal']} a day   |   {p['decks']} decks selected"
        )
        self.hint.text = study.next_level_hint(self.app_ref.engine, ROOT, self.app_ref.lang)
        if remaining == 0:
            self.start_btn.text = "Nothing due - review anyway"
        else:
            self.start_btn.text = "Start today's session"

    def start_session(self, *a):
        self.session = study.build_session(self.app_ref.engine, ROOT, lang=self.app_ref.lang)
        if not self.session:
            self.status.text = "No cards in the selected decks"
            return
        self.index = 0
        self.reviewed = 0
        self.plan_box.opacity = 0
        self.plan_box.disabled = True
        self.card_area.opacity = 1
        self.card_area.disabled = False
        self.next_card()

    def next_card(self):
        if self.index >= len(self.session):
            self.status.text = f"Session complete - {self.reviewed} cards"
            self.show_plan()
            return
        card = self.session[self.index]
        self.progress.text = f"Card {self.index + 1} of {len(self.session)}"
        self.prompt.text = card["front"]
        self.answer.text = ""
        self.flip_btn.disabled = False

    def flip(self, *a):
        if self.index >= len(self.session):
            return
        card = self.session[self.index]
        self.answer.text = card["back"] + ("\n" + card["hint"] if card.get("hint") else "")
        self.flip_btn.disabled = True

    def rate(self, q):
        if self.index >= len(self.session):
            return
        card = self.session[self.index]
        self.app_ref.engine.review(card["id"], q)
        self.app_ref.progress.record_review(self.app_ref.lang, q >= 3)
        self.reviewed += 1
        self.index += 1
        self.next_card()


class SettingsScreen(BaseScreen):
    """Daily goals, deck selection and theme."""

    def __init__(self, app_ref, **kwargs):
        super().__init__(app_ref, "Settings", **kwargs)
        from kivy.uix.scrollview import ScrollView

        inner = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=6)
        inner.add_widget(Label(text="Daily goal (cards per day)"))
        self.goal = _spinner([10, 20, 30, 50, 100])
        inner.add_widget(self.goal)
        inner.add_widget(Label(text="New cards per day"))
        self.new_per = _spinner([0, 5, 10, 15, 25, 50])
        inner.add_widget(self.new_per)
        inner.add_widget(Label(text="Reviews per day"))
        self.rev_per = _spinner([20, 50, 100, 200, 400])
        inner.add_widget(self.rev_per)
        inner.add_widget(Label(text="Theme"))
        self.theme = _spinner(["dark", "light"])
        inner.add_widget(self.theme)
        inner.add_widget(Label(text="Study decks (none checked = all)"))
        self.deck_boxes = []
        for deck in app_ref.engine.list_decks(app_ref.lang):
            row = BoxLayout(orientation="horizontal", size_hint=(1, 0.06))
            check = _check(deck.get("name", ""))
            row.add_widget(check)
            lbl = Label(text=f"{deck['name']} ({app_ref.engine.cards_count(deck['id'])})")
            row.add_widget(lbl)
            inner.add_widget(row)
            self.deck_boxes.append((deck["name"], check))
        save_btn = Button(text="Save settings", size_hint=(1, 0.1))
        save_btn.bind(on_press=self.save)
        inner.add_widget(save_btn)

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(inner)
        self.box.add_widget(scroll)
        self.add_home_button()
        self.load_values()

    def load_values(self):
        s = settings.load(ROOT)
        self.goal.text = str(s.get("daily_goal", 30))
        self.new_per.text = str(s.get("new_per_day", 15))
        self.rev_per.text = str(s.get("review_per_day", 100))
        self.theme.text = s.get("theme", "dark")
        active = set(s.get("active_decks") or [])
        for name, check in self.deck_boxes:
            check.active = (name in active) if active else True

    def save(self, *a):
        chosen = [name for name, check in self.deck_boxes if check.active]
        values = {
            "daily_goal": int(self.goal.text),
            "new_per_day": int(self.new_per.text),
            "review_per_day": int(self.rev_per.text),
            "theme": self.theme.text,
            "active_decks": chosen,
        }
        settings.save(ROOT, values)
        self.status.text = "Saved"
        apply_theme(self.theme.text)


class SenseiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_path = ROOT
        self.lang = "ja"
        self.session_count = 0
        data_dir = ROOT / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.conn = connect(str(data_dir / "sensei.db"))
        self.engine = FlashCardEngine(self.conn)
        self.progress = ProgressTracker(self.conn)
        existing = {d["name"] for d in self.engine.list_decks()}
        for name, fname in [("Hiragana", "hiragana.json"), ("Katakana", "katakana.json"), ("Kanji Starter", "kanji_n5.json")]:
            if name not in existing:
                try:
                    load_deck_from_json(self.engine, "ja", ROOT / "lang" / "ja" / fname, name)
                except Exception:
                    pass
        decks = self.engine.list_decks()
        self.deck_id = decks[0]["id"] if decks else None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(self, name="Home"))
        self.sm.add_widget(FlashcardScreen(self, name="Flashcards"))
        self.sm.add_widget(VoiceScreen(self, name="Voice"))
        self.sm.add_widget(TranslateScreen(self, name="Translate"))
        self.sm.add_widget(WorkbookScreen(self, name="Workbook"))
        self.sm.add_widget(ReadingScreen(self, name="Reading"))
        self.sm.add_widget(ListeningScreen(self, name="Listening"))
        self.sm.add_widget(SpeakingScreen(self, name="Speaking"))
        self.sm.add_widget(NewsScreen(self, name="News"))
        self.sm.add_widget(ShadowingScreen(self, name="Shadowing"))
        self.sm.add_widget(ModelScreen(self, name="Model"))
        self.sm.add_widget(AboutScreen(self, name="About"))
        self.sm.add_widget(TodayScreen(self, name="Today"))
        self.sm.add_widget(SettingsScreen(self, name="Settings"))
        self.sm.add_widget(ProgressScreen(self, name="Progress"))
        threading.Thread(target=self._import_full_content, daemon=True).start()
        theme = settings.get(ROOT, "theme", "dark")
        Clock.schedule_once(lambda dt: apply_theme(theme), 0.2)
        return self.sm

    def _import_full_content(self):
        jlpt_dir = ROOT / "assets" / "jlpt"
        if not jlpt_dir.is_dir():
            return
        if any(d["name"] == "Vocab N5" for d in self.engine.list_decks()):
            return
        try:
            import_openjlpt_all(self.engine, str(ROOT))
        except Exception:
            pass

    def go(self, name):
        self.sm.current = name
        screen = self.sm.get_screen(name)
        if hasattr(screen, "on_enter"):
            try:
                screen.on_enter()
            except Exception:
                pass
        if name == "Home":
            try:
                self.sm.get_screen("Home").refresh_decks()
            except Exception:
                pass


if __name__ == "__main__":
    SenseiApp().run()

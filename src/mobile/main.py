import sys
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

from core.db import connect
from core.flashcards import FlashCardEngine
from core.progress import ProgressTracker
from core.seed import load_deck_from_json
from core.import_openjlpt import import_all as import_openjlpt_all
try:
    from core.translator import translate
    _HAS_TRANSLATE = True
except Exception:
    _HAS_TRANSLATE = False
    def translate(*a, **k):
        raise RuntimeError("translation not available")
try:
    from core.voice import synthesize_to_wav, transcribe_samples, record_samples
    _HAS_VOICE = True
except Exception:
    _HAS_VOICE = False
from core.immersion import load_passages, listening_items
from core.speaking import score_pronunciation
from core.immersion import listening_items as li

import os
import threading
import tempfile
import wave


class HomeScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Japanese Sensei AI", font_size=24))
        for name in ["Flashcards", "Translate", "Voice", "Workbook", "Reading", "Listening", "Speaking", "News", "Shadowing", "Progress"]:
            btn = Button(text=name, size_hint=(1, 0.12))
            btn.bind(on_press=lambda x, n=name: self.app_ref.go(n))
            layout.add_widget(btn)
        self.add_widget(layout)


class FlashcardScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.current = None
        self.flipped = False
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.status = Label(text="Loading...", size_hint=(1, 0.1))
        layout.add_widget(self.status)
        self.card_label = Label(text="", font_size=48, size_hint=(1, 0.4))
        layout.add_widget(self.card_label)
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=5)
        self.flip_btn = Button(text="Show Answer")
        self.flip_btn.bind(on_press=self.flip)
        btn_row.add_widget(self.flip_btn)
        self.next_btn = Button(text="Next")
        self.next_btn.bind(on_press=self.next_card)
        btn_row.add_widget(self.next_btn)
        layout.add_widget(btn_row)
        rate_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=3)
        for q in range(6):
            b = Button(text=str(q))
            b.bind(on_press=lambda x, qq=q: self.rate(qq))
            rate_row.add_widget(b)
        layout.add_widget(rate_row)
        back_btn = Button(text="Home", size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: self.app_ref.go("Home"))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def on_enter(self):
        self.next_card()

    def next_card(self):
        self.flipped = False
        due = self.app_ref.engine.due_cards(self.app_ref.deck_id, limit=1)
        if not due:
            self.card_label.text = "No cards due!"
            self.current = None
            return
        self.current = due[0]
        self.card_label.text = self.current["front"]
        self.status.text = f"Due: {len(self.app_ref.engine.due_cards(self.app_ref.deck_id))}"

    def flip(self, *a):
        if self.current is None:
            return
        self.flipped = True
        self.card_label.text = self.current["back"] + "\n" + (self.current.get("hint", "") or "")

    def rate(self, q):
        if self.current is None:
            return
        self.app_ref.engine.review(self.current["id"], q)
        self.app_ref.progress.record_review("ja", q >= 3)
        self.next_card()


class TranslateScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Translator", font_size=20))
        self.input = TextInput(size_hint=(1, 0.3), multiline=True)
        layout.add_widget(self.input)
        btn = Button(text="Translate", size_hint=(1, 0.1))
        btn.bind(on_press=self.do_translate)
        layout.add_widget(btn)
        self.output = TextInput(size_hint=(1, 0.3), multiline=True, readonly=True)
        layout.add_widget(self.output)
        back_btn = Button(text="Home", size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: self.app_ref.go("Home"))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def do_translate(self, *a):
        text = self.input.text.strip()
        if not text:
            return
        try:
            out = translate(text)
            self.output.text = out
        except Exception as e:
            self.output.text = f"Error: {e}"


class VoiceScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="Voice (Japanese)", font_size=20))
        self.text_input = TextInput(size_hint=(1, 0.3), multiline=True)
        layout.add_widget(self.text_input)
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=5)
        speak_btn = Button(text="Speak")
        speak_btn.bind(on_press=self.speak)
        btn_row.add_widget(speak_btn)
        listen_btn = Button(text="Listen 4s")
        listen_btn.bind(on_press=self.listen)
        btn_row.add_widget(listen_btn)
        layout.add_widget(btn_row)
        self.status = Label(text="Ready", size_hint=(1, 0.1))
        layout.add_widget(self.status)
        back_btn = Button(text="Home", size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: self.app_ref.go("Home"))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def speak(self, *a):
        text = self.text_input.text.strip()
        if not text:
            return
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text):
        try:
            d = tempfile.mkdtemp()
            path = os.path.join(d, "tts.wav")
            synthesize_to_wav(text, path)
            # play
            import numpy as np
            import sounddevice as sd
            with wave.open(path, "rb") as wf:
                rate = wf.getframerate()
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            stream = sd.OutputStream(samplerate=rate, channels=1, dtype="int16")
            stream.start()
            for i in range(0, len(data), 4096):
                stream.write(data[i:i + 4096].reshape(-1, 1))
            stream.stop()
            stream.close()
            self.status.text = "Done"
        except Exception as e:
            self.status.text = f"Error: {e}"

    def listen(self, *a):
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        try:
            self.status.text = "Listening..."
            samples = record_samples(4.0)
            text = transcribe_samples(samples)
            self.text_input.text = text
            self.status.text = "Heard"
        except Exception as e:
            self.status.text = f"Error: {e}"


class SimpleScreen(Screen):
    def __init__(self, app_ref, name, message, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text=name, font_size=20))
        layout.add_widget(Label(text=message, size_hint=(1, 0.8)))
        back_btn = Button(text="Home", size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: app_ref.go("Home"))
        layout.add_widget(back_btn)
        self.add_widget(layout)


class SenseiApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_path = ROOT
        db_path = ROOT / "data" / "sensei.db"
        self.conn = connect(str(db_path))
        self.engine = FlashCardEngine(self.conn)
        self.progress = ProgressTracker(self.conn)
        existing = {d["name"] for d in self.engine.list_decks()}
        if not existing:
            try:
                load_deck_from_json(self.engine, "ja", ROOT / "lang" / "ja" / "hiragana.json", "Hiragana")
            except Exception:
                pass
        self.deck_id = None
        decks = self.engine.list_decks()
        if decks:
            self.deck_id = decks[0]["id"]

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(self, name="Home"))
        self.sm.add_widget(FlashcardScreen(self, name="Flashcards"))
        if _HAS_TRANSLATE:
            self.sm.add_widget(TranslateScreen(self, name="Translate"))
        else:
            self.sm.add_widget(SimpleScreen(self, "Translate", "Translation not available on this device."))
        if _HAS_VOICE:
            self.sm.add_widget(VoiceScreen(self, name="Voice"))
        else:
            self.sm.add_widget(SimpleScreen(self, "Voice", "Voice not available on this device."))
        for n in ["Workbook", "Reading", "Listening", "Speaking", "News", "Shadowing", "Progress"]:
            self.sm.add_widget(SimpleScreen(self, n, f"{n} (coming soon in mobile)"))
        return self.sm

    def go(self, name):
        self.sm.current = name
        screen = self.sm.get_screen(name)
        if hasattr(screen, "on_enter"):
            screen.on_enter()


if __name__ == "__main__":
    SenseiApp().run()

"""Android native speech: TextToSpeech + SpeechRecognizer via pyjnius.

Used only on Android. Desktop uses core/voice.py (piper + faster-whisper).
Every entry point degrades gracefully: if pyjnius or a service is missing,
the caller gets False / empty text instead of a crash.
"""
import threading


def is_available():
    try:
        from jnius import autoclass  # noqa
        return True
    except Exception:
        return False


def _log(msg):
    print(f"[android_speech] {msg}")
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass


def _activity():
    from jnius import autoclass
    act = autoclass("org.kivy.android.PythonActivity").mActivity
    if act is None:
        raise RuntimeError("no activity yet")
    return act


def run_on_ui_thread(fn):
    """Post a callable onto the Android UI thread (required by the
    speech APIs, which refuse calls from background threads)."""
    from jnius import autoclass, PythonJavaClass, java_method

    class UiRunnable(PythonJavaClass):
        __javainterfaces__ = ["java/lang/Runnable"]
        __javacontext__ = "app"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.fn = fn

        @java_method("()V")
        def run(self):
            self.fn()

    Handler = autoclass("android.os.Handler")
    Looper = autoclass("android.os.Looper")
    handler = Handler(Looper.getMainLooper())
    handler.post(UiRunnable())


def _make_tts_listener():
    from jnius import PythonJavaClass, java_method

    class TtsInitListener(PythonJavaClass):
        __javainterfaces__ = ["android/speech/tts/TextToVoice$OnInitListener"]
        __javacontext__ = "app"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.status = -1

        @java_method("(I)V")
        def onInit(self, status):
            self.status = int(status)

    return TtsInitListener()


class AndroidTTS:
    """Thin wrapper over android.speech.tts.TextToSpeech.

    Created lazily: the Activity is not ready during module import.
    """

    QUEUE_FLUSH = 0
    QUEUE_ADD = 1

    def __init__(self, lang="ja"):
        self.lang = lang
        self._tts = None
        self._listener = None
        self._lock = threading.Lock()
        self.last_error = ""

    @property
    def ready(self):
        return self._tts is not None

    def _ensure(self):
        if self._tts is not None:
            return self._tts
        with self._lock:
            if self._tts is not None:
                return self._tts
            try:
                from jnius import autoclass
                activity = _activity()
                self._listener = _make_tts_listener()
                self._tts = autoclass("android.speech.tts.TextToSpeech")(
                    activity, self._listener
                )
                self.set_language(self.lang)
                _log(f"TextToSpeech created (init status {getattr(self._listener, 'status', '?')})")
            except Exception as e:
                self.last_error = f"{type(e).__name__}: {e}"
                _log(f"TextToSpeech failed: {self.last_error}")
                self._tts = None
        return self._tts

    def set_language(self, lang=None):
        tts = self._tts
        if not tts:
            return False
        try:
            from jnius import autoclass
            Locale = autoclass("java.util.Locale")
            code = (lang or self.lang).split("-")
            loc = Locale(code[0], code[1] if len(code) > 1 else "")
            result = int(tts.setLanguage(loc))
            _log(f"setLanguage({lang}) -> {result}")
            return result >= 0
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            _log(f"setLanguage failed: {self.last_error}")
            return False

    def speak(self, text):
        text = (text or "").strip()
        if not text:
            return False
        tts = self._ensure()
        if not tts:
            return False
        try:
            tts.speak(text, self.QUEUE_FLUSH, None)
            return True
        except Exception:
            try:
                tts.speak(text, self.QUEUE_FLUSH, None, "sensei")
                return True
            except Exception as e:
                self.last_error = f"{type(e).__name__}: {e}"
                _log(f"speak failed: {self.last_error}")
                return False

    def stop(self):
        try:
            if self._tts:
                self._tts.stop()
        except Exception:
            pass

    def shutdown(self):
        try:
            if self._tts:
                self._tts.shutdown()
        except Exception:
            pass
        self._tts = None


def _make_recognizer_listener(on_result, on_error):
    from jnius import PythonJavaClass, java_method

    class RecognizerListener(PythonJavaClass):
        __javainterfaces__ = ["android/speech/RecognitionListener"]
        __javacontext__ = "app"

        @java_method("(Landroid/os/Bundle;)V")
        def onResults(self, results):
            try:
                values = results.getStringArrayList("results")
                text = ""
                if values is not None and values.size() > 0:
                    text = str(values.get(0))
                _log(f"recognizer result: {text!r}")
                on_result(text)
            except Exception as e:
                _log(f"onResults parse failed: {e}")
                on_result("")

        @java_method("(ILandroid/os/Bundle;)V")
        def onError(self, error, extras):
            _log(f"recognizer error {int(error)}")
            on_error(int(error))

        @java_method("(Landroid/os/Bundle;)V")
        def onReadyForSpeech(self, params):
            pass

        @java_method("()V")
        def onBeginningOfSpeech(self):
            pass

        @java_method("(I)V")
        def onRmsChanged(self, rms):
            pass

        @java_method("([B)V")
        def onBufferReceived(self, buffer):
            pass

        @java_method("()V")
        def onEndOfSpeech(self):
            pass

        @java_method("(I)V")
        def onPartialResults(self, partial):
            pass

        @java_method("(I)V")
        def onEvent(self, event):
            pass

    return RecognizerListener()


class AndroidSTT:
    """SpeechRecognizer wrapper."""

    def __init__(self, lang="ja"):
        self.lang = lang
        self._recognizer = None
        self._listener = None
        self.last_error = ""

    def _ensure(self):
        if self._recognizer is not None:
            return self._recognizer
        try:
            from jnius import autoclass
            activity = _activity()
            self._recognizer = autoclass("android.speech.SpeechRecognizer").createSpeechRecognizer(activity)
            _log("SpeechRecognizer created")
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            _log(f"SpeechRecognizer failed: {self.last_error}")
            self._recognizer = None
        return self._recognizer

    def listen(self, on_result, on_error):
        def start():
            rec = self._ensure()
            if not rec:
                on_error(-1)
                return
            try:
                from jnius import autoclass
                RecognizerIntent = autoclass("android.speech.RecognizerIntent")
                intent = RecognizerIntent.ACTION_RECOGNIZE_SPEECH
                intent.putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM,
                )
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, self.lang)
                intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, False)
                self._listener = _make_recognizer_listener(on_result, on_error)
                rec.setRecognitionListener(self._listener)
                rec.startListening(intent)
            except Exception as e:
                self.last_error = f"{type(e).__name__}: {e}"
                _log(f"startListening failed: {self.last_error}")
                on_error(-1)

        try:
            run_on_ui_thread(start)
            return True
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            _log(f"run_on_ui_thread failed: {self.last_error}")
            on_error(-1)
            return False

    def stop(self):
        try:
            if self._recognizer:
                self._recognizer.stopListening()
        except Exception:
            pass

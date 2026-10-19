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


def _activity():
    from jnius import autoclass
    return autoclass("org.kivy.android.PythonActivity").mActivity


class _TtsInitListener:
    pass


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
    """Thin wrapper over android.speech.tts.TextToVoice."""

    QUEUE_FLUSH = 0
    QUEUE_ADD = 1

    def __init__(self, lang="ja"):
        self.ok = False
        self.lang = lang
        self._tts = None
        try:
            from jnius import autoclass
            self._tts = autoclass("android.speech.tts.TextToSpeech")(
                _activity(), _make_tts_listener()
            )
            self.ok = True
        except Exception:
            self._tts = None

    def set_language(self, lang=None):
        if not self._tts:
            return False
        try:
            from jnius import autoclass
            Locale = autoclass("java.util.Locale")
            code = (lang or self.lang).split("-")
            loc = Locale(code[0], code[1] if len(code) > 1 else "")
            result = self._tts.setLanguage(loc)
            return int(result) >= 0
        except Exception:
            return False

    def speak(self, text):
        if not self._tts:
            return False
        try:
            self._tts.speak(text, self.QUEUE_FLUSH, None)
            return True
        except Exception:
            try:
                self._tts.speak(text, self.QUEUE_FLUSH, None, "sensei")
                return True
            except Exception:
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
                values = results.getStringArrayList(
                    results.keySet().toArray()[0]
                    if False else "results"
                )
                text = ""
                if values is not None and values.size() > 0:
                    text = str(values.get(0))
                on_result(text)
            except Exception:
                on_result("")

        @java_method("(ILandroid/os/Bundle;)V")
        def onError(self, error, extras):
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
    """SpeechRecognizer wrapper. Must be created and used on the UI thread."""

    def __init__(self, lang="ja"):
        self.ok = False
        self.lang = lang
        self._recognizer = None
        self._listener = None
        try:
            from jnius import autoclass
            self._recognizer = autoclass("android.speech.SpeechRecognizer").createSpeechRecognizer()
            self.ok = True
        except Exception:
            self._recognizer = None

    def listen(self, on_result, on_error):
        if not self._recognizer:
            on_error(-1)
            return False
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
            self._recognizer.setRecognitionListener(self._listener)
            self._recognizer.startListening(intent)
            return True
        except Exception:
            on_error(-1)
            return False

    def stop(self):
        try:
            if self._recognizer:
                self._recognizer.stopListening()
        except Exception:
            pass

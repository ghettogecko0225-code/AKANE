"""Offline speech recognition with Vosk.

Works on Android and desktop. On Android the microphone is captured with
android.media.AudioRecord (pyjnius) because sounddevice has no Android
support; on desktop it uses sounddevice.

The Japanese model is bundled in assets/models/vosk and is Apache 2.0, so it
can be redistributed in a commercial app.
"""
import json
import threading
from pathlib import Path

SAMPLE_RATE = 16000

_model_cache = {}
_lock = threading.Lock()


def model_dir(root):
    root = Path(root)
    candidates = [root / "assets" / "asr", root / "assets" / "models" / "vosk"]
    for base in candidates:
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.is_dir() and (child / "am" / "final.mdl").exists():
                return child
    return None


def is_available(root):
    try:
        import vosk  # noqa
    except Exception:
        return False
    return model_dir(root) is not None


def _load_model(root):
    path = model_dir(root)
    if path is None:
        return None
    key = str(path)
    with _lock:
        if key in _model_cache:
            return _model_cache[key]
        try:
            from vosk import Model, SetLogLevel
            SetLogLevel(-1)
            model = Model(str(path))
            _model_cache[key] = model
            return model
        except Exception:
            _model_cache[key] = None
            return None


def recognize_pcm(root, pcm_bytes, sample_rate=SAMPLE_RATE):
    """Recognize 16-bit little-endian mono PCM. Returns text ('' on failure)."""
    model = _load_model(root)
    if model is None:
        return ""
    try:
        from vosk import KaldiRecognizer
        rec = KaldiRecognizer(model, sample_rate)
        rec.AcceptWaveform(pcm_bytes)
        result = json.loads(rec.FinalResult())
        return (result.get("text") or "").strip()
    except Exception:
        return ""


def capture_android_pcm(seconds=5.0, sample_rate=SAMPLE_RATE):
    """Record mono 16-bit PCM with android.media.AudioRecord."""
    from jnius import autoclass
    AudioRecord = autoclass("android.media.AudioRecord")
    MediaRecorder = autoclass("android.media.MediaRecorder")
    buffer_size = int(
        AudioRecord.getMinBufferSize(
            sample_rate, AudioRecord.CHANNEL_IN_MONO, AudioRecord.ENCODING_PCM_16BIT
        )
    )
    buffer_size = max(buffer_size, 4096)
    recorder = AudioRecord(
        MediaRecorder.AudioSource.VOICE_RECOGNITION,
        sample_rate,
        AudioRecord.CHANNEL_IN_MONO,
        AudioRecord.ENCODING_PCM_16BIT,
        buffer_size,
    )
    if recorder.getState() != AudioRecord.STATE_INITIALIZED:
        raise RuntimeError("AudioRecord failed to initialize")
    recorder.startRecording()
    total = bytearray()
    try:
        import time
        deadline = time.time() + seconds
        while time.time() < deadline:
            chunk = bytearray(buffer_size)
            read = recorder.read(chunk, 0, len(chunk))
            if read <= 0:
                break
            total.extend(chunk[:read])
    finally:
        try:
            recorder.stop()
        except Exception:
            pass
        try:
            recorder.release()
        except Exception:
            pass
    return bytes(total)


def capture_desktop_pcm(seconds=5.0, sample_rate=SAMPLE_RATE):
    import numpy as np
    import sounddevice as sd
    rec = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    return rec[:, 0].tobytes()


def capture_pcm(root, seconds=5.0):
    try:
        from jnius import autoclass  # noqa
        return capture_android_pcm(seconds)
    except Exception:
        return capture_desktop_pcm(seconds)


def listen(root, seconds=5.0, on_done=None):
    """Capture the microphone and recognize it. Calls on_done(text)."""
    def worker():
        try:
            pcm = capture_pcm(root, seconds)
            text = recognize_pcm(root, pcm)
        except Exception:
            text = ""
        if on_done:
            on_done(text)

    threading.Thread(target=worker, daemon=True).start()

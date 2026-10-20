import os
import sys
import time
import wave
import threading
import tempfile
import pathlib

try:
    import onnxruntime  # noqa
except Exception:
    pass
try:
    import faster_whisper  # noqa
except Exception:
    pass

import numpy as np

from core.paths import models_root

MODELS_DIR = models_root()
PIPER_DIR = MODELS_DIR / "piper"
JAPANESE_VOICE = "ja_JP-hi_fi_captain-medium"

_piper_cache = {}


def _load_piper(name):
    if name in _piper_cache:
        return _piper_cache[name]
    from piper import PiperVoice
    v = PiperVoice.load(
        str(PIPER_DIR / f"{name}.onnx"),
        config_path=str(PIPER_DIR / f"{name}.onnx.json"),
    )
    _piper_cache[name] = v
    return v


def synthesize_to_wav(text, out_path, voice_name=JAPANESE_VOICE):
    v = _load_piper(voice_name)
    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(v.config.sample_rate)
        v.synthesize_wav(text, wf)


_whisper_model = None


def get_transcriber():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model


def transcribe_samples(samples_f32, root=None):
    """Transcribe float32 samples. Uses sherpa-onnx (fast, accurate for
    Japanese) and falls back to faster-whisper."""
    if root is not None:
        try:
            from core import asr
            pcm = (samples_f32 * 32767).astype("int16").tobytes()
            text = asr.recognize_pcm(str(root), pcm)
            if text:
                return text
        except Exception:
            pass
    m = get_transcriber()
    segments, _ = m.transcribe(samples_f32, language="ja", beam_size=1)
    return " ".join(seg.text.strip() for seg in segments).strip()


def transcribe_pcm(root, pcm_bytes):
    """Offline Japanese recognition with the bundled sherpa-onnx model."""
    try:
        from core import asr
        return asr.recognize_pcm(root, pcm_bytes)
    except Exception:
        return ""


def play_wav(path):
    import sounddevice as sd
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate()
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    stream = sd.OutputStream(samplerate=rate, channels=1, dtype="int16")
    stream.start()
    try:
        for i in range(0, len(data), 4096):
            stream.write(data[i:i + 4096].reshape(-1, 1))
    finally:
        stream.stop()
        stream.close()


def record_samples(seconds=4.0, sample_rate=16000):
    import sounddevice as sd
    rec = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    return rec[:, 0]


def speak(text, root=None):
    """Speak Japanese: pre-rendered audio pack first, piper as fallback."""
    if root is not None:
        try:
            from core.audio_pack import AudioPlayer
            player = AudioPlayer(root)
            if player.play(text):
                return True
        except Exception:
            pass
    try:
        d = pathlib.Path(tempfile.gettempdir()) / "sensei_tts"
        d.mkdir(exist_ok=True)
        out = d / f"utt_{int(time.time() * 1000)}.wav"
        synthesize_to_wav(text, str(out))
        play_wav(str(out))
        return True
    except Exception:
        return False

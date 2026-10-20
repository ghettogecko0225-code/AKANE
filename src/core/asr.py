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


def _import_vosk():
    """Import vosk, working around its Linux-only platform check.

    vosk's open_dll() only accepts sys.platform 'linux'/'win32'/'darwin'.
    Android reports 'android', so we present 'linux' for the import.
    """
    import sys
    original = sys.platform
    if original == "android":
        sys.platform = "linux"
    try:
        import vosk
        return vosk
    finally:
        sys.platform = original


def is_available(root):
    try:
        _import_vosk()
    except Exception:
        return False
    return model_dir(root) is not None


def _log(msg):
    line = f"[asr] {msg}"
    print(line)
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass
    try:
        import os
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        log_dir = root / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "asr_log.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _load_model(root):
    path = model_dir(root)
    if path is None:
        return None
    key = str(path)
    with _lock:
        if key in _model_cache:
            return _model_cache[key]
        try:
            vosk = _import_vosk()
            vosk.SetLogLevel(-1)
            model = vosk.Model(str(path))
            _model_cache[key] = model
            _log(f"vosk model loaded: {path.name}")
            return model
        except Exception as e:
            _log(f"vosk model load failed: {type(e).__name__}: {e}")
            _model_cache[key] = None
            return None


def recognize_pcm(root, pcm_bytes, sample_rate=SAMPLE_RATE):
    """Recognize 16-bit little-endian mono PCM. Returns text ('' on failure)."""
    model = _load_model(root)
    if model is None:
        return ""
    try:
        vosk = _import_vosk()
        rec = vosk.KaldiRecognizer(model, sample_rate)
        rec.AcceptWaveform(pcm_bytes)
        result = json.loads(rec.FinalResult())
        text = (result.get("text") or "").strip()
        _log(f"recognized: {text!r}")
        return text
    except Exception as e:
        _log(f"recognize failed: {type(e).__name__}: {e}")
        return ""


def _rms_peak(pcm_bytes):
    if len(pcm_bytes) < 2:
        return 0.0, 0
    import array
    samples = array.array("h")
    samples.frombytes(pcm_bytes[: len(pcm_bytes) - (len(pcm_bytes) % 2)])
    if not samples:
        return 0.0, 0
    total = 0
    peak = 0
    for s in samples:
        total += s * s
        if s > peak:
            peak = s
        elif -s > peak:
            peak = -s
    return (total / len(samples)) ** 0.5, peak


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
    buffer_size = max(buffer_size * 2, 8192)
    recorder = None
    for source_name in ("VOICE_RECOGNITION", "MIC", "VOICE_COMMUNICATION"):
        try:
            source = getattr(MediaRecorder.AudioSource, source_name)
        except Exception:
            continue
        try:
            candidate = AudioRecord(
                source,
                sample_rate,
                AudioRecord.CHANNEL_IN_MONO,
                AudioRecord.ENCODING_PCM_16BIT,
                buffer_size,
            )
        except Exception:
            continue
        if candidate.getState() == AudioRecord.STATE_INITIALIZED:
            recorder = candidate
            _log(f"AudioRecord ready (source={source_name}, buffer={buffer_size})")
            break
        try:
            candidate.release()
        except Exception:
            pass
    if recorder is None:
        raise RuntimeError("AudioRecord failed to initialize")
    recorder.startRecording()
    total = bytearray()
    try:
        import time
        deadline = time.time() + seconds
        idle = 0
        while time.time() < deadline:
            chunk = bytearray(buffer_size)
            try:
                read = recorder.read(chunk, 0, len(chunk))
            except Exception as e:
                _log(f"AudioRecord.read failed: {e}")
                break
            if read > 0:
                total.extend(chunk[:read])
                idle = 0
            else:
                # A short read is not a failure: keep waiting for data.
                idle += 1
                time.sleep(0.02)
                if idle > 200:
                    _log("AudioRecord returned no data repeatedly")
                    break
    finally:
        try:
            recorder.stop()
        except Exception:
            pass
        try:
            recorder.release()
        except Exception:
            pass
    pcm = bytes(total)
    rms, peak = _rms_peak(pcm)
    _log(f"captured {len(pcm)} bytes, rms={rms:.0f}, peak={peak}")
    return pcm


def capture_desktop_pcm(seconds=5.0, sample_rate=SAMPLE_RATE):
    import numpy as np
    import sounddevice as sd
    rec = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    return rec[:, 0].tobytes()


def capture_pcm(root, seconds=5.0):
    import sys
    if sys.platform == "android":
        return capture_android_pcm(seconds)
    return capture_desktop_pcm(seconds)


def listen_and_recognize(root, seconds=5.0):
    """Record and recognise in one pass, streaming audio into Vosk.

    Returns (text, info) where info has bytes/rms/peak so the UI can say
    whether the failure was the microphone, the volume, or the language.
    """
    import sys
    info = {"bytes": 0, "rms": 0.0, "peak": 0}
    model = _load_model(root)
    if model is None:
        return "", info
    vosk = _import_vosk()
    try:
        rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    except Exception as e:
        _log(f"KaldiRecognizer failed: {e}")
        return "", info
    pcm = capture_pcm(root, seconds)
    info["bytes"] = len(pcm)
    info["rms"], info["peak"] = _rms_peak(pcm)
    if not pcm:
        _log("no audio captured")
        return "", info
    try:
        rec.AcceptWaveform(pcm)
        result = json.loads(rec.FinalResult())
        text = (result.get("text") or "").strip()
        if not text:
            try:
                partial = json.loads(rec.PartialResult() or "{}")
                text = (partial.get("text") or "").strip()
            except Exception:
                text = ""
        _log(f"recognized: {text!r} (bytes={info['bytes']}, rms={info['rms']:.0f})")
        return text, info
    except Exception as e:
        _log(f"recognize failed: {type(e).__name__}: {e}")
        return "", info


def listen(root, seconds=5.0, on_done=None):
    """Capture the microphone and recognize it. Calls on_done(text, info)."""
    def worker():
        try:
            text, info = listen_and_recognize(root, seconds)
        except Exception as e:
            _log(f"listen failed: {type(e).__name__}: {e}")
            text, info = "", {"bytes": 0, "rms": 0.0, "peak": 0}
        if on_done:
            on_done(text, info)

    threading.Thread(target=worker, daemon=True).start()

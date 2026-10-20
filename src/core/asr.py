"""Offline speech recognition with Vosk.

Works on Android and desktop. On Android the microphone is captured with
android.media.AudioRecord (pyjnius) because sounddevice has no Android
support; on desktop it uses sounddevice.

The Japanese model is bundled in assets/models/vosk and is Apache 2.0, so it
can be redistributed in a commercial app.
"""
import json
import os
import shutil
import threading
import urllib.request
import zipfile
from pathlib import Path

SAMPLE_RATE = 16000

BIG_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip"
BIG_MODEL_NAME = "vosk-model-ja-0.22"
SMALL_MODEL_NAME = "vosk-model-small-ja-0.22"

_model_cache = {}
_lock = threading.Lock()


def bundled_model_dir(root):
    """The small model shipped inside the app."""
    root = Path(root)
    candidates = [root / "assets" / "asr", root / "assets" / "models" / "vosk"]
    for base in candidates:
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.is_dir() and (child / "am" / "final.mdl").exists():
                return child
    return None


def downloaded_model_dir(root):
    """The big model, if the user has downloaded it."""
    path = Path(root) / "data" / "asr" / BIG_MODEL_NAME
    if (path / "am" / "final.mdl").exists():
        return path
    return None


def model_dir(root):
    """The model in use: the downloaded big one if present, else bundled."""
    return downloaded_model_dir(root) or bundled_model_dir(root)


def model_info(root):
    """Describe which model is active and what else is available."""
    active = model_dir(root)
    big = downloaded_model_dir(root)
    bundled = bundled_model_dir(root)
    if active is None:
        return {"active": "none", "detail": "no model found"}
    name = active.name
    if active == big:
        return {
            "active": "big",
            "name": name,
            "detail": "Big model (1GB) - best accuracy",
            "has_big": True,
            "has_small": bundled is not None,
        }
    return {
        "active": "small",
        "name": name,
        "detail": "Small model (bundled) - fast, less accurate",
        "has_big": False,
        "has_small": True,
    }


def reset_model_cache():
    """Drop the loaded model so the next use picks up a new one."""
    with _lock:
        _model_cache.clear()


def delete_big_model(root):
    """Remove the downloaded big model and free the space."""
    reset_model_cache()
    target = Path(root) / "data" / "asr"
    if not target.is_dir():
        return False
    removed = False
    for child in target.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
            removed = True
        except Exception:
            pass
    return removed


def download_big_model(root, on_progress=None, on_done=None, on_error=None):
    """Download, unzip and install the 1GB Japanese model.

    Runs in a background thread. on_progress(done_bytes, total_bytes) is
    called with the download progress.
    """

    def worker():
        try:
            target = Path(root) / "data" / "asr"
            target.mkdir(parents=True, exist_ok=True)
            zip_path = target / (BIG_MODEL_NAME + ".zip")
            _log(f"downloading {BIG_MODEL_URL}")
            with urllib.request.urlopen(BIG_MODEL_URL, timeout=120) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                done = 0
                with open(zip_path, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 512)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        if on_progress:
                            on_progress(done, total)
            _log(f"download complete ({done} bytes), extracting")
            with zipfile.ZipFile(zip_path) as archive:
                archive.extractall(target)
            try:
                zip_path.unlink()
            except Exception:
                pass
            installed = target / BIG_MODEL_NAME
            if not (installed / "am" / "final.mdl").exists():
                raise RuntimeError("model archive did not contain the model")
            reset_model_cache()
            _log(f"big model installed at {installed}")
            if on_done:
                on_done(str(installed))
        except Exception as e:
            _log(f"big model download failed: {type(e).__name__}: {e}")
            if on_error:
                on_error(e)

    threading.Thread(target=worker, daemon=True).start()


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


def available_ram_mb():
    """Free RAM in MB, or None if it cannot be determined."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except Exception:
        pass
    return None


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
            _log(f"vosk model load failed for {path.name}: {type(e).__name__}: {e}")
            # If the big model cannot be loaded (usually out of memory on a
            # small phone) fall back to the bundled small model.
            fallback = bundled_model_dir(root)
            if fallback is not None and fallback != path:
                _log(f"falling back to {fallback.name}")
                try:
                    vosk = _import_vosk()
                    vosk.SetLogLevel(-1)
                    model = vosk.Model(str(fallback))
                    _model_cache[key] = model
                    _model_cache[str(fallback)] = model
                    return model
                except Exception as e2:
                    _log(f"small model load failed: {type(e2).__name__}: {e2}")
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


def _resample_pcm(pcm, src_rate, dst_rate=SAMPLE_RATE):
    """Linear resample of 16-bit PCM (used when the mic refuses 16 kHz)."""
    if src_rate == dst_rate or not pcm:
        return pcm
    import array
    src = array.array("h")
    src.frombytes(pcm[: len(pcm) - (len(pcm) % 2)])
    if len(src) < 2:
        return pcm
    n_out = int(len(src) * dst_rate / src_rate)
    out = array.array("h", bytes(2 * n_out))
    step = src_rate / dst_rate
    for i in range(n_out):
        pos = i * step
        i0 = int(pos)
        if i0 >= len(src) - 1:
            out[i] = src[-1]
            continue
        frac = pos - i0
        out[i] = int(src[i0] * (1 - frac) + src[i0 + 1] * frac)
    return out.tobytes()


def capture_android_pcm(seconds=5.0, sample_rate=SAMPLE_RATE):
    """Record mono 16-bit PCM with android.media.AudioRecord.

    The channel/encoding constants live on android.media.AudioFormat, not
    on AudioRecord. Some devices refuse VOICE_RECOGNITION, so several
    sources and sample rates are tried before giving up.
    """
    from jnius import autoclass
    AudioRecord = autoclass("android.media.AudioRecord")
    AudioFormat = autoclass("android.media.AudioFormat")
    channel = AudioFormat.CHANNEL_IN_MONO
    encoding = AudioFormat.ENCODING_PCM_16BIT

    try:
        AudioManager = autoclass("android.media.AudioManager")
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        manager = activity.getSystemService("audio")
        mics = manager.getMicrophones()
        _log(f"device microphones: {mics.size() if mics else 0}")
    except Exception as e:
        _log(f"microphone check failed: {type(e).__name__}: {e}")

    # android.media.MediaRecorder.AudioSource values (read as plain ints so
    # we do not depend on nested-class access through pyjnius).
    SOURCES = [
        ("MIC", 1),
        ("VOICE_RECOGNITION", 6),
        ("VOICE_COMMUNICATION", 7),
        ("DEFAULT", 0),
    ]
    rates = [sample_rate, 48000, 44100]
    recorder = None
    used_rate = sample_rate
    for rate in rates:
        try:
            min_buffer = int(AudioRecord.getMinBufferSize(rate, channel, encoding))
        except Exception as e:
            min_buffer = 0
            _log(f"getMinBufferSize({rate}) raised {e}")
        if min_buffer <= 0:
            _log(f"getMinBufferSize({rate}) -> {min_buffer}")
        buffer_size = max(min_buffer * 2, 8192)
        for source_name, source_value in SOURCES:
            try:
                candidate = AudioRecord(
                    source_value, rate, channel, encoding, buffer_size
                )
            except Exception as e:
                _log(
                    f"AudioRecord({source_name},{rate}) raised "
                    f"{type(e).__name__}: {e}"
                )
                continue
            try:
                state = candidate.getState()
            except Exception as e:
                state = -1
                _log(f"getState failed: {e}")
            if state == AudioRecord.STATE_INITIALIZED:
                recorder = candidate
                used_rate = rate
                _log(
                    f"AudioRecord ready: source={source_name} rate={rate} "
                    f"buffer={buffer_size}"
                )
                break
            _log(f"AudioRecord({source_name},{rate}) state={state}")
            try:
                candidate.release()
            except Exception:
                pass
        if recorder is not None:
            break
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
    _log(f"captured {len(pcm)} bytes at {used_rate}Hz, rms={rms:.0f}, peak={peak}")
    if used_rate != sample_rate:
        pcm = _resample_pcm(pcm, used_rate, sample_rate)
        _log(f"resampled to {sample_rate}Hz: {len(pcm)} bytes")
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


def _normalize_gain(pcm, target_peak=12000, max_gain=400.0):
    """Scale quiet microphone audio up to a level the recogniser can use.

    Phone microphones often hand back very low amplitude audio (rms of a
    few counts), which is effectively silence to a speech model.
    """
    import array
    if not pcm:
        return pcm
    samples = array.array("h")
    samples.frombytes(pcm[: len(pcm) - (len(pcm) % 2)])
    if not samples:
        return pcm
    peak = 0
    for s in samples:
        a = s if s >= 0 else -s
        if a > peak:
            peak = a
    if peak == 0 or peak >= target_peak:
        return pcm
    gain = min(target_peak / peak, max_gain)
    for i, s in enumerate(samples):
        v = int(s * gain)
        samples[i] = 32767 if v > 32767 else (-32768 if v < -32768 else v)
    out = samples.tobytes()
    rms2, peak2 = _rms_peak(out)
    _log(f"gain applied x{gain:.1f}: rms {rms2:.0f}, peak {peak2}")
    return out


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
    info["raw_peak"] = info["peak"]
    if not pcm:
        _log("no audio captured")
        return "", info
    pcm = _normalize_gain(pcm)
    info["rms"], info["peak"] = _rms_peak(pcm)
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

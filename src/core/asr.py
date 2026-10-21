"""Offline speech recognition with sherpa-onnx.

sherpa-onnx runs a streaming Zipformer transducer built for Japanese and
English (ReazonSpeech 2025 corpus). The int8 model is 70MB, loads in about
3 seconds and transcribes faster than real time, all on-device.

The Android build gets sherpa-onnx from a prebuilt Android wheel
(cp314-cp314-android_24_arm64_v8a), so no compiler is needed.

Audio capture on Android uses android.media.AudioRecord through pyjnius
(sounddevice has no Android support).
"""
import json
import threading
from pathlib import Path

SAMPLE_RATE = 16000
SHERPA_DIRNAME = "asr_sherpa"

_lock = threading.Lock()
_sherpa_cache = {}


def _log(msg):
    print(f"[asr] {msg}")
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass
    try:
        from pathlib import Path as _P
        root = _P(__file__).resolve().parents[2]
        log_dir = root / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "asr_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[asr] {msg}\n")
    except Exception:
        pass


def sherpa_model_dir(root):
    """Folder holding the zipformer model (encoder/decoder/joiner/tokens)."""
    root = Path(root)
    for base in (root / "assets" / SHERPA_DIRNAME, root / "data" / SHERPA_DIRNAME):
        if not base.is_dir():
            continue
        tokens = base / "tokens.txt"
        encoders = sorted(base.glob("encoder*.int8.onnx"))
        decoders = sorted(base.glob("decoder*.int8.onnx"))
        joiners = sorted(base.glob("joiner*.int8.onnx"))
        if tokens.exists() and encoders and decoders and joiners:
            return base
    return None


def sherpa_available(root):
    try:
        import sherpa_onnx  # noqa
    except Exception:
        return False
    return sherpa_model_dir(root) is not None


def is_available(root):
    """True when offline recognition is usable."""
    return sherpa_available(root)


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


def model_info(root):
    """Describe the active engine."""
    if sherpa_available(root):
        return {
            "active": "sherpa",
            "name": "sherpa-onnx zipformer ja-en (int8)",
            "detail": "Best accuracy - Japanese + English, 70MB, fully offline",
        }
    return {"active": "none", "name": "none", "detail": "no model found"}


def reset_model_cache():
    """Drop the loaded model so the next use picks up a new one."""
    with _lock:
        _sherpa_cache.clear()


def _load_sherpa(root):
    base = sherpa_model_dir(root)
    if base is None:
        return None
    key = str(base)
    with _lock:
        if key in _sherpa_cache:
            return _sherpa_cache[key]
        try:
            import sherpa_onnx
            tokens = sorted(base.glob("tokens.txt"))[0]
            encoder = sorted(base.glob("encoder*.int8.onnx"))[0]
            decoder = sorted(base.glob("decoder*.int8.onnx"))[0]
            joiner = sorted(base.glob("joiner*.int8.onnx"))[0]
            rec = sherpa_onnx.OfflineRecognizer.from_transducer(
                tokens=str(tokens),
                encoder=str(encoder),
                decoder=str(decoder),
                joiner=str(joiner),
                num_threads=2,
                provider="cpu",
            )
            _sherpa_cache[key] = rec
            _log(f"sherpa recognizer ready: {base.name}")
            return rec
        except Exception as e:
            _log(f"sherpa load failed: {type(e).__name__}: {e}")
            _sherpa_cache[key] = None
            return None


def _pcm_to_float32(pcm_bytes):
    """16-bit PCM -> array of float32 samples (no numpy needed, so this
    works on Android where numpy is not installed)."""
    import array
    ints = array.array("h")
    ints.frombytes(pcm_bytes[: len(pcm_bytes) - (len(pcm_bytes) % 2)])
    floats = array.array("f", bytes(4 * len(ints)))
    for i, value in enumerate(ints):
        floats[i] = value / 32768.0
    return floats


def recognize_pcm(root, pcm_bytes, sample_rate=SAMPLE_RATE):
    """Recognize 16-bit little-endian mono PCM. Returns the text."""
    rec = _load_sherpa(root)
    if rec is None:
        return ""
    try:
        samples = _pcm_to_float32(pcm_bytes)
        stream = rec.create_stream()
        stream.accept_waveform(sample_rate, samples)
        rec.decode_stream(stream)
        text = (stream.result.text or "").strip()
        _log(f"sherpa recognized: {text!r}")
        return text
    except Exception as e:
        _log(f"sherpa recognize failed: {type(e).__name__}: {e}")
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


def listen_and_recognize(root, seconds=5.0):
    """Record and recognise in one pass.

    Returns (text, info) where info has bytes/rms/peak so the UI can say
    whether the failure was the microphone, the volume, or the language.
    """
    info = {"bytes": 0, "rms": 0.0, "peak": 0}
    pcm = capture_pcm(root, seconds)
    info["bytes"] = len(pcm)
    info["rms"], info["peak"] = _rms_peak(pcm)
    info["raw_peak"] = info["peak"]
    if not pcm:
        _log("no audio captured")
        return "", info
    pcm = _normalize_gain(pcm)
    info["rms"], info["peak"] = _rms_peak(pcm)
    text = recognize_pcm(root, pcm)
    _log(f"recognized: {text!r} (bytes={info['bytes']}, rms={info['rms']:.0f})")
    return text, info


def listen(root, seconds=5.0, on_done=None):
    """Capture the microphone and recognize it. Calls on_done(text, info)."""
    def worker():
        try:
            text, info = listen_and_recognize(root, seconds)
        except Exception as e:
            _log(f"listen failed: {type(e).__name__}: {e}")
            text, info = "", {"bytes": 0, "rms": 0.0, "peak": 0, "raw_peak": 0}
        if on_done:
            on_done(text, info)

    threading.Thread(target=worker, daemon=True).start()

import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request

from core.paths import models_root

try:
    import ctranslate2
    import sentencepiece
    _HAS_CT2 = True
except Exception:
    _HAS_CT2 = False

TRANS_DIR = models_root() / "translation"

_MODELS = {}


def has_local_models():
    if not _HAS_CT2:
        return False
    return (TRANS_DIR / "ja-en").is_dir() or (TRANS_DIR / "en-ja").is_dir()


def _load(direction):
    if direction in _MODELS:
        return _MODELS[direction]
    if direction == "ja-en":
        d = TRANS_DIR / "ja-en" / "opus-mt-ja-en-ct2"
    else:
        d = TRANS_DIR / "en-ja" / "opus-tatoeba-en-ja-ct2"
    tr = ctranslate2.Translator(str(d), device="cpu", compute_type="int8")
    sp_src = sentencepiece.SentencePieceProcessor(model_file=str(d / "source.spm"))
    sp_tgt = sentencepiece.SentencePieceProcessor(model_file=str(d / "target.spm"))
    _MODELS[direction] = (tr, sp_src, sp_tgt)
    return _MODELS[direction]


def _is_japanese(text):
    for ch in text:
        cp = ord(ch)
        if (0x3040 <= cp <= 0x30FF) or (0x4E00 <= cp <= 0x9FFF) or (0x3400 <= cp <= 0x4DBF):
            return True
    return False


def _translate_local(text, direction):
    tr, sp_src, sp_tgt = _load(direction)
    toks = sp_src.encode(text, out_type=str) + ["</s>"]
    res = tr.translate_batch([toks])
    return sp_tgt.decode(res[0].hypotheses[0])


def _ssl_context():
    """SSL context with a real CA bundle.

    Android's Python has no system CA store, so HTTPS fails with
    "certificate verify failed" unless we point it at certifi's bundle.
    """
    import ssl
    try:
        import certifi
        path = certifi.where()
        return ssl.create_default_context(cafile=path)
    except Exception:
        return ssl.create_default_context()


def _google_request(text, target, host):
    q = urllib.parse.quote(text)
    url = (
        f"https://{host}/translate_a/single?client=gtx&sl=auto"
        f"&tl={target}&dt=t&q={q}"
    )
    with urllib.request.urlopen(url, timeout=15, context=_ssl_context()) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data or not data[0]:
        raise RuntimeError("translator returned nothing")
    return "".join(part[0] for part in data[0] if part and part[0])


def _mymemory_request(text, target):
    source = "ja" if target == "en" else "en"
    q = urllib.parse.quote(text)
    url = (
        f"https://api.mymemory.translated.net/get?q={q}&langpair={source}|{target}"
    )
    with urllib.request.urlopen(url, timeout=15, context=_ssl_context()) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("responseStatus") != 200:
        raise RuntimeError("translator rejected the request")
    translated = (data.get("responseData") or {}).get("translatedText")
    if not translated:
        raise RuntimeError("translator returned nothing")
    return translated


PROVIDERS = (
    ("google", lambda text, target: _google_request(text, target, "translate.googleapis.com")),
    ("google-alt", lambda text, target: _google_request(text, target, "translate.google.com")),
    ("mymemory", _mymemory_request),
)


def _translate_online(text, direction):
    target = "en" if direction == "ja-en" else "ja"
    last_error = None
    for name, provider in PROVIDERS:
        try:
            return provider(text, target)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_error = "translator is busy right now, try again in a minute"
            else:
                last_error = f"translator error ({exc.code})"
        except urllib.error.URLError as exc:
            last_error = f"no internet connection ({exc.reason})"
        except RuntimeError as exc:
            last_error = str(exc)
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(last_error or "translation failed")


def translate(text, direction=None):
    text = (text or "").strip()
    if not text:
        return ""
    if direction is None:
        direction = "ja-en" if _is_japanese(text) else "en-ja"
    if _HAS_CT2 and has_local_models():
        try:
            return _translate_local(text, direction)
        except Exception:
            pass
    return _translate_online(text, direction)

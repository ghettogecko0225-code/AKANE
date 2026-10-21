import json
import pathlib
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


def _translate_online(text, direction):
    target = "en" if direction == "ja-en" else "ja"
    q = urllib.parse.quote(text)
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto"
        f"&tl={target}&dt=t&q={q}"
    )
    with urllib.request.urlopen(url, timeout=15, context=_ssl_context()) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(part[0] for part in data[0] if part and part[0])


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

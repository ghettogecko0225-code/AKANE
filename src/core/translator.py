import pathlib
import ctranslate2
import sentencepiece

from core.paths import models_root

TRANS_DIR = models_root() / "translation"

_MODELS = {}


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


def translate(text, direction=None):
    text = (text or "").strip()
    if not text:
        return ""
    if direction is None:
        direction = "ja-en" if _is_japanese(text) else "en-ja"
    tr, sp_src, sp_tgt = _load(direction)
    toks = sp_src.encode(text, out_type=str) + ["</s>"]
    res = tr.translate_batch([toks])
    return sp_tgt.decode(res[0].hypotheses[0])

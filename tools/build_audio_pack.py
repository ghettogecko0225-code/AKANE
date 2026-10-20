"""Render a compact Japanese audio pack for offline playback.

Reads the curated content (kana decks, kanji starter, immersion passages,
news, dialogues) plus the N5 example sentences, synthesizes each with the
local piper voice and encodes to OGG so the phone can play it without
depending on a device TTS voice.

Run with the Studio venv:
    python tools/build_audio_pack.py
"""
import json
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from core.voice import synthesize_to_wav  # noqa: E402

OUT_DIR = ROOT / "assets" / "audio"
FFMPEG = "ffmpeg"


def collect_texts():
    items = []

    for fname in ["hiragana.json", "katakana.json", "kanji_n5.json"]:
        path = ROOT / "lang" / "ja" / fname
        if not path.exists():
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            items.append((f"card_{fname[:-5]}_{row['front']}", row["front"]))

    for fname in ["dialogues.json", "articles.json", "passages.json"]:
        path = ROOT / "assets" / "immersion" / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, row in enumerate(data):
            for key in ["line", "text", "title", "translation"]:
                value = row.get(key)
                if value and value.strip():
                    items.append((f"{fname[:-5]}_{i}_{key}", value.strip()))
            for j, ex in enumerate(row.get("examples", []) or []):
                if ex.get("ja"):
                    items.append((f"{fname[:-5]}_{i}_ex{j}", ex["ja"].strip()))
            for j, q in enumerate(row.get("questions", []) or []):
                if q.get("q"):
                    items.append((f"{fname[:-5]}_{i}_q{j}", q["q"].strip()))

    vocab_dir = ROOT / "assets" / "jlpt" / "vocab"
    for level in ["n5"]:
        path = vocab_dir / f"{level}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, w in enumerate(data):
            for j, ex in enumerate(w.get("examples", []) or []):
                if ex.get("ja"):
                    items.append((f"{level}_{i}_{j}", ex["ja"].strip()))

    grammar_dir = ROOT / "assets" / "jlpt" / "grammar"
    for level in ["n5", "n4", "n3"]:
        path = grammar_dir / f"{level}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, g in enumerate(data):
            for j, ex in enumerate(g.get("examples", []) or []):
                if ex.get("ja"):
                    items.append((f"g{level}_{i}_{j}", ex["ja"].strip()))
    return items


def to_ogg(wav_path, ogg_path):
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(wav_path),
        "-c:a", "libvorbis", "-q:a", "3", "-ac", "1", "-ar", "22050",
        str(ogg_path),
    ]
    try:
        subprocess.run(cmd, check=True, timeout=60)
        return True
    except Exception as e:
        print(f"ffmpeg failed: {e}")
        return False


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = collect_texts()
    print(f"rendering {len(items)} clips -> {OUT_DIR}")
    manifest = {}
    tmp = Path(tempfile.mkdtemp())
    done = 0
    for key, text in items:
        wav = tmp / "tts.wav"
        ogg = OUT_DIR / f"{key}.ogg"
        if ogg.exists():
            manifest[text] = f"audio/{ogg.name}"
            done += 1
            continue
        try:
            synthesize_to_wav(text, str(wav))
        except Exception as e:
            print(f"synth failed for {key}: {e}")
            continue
        if to_ogg(wav, ogg):
            manifest[text] = f"audio/{ogg.name}"
            done += 1
        if done % 50 == 0:
            print(f"  {done}/{len(items)}")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=0), encoding="utf-8"
    )
    total = sum(f.stat().st_size for f in OUT_DIR.glob("*.ogg"))
    print(f"done: {done} clips, {total/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()

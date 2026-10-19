# Japanese Sensei AI

Created by Groq Side-Chat on 2026-10-18.

## Status
- Phase 1 (core) complete: SM-2 flashcard engine, SQLite storage, progress tracker, seed loader, config.yaml, language-agnostic design (lang/<code>/).
- Phase 2 (UI) complete: PyQt6 desktop app (src/pc/main.py, main_window.py, flashcard_view.py). Flashcard session with flip + 0-5 rating + next due + streak/stats.
- Phase 3 (voice) complete: STT via faster-whisper (Japanese), TTS via piper (ja_JP-hi_fi_captain-medium). Voice panel record 4s + speak.
- Phase 4 (translation) complete: ctranslate2 Opus-MT ja<->en (int8). Translate panel auto direction.
- Phase 5 (workbook) complete: text drills with scoring. Katakana + Kanji Starter decks.
- Content import complete: OpenJLPT N5-N1 (vocab 7,811 / kanji 2,383 / grammar 526) imported = 10,832 cards total. Hint shows example sentences.
- Immersion complete: Reading comprehension (passages N5-N4 with MCQ) + Listening drills (TTS audio -> type what you hear). Tabs added.
- Speaking practice complete: record speech, STT transcribe, Levenshtein pronunciation accuracy score. Tab added.
- Progress & schedule complete: bar chart (30 days), streak, mastery, 7-day forecast, configurable new/review per day. Tab added.
- Immersion expanded: News reader (articles N2-N4 with vocab) + Shadowing (listen & repeat dialogue). Tabs added.
- Tests: 5/5 passing (pytest via Studio venv).
- Runtime: Studio venv (Python 3.10) + PyQt6 installed there.
- Backups: D:\Backups\JAPANESE_SENSEI_AI_*.zip

## Remaining
- Android (Kivy/Buildozer) packaging.
- More content (vocab, grammar, kanji beyond N5).
- Packaging as standalone exe (PyInstaller).
- Per-language hive folders for other languages.

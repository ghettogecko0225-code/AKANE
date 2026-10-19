# Japanese Sensei AI

Created by Groq Side-Chat on 2026-10-18.

## Status
- Phase 1 (core) complete: SM-2 flashcard engine, SQLite storage, progress tracker, seed loader, config.yaml, language-agnostic design (lang/<code>/).
- Phase 2 (UI) complete: PyQt6 desktop app (src/pc/main.py, main_window.py, flashcard_view.py). Tabs: Flashcards, Voice, Translate, Workbook, Reading, Listening, Speaking, Progress, News, Shadowing.
- Phase 3 (voice) complete: STT via faster-whisper (Japanese), TTS via piper (ja_JP-hi_fi_captain-medium). Models live in Studio/models.
- Phase 4 (translation) complete: ctranslate2 Opus-MT ja<->en (int8). Models in Studio/models/translation.
- Phase 5 (workbook) complete: text drills with scoring. Katakana + Kanji Starter decks.
- Content import complete: OpenJLPT N5-N1 (vocab 7,811 / kanji 2,383 / grammar 526) = 10,832 cards. Hint shows example sentences.
- Immersion complete: Reading comprehension, Listening drills, News reader, Shadowing, Speaking (pronunciation score), Progress + 30-day chart + forecast.
- Tests: 9/9 passing (pytest via Studio venv).
- Runtime: Studio venv (Python 3.10) + PyQt6 installed there.
- Windows .exe built: dist/JapaneseSenseiAI/JapaneseSenseiAI.exe (PyInstaller).
- Android APK: built via GitHub Actions (buildozer + Kivy), installed on phone as org.sensei.japanesesensei. Flashcards + Workbook + Reading work on phone. Voice/Translate disabled on mobile (no numpy/ML on Android). Japanese font (assets/fonts/msgothic.ttc) required for hiragana rendering.
- GitHub repo: https://github.com/ghettogecko0225-code/Japanese-Sensei-AI (branch main).
- Backups: D:\Backups\JAPANESE_SENSEI_AI_*.zip

## Remaining
- Mobile: Listening, Speaking, News, Shadowing, Progress screens still placeholders.
- More content (vocab, grammar, kanji beyond N5).
- Packaging as installer (Inno Setup) for selling.
- Per-language hive folders for other languages.
- Android voice via native Android TTS/STT instead of local models.

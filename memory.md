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
- Android APK: built via GitHub Actions (buildozer + Kivy), installed on phone as org.sensei.japanesesensei. All 10 screens working (Flashcards, Voice, Translate, Workbook, Reading, Listening, Speaking, News, Shadowing, Progress). Full JLPT content (18 decks / 10,832 cards) bundled in assets/jlpt and imported on first run. Verified on device: 18 decks, 10,832 cards, Japanese TTS speaking (ja-JP), audio pack playing via MediaPlayer.
- Android voice: core/android_speech.py uses Android native TextToSpeech + SpeechRecognizer via pyjnius. Gotchas found: interface is TextToSpeech$OnInitListener (NOT TextToVoice); RecognitionListener.onError takes a single int; setLanguage must be re-applied after onInit; RecognizerIntent.ACTION_RECOGNIZE_SPEECH is a String so you must build an Intent.
- Offline audio pack: assets/audio (2,329 pre-rendered OGG clips, 41MB) + manifest.json, built by tools/build_audio_pack.py with the local piper voice. Guarantees Japanese audio on any device. core/audio_pack.py plays via MediaPlayer (Android) or soundfile (desktop).
- APK signing: stable debug key at .keystore/sensei-debug.keystore (alias sensei / pass sensei123), re-signed in CI so updates install over the top without wiping data. A real release key must stay PRIVATE.
- Japanese speech recognition: bundled Vosk small-ja model (assets/asr, 94MB, Apache 2.0) = fully OFFLINE Japanese ASR inside the app. p4a has a built-in vosk recipe (prebuilt AAR, no compiler). Gotcha: vosk's open_dll() only accepts sys.platform linux/win32/darwin, so core/asr.py temporarily reports 'linux' while importing (verified on device via the app's own pythonbin).
- Android mic capture for Vosk: android.media.AudioRecord via pyjnius (sounddevice has no Android support). core/asr.py capture_android_pcm() records 16kHz mono PCM16.
- Pronunciation scoring is kanji/kana aware: core/speaking.py build_reading_map() maps 6,540 JLPT kanji words to hiragana so a kanji target scores fairly against kana speech.
- Japanese speech recognition on this phone: device's own recognizer has no Japanese model (error 7), so the bundled Vosk model is the primary engine and the device engine is only a fallback.
- GitHub repo: https://github.com/ghettogecko0225-code/Japanese-Sensei-AI (branch main).
- Backups: D:\Backups\JAPANESE_SENSEI_AI_*.zip

## Remaining
- Mobile: Listening, Speaking, News, Shadowing, Progress screens still placeholders.
- More content (vocab, grammar, kanji beyond N5).
- Packaging as installer (Inno Setup) for selling.
- Per-language hive folders for other languages.
- Android voice via native Android TTS/STT instead of local models.

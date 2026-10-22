# AKANE (formerly Japanese Sensei AI)

Created by Groq Side-Chat on 2026-10-18. Renamed twice, finally to AKANE on 2026-10-21.

## Status
- **THE APP IS "AKANE"** (package `com.hivepulse.akane`, icon label "AKANE", repo
  github.com/ghettogecko0225-code/AKANE). 茜 = the deep crimson of a rising sun,
  which is what the icon already was. Letters: **AI - Kanji - Audio - Nihongo -
  Everywhere**.
- **THE NAME HISTORY (why it changed twice - do not undo this):**
  1. "Japanese Sensei AI" - "Japanese Sensei" is the exact name of a live Play
     app (`com.katanaapps.shiftalk`, Education, 1K+ downloads) and of the iOS
     app "Sensei Japanese" (`id6761647436`). Same-name listings in the same
     category get rejected.
  2. "Benkyo Studio" - ALSO crowded: iOS "Benkyo: Speak & Learn Japanese"
     (`id6737715026`, MWD Services LLC) has a near-identical feature list, plus
     "Benkyo: Japanese Flashcards", "Benkyo - Language Learning", benkyo.app.
  3. "AKANE" - checked Play Store (US + JP) + Apple App Store: ZERO collisions.
     Other Japanese-learning names that were checked and are TAKEN: YOMI, SUMI,
     FUDE, NARU, HARU, WASHI, SORA (OpenAI), KAMI, AKARI, YUGEN, MUSE, LYRA,
     VEGA, AION, YUMI, HAKU, KAZE, RYUU, MUSUBI, NAMI, HANA, TERU, MIZU, KUMO.
  Brand strings live in ONE place: `src/core/brand.py`.
- **COMPANY / DOMAIN:** Kevin's domain `hivepulseinteractive.com` is live
  (Cloudflare + Zoho Mail, site at hivepulseinteractive.com). Privacy policy
  goes to `hivepulseinteractive.com/privacy.html`, contact is
  `privacy@hivepulseinteractive.com`. No separate app domain is needed.
- **PLAY ACCOUNT:** register as an ORGANISATION account (Hive Pulse Interactive
  LLC), not personal. Organisation accounts are EXEMPT from the 12-tester /
  14-day closed test. It needs a D-U-N-S number (free, up to 30 days) + LLC
  documents + website verification via Google Search Console.
- Phase 1 (core) complete: SM-2 flashcard engine, SQLite storage, progress tracker, seed loader, config.yaml, language-agnostic design (lang/<code>/).
- Phase 2 (UI) complete: PyQt6 desktop app (src/pc/main.py, main_window.py, flashcard_view.py). Tabs: Flashcards, Voice, Translate, Workbook, Reading, Listening, Speaking, Progress, News, Shadowing.
- Phase 3 (voice) complete: STT via faster-whisper (Japanese), TTS via piper (ja_JP-hi_fi_captain-medium). Models live in Studio/models.
- Phase 4 (translation) complete: ctranslate2 Opus-MT ja<->en (int8). Models in Studio/models/translation.
- Phase 5 (workbook) complete: text drills with scoring. Katakana + Kanji Starter decks.
- Content import complete: OpenJLPT N5-N1 (vocab 7,811 / kanji 2,383 / grammar 526) = 10,832 cards. Hint shows example sentences.
- Immersion complete: Reading comprehension, Listening drills, News reader, Shadowing, Speaking (pronunciation score), Progress + 30-day chart + forecast.
- Tests: 9/9 passing (pytest via Studio venv).
- Runtime: Studio venv (Python 3.10) + PyQt6 installed there.
- Windows .exe built: dist/Akane/Akane.exe (PyInstaller, spec renamed JapaneseSenseiAI.spec -> Akane.spec).
- Android APK: built via GitHub Actions (buildozer + Kivy), installed on phone as org.sensei.japanesesensei. All 10 screens working (Flashcards, Voice, Translate, Workbook, Reading, Listening, Speaking, News, Shadowing, Progress). Full JLPT content (18 decks / 10,832 cards) bundled in assets/jlpt and imported on first run. Verified on device: 18 decks, 10,832 cards, Japanese TTS speaking (ja-JP), audio pack playing via MediaPlayer.
- Android voice: core/android_speech.py uses Android native TextToSpeech + SpeechRecognizer via pyjnius. Gotchas found: interface is TextToSpeech$OnInitListener (NOT TextToVoice); RecognitionListener.onError takes a single int; setLanguage must be re-applied after onInit; RecognizerIntent.ACTION_RECOGNIZE_SPEECH is a String so you must build an Intent.
- Offline audio pack: assets/audio (2,329 pre-rendered OGG clips, 41MB) + manifest.json, built by tools/build_audio_pack.py with the local piper voice. Guarantees Japanese audio on any device. core/audio_pack.py plays via MediaPlayer (Android) or soundfile (desktop).
- APK signing: stable debug key at .keystore/sensei-debug.keystore (alias sensei / pass sensei123), re-signed in CI so updates install over the top without wiping data. A real release key must stay PRIVATE.
- Japanese speech recognition: bundled Vosk small-ja model (assets/asr, 94MB, Apache 2.0) = fully OFFLINE Japanese ASR inside the app. p4a has a built-in vosk recipe (prebuilt AAR, no compiler). Gotcha: vosk's open_dll() only accepts sys.platform linux/win32/darwin, so core/asr.py temporarily reports 'linux' while importing (verified on device via the app's own pythonbin).
- Android mic capture: android.media.AudioRecord via pyjnius (sounddevice has no Android support). Gotchas, all fixed: (1) CHANNEL_IN_MONO / ENCODING_PCM_16BIT live on android.media.AudioFormat, NOT AudioRecord; (2) getattr(MediaRecorder.AudioSource, "MIC") throws in pyjnius, so use raw ints (MIC=1, VOICE_RECOGNITION=6, VOICE_COMMUNICATION=7, DEFAULT=0); (3) a read() returning 0 is NOT a failure - keep waiting, do not break; (4) the phone's mic returns very quiet audio (rms ~12-80, peak ~54-474), so core/asr.py _normalize_gain() boosts it (x25-400) before recognition - without this the recogniser hears nothing.
- HTTPS on Android needs certifi (Android's Python has no CA store): core/translator.py _ssl_context() points ssl at certifi.where(). Translation tries 3 providers in order (googleapis, google.com, mymemory) because the free endpoint rate-limits (HTTP 429); it shows a friendly message.
- Kivy UI must only be touched from the main thread: mobile/main.py _ui() wraps speech/translate callbacks in Clock.schedule_once (otherwise Kivy can crash).
- **100% OFFLINE (final state)**: the phone app has NO Translate screen and the manifest requests ONLY RECORD_AUDIO - no INTERNET permission at all, so the OS physically cannot let it send data anywhere. core/translator.py is now local-only (ctranslate2 + bundled OPUS-MT models); the desktop keeps its Translate tab because that one is already 100% local (no key, no network). The About screen states "This app has NO internet permission".
- **PRODUCT LAYER (added last)**: core/study.py builds the daily plan (due/new counts, session limited by daily goal + new/day + reviews/day); core/settings.py stores goals/theme/deck selection in data/settings.json; core/theme.py holds the shared dark/light palette plus rgba() hex->RGBA (Kivy needs RGBA FLOATS, Qt accepts hex strings - mixing them up made the phone card white with invisible text); tools/make_brand.py draws the icon (navy tile, rising sun, ã€Œã‚ã€) + splash.
- Phone home screen order: Today, Flashcards, Voice, Workbook, Reading, Listening, Speaking, News, Shadowing, Model, Progress, Settings, About. Desktop has the same features in the sidebar (Today plan, Settings dialog, About & Credits).
- Big model (optional, in-app download): core/asr.py download_big_model() fetches vosk-model-ja-0.22 (997MB zip / 1.5GB unpacked) at runtime - NOT bundled, so the APK stays 111MB and the Play Store limit is safe. Needs 1.1GB RAM (phone has 3.6GB, leaves ~300MB free) and largeHeap (android/extra_manifest_application_arguments.xml). UI: "Model" tab with progress + RAM check + remove.
- **PRIMARY ENGINE IS sherpa-onnx** (assets/asr_sherpa, 70MB int8): sherpa-onnx-zipformer-ja-en-reazonspeech-2025-01-17 (encoder/decoder/joiner int8 + tokens.txt). sherpa-onnx publishes PREBUILT ANDROID WHEELS including cp314 (cp314-cp314-android_24_arm64_v8a) - p4a installs it like vosk, no compiler. It is bilingual (Japanese + English) so beginners can be transcribed too. Vosk is now only the fallback.
- p4a + sherpa on Android required THREE local recipes (p4a-recipes/, wired with `p4a.local_recipes`): sherpa_onnx (download+unpack the Android wheels) and charset_normalizer (pure-python wheel, because pip on the build host refuses wheels tagged android_*). Requirements must use UNDERSCORES (sherpa_onnx, charset_normalizer) - p4a compares metadata names with underscores.
- The sherpa recipe must also copy libonnxruntime.so / libsherpa-onnx-c-api.so / libc++_shared.so (from the NDK) into ctx.get_libs_dir(arch) so Android's linker finds them.
- sherpa recognition must be NUMPY-FREE on Android (numpy is not in the p4a dist): core/asr.py _pcm_to_float32() uses array.array('f').
- Engine accuracy measured on ä»Šæ—¥ã¯ã„ã„å¤©æ°—ã§ã™ã­ã€‚: sherpa-onnx zipformer ja-en int8 = 'ä»Šæ—¥ã¯ã„ã„å¤©æ°—ã§ã™ã­' EXACT (70MB, 0.10s) | faster-whisper base = EXACT (150MB, 1.0s) | vosk small-ja = 'ä»Šæ—¥ ã¯ ã„ã„ å¤©æ°— ã§ã™ ã­' (94MB, 3.9s) | vosk big-ja 1GB = same as small (1.6GB RAM) - so the 1GB model was NOT worth it.
- Android diagnostics: logcat DROPS prints from background threads. core/asr.py writes to <app>/data/asr_log.txt instead - pull it with: adb shell run-as org.sensei.japanesesensei cat files/app/data/asr_log.txt
- **LICENCE CLEAN-UP (2026-10-21)**: MS Gothic (msgothic.ttc, Microsoft, NOT redistributable) was DELETED from assets/fonts and replaced with NotoSansCJKjp-Regular.otf (SIL OFL 1.1) + assets/fonts/OFL.txt. Icon/splash regenerated from the bundled font (tools/make_brand.py no longer reads C:\Windows\Fonts). Mobile font registration in src/mobile/main.py now points at the .otf.
- Verified licences: phone stack is fully permissive (Kivy MIT, sherpa-onnx Apache-2.0, ReazonSpeech model Apache-2.0 + explicitly free for commercial use, onnxruntime MIT, Noto OFL). Data = OpenJLPT CC BY-SA 4.0 (attribution + share-alike on the card data). Desktop-only: PyQt6 GPL-3.0-only + piper-tts GPL-3.0-or-later -> the Windows build is released as GPL-3.0 open source. Repo LICENSE = GPL-3.0; THIRD-PARTY-NOTICES.md = full inventory; docs/licensing-decision.md = plain-English rationale.
- `android.api = 36` (Play target SDK requirement), version 1.0.0, `otf` added to source.include_exts, package id com.hivepulse.akane.
- Play Store package written: docs/playstore/listing.md (name/short/full copy + screenshot plan + content-rating answers + 12-tester/14-day new-account rule), privacy-policy.md + publishable privacy-policy.html, data-safety.md (all "not collected" - the app has no INTERNET permission and zero network code in the mobile path).
- Still open for the launch: real release keystore (never commit it), publish the privacy policy to a public URL, privacy@akanestudio.app mailbox, feature graphic (1024x500) + 1080x1920 screenshots, start the 12-tester closed test.
- Pronunciation scoring is kanji/kana aware: core/speaking.py build_reading_map() maps 6,540 JLPT kanji words to hiragana so a kanji target scores fairly against kana speech.
- Japanese speech recognition on this phone: device's own recognizer has no Japanese model (error 7), so the bundled Vosk model is the primary engine and the device engine is only a fallback.
- GitHub repo: https://github.com/ghettogecko0225-code/AKANE (branch main, PUBLIC, renamed from Japanese-Sensei-AI - the old URL redirects). Repo is PUBLIC - GPL compliance relies on that.
- Backups: D:\Backups\JAPANESE_SENSEI_AI_*.zip
- **PLAY UPLOAD MUST BE AN APP BUNDLE (.aab)**: Google requires new apps to be published as a bundle, and the debug APK is 146 MB which is over the 100 MB APK upload limit. The CI workflow now has a second job `bundle` that runs `buildozer android release` (buildozer's default release_artifact is aab; set explicitly in buildozer.spec) and uploads akane-aab.
- Verified on the Galaxy A15 (R5CXA4GM9JK) after the rename: `dumpsys package com.hivepulse.akane` shows targetSdk=36, versionName=1.0.0, and requested permissions = RECORD_AUDIO ONLY (no INTERNET).
- Real Play Store screenshots captured from the device with tools/capture_screenshots.py -> assets/store_screenshots/ (today, flashcards, reading, speaking, progress, about). GOTCHA: the Android back key EXITS the Kivy app instead of popping its screen stack, so the capture script relaunches the app before every screen.
- FIXED (2026-10-21): the WINDOWS build only ever had the 3 seed decks (112 cards) because the desktop looked for assets/openjlpt/data/json (not bundled, and only a gitlink in the repo) while the real packaged data is assets/jlpt. Fixed by bundling assets/jlpt in Akane.spec and pointing pc/main_window.py import_content() + the auto-import check at assets/jlpt first. Verified in the frozen build: 18 decks / 10,832 cards, same as the phone.

## Remaining
- **Play Store launch**: publish privacy policy to a public URL, create privacy@akanestudio.app, buy the akanestudio.app domain, make the 1024x500 feature graphic + 1080x1920 screenshots, generate a PRIVATE release keystore, start the 12-tester / 14-day closed test.
- Packaging the Windows build as an installer (Inno Setup) if it is going to be sold.
- More content (vocab, grammar, kanji beyond N5).
- Per-language hive folders for other languages.
- Optional (only if the Windows build must stay closed source): PyQt6 -> PySide6 and Piper -> a permissive Japanese TTS.

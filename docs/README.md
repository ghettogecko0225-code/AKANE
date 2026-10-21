# Benkyo Studio - Architecture Overview

How the app is actually put together, as of the 1.0.0 release (21 October 2026).

This replaces the original planning document, which described Vosk, Coqui-TTS and
a `build_android.sh` that the finished app does not use.

## What it is

One application in two front ends over one shared core:

| Front end | Stack | Package |
|---|---|---|
| Android phone | Kivy 2.3.1 | `com.hivepulse.benkyo` |
| Windows desktop | PyQt6 6.11 | `BenkyoStudio.exe` |

Both read the same `src/core/` logic and the same bundled content, so a card
studied on the phone behaves the same on the desktop.

**Everything runs on the device.** The phone build holds no `INTERNET`
permission, so it cannot phone home even by accident.

## Layout

```
Benkyo Studio (project root)
│
├─ main.py                     # phone entry point -> mobile.main.BenkyoApp
│
├─ src/
│   ├─ core/                   # shared logic, no UI imports
│   │   ├─ brand.py            # app name, package id, public links (single source)
│   │   ├─ db.py               # SQLite connection + schema
│   │   ├─ flashcards.py       # SM-2 spaced repetition engine
│   │   ├─ scheduler.py        # daily plan: due / new / reviews
│   │   ├─ study.py            # plan building
│   │   ├─ settings.py         # settings.json (goals, theme, deck)
│   │   ├─ theme.py            # shared palette + rgba() for Kivy
│   │   ├─ asr.py              # sherpa-onnx speech recognition
│   │   ├─ android_speech.py   # Android TTS / recogniser via pyjnius
│   │   ├─ voice.py            # desktop TTS (piper) + audio pack fallback
│   │   ├─ audio_pack.py       # plays the 2,329 pre-rendered OGG clips
│   │   ├─ translator.py       # local ctranslate2 translation (desktop only)
│   │   ├─ speaking.py         # pronunciation scoring, kanji-aware readings
│   │   ├─ immersion.py        # reading / listening / news / shadowing content
│   │   ├─ workbook.py         # text drills with scoring
│   │   ├─ progress.py         # progress tracker
│   │   ├─ seed.py             # deck loader
│   │   ├─ import_openjlpt.py  # imports assets/jlpt on first run
│   │   ├─ paths.py            # resource / data / model roots
│   │   ├─ credits.py          # About & Licenses text
│   │   └─ ...
│   ├─ pc/                     # desktop UI (PyQt6)
│   │   ├─ main.py             # QApplication bootstrap
│   │   ├─ main_window.py      # sidebar + tabs + Today + Settings + About
│   │   └─ *_panel.py          # one panel per feature
│   └─ mobile/                 # phone UI (Kivy)
│       └─ main.py             # all 13 screens
│
├─ assets/
│   ├─ jlpt/                   # 10,832 cards, CC BY-SA 4.0 (OpenJLPT)
│   ├─ audio/                  # 2,329 OGG clips + manifest.json
│   ├─ asr_sherpa/             # 70 MB int8 ReazonSpeech zipformer model
│   ├─ fonts/                  # Noto Sans CJK JP (OFL) + OFL.txt
│   ├─ immersion/              # passages, dialogues, articles
│   └─ brand/                  # icon, splash, Play feature graphic
│
├─ docs/
│   ├─ licensing-decision.md   # what we ship under what terms, and why
│   ├─ playstore/              # listing copy, privacy policy, data safety
│   └─ README.md               # this file
│
├─ buildozer.spec              # Android build (package id, API level, assets)
├─ BenkyoStudio.spec           # PyInstaller build for Windows
├─ p4a-recipes/                # local recipes for sherpa-onnx + charset_normalizer
├─ tools/                      # make_brand.py, make_feature_graphic.py, audio pack
├─ THIRD-PARTY-NOTICES.md      # every bundled licence
└─ LICENSE                     # GPL-3.0
```

## The core is UI-free

`src/core/` never imports PyQt6 or Kivy. Both front ends import it, which is why
the same scheduler, scorer and card engine run on both platforms. Anything
platform-specific lives behind a thin wrapper (`android_speech.py` for pyjnius,
`voice.py` for the desktop).

## Data flow: a flashcard session

1. The UI asks `FlashCardEngine` for the next card due.
2. `FlashCardEngine` queries SQLite for the SM-2 due date and pulls the card
   from `assets/jlpt`.
3. The card is rendered; audio plays from the pre-rendered pack if a clip
   exists, otherwise the on-device voice is synthesised.
4. The user rates it; the SM-2 interval is updated and written back.
5. `ProgressTracker` updates the daily stats and the 30-day chart.

## Voice, end to end

```
 speak (phone)                        speak (desktop)
      │                                     │
 core/asr.py                           core/voice.py
 sherpa-onnx int8                      piper (MIT voice model)
 ReazonSpeech zipformer                  + pre-rendered pack
      │                                     │
 audio in memory -> text -> score      text -> wav -> playback
 (never written to disk, never sent)   (never sent anywhere)
```

The microphone is captured with `android.media.AudioRecord` through pyjnius
because `sounddevice` has no Android support. The phone's own recogniser has no
Japanese model installed, so the bundled sherpa model is the real engine.

## Content pipeline

```
OpenJLPT (CC BY-SA 4.0)
   └─ assets/jlpt/*.json  ──import_openjlpt──>  SQLite  ──> 18 decks
                                                            10,832 cards
```

`assets/openjlpt/` holds the upstream project with its `LICENSE` and
`NOTICE.md`, so the attribution travels with the data.

## Build

| Target | Command | Output |
|---|---|---|
| Windows | `pyinstaller BenkyoStudio.spec` | `dist/BenkyoStudio/BenkyoStudio.exe` |
| Android | `buildozer android debug` (or push to GitHub Actions) | `bin/*.apk` |

The Android build is done on GitHub Actions (`ubuntu-22.04`, Java 17, Python
3.11) and the APK is signed with the stable key in `.keystore/` so updates
install over the top without wiping study data.

Two local p4a recipes are required and are not optional:

- `p4a-recipes/sherpa_onnx` - fetches the prebuilt **Android** wheels by hand,
  because pip on the build host will not install wheels tagged `android_*`.
- `p4a-recipes/charset_normalizer` - same problem, pure-python wheel.

Requirements in `buildozer.spec` must use **underscores** (`sherpa_onnx`,
`charset_normalizer`), because p4a compares distribution names that way.

## Testing

- `pytest tests/` - 9 tests over the card engine, scheduler, scoring and import.
- A Kivy screen-interaction script drives all 13 phone screens headlessly.
- The Android build is verified on a physical device (Galaxy A15, `R5CXA4GM9JK`)
  including the microphone path, because that is the only way to catch the
  pyjnius and AudioRecord quirks.

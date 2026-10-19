# Japanese Sensei AI – Architecture Overview

## Goal
Create a cross‑platform language‑learning suite that runs **locally** on a PC (Windows/macOS/Linux) and on Android (Galaxy A15 or newer). The app will provide:
- Flash‑card system (Hiragana/Katakana, vocab, kanji)
- Interactive work‑books & writing exercises (stroke order, handwriting recognition)
- Conversational speaking practice with speech‑to‑text & text‑to‑speech
- Real‑time translation engine (local LLM + NMT)
- Progress tracking & daily schedule (10 min – 1 h)
- Modular design so future language hives can be added.

## High‑level Architecture
```
Japanese Sensei AI (project root)
│
├─ src/                         # Source code
│   ├─ pc/                     # Desktop (PyQt6) entry point
│   │   ├─ main.py            # Qt app bootstrap
│   │   └─ ...                # UI widgets, controllers
│   ├─ mobile/                 # Android (Kivy/Qt for Android) entry point
│   │   ├─ main.py            # Kivy app bootstrap
│   │   └─ ...                # Mobile‑specific UI
│   ├─ core/                  # Shared logic (model loading, scheduler, utils)
│   │   ├─ models/            # Wrapper for local LLM/NMT models
│   │   ├─ flashcards.py      # Flash‑card engine
│   │   ├─ workbook.py        # Exercise generation & evaluation
│   │   ├─ translator.py      # Translation pipeline
│   │   ├─ speech.py          # STT/TTS using Vosk + Coqui TTS
│   │   └─ progress.py        # User progress DB (SQLite)
│   └─ assets/                # Static data (images, audio samples)
│
├─ assets/                     # Model files, icons, fonts
│   ├─ models/                 # Local LLM (e.g., Phi‑3 Mini) & NMT (MarianMT)
│   └─ icons/                  # App icons for desktop & Android
│
├─ docs/                       # Documentation
│   ├─ architecture.md        # Detailed diagram (included below)
│   └─ user_guide.md          # How to use the app
│
├─ requirements.txt            # Python deps (PyQt6, transformers, sentencepiece, ...)
├─ build_android.sh            # Script that uses Buildozer / p4a to package Kivy app
└─ README.md (this file)
```

## Core Components
| Component | Responsibility | Key Libraries |
|-----------|----------------|---------------|
| **UI Layer** | Platform‑specific front‑end (Qt for PC, Kivy for Android). Handles navigation, theming, and input events. | PyQt6, Kivy, QtQuick (optional) |
| **Model Manager** | Loads/initialises local LLM (for conversational AI) and NMT model (for translation). Provides inference APIs. | 🤗 Transformers, sentence‑piece, torch/ggml compiled binaries |
| **Flash‑Card Engine** | Spaced‑repetition scheduler (SM‑2), card CRUD, audio playback. | SQLite, pandas |
| **Workbook Engine** | Generates reading/writing drills, validates handwriting via **handwritten‑character recognition** (HCR) using a tiny CNN. | OpenCV, TensorFlow Lite (or ONNX Runtime) |
| **Speech Module** | Offline speech‑to‑text (Japanese) and text‑to‑speech for pronunciation feedback. | Vosk, Coqui‑TTS |
| **Progress Tracker** | Stores daily study time, mastery levels, streaks. Syncs locally across PC & phone via exported JSON. | SQLite + simple JSON export |
| **Scheduler** | Pushes notifications on Android & system tray alerts on PC to remind the user to study (10 min‑1 h). | plyer (cross‑platform notifications) |

## Data Flow Example (Flash‑Card Session)
1. UI (PC or Mobile) requests next due card → **FlashCardEngine** queries SQLite for SM‑2 due date.
2. Card data (prompt, audio, image) sent back to UI.
3. User marks **Correct / Wrong** → engine updates SM‑2 interval and stores result.
4. **ProgressTracker** updates daily stats; if session length > 10 min, a “session complete” toast appears.

## Translation Pipeline
```
User input → Speech (optional) → STT (Vosk) → Text →
   ├─ Pre‑process (tokenize) →
   ├─ NMT Model (MarianMT‑ja‑en) →
   └─ TTS (Coqui) → Audio playback
```
All models are stored under `assets/models/` and loaded with **torch‑script** or **ggml** for minimal RAM usage (~1‑2 GB).

## Build Strategy
| Target | Tech Stack | Packaging |
|--------|------------|-----------|
| **Desktop (Windows/macOS/Linux)** | Python 3.11, PyQt6, bundled torch/transformers binaries | Use **PyInstaller** to create a single‑folder exe (or .app/.appimage). |
| **Android** | Python 3.11, Kivy, Buildozer (p4a) | `build_android.sh` creates an APK that includes the model files (compressed, extracted on first run). |

### Steps
1. Write pure‑Python core in `src/core/` – no UI dependencies.
2. Create thin wrappers in `src/pc/` and `src/mobile/` that import the core.
3. For Android, convert heavy models to **ggml** or **ONNX** to avoid the large torch dependency.
4. Test on a PC first, then run `build_android.sh` to generate the APK.

## Future‑Proofing (Language Hive Expansion)
- The **core** package is language‑agnostic; a `lang/ja/` folder contains Japanese resources, while `lang/es/` could be added later.
- UI reads a config `config.yaml` that lists available hives. Adding a new hive only requires new vocab/kanji sets and optional model files.

---
### Next Steps for You
1. **Clone the repo** (or copy the folder) onto your dev machine.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the desktop prototype: `python src/pc/main.py`.
4. When the core is stable, start the Android build: `./build_android.sh`.
5. Iterate on flash‑card content and model quantisation to keep the app under 2 GB.

Feel free to ask for any of the individual modules (e.g., a starter `flashcards.py` implementation) or the Buildozer spec file.

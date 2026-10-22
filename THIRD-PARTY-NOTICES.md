# Third-Party Notices

**AKANE** (formerly "Japanese Sensei AI") ships the following third-party
software and data. This file is the attribution notice required by those licenses
and it is also shown inside the app (About â†’ Licenses).

The project itself is released under the **GNU General Public License v3.0**
(see [LICENSE](LICENSE)). Every dependency listed below is compatible with GPL-3.0.

---

## 1. Application code and frameworks

| Component | Version | License | Used for |
|---|---|---|---|
| [Kivy](https://kivy.org) | 2.3.1 | MIT | Android app UI framework |
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | 6.11.0 | GPL-3.0-only | Windows desktop UI framework |
| [PyQt6-Qt6](https://www.riverbankcomputing.com/software/qt/) | 6.11.2 | LGPL-3.0 | Qt 6 runtime used by PyQt6 |
| [Python](https://www.python.org) | 3.11+ | PSF License | Runtime |
| [SQLite](https://www.sqlite.org) | bundled with Python | Public domain | Study database |
| [NumPy](https://numpy.org) | 2.2.6 | BSD-3-Clause | Audio buffers |
| [soundfile](https://github.com/libsndfile/libsndfile) | 0.14.0 | BSD-3-Clause (libsndfile: LGPL-2.1) | OGG/FLAC audio reading |
| [sounddevice](https://github.com/matousc89/python-sounddevice) | 0.5.6 | MIT | Microphone capture |
| [cffi](https://cffi.readthedocs.io) | 2.1.1 | MIT-0 | C bindings used by soundfile |
| [certifi](https://github.com/certifi/python-certifi) | 2026.7.22 | MPL-2.0 | CA bundle (used by requests, unused at runtime on phone) |
| [charset-normalizer](https://github.com/jawah/charset_normalizer) | 3.5.2 | MIT | Text encoding detection |
| [requests](https://requests.readthedocs.io) | 2.32.3 | Apache-2.0 | HTTP client (desktop tooling only) |
| [urllib3](https://urllib3.readthedocs.io) | 2.7.0 | MIT | HTTP transport |
| [idna](https://github.com/kjd/idna) | 3.18 | BSD-3-Clause | IDNA encoding |
| [tqdm](https://github.com/tqdm/tqdm) | 4.70.0 | MIT AND MPL-2.0 | Progress bars |
| [srt](https://github.com/cdOWNER/srt) | 3.5.3 | MIT | Subtitle parsing (listening mode) |
| [websockets](https://github.com/python-websockets/websockets) | 16.1.1 | BSD-3-Clause | Local ASR streaming helper |
| [setuptools](https://github.com/pypa/setuptools) | 84.0.0 | MIT | Packaging |
| [pip](https://github.com/pypa/pip) | 23.0.1 | MIT | Packaging |

### Speech recognition and speech

| Component | Version | License | Used for |
|---|---|---|---|
| [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | 1.13.8 | Apache-2.0 | Offline Japanese + English speech recognition (also the Android text-to-speech on-device stack) |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | 1.23.2 | MIT | Inference runtime for the ASR model |
| [ReazonSpeech](https://github.com/reazon-research/ReazonSpeech) (zipformer JA+EN model) | 2025-01-17 | Apache-2.0 | The ASR model weights. Free for commercial use. |
| [piper](https://github.com/OHF-Voice/piper1-gpl) (`piper-tts`) | 1.8.0 | GPL-3.0-or-later | Windows desktop text-to-speech (Japanese voice `ja_JP-hi_fi_captain-medium`) |
| [piper-voices](https://huggingface.co/rhasspy/piper-voices) | voice data | MIT | The `ja_JP-hi_fi_captain-medium` voice model, and the 2,329 pre-rendered audio clips shipped with the app |

### Translation (Windows desktop build only)

| Component | License | Used for |
|---|---|---|
| [CTranslate2](https://github.com/OpenNMT/CTranslate2) | MIT | Inference runtime |
| [OPUS-MT ja-en](https://huggingface.co/Helsinki-NLP/opus-mt-ja-en) (Helsinki-NLP) | CC BY 4.0 | Japanese â†” English translation models |
| [SentencePiece](https://github.com/google/sentencepiece) | Apache-2.0 | Japanese text segmentation |
| [Hugging Face Transformers](https://github.com/huggingface/transformers) | Apache-2.0 | Tokenizer files |

---

## 2. Fonts

| Font | License | Used for |
|---|---|---|
| [Noto Sans CJK JP](https://github.com/notofonts/noto-cjk) (`NotoSansCJKjp-Regular.otf`) | SIL Open Font License 1.1 | The Japanese text face bundled in `assets/fonts/`. Full licence text: [`assets/fonts/OFL.txt`](assets/fonts/OFL.txt). |

> The earlier build bundled **MS Gothic**, a Microsoft font that may not be
> redistributed. It was removed and replaced with the OFL-licensed Noto Sans CJK JP.

---

## 3. Study content (data)

| Source | License | Used for |
|---|---|---|
| [OpenJLPT](https://github.com/evanclan/OpenJLPT) | **CC BY-SA 4.0** | The 10,832 JLPT N5â€“N1 vocabulary, kanji and grammar cards in `assets/jlpt` |
| [Jonathan Waller's JLPT Resources](https://www.tanos.co.uk/jlpt/) | CC BY | JLPT level assignments and English glosses |
| [JMdict](https://www.edrdg.org/jmdict/j_jmdict.html) (EDRDG) | CC BY-SA 4.0 | Dictionary entries, readings, parts of speech |
| [KANJIDIC2](https://www.edrdg.org/wiki/KANJIDIC_Project.html) (EDRDG) | CC BY-SA 4.0 | Kanji readings, stroke counts, radicals |
| [Tatoeba](https://tatoeba.org) | CC BY 2.0 FR | Example sentences |

Full attribution text: [`assets/openjlpt/NOTICE.md`](assets/openjlpt/NOTICE.md).
Licence text: [`assets/openjlpt/LICENSE`](assets/openjlpt/LICENSE).

**Share-alike obligation.** The card data in `assets/jlpt` is a derivative of
OpenJLPT and is therefore released under **CC BY-SA 4.0**. Anyone who wants to
reuse or redistribute those cards must:

1. credit OpenJLPT and the upstream sources above,
2. link to <https://creativecommons.org/licenses/by-sa/4.0/>, and
3. release their own derivative dataset under CC BY-SA 4.0.

The cards can be downloaded from
[`assets/jlpt`](https://github.com/ghettogecko0225-code/AKANE/tree/main/assets/jlpt).

The **application code** is GPL-3.0; the **card data** is CC BY-SA 4.0. These are
compatible: CC BY-SA 4.0 is one-way compatible with GPL-3.0.

### Original content written for this app

The immersion passages, dialogues, news-style reading texts, workbook exercises,
speakable-word list and the pre-rendered voice clips were written or generated
specifically for AKANE and are covered by the project licence (GPL-3.0).
The voice clips were rendered with the MIT-licensed `ja_JP-hi_fi_captain-medium`
Piper voice.

---

## 4. Store and platform notices

- **Google Play** requires that apps which are distributed under a copyleft
  licence make the corresponding source available. Source code:
  <https://github.com/ghettogecko0225-code/AKANE>
- **Android** is a trademark of Google LLC. This app is not affiliated with,
  endorsed by or sponsored by Google LLC or the Japan Foundation.
- **JLPT** is a registered trademark of the Japan Foundation. This app is an
  unofficial study tool and is not affiliated with the Japan Foundation.
- **Qt** is a trademark of The Qt Company Ltd. The Windows build uses PyQt6.
- The app icon and splash artwork are original work created for this project.

---

## 5. Removed components

These were part of earlier builds and are no longer shipped:

| Component | Why it was removed |
|---|---|
| [Vosk](https://github.com/alphacep/vosk) | Accuracy was far worse than sherpa-onnx for Japanese. Apache-2.0. |
| MS Gothic (`msgothic.ttc`) | Microsoft font, may not be redistributed. Replaced with Noto Sans CJK JP (OFL). |
| `requests` / `certifi` (on Android) | The phone build no longer needs network access, so the `INTERNET` permission was removed. |

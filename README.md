# AKANE

**Study Japanese. Fully offline.**

AKANE (å‹‰å¼· = "study") is a complete JLPT study system for **N5 to N1**
that runs entirely on your own device. No account, no ads, no tracking, no
subscription - and on Android it holds **no internet permission at all**, so it
physically cannot send anything anywhere.

- **10,832 cards** - vocabulary, kanji and grammar, organised by level
- **Speak and get scored** - on-device Japanese speech recognition with
  kanji-aware pronunciation scoring
- **2,329 native audio clips** - pre-rendered, so listening works with no signal
- **Reading, Listening, Shadowing, News, Workbook** - immersion content built in
- **A daily plan** that knows what is due, what is new and what to review
- **Progress you can see** - every level, every kanji, every mistake

Runs on **Android** (Kivy) and **Windows** (PyQt6) from one shared core.

## Install

**Android** - build the APK yourself, or grab a signed build from the releases
page.

```
buildozer android debug
```

**Windows**

```
pyinstaller AKANEStudio.spec
```

## Build from source

```bash
git clone https://github.com/ghettogecko0225-code/AKANE.git
cd Japanese-Sensei-AI
pip install -r requirements.txt
python src/pc/main.py          # desktop
python main.py                 # phone (Kivy, needs a desktop too)
```

The Android build needs two local p4a recipes that are included in the repo -
see [`docs/README.md`](docs/README.md) for the details and the gotchas.

## Project layout

| Path | What is in it |
|---|---|
| `src/core/` | Shared logic: cards, scheduler, speech, scoring, progress |
| `src/pc/` | Windows front end (PyQt6) |
| `src/mobile/` | Android front end (Kivy) |
| `assets/jlpt/` | The 10,832 study cards (CC BY-SA 4.0) |
| `assets/audio/` | 2,329 pre-rendered audio clips |
| `assets/asr_sherpa/` | The offline speech recognition model |
| `docs/playstore/` | Store listing copy, privacy policy, data safety answers |
| `tools/` | Brand art, feature graphic, audio pack builder |

## Privacy

The phone build requests one permission: the microphone, and only when you tap
record. Audio is processed in memory and discarded. Nothing is uploaded, nothing
is sold, and uninstalling the app deletes everything because all of it lives in
the app's own private storage.

Full policy: [`docs/playstore/privacy-policy.md`](docs/playstore/privacy-policy.md)

## Licence

- **Application code** - GNU General Public License v3.0. See [`LICENSE`](LICENSE).
- **Study data** (`assets/jlpt`) - CC BY-SA 4.0, from
  [OpenJLPT](https://github.com/evanclan/OpenJLPT), which uses JMdict, KANJIDIC2,
  Jonathan Waller's JLPT lists and Tatoeba.
- **Everything else** - MIT, Apache-2.0, BSD, SIL OFL and CC BY. Full inventory
  with versions: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

Why these terms and what they mean for selling the app:
[`docs/licensing-decision.md`](docs/licensing-decision.md)

## Not affiliated

"Japanese Language Proficiency Test" and "JLPT" are trademarks of the Japan
Foundation. This is an unofficial study tool and is not affiliated with or
endorsed by the Japan Foundation. Android is a trademark of Google LLC.

---

å‹‰å¼· - akane: to study.

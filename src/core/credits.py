"""Credits and licence text shown in the app's About screen.

Kept in one place so the app can print the same attribution that ships in
THIRD-PARTY-NOTICES.md and on the store listing.
"""

CREDITS = """AKANE - Japanese study, fully offline.

AI - Kanji - Audio - Nihongo - Everywhere.

Everything here runs on this device. The app has no internet permission:
no account, no ads, no tracking, nothing you say or study leaves the phone.

CONTENT
- JLPT N5-N1 vocabulary, kanji and grammar: OpenJLPT
  by evanclan (github.com/evanclan/OpenJLPT), CC BY-SA 4.0, which uses
  JMdict and KANJIDIC2 (EDRDG), Jonathan Waller's JLPT lists
  (tanos.co.uk) and Tatoeba. Our card set is a derivative and is offered
  under the same CC BY-SA 4.0 licence.
  https://github.com/evanclan/OpenJLPT
  https://creativecommons.org/licenses/by-sa/4.0/

SPEECH RECOGNITION
- sherpa-onnx (Apache 2.0), github.com/k2-fsa/sherpa-onnx
- ReazonSpeech zipformer Japanese + English model (Apache 2.0)
  https://github.com/reazon-research/ReazonSpeech

SPEECH
- Piper voice ja_JP-hi_fi_captain-medium (MIT) for the desktop build and
  for the bundled audio clips: huggingface.co/rhasspy/piper-voices
- Android system text-to-speech for phone playback

TRANSLATION (desktop build only)
- OPUS-MT Helsinki-NLP (CC BY 4.0) and CTranslate2 (MIT),
  both run locally on this device.

FONT
- Noto Sans CJK JP (SIL Open Font License 1.1), notofonts/noto-cjk

FRAMEWORKS
- Kivy (MIT) on Android, PyQt6 (GPL 3.0) on the Windows build.

SOURCE CODE
This app is open source under the GNU General Public License v3.0.
The full source, the complete licence text and every third-party licence
are available here:
{source}

The card data is CC BY-SA 4.0 and can be downloaded from here:
{data}

OFFLINE BY DESIGN
No internet permission. Every card, every audio clip, speech recognition and
translation run on this device. Nothing you say, type or study is ever sent
anywhere.
"""


def credits_text(source_url: str, data_url: str) -> str:
    return CREDITS.format(source=source_url, data=data_url)

"""Single source of truth for the app's name, id and public links.

Named AKANE (茜) on 21 October 2026.

Why it was renamed twice:
  1. "Japanese Sensei AI" -> "Benkyo Studio": "Japanese Sensei" is the exact
     name of a live Google Play app (com.katanaapps.shiftalk) and of the iOS
     app "Sensei Japanese" (id6761647436). A same-name listing in the same
     category reads as a knock-off and Google can refuse it.
  2. "Benkyo Studio" -> "AKANE": "Benkyo" turned out to be crowded in this
     exact category too - iOS has "Benkyo: Speak & Learn Japanese"
     (id6737715026, MWD Services LLC) with a near-identical feature list,
     plus "Benkyo: Japanese Flashcards", "Benkyo - Language Learning" and
     benkyo.app. AKANE was checked against the Play Store (US + JP) and the
     Apple App Store and has zero name collisions.

AKANE means 茜 - the deep crimson of a rising sun, which is what the app icon
is. The letters stand for AI - Kanji - Audio - Nihongo - Everywhere.
"""

APP_NAME = "AKANE"
APP_LABEL = "AKANE"
APP_KANJI = "茜"
APP_TAGLINE = "Japanese study, fully offline."
APP_MEANING = "AI - Kanji - Audio - Nihongo - Everywhere"
APP_ID = "com.hivepulse.akane"
SOURCE_URL = "https://github.com/ghettogecko0225-code/AKANE"
DATA_LICENSE_URL = SOURCE_URL + "/tree/main/assets/jlpt"
LICENSE_URL = SOURCE_URL + "/blob/main/LICENSE"
THIRD_PARTY_URL = SOURCE_URL + "/blob/main/THIRD-PARTY-NOTICES.md"

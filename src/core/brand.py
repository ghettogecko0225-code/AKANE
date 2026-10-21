"""Single source of truth for the app's name, id and public links.

Renamed from "Japanese Sensei AI" to "Benkyo Studio" in October 2026.
Reason: "Japanese Sensei" is already the exact name of a live Google Play
app (com.katanaapps.shiftalk) and of the iOS app "Sensei Japanese"
(id6761647436). Two apps with the same name in the same Play category
reads as a knock-off, and Google can reject a listing for it.
"Benkyo Studio" was checked against the Play Store (US + JP) and the
Apple App Store and has no name match.
"""

APP_NAME = "Benkyo Studio"
APP_LABEL = "Benkyo"
APP_TAGLINE = "Japanese study, fully offline."
APP_ID = "com.hivepulse.benkyo"
SOURCE_URL = "https://github.com/ghettogecko0225-code/Benkyo-Studio"
DATA_LICENSE_URL = SOURCE_URL + "/tree/main/assets/jlpt"
LICENSE_URL = SOURCE_URL + "/blob/main/LICENSE"
THIRD_PARTY_URL = SOURCE_URL + "/blob/main/THIRD-PARTY-NOTICES.md"

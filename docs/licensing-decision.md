# Licensing decision - what we ship, under what terms, and why

Written 21 October 2026, before the first public release.

---

## 1. The one hard blocker we had to fix

The app shipped **MS Gothic** (`msgothic.ttc`) inside `assets/fonts/`. That is a
Microsoft font. Microsoft does not allow it to be redistributed inside another
product, and it is not covered by any open-source licence. Shipping it to the
Google Play Store would have been infringement.

**Fixed.** The proprietary font was deleted and replaced with
**Noto Sans CJK JP**, licensed under the **SIL Open Font License 1.1** - free to
bundle, including in a commercial product, as long as the OFL text ships with
it (it does: `assets/fonts/OFL.txt`).

The icon and splash artwork were regenerated with the new font and checked
visually.

## 2. The full inventory

Every component that ships, with the licence we verified from the installed
package metadata or the upstream model card:

| Component | Licence | Verdict |
|---|---|---|
| Kivy (Android UI) | MIT | Fine, commercial use allowed |
| sherpa-onnx (speech recognition engine) | Apache-2.0 | Fine |
| ReazonSpeech model weights | Apache-2.0 | Fine - upstream states free commercial use |
| ONNX Runtime | MIT | Fine |
| Piper voice `ja_JP-hi_fi_captain-medium` | MIT | Fine - the pre-rendered audio clips are covered |
| Piper-TTS 1.8.0 (Windows TTS code) | **GPL-3.0-or-later** | Forces GPL on the Windows build |
| PyQt6 6.11 (Windows UI) | **GPL-3.0-only** | Forces GPL on the Windows build |
| PyQt6-Qt6 (Qt runtime) | LGPL-3.0 | Fine |
| CTranslate2, SentencePiece, Transformers | MIT / Apache-2.0 | Fine |
| OPUS-MT translation models | CC BY 4.0 | Fine with attribution |
| Noto Sans CJK JP | OFL-1.1 | Fine, fixed above |
| OpenJLPT study data | **CC BY-SA 4.0** | Fine, but share-alike on the data |
| Jonathan Waller JLPT lists | CC BY | Attribution only |
| JMdict / KANJIDIC2 | CC BY-SA 4.0 | Attribution only |
| Tatoeba sentences | CC BY 2.0 FR | Attribution only |
| SQLite | Public domain | Fine |

Full detail with versions: [`../THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

## 3. What that means for the phone app

**The phone app has no GPL component at all.** Kivy is MIT, sherpa-onnx is
Apache-2.0, the model is Apache-2.0, the font is OFL. The only copyleft
condition is the **study data**, which is CC BY-SA 4.0.

So for the phone app we must:

1. **Credit** OpenJLPT and the upstream sources - done in the app's
   *About & Licenses* screen, in `THIRD-PARTY-NOTICES.md`, and in the store
   listing.
2. **Link** to <https://creativecommons.org/licenses/by-sa/4.0/> - done.
3. **Offer our card data under CC BY-SA 4.0** - the deck files live in
   `assets/jlpt` in the public repository, and the app's About screen links
   straight to them. Done.
4. Ship the **third-party notices** - done, in the app and in the repo.

That is the whole obligation for the Play Store build.

## 4. The decision we made about the Windows build

PyQt6 is **GPL-3.0-only** and the Piper TTS code is **GPL-3.0-or-later**.
Distributing a Windows `.exe` that contains them as a *closed-source* product
would be a licence violation. There are only three ways out:

| Option | Cost | Result |
|---|---|---|
| **A. Ship the Windows build as GPL-3.0 open source** | Almost none - the source is already public | 100% compliant. GPL still lets us **charge money** for it; it only requires that we publish the source of what we ship. |
| B. Replace PyQt6 with PySide6 (LGPL) and Piper with a permissive engine | Days of work, new 300 MB model, risk of breaking the build | Windows build could stay closed source |
| C. Buy a commercial PyQt6 licence | ~$350-1,500 depending on seats | Windows build could stay closed source |

**We chose Option A for the launch.**

Reasons:

- The phone app is the product. It is the one that goes on the Play Store and
  it carries no GPL component, so nothing about it is blocked.
- The Windows build is a free extra. Releasing it under GPL-3.0 is completely
  legal, it costs nothing, and it removes an entire class of risk.
- The source is already public on GitHub, so Option A needs no extra work.
- GPL protects us: anyone who builds on it has to release their changes and
  keep the attribution.

The whole repository is therefore released under **GPL-3.0** (`LICENSE`), with
the study data under **CC BY-SA 4.0**. These two are compatible - CC BY-SA 4.0
is one-way compatible with GPL-3.0.

**If we ever want a closed-source Windows product**, the work is:

1. `PyQt6` -> `PySide6` - mechanical, the APIs are the same (about half a day
   plus testing).
2. Piper -> a permissive Japanese TTS. The options are sherpa-onnx's Kokoro
   models (Apache-2.0, but the Japanese path pulls in espeak-ng data, which is
   GPL) or MeloTTS (MIT, but it drags in PyTorch). This is the expensive one.
3. Re-issue the Windows build under a proprietary licence.

## 5. Obligations that come with what we ship

| Obligation | Where it is satisfied |
|---|---|
| Publish the source of the shipped app | The repository is public; the Play listing links to it (required by Google for copyleft apps) |
| Keep copyright and licence notices | `THIRD-PARTY-NOTICES.md`, the in-app *About & Licenses* screen |
| Offer the CC BY-SA data under CC BY-SA 4.0 | `assets/jlpt` in the repository, linked from the app and the store listing |
| Do not add restrictions on the GPL code | We have not |
| State that the app is unofficial | Privacy policy and store listing say so |
| Keep the OFL text with the font | `assets/fonts/OFL.txt` |

## 6. Trademarks - why the app was renamed

`Japanese Sensei` is already the exact name of a live Google Play app
(`com.katanaapps.shiftalk`, Education, 1K+ downloads) and of the iOS app
`Sensei Japanese` (`id6761647436`). A second app with the same name in the
same category reads as a knock-off, and Google can reject the listing or a
third party can complain about it.

The app was renamed to **AKANE** (勉強 = "study").

- Checked on Google Play in the **US** and **JP** locales: no exact name match.
- Checked on the Apple App Store: no exact name match.
- The domain `akanestudio.app` was **not registered** when checked on 21 October
  2026 (no NS or A records, RDAP returns not-found). **Buy it before launch**
  so the privacy-policy email address works and so the name cannot be squatted.

Also checked, so they are not surprised: there is an unrelated iOS app called
`AKANE: Speak & Learn Japanese`. That is a different store and a different
name, so it does not block this launch, but it is why the store title is
`AKANE: Learn Japanese` rather than just `AKANE`.

## 7. Open items that are not licences but still block the launch

1. **Release signing key.** `.keystore/sensei-debug.keystore` is a debug key
   with a password in the repository. Generate a real release key, keep it
   private and never commit it.
2. **Privacy-policy URL.** `docs/playstore/privacy-policy.html` has to be
   published to a public URL, and `privacy@akanestudio.app` needs to be a real
   mailbox.
3. **`android.api = 36`** - set. Play requires a current target SDK.
4. **Feature graphic and screenshots** - still to be produced.
5. **Personal Play accounts** need 12 testers for 14 days before the first
   production release. Start that clock now.

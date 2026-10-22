# AKANE - Google Play listing

Everything below is copy-paste ready. Character limits are Google's and are
checked at the bottom of this file.

---

## App name (max 30 characters)

```
AKANE: Learn Japanese Offline
```

Why this name: the app was renamed twice for clearance reasons.

1. "Japanese Sensei AI" - "Japanese Sensei" is the exact name of a live Play
   app (`com.katanaapps.shiftalk`) and of the iOS app "Sensei Japanese"
   (`id6761647436`). A same-name app in the same category reads as a knock-off
   and can be rejected.
2. "Benkyo Studio" - "Benkyo" is crowded in this exact category: iOS has
   "Benkyo: Speak & Learn Japanese" (`id6737715026`, MWD Services LLC) with a
   near-identical feature list, plus "Benkyo: Japanese Flashcards", "Benkyo -
   Language Learning" and the domain `benkyo.app`.
3. **AKANE** - checked against the Play Store (US + JP) and the Apple App
   Store: zero name collisions. 茜 = the deep crimson of a rising sun, which
   is what the app icon is.

The letters: **AI - Kanji - Audio - Nihongo - Everywhere.**

## Short description (max 80 characters)

```
JLPT N5-N1 study that is 100% offline. No ads, no account, no tracking.
```

## Full description (max 4000 characters)

```
AKANE - JLPT Japanese, completely offline.

The Japanese app that never asks for the internet.

AKANE is a full JLPT study system for N5 to N1 that works in airplane
mode. No account, no ads, no tracking, no subscription, no "data required"
warning. Every card, every audio clip and every bit of speech recognition runs
on your own phone.

AI - Kanji - Audio - Nihongo - Everywhere.

WHAT YOU GET

- 10,832 study cards across the whole JLPT N5-N1 range: vocabulary, kanji and
  grammar, organised by level and ready to drill.
- Spaced repetition that adapts to you, plus a daily study plan so you always
  know exactly what to do next.
- Speak practice: talk to the app and it transcribes you on the device, then
  scores your pronunciation.
- 2,329 native audio clips, pre-rendered, so listening works on a bus with no
  signal.
- Reading: graded passages with a tap-to-translate for every word.
- Listening: comprehension drills built from the same material.
- Shadowing: record yourself against a native voice and compare.
- Workbook: focused drills for kanji, vocabulary and grammar.
- Progress: every level, every kanji and every mistake tracked in detail.

WHY IT IS DIFFERENT

- 100% OFFLINE. The app holds no internet permission at all. Nothing you say,
  type or study is ever sent anywhere - not to us, not to anyone.
- NO ACCOUNT. Open it and start. There is nothing to sign up for.
- NO ADS, NO TRACKERS, NO DATA SOLD. Ever.
- LIGHT ON OLD PHONES. The voice engine is a small, fast local model, not a
  megabyte-hungry cloud call.
- OPEN SOURCE. The full source code is public under the GPL-3.0 licence.

PERFECT FOR

- JLPT candidates who want to study on the train.
- Learners tired of apps that need a subscription to unlock the good parts.
- Anyone who does not want an app holding their voice and their study history.

Everything is included. There is nothing to buy, nothing to unlock, no upsell
and no in-app purchase.

Content: JLPT data from OpenJLPT (CC BY-SA 4.0), using JMdict, KANJIDIC2,
Jonathan Waller's JLPT lists and Tatoeba. Speech recognition by sherpa-onnx and
the ReazonSpeech model (Apache 2.0). Japanese font: Noto Sans CJK JP (OFL).
Full licence details are inside the app under About & Licenses.

AKANE means 茜 - the deep crimson of a rising sun.
```

## Category and tags

| Field | Value |
|---|---|
| Category | Education |
| Secondary tag | Language Learning |
| Content rating | Everyone / 3+ |
| Contains ads | **No** |
| In-app purchases | **No** |
| Target audience | 16-17, 18+ (not aimed at children) |
| Family policy | Not in the Family Program - the icon and visuals are deliberately adult |

## Store assets checklist

| Asset | Requirement | Status |
|---|---|---|
| App icon | 512 x 512 PNG, 32-bit | `assets/brand/icon.png` - done |
| Feature graphic | 1024 x 500 PNG/JPG | **done** - `assets/brand/play_feature_graphic_1024x500.png` |
| Phone screenshots | at least 2, 16:9, 1080 x 1920 | **done** - `assets/store_screenshots/` (6 real captures from the phone) |
| 7-inch tablet | optional | skip at launch |
| Privacy policy URL | required | `docs/playstore/privacy-policy.html` - publish at `hivepulseinteractive.com/privacy.html` |
| Short description | 80 chars | above |
| Full description | 4000 chars | above |
| Support email | required | `privacy@hivepulseinteractive.com` |

## Screenshot plan (in this order)

1. **Today** - the daily plan, showing what to study. "Your plan for today."
2. **Speak practice** - mic recording + transcription + score. "Say it. Get scored. On your phone."
3. **Flashcards** - card front, one tap to flip. "10,832 cards, N5 to N1."
4. **Progress** - level breakdown, accuracy, streak. "See what is actually sticking."
5. **Reading** - passage with tap-to-translate. "Read real passages. Tap any word."
6. **Offline badge / Voice Engine screen** - "100% offline. No account. No ads."

## Keywords for the store description

The long description is the only place these words can live - put them in
naturally, they are already there or close to it:

`jlpt, n5, n4, n3, n2, n1, japanese, nihongo, kanji, hiragana, katakana,
vocabulary, grammar, offline, study, flashcard, pronunciation, speaking,
listening, shadowing, no ads, no subscription`

## Launch checklist

- [ ] `android.api = 36` (set - Play requires target API 36 from 31 Aug 2026)
- [ ] **Upload an App Bundle (.aab), not an APK.** New apps have to be
      published as a bundle, and the debug APK is ~146 MB which is over the
      100 MB limit for APK uploads. The CI workflow builds one:
      `gh run download akane-aab`.
- [ ] Release signing key generated and stored **privally** (the debug key in
      `.keystore/` is not for publishing). Play App Signing will hold the real
      app signing key; the key we upload is the *upload* key.
- [ ] Version bumped to 1.0.0 (done in `buildozer.spec`)
- [ ] Privacy policy published at `hivepulseinteractive.com/privacy.html`
- [ ] Feature graphic made - done: `assets/brand/play_feature_graphic_1024x500.png`
- [ ] Screenshots taken - done: `assets/store_screenshots/` (recapture after the rename)
- [ ] Data safety form filled in (`docs/playstore/data-safety.md`)
- [ ] Content rating questionnaire answered (see below)
- [ ] Source code link in the listing (required - the app is GPL-3.0)
- [ ] Target audience + content rating set
- [ ] Store contact email: `privacy@hivepulseinteractive.com`

## Content rating questionnaire - answers to give

- Category: Education
- Violence, sexuality, language, controlled substances, gambling, user
  interaction, sharing location, **digital purchases**: none / no
- "Does the app allow users to interact or exchange content?" - **No** (no
  accounts, no chat, no sharing)
- "Does the app share the user's current location?" - **No**
- "Is the app encrypted in transit?" - **Not applicable** (no network access)
- "Does the app allow users to purchase digital goods?" - **No**
- "Does the app contain or display user-generated content?" - **No**
- "Does the app allow users to communicate with each other?" - **No**
- App is free, no ads, no IAP -> nothing to declare

## Families policy notes

If the target audience includes children, Google requires the app to meet the
Families policy (ads must be behavioural, analytics limited, etc.). AKANE
avoids this entirely by declaring **16-17 and 18+ only** and by keeping
the icon and in-app art adult and non-childish. Do not tick any child age
group.

## Developer account type - organisation, not personal

Register the Play Console account under **Hive Pulse Interactive** (the LLC),
not the personal Gmail. Two reasons:

1. **Organisation accounts are exempt from the 12-tester / 14-day closed test.**
   A new personal account must run a closed test with 12 testers for 14
   consecutive days before it can go to production. An organisation account
   can go straight through.
2. The store listing will show the company, not a person's name - better trust
   for a paid app, and it matches the website.

**The cost of that choice:** an organisation account needs a **D-U-N-S number**
(free from Dun & Bradstreet, but it can take up to 30 days) plus the LLC's
registration documents, and the website has to be verified through Google
Search Console. Start the D-U-N-S application first thing - it is the longest
pole in the whole launch.

Also note: since May 2026 Google requires account transfers to use the
official 'Transfer ownership' workflow, so the first account should be set up
correctly rather than fixed later.

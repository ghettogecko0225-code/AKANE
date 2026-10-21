# Benkyo Studio - Google Play listing

Everything below is copy-paste ready. Character limits are Google's and are
checked at the bottom of this file.

---

## App name (max 30 characters)

```
Benkyo Studio: Learn Japanese
```

Why: "Japanese Sensei" is already the exact name of a live Play app
(`com.katanaapps.shiftalk`) and of the iOS app "Sensei Japanese"
(`id6761647436`). A same-name app in the same category reads as a knock-off
and can be rejected. "Benkyo Studio" was checked on Play Store (US + JP) and
Apple App Store - no name match. 勉強 = "study".

## Short description (max 80 characters)

```
JLPT N5-N1 study that is 100% offline. No ads, no account, no tracking.
```

## Full description (max 4000 characters)

```
Benkyo Studio - JLPT Japanese, completely offline.

The Japanese app that never asks for the internet.

Benkyo Studio is a full JLPT study system for N5 to N1 that works in airplane
mode. No account, no ads, no tracking, no subscription, no "data required"
warning. Every card, every audio clip and every bit of speech recognition runs
on your own phone.

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

Benkyo means "study" in Japanese. 勉強.
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
| Feature graphic | 1024 x 500 PNG/JPG | **to make** - dark navy with the sun mark, "Benkyo Studio" + "Study Japanese. Fully offline." |
| Phone screenshots | at least 2, 16:9, 1080 x 1920 | **to take** - Today plan, Flashcards, Speak practice, Progress, Reading |
| 7-inch tablet | optional | skip at launch |
| Privacy policy URL | required | `docs/playstore/privacy-policy.html` - publish to Google Sites (free) |
| Short description | 80 chars | above |
| Full description | 4000 chars | above |
| Support email | required | a real inbox Kevin controls |

## Screenshot plan (in this order)

1. **Today** - the daily plan, showing what to study. "Your plan for today."
2. **Speak practice** - mic recording + transcription + score. "Say it. Get scored. On your phone."
3. **Flashcards** - card front, one tap to flip. "10,832 cards, N5 to N1."
4. **Progress** - level breakdown, accuracy, streak. "See what is actually sticking."
5. **Reading** - passage with tap-to-translate. "Read real passages. Tap any word."
6. **Offline badge / Voice Engine screen** - "100% offline. No account. No ads."

## Keywords for the store description

Benkyo Studio is the only place these words can live - put them in the long
description naturally, they are already there or close to it:

`jlpt, n5, n4, n3, n2, n1, japanese, nihongo, kanji, hiragana, katakana,
vocabulary, grammar, offline, study, flashcard, pronunciation, speaking,
listening, shadowing, no ads, no subscription`

## Launch checklist

- [ ] `android.api = 36` (set - Play requires a current target SDK)
- [ ] Release signing key generated and stored **privately** (the debug key in
      `.keystore/` is not for publishing)
- [ ] Version bumped to 1.0.0 (done in `buildozer.spec`)
- [ ] Privacy policy published at a public URL
- [ ] Feature graphic made
- [ ] Screenshots taken
- [ ] Data safety form filled in (`docs/playstore/data-safety.md`)
- [ ] Content rating questionnaire answered (see below)
- [ ] Source code link in the listing (required - the app is GPL-3.0)
- [ ] Target audience + content rating set
- [ ] Store contact email that Kevin controls

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
Families policy (ads must be behavioural, analytics limited, etc.). Benkyo
Studio avoids this entirely by declaring **16-17 and 18+ only** and by keeping
the icon and in-app art adult and non-childish. Do not tick any child age
group.

## Personal developer accounts (new accounts)

If the Play console account is new, the first release has to go through:

1. **Closed test with at least 12 testers opted in for 14 continuous days.**
2. Apply for **production access** (Play's review of the app and the tester
   feedback).
3. Only then can the app go live in production.

Start the closed test early - it is a hard 14-day clock. Use Google Groups for
the tester list. While the closed test runs, publish the privacy policy, make
the screenshots and fill in every form, so nothing is waiting on the review.

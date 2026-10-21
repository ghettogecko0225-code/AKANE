# Privacy Policy - Benkyo Studio

**Last updated: 21 October 2026**

## The short version

Benkyo Studio collects no personal data. It has no internet permission, so it
technically cannot send anything anywhere.

---

## 1. Who we are

Benkyo Studio is published by Hive Pulse Interactive ("we"). It is an open
source study app for the Japanese language.

- App name: Benkyo Studio
- Android package id: `com.hivepulse.benkyo`
- Source code: <https://github.com/ghettogecko0225-code/Benkyo-Studio>

## 2. Data we collect

**None.**

The Android version of Benkyo Studio requests only the `RECORD_AUDIO`
permission and explicitly does **not** request the `INTERNET` permission. There
is no code in the app that can open a network connection.

That means the app cannot and does not:

- create an account or ask you to sign in,
- collect your name, email address, phone number or device identifiers,
- run analytics, advertising or crash-reporting SDKs,
- show ads or sponsored content,
- send notifications or push messages,
- collect your location,
- collect your contacts, photos, files or clipboard,
- share anything with us or with any third party.

There are no third-party analytics, advertising or attribution services in the
app. There are no tracking pixels, no SDKs and no hidden network calls.

## 3. What stays on your device

Everything the app needs is stored in the app's own private storage on your
device:

| What | Why | Where |
|---|---|---|
| Study progress, review history, scores | So the app can build your daily plan and show your progress | `benkyo.db` in the app's private storage |
| Your settings (theme, language, voice, daily goal) | So the app remembers how you like to study | The same private storage |
| A small diagnostic log | To help debug speech-recognition problems on your own device | `asr_log.txt` in the app's private storage |

This data is never uploaded. It is visible only to the app itself and to anyone
with physical access to your unlocked device.

## 4. Microphone

The app asks for the microphone only when you tap a button that records audio
(for example **Speak** or **Shadowing**).

- The audio is captured in memory, processed by the on-device speech model, and
  discarded.
- Voice recordings are **not** saved as files and are **not** transmitted.
- The app starts recording only after you tap the record button and stops when
  the capture finishes or you leave the screen.

## 5. Removing your data

- **Uninstalling the app deletes everything**, including your study history and
  settings, because all of it lives in the app's private storage.
- To clear it without uninstalling: Android **Settings â†’ Apps â†’ Benkyo Studio â†’
  Storage â†’ Clear data**.

## 6. Children

Benkyo Studio is a general-audience study app and is **not directed at children
under 13**. It is not part of Google Play's Family Program and does not collect
any information from anyone, including children.

## 7. Third-party content and open source

The app ships open-source components and open-licensed study content. These
projects are not responsible for the app, and we are not responsible for them.
Full details are inside the app under **About & Licenses**.

- JLPT study data from [OpenJLPT](https://github.com/evanclan/OpenJLPT),
  which uses JMdict, KANJIDIC2, Jonathan Waller's JLPT lists and Tatoeba -
  licensed **CC BY-SA 4.0**.
- Speech recognition by [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) and
  the [ReazonSpeech](https://github.com/reazon-research/ReazonSpeech) model -
  **Apache 2.0**.
- Japanese font Noto Sans CJK JP - **SIL Open Font License 1.1**.
- The application itself is open source under the **GNU General Public License
  v3.0**. Source: <https://github.com/ghettogecko0225-code/Benkyo-Studio>

"Japanese Language Proficiency Test" and "JLPT" are trademarks of the Japan
Foundation. This app is an unofficial study tool and is not affiliated with or
endorsed by the Japan Foundation. Android is a trademark of Google LLC.

## 8. Changes to this policy

If a future version of the app changes what it stores or does, this policy will
be updated before that version ships and the date at the top will change. The
policy is versioned in the app's source repository, so every change is visible
in the public history.

## 9. Contact

Questions, requests or concerns:

**privacy@benkyostudio.app**

We will answer privacy questions in plain English, and we do not need your
device or your data to do it.

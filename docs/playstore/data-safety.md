# Play Console - Data safety form

Copy these answers into the Play Console **Data safety** section. The form
asks about the app's behaviour, not about what is stored locally, so most
answers are "no data collected".

The whole form is short because the app has **no `INTERNET` permission**.

---

## Section 1 - Data collection and security

| Question | Answer |
|---|---|
| Does your app collect or share any of the required user data types? | **No** |
| Is all of the user data collected by your app encrypted in transit? | **Not applicable** - the app has no network access |
| Do you provide a way for users to request that their data is deleted? | **Yes** - uninstalling the app deletes everything, and the app also has no server-side data to delete. The in-app privacy policy explains this. |
| Do you collect data from children under 13? | **No** - no data is collected from anyone, and the app is not directed at children |

## Section 2 - Data types

Every row in the data-type table: **Not collected / Not shared**.

- Location
- Personal info (name, email, phone, user IDs, addresses)
- Financial info
- Health and fitness
- Messages
- Photos and videos
- Audio files
- Files and docs
- Calendar
- Contacts
- App activity (in-app interactions, other user-generated content, app info)
- Web browsing
- Info about your device (device IDs, advertising IDs)

## Section 3 - Purpose of collection

**Not applicable.** No data is collected.

## Section 4 - Security practices

| Question | Answer |
|---|---|
| Are your app's data collection practices in line with the Play Data safety policy? | **Yes** |
| Do you use Play Integrity API? | **No** |
| Do you have a data deletion mechanism? | **Yes** - clearing app data or uninstalling removes everything, because nothing is ever uploaded |

## Section 5 - App access and operations

| Question | Answer |
|---|---|
| Does your app require a user account? | **No** |
| Does your app send "sensitive" data off the device? | **No** - no network access exists in the app |
| Is the app a "news" app, a "weather" app or similar live-content app? | **No** |
| Does the app provide a way to interact with other users or share content? | **No** |
| Does the app allow users to buy digital goods? | **No** |
| Does the app display user-generated content? | **No** |
| Does the app share the user's current location? | **No** |

## Section 6 - Government or health apps

Not applicable - not a government or health app.

---

## Things that will be checked against the binary

Google's automated checks read the APK, so make sure the truth in the form
matches the build:

1. The merged manifest must **not** contain `android.permission.INTERNET`.
   - `buildozer.spec` has `android.permissions = RECORD_AUDIO` only.
   - Check with `aapt dump permissions app-debug.apk` before uploading.
2. No analytics or ad SDKs in the APK.
   - The build installs only `python3`, `kivy`, `pyjnius`, `sherpa_onnx` and
     `charset_normalizer`.
3. No Firebase, no Google Play Services, no Facebook SDK.
4. The app must not use the `QUERY_ALL_PACKAGES` permission.
5. The app must not load remote code (it does not - everything is bundled).
6. The app must not access the device's other files or the user's media
   library beyond the microphone.

If the app asks for `RECORD_AUDIO`, add a short in-app explanation the first
time the microphone is used - it already shows a status line such as
"Listening (offline Japanese model)...". Play's Data safety form also asks
whether the microphone is used and why: answer **"App functionality"**.

## Privacy policy requirement

A privacy policy URL is required even when no data is collected. Publish
`docs/playstore/privacy-policy.html` to a free Google Site and put that URL in
the Play Console **App content → Privacy policy** box and in the store listing.

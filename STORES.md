# Publishing Healthy Habits to the App Store and Google Play

The iOS and Android apps are built from the same code as the web app (`app/`),
wrapped with [Capacitor](https://capacitorjs.com/). GitHub Actions builds them
(`.github/workflows/mobile.yml`), so you don't need a Mac or Android Studio.

| | Apple App Store | Google Play |
|---|---|---|
| Developer account | $99 / year | $25 one-off |
| Price | **$3.99** (one-off, paid up front) | **$3.99** (one-off, paid up front) |
| Store's cut of sales | 15% with the Small Business Program (you get about $3.39 per sale) | 15% (about $3.39 per sale) |
| Review time | usually 1–3 days | a few hours to a few days (first review can take longer) |
| Testing before launch | TestFlight | New personal accounts must run a **closed test with 12 testers for 14 days** before going public |

**App ID (both stores):** `com.markwoodings.healthyhabits`. You can't change it
after the first upload. If you want a different one, change it in
`capacitor.config.json`, `android/app/build.gradle` and the Xcode project first.

**What's native in the store version:**
- Exact-time daily reminder notifications. They're scheduled on the device and skipped on days every habit is done.
- Haptic taps when ticking off habits.
- Backups exported through the share sheet.
- Proper app icons and a splash screen.

These native features matter because Apple rejects apps that are just a website in a wrapper.

---

## What's in this repo for the stores

- `store/screenshots/ios/`: six 1320×2868 screenshots (iPhone 6.9″, the size Apple requires)
- `store/screenshots/android/`: six 1080×1920 phone screenshots
- `store/play-feature-graphic.png`: the 1024×500 banner Google Play requires
- `store/play-icon-512.png` and `store/app-store-icon-1024.png`: store icons
- Privacy policy (both stores require one): https://markwoodings-max.github.io/calendar/privacy.html

---

## Google Play: step by step

1. **Create a developer account** at https://play.google.com/console (the $25 fee, plus identity verification).
   Then set up a **payments profile** (Play Console → *Settings* → *Payments profile*). Paid apps can't be
   published without one, and it's where your sales are paid out.
2. **Add the upload key to GitHub.** You were given `healthy-habits-upload.jks` and a
   `README-KEEP-SAFE.txt` file. Add the four secrets it lists at
   https://github.com/markwoodings-max/calendar/settings/secrets/actions and keep the files backed up somewhere private.
3. **Build.** Go to https://github.com/markwoodings-max/calendar/actions →
   **Build mobile apps** → **Run workflow**. When it finishes, download the
   **android-play-store-aab** artifact and unzip it to get `app-release.aab`.
4. **In Play Console:** *Create app* → name "Healthy Habits", type App, **Paid**.
   ⚠️ Choose Paid here. Google never lets a free app become paid later.
   Then go to *Monetize* → *App pricing* → set **USD 3.99**. Google converts it to local prices in
   other countries, and you can adjust any of them.
5. **Set up the store listing** using the copy below, the screenshots, the feature graphic and the 512 icon.
6. **Fill in the App content forms:**
   - **Privacy policy:** the URL above.
   - **Ads:** No.
   - **Data safety:** "No data collected" and "No data shared". All data stays on the device.
   - **Content rating questionnaire:** Health & fitness/utility with no violence, etc. This gives a PEGI 3 / Everyone rating.
   - **Target audience:** 18+ (or 13+). Avoid "children", which triggers extra rules.
   - **Health apps declaration:** a general wellness / habit tracker, not a medical device.
7. **Testing → Closed testing:** create a track, upload the `.aab`, and add at least 12 testers by
   Gmail address (friends, family, customers). Keep it running for 14 days.
8. **Apply for production** from the Dashboard, then promote the build.

Every later release: bump `versionName` in `android/app/build.gradle` (e.g. "1.1"),
run the workflow and upload the new `.aab`. The version code increases automatically.

## Apple App Store: step by step (no Mac needed)

1. **Enrol** in the Apple Developer Program at https://developer.apple.com/programs/ ($99/yr).
   Enrolling as an individual is quickest.
   Then in App Store Connect → *Business*, accept the **Paid Apps Agreement** and add your bank and
   tax details. A paid app can't go on sale until these show as "Active".
   Also apply for the **App Store Small Business Program**
   (https://developer.apple.com/app-store/small-business-program/). It cuts Apple's commission
   from 30% to 15%.
2. **Create the app record** in https://appstoreconnect.apple.com → *Apps* → **+** → New App:
   - Platform: iOS
   - Name: Healthy Habits (it must be unique on the store; see alternatives below)
   - Bundle ID: register `com.markwoodings.healthyhabits` at
     https://developer.apple.com/account/resources/identifiers first if it isn't listed
   - SKU: `healthyhabits1`
3. **Create an API key** so GitHub can sign and upload for you: App Store Connect →
   *Users and Access* → *Integrations* → *App Store Connect API* → **+**, with the **Admin** role.
   Download the `.p8` file (you only get one chance), and note the **Key ID** and **Issuer ID**.
4. **Find your Team ID** at https://developer.apple.com/account → *Membership details*.
5. **Add four GitHub secrets** at https://github.com/markwoodings-max/calendar/settings/secrets/actions:
   - `APPSTORE_TEAM_ID`: your Team ID
   - `APPSTORE_KEY_ID`: the Key ID
   - `APPSTORE_ISSUER_ID`: the Issuer ID
   - `APPSTORE_KEY_P8`: open the `.p8` file in a text editor and paste all of it, including the BEGIN/END lines
6. **Build and upload.** Actions → **Build mobile apps** → **Run workflow**. The iOS job signs
   the app and uploads it to App Store Connect. About 10–30 minutes later it appears under **TestFlight**.
7. **Test on your iPhone** with the TestFlight app. Add yourself under *Internal Testing*.
8. **Fill in the listing** (copy below): screenshots (6.9″), description, keywords, support URL,
   privacy policy URL, category and age rating questionnaire (all "None", which gives 4+).
   Under *Pricing and Availability*, set the base price to **USD 3.99**; Apple sets the other
   countries' prices from it.
9. **App Privacy:** choose **"Data Not Collected"**.
10. **Select the build** on the version page → **Add for Review** → **Submit**.

A Mac with Xcode also works: run `npm install && npx cap open ios`, then use Product → Archive.

---

## Store listing copy

**Name:** Healthy Habits
(Alternatives if the name is taken: "Healthy Habits: Daily Tracker", "Small Steps Habit Tracker")

**Subtitle (App Store, 30 chars):** Habit, mood & water tracker

**Short description (Play, 80 chars):** Track daily habits, mood, water and sleep. Private, simple and offline.

**Keywords (App Store, 100 chars):**
habit,tracker,routine,goals,mood,water,sleep,wellness,self care,journal,planner,streak,reminder

**Category:** Health & Fitness (secondary: Lifestyle)

**Description:**

> Small steps add up. Healthy Habits helps you build a routine you can keep, one tick at a time.
>
> TRACK WHAT MATTERS
> • Tick off your daily habits and watch your streaks grow
> • Log your mood, water and sleep in seconds
> • Start with 8 proven healthy habits, or add your own
>
> SEE YOUR PROGRESS
> • Monthly calendar shaded by how much you got done
> • A full habit grid for every month
> • Year in Pixels: colour each day by mood and spot the patterns
> • Totals, perfect days and your best streak
>
> REFLECT AND ADJUST
> • Set a monthly intention
> • Guided monthly reflection: wins, what got in the way, what to change
> • Rate your month and pick one word for it
>
> GENTLE REMINDERS
> • A daily reminder at the time you choose
> • Skipped automatically on days you've already done everything
>
> PRIVATE BY DESIGN
> • No account, no ads, no tracking
> • Your data never leaves your phone
> • Works fully offline
> • Export a backup whenever you like
>
> Healthy Habits is a personal wellness tool and is not medical advice.

**Promotional text (App Store, can be changed anytime):** Build habits that stick, with daily check-ins, streaks, mood tracking and a gentle evening reminder.

**Support URL:** https://markwoodings-max.github.io/calendar/privacy.html (or your own site)

## Pricing

**$3.99, paid up front**, in both stores. There's no free tier, no ads and no in-app
purchases, which fits the "private, no tracking" message. You set the price in the store
consoles (steps above), not in the code, so you can change it any time without an update.

- **About $3.39 per sale** after the 15% store fee (before tax/VAT, which the stores handle for you).
- **Launch discounts:** both stores let you schedule temporary price drops, e.g. $1.99 for launch week.
- **The web version:** the GitHub Pages copy of the app is free for anyone with the link.
  Once the store apps are live, reduce that site to just the privacy policy (or a page linking to the stores).
- **Bundles:** you can still sell the printable PDF separately, or give PDF buyers a
  promo code for the app (App Store: *Promo Codes*; Play: *Promotions*).

## Updating the apps

1. Change the code in `app/`. The same code serves the web and both stores.
2. Bump the version: `versionName` in `android/app/build.gradle`, and `MARKETING_VERSION` in the Xcode project (both are "1.0" now).
3. Push, or run the workflow. It builds both apps; iOS uploads itself when the App Store secrets are set.

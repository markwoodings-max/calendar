# Healthy Habits Calendar

A 42-page digital planner for tracking healthy habits, built to sell as a
downloadable product. It prints well, and it also works as a hyperlinked
planner in GoodNotes, Notability and other PDF note-taking apps.

The finished files are in [`dist/`](dist/):

| File | Size | Use |
|---|---|---|
| `healthy-habits-2027-letter.pdf` | US Letter, landscape | US/Canada buyers, and iPad |
| `healthy-habits-2027-a4.pdf` | A4, landscape | UK/EU/AU buyers, and iPad |
| `healthy-habits-app.zip` | Phone/desktop app | See [The app](#the-app) |

A good product ladder is the printable PDF at a low price, the app on its own,
and a bundle of both at a premium.

## What's inside

1. **Cover**: title, year, tagline and your name.
2. **Welcome**: six steps for using the planner, plus a personal-use notice and a note that it isn't medical advice.
3. **My Habits**: space to choose up to 12 habits and write down why each one matters.
4. **Year at a Glance**: twelve mini calendars. Tapping one opens that month.
5. **Year in Pixels**: a mood grid for the whole year with a colour key.
6. **For each month (3 pages)**:
   - **Calendar**: a monthly intention, focus habits, notes, and a "did every habit" circle on each day.
   - **Habit tracker**: a grid of 12 habits by 31 days, with weekends shaded and a total for each row. Below it are rows to log mood, energy, water and sleep.
   - **Reflection**: six prompts (wins, blockers, lessons, keep, change, next month), a 1–10 rating for the month, a completion % box and a "one word" line.
7. **Notes**: a lined page.

Every page has clickable tabs down the right edge (Year, Jan–Dec, Notes). Each
month page also has Calendar / Habits / Reflection buttons, and the PDF has a
full bookmark outline.

## The app

[`app/`](app/) holds a phone app version of the planner. It's an installable
web app (a "PWA"): it works offline, it can be added to the home screen on
iPhone, Android and desktop, and it needs no app-store approval.

What buyers can do in it:

- **Today**: tick off habits (with streaks), pick a mood, count glasses of water, log sleep and write a note.
- **Month**: set a monthly intention, see a calendar shaded by how many habits were done each day (tap a day to open it), and scroll the full habit grid.
- **Year**: a Year in Pixels mood grid, plus totals for habits done, perfect days and best streak.
- **Reflect**: the same monthly prompts as the PDF, a 1–10 rating and an automatic habit-completion %.
- **Habits**: add, rename, reorder or delete habits, choose the week start and water goal, and back up or restore their data.
- **Daily reminder**: switch it on and pick a time (8 PM by default). It reaches buyers three ways:
  - **"Add reminder to my calendar"** creates a daily repeating calendar event with an alert. It works on every phone, even with the app closed, and it's the most reliable option on iPhone.
  - **Background notifications** on Android and desktop Chrome/Edge when the app is installed. The browser chooses the exact minute, usually close to the set time.
  - **In-app nudges** when the app is opened after the reminder time, if habits are still unticked.

  Web apps can't schedule a notification for an exact time without a push server. That's why the calendar option exists, and it's what makes reminders work with no server to run.

Everything a buyer enters stays private on their own device. There are no
accounts and no server, so you have nothing to run or pay for beyond hosting
the files. Buyers should use **Export backup** to move to a new phone.

To rebrand it, edit `app/config.js` (title, your name, default habits, mood colours).
When you ship an update, change `VERSION` in `app/sw.js` so installed copies refresh.

### Getting it to buyers

The app is plain files, so any static host works:

1. **Host it.** The simplest option is Netlify Drop (drag the `app` folder onto
   app.netlify.com/drop), or turn on GitHub Pages for this repo. Both are free
   and use HTTPS, which offline mode and installing need.
2. **Sell the link.** On Etsy, Gumroad, Payhip or a Stan Store, make the
   product's delivery file a short PDF with the app link and install steps:
   - **iPhone:** open in Safari → Share → *Add to Home Screen*
   - **Android:** open in Chrome → ⋮ → *Install app*
3. You can also sell `dist/healthy-habits-app.zip` as the download itself. Buyers
   who want to use it on a phone still need to host it somewhere, so the link is
   friendlier for most buyers.

A shared link can be passed on to people who didn't buy. For a $5–$15 product
that is usually an acceptable trade-off. If it becomes a problem, you can add
license keys (Gumroad and Lemon Squeezy both offer them).

### Apple App Store / Google Play (optional, later)

The same code can be wrapped as a native app with [Capacitor](https://capacitorjs.com/)
if you want a real App Store or Play Store listing. It costs more: Apple charges
$99 a year and Google a one-time $25, both run a review, and each store takes a
15–30% cut. Apple also sometimes rejects apps that are "just a website", so plan
to add native touches first. Swapping the reminder for Capacitor's Local
Notifications plugin gives exact-time reminders on both platforms.

## Customising and regenerating

Edit `config.json` to change these settings:

- `brand`: your name, the product title, the tagline and an optional website (shown in the footer)
- `year` and `week_start` (`sunday` or `monday`)
- `habits`: the pre-filled habits, plus how many blank rows to add
- `colors` and `mood_colors`: the palette

Then run:

```bash
pip install reportlab
python generate.py                    # both sizes
python generate.py --year 2028        # next year's edition
python generate.py --week-start monday --size a4
```

## Selling it

**Where to sell:** Etsy has the most buyers already searching for planners.
Gumroad, Payhip and Lemon Squeezy are simple, low-fee options, or you can link
a Stan Store from Instagram or TikTok. All of them deliver the PDF
automatically after payment.

**Suggested listing bundle:** one zip containing both PDFs (Letter and A4), plus
a short "How to import into GoodNotes" note.

**Pricing:** similar habit-tracker PDFs usually sell for about $5–$15. A
hyperlinked, full-year planner with both paper sizes fits the upper part of
that range.

**Listing images:** use the cover, a habit tracker page, Year in Pixels and a
reflection page. Mock-ups on an iPad or a printed page on a desk convert best.

**Product ideas to grow the line:**
- Undated or Monday-start editions (one `config.json` change each)
- Themed versions with different habits and colours (fitness, sleep, mindfulness, hydration)
- A new edition each year using `--year`

**Things to keep in mind:**
- The Welcome page includes a personal-use / no-resale notice.
- It also says the planner isn't medical advice. Keep health claims in your listings modest as well.
- Some platforms handle VAT/sales tax on digital goods for you (Etsy, Gumroad, Payhip, Lemon Squeezy). Check this for yours.

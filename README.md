# Healthy Habits Calendar

A 42-page digital planner for tracking healthy habits, built to sell as a
downloadable product. It prints well, and it also works as a hyperlinked
planner in GoodNotes, Notability and other PDF note-taking apps.

The finished files are in [`dist/`](dist/):

| File | Size | Use |
|---|---|---|
| `healthy-habits-2027-letter.pdf` | US Letter, landscape | US/Canada buyers, and iPad |
| `healthy-habits-2027-a4.pdf` | A4, landscape | UK/EU/AU buyers, and iPad |

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

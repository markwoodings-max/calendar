#!/usr/bin/env python3
"""Generate the Healthy Habits printable / digital planner PDFs.

Usage:
    python generate.py                     # both sizes, settings from config.json
    python generate.py --size letter       # one size only
    python generate.py --year 2028 --week-start monday

Output lands in dist/. Every page is hyperlinked (side tabs, year overview,
month sub-navigation) so the same PDF works printed or in GoodNotes/Notability.
"""

import argparse
import calendar
import json
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfgen import canvas

ROOT = Path(__file__).parent
SIZES = {"letter": landscape(letter), "a4": landscape(A4)}
MONTHS = list(calendar.month_name)[1:]
MONTH_ABBR = [m[:3].upper() for m in MONTHS]

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SERIF = "Times-Roman"
FONT_SERIF_ITALIC = "Times-Italic"

MARGIN = 36
TAB_W = 30
HEADER_H = 74


class Planner:
    def __init__(self, cfg, size_name, out_path):
        self.cfg = cfg
        self.year = cfg["year"]
        self.brand = cfg["brand"]
        self.col = {k: HexColor(v) for k, v in cfg["colors"].items()}
        self.mood = {k: HexColor(v) for k, v in cfg["mood_colors"].items()}
        self.habits = list(cfg["habits"]) + [""] * cfg.get("blank_habit_rows", 0)
        first = 6 if cfg["week_start"] == "sunday" else 0
        self.cal = calendar.Calendar(firstweekday=first)
        self.weekday_labels = ["S", "M", "T", "W", "T", "F", "S"] if first == 6 else ["M", "T", "W", "T", "F", "S", "S"]
        self.W, self.H = SIZES[size_name]
        self.c = canvas.Canvas(str(out_path), pagesize=(self.W, self.H))
        self.c.setTitle(f"{self.brand['title']} {self.year}")
        self.c.setAuthor(self.brand["author"])
        self.c.setSubject("Healthy habits calendar and tracker")
        # content area (right side reserved for navigation tabs)
        self.left = MARGIN
        self.right = self.W - TAB_W - 18
        self.top = self.H - MARGIN - HEADER_H
        self.bottom = MARGIN

    # ---------- shared drawing helpers ----------

    def background(self):
        c = self.c
        c.setFillColor(self.col["background"])
        c.rect(0, 0, self.W, self.H, stroke=0, fill=1)

    def header(self, title, subtitle=None, key=None, month=None):
        c = self.c
        if key:
            c.bookmarkPage(key)
        y = self.H - MARGIN - 30
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_SERIF, 30)
        c.drawString(self.left, y, title)
        if subtitle:
            c.setFillColor(self.col["muted"])
            c.setFont(FONT_SERIF_ITALIC, 13)
            c.drawString(self.left, y - 20, subtitle)
        if month is not None:
            self.month_subnav(month, y)
        c.setStrokeColor(self.col["secondary"])
        c.setLineWidth(1.2)
        c.line(self.left, self.top + 12, self.right, self.top + 12)

    def month_subnav(self, month, y):
        """Calendar · Habits · Reflection links in the top right of month pages."""
        c = self.c
        items = [("Calendar", f"m{month}"), ("Habits", f"m{month}h"), ("Reflection", f"m{month}r")]
        x = self.right
        c.setFont(FONT_BOLD, 9)
        for label, dest in reversed(items):
            w = c.stringWidth(label.upper(), FONT_BOLD, 9) + 16
            x -= w
            c.setFillColor(self.col["tint"])
            c.setStrokeColor(self.col["line"])
            c.roundRect(x, y - 4, w, 18, 9, stroke=1, fill=1)
            c.setFillColor(self.col["primary"])
            c.drawCentredString(x + w / 2, y + 2, label.upper())
            c.linkRect("", dest, (x, y - 4, x + w, y + 14), thickness=0)
            x -= 6

    def tabs(self, active=None):
        """Clickable side tabs: YEAR + 12 months + NOTES."""
        c = self.c
        labels = [("YEAR", "year")] + [(MONTH_ABBR[i], f"m{i + 1}") for i in range(12)] + [("NOTES", "notes")]
        x = self.W - TAB_W
        top = self.H - 24
        h = (top - 24) / len(labels)
        for i, (label, dest) in enumerate(labels):
            y = top - (i + 1) * h
            is_active = dest == active
            c.setFillColor(self.col["primary"] if is_active else (self.col["tint"] if i % 2 else self.col["background"]))
            c.setStrokeColor(self.col["line"])
            c.setLineWidth(0.5)
            c.rect(x, y, TAB_W, h, stroke=1, fill=1)
            c.saveState()
            c.translate(x + TAB_W / 2 + 3, y + h / 2)
            c.rotate(90)
            c.setFillColor(white if is_active else self.col["primary"])
            c.setFont(FONT_BOLD, 7.5)
            c.drawCentredString(0, 0, label)
            c.restoreState()
            c.linkRect("", dest, (x, y, x + TAB_W, y + h), thickness=0)

    def footer(self):
        c = self.c
        c.setFont(FONT, 7)
        c.setFillColor(self.col["muted"])
        text = f"{self.brand['title']} {self.year}  ·  © {self.brand['author']}"
        if self.brand.get("website"):
            text += f"  ·  {self.brand['website']}"
        c.drawString(self.left, 16, text)

    def lined_box(self, x, y_top, w, h, label, spacing=18):
        c = self.c
        c.setFillColor(white)
        c.setStrokeColor(self.col["line"])
        c.setLineWidth(0.8)
        c.roundRect(x, y_top - h, w, h, 8, stroke=1, fill=1)
        c.setFillColor(self.col["secondary"])
        c.setFont(FONT_BOLD, 8.5)
        c.drawString(x + 10, y_top - 16, label.upper())
        c.setStrokeColor(self.col["line"])
        c.setLineWidth(0.5)
        ly = y_top - 16 - spacing
        while ly > y_top - h + 8:
            c.line(x + 10, ly, x + w - 10, ly)
            ly -= spacing

    def end_page(self, active=None):
        self.tabs(active)
        self.footer()
        self.c.showPage()

    # ---------- pages ----------

    def cover(self):
        c = self.c
        self.background()
        c.setFillColor(self.col["tint"])
        c.circle(self.W * 0.78, self.H * 0.62, 190, stroke=0, fill=1)
        c.setFillColor(self.col["secondary"])
        c.circle(self.W * 0.86, self.H * 0.30, 70, stroke=0, fill=1)
        c.setFillColor(self.col["accent"])
        c.circle(self.W * 0.70, self.H * 0.80, 28, stroke=0, fill=1)

        x = MARGIN + 30
        c.setFillColor(self.col["muted"])
        c.setFont(FONT_BOLD, 11)
        c.drawString(x, self.H * 0.66, "PLANNER  ·  TRACKER  ·  JOURNAL")
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_SERIF, 64)
        c.drawString(x, self.H * 0.52, self.brand["title"])
        c.setFont(FONT_SERIF, 96)
        c.setFillColor(self.col["secondary"])
        c.drawString(x, self.H * 0.52 - 100, str(self.year))
        c.setFillColor(self.col["text"])
        c.setFont(FONT_SERIF_ITALIC, 18)
        c.drawString(x, self.H * 0.52 - 135, self.brand["tagline"])
        c.setFillColor(self.col["muted"])
        c.setFont(FONT, 11)
        c.drawString(x, MARGIN + 10, f"by {self.brand['author']}")
        c.setFont(FONT, 9)
        c.drawString(x, MARGIN - 6, "Tap the tabs on the right edge of any page to jump around.")
        self.tabs()
        c.showPage()

    def how_to(self):
        c = self.c
        self.background()
        self.header("Welcome", "How to get the most from this planner", key="howto")
        steps = [
            ("Pick your habits", "Choose 5–10 habits on the next page. Small and specific beats big and vague."),
            ("Set a monthly intention", "At the start of each month, write one sentence about how you want to feel."),
            ("Track daily", "Fill in a circle each day you complete a habit. Colour the calendar circle when you hit them all."),
            ("Colour your mood", "Use the Year in Pixels page to colour each day by mood and spot patterns."),
            ("Reflect monthly", "Use the reflection page to celebrate wins and adjust what isn't working."),
            ("Be kind to yourself", "Missed a day? Never miss twice. Progress, not perfection."),
        ]
        col_w = (self.right - self.left - 24) / 2
        y = self.top - 10
        for i, (title, body) in enumerate(steps):
            col, row = i % 2, i // 2
            x = self.left + col * (col_w + 24)
            yy = y - row * 110
            c.setFillColor(self.col["secondary"])
            c.circle(x + 18, yy - 18, 16, stroke=0, fill=1)
            c.setFillColor(white)
            c.setFont(FONT_BOLD, 14)
            c.drawCentredString(x + 18, yy - 23, str(i + 1))
            c.setFillColor(self.col["primary"])
            c.setFont(FONT_BOLD, 13)
            c.drawString(x + 46, yy - 16, title)
            c.setFillColor(self.col["text"])
            c.setFont(FONT, 10.5)
            self.wrap(body, x + 46, yy - 34, col_w - 50, 14)

        c.setFillColor(self.col["muted"])
        c.setFont(FONT, 8)
        notes = [
            "For personal use only. Please do not share, resell or redistribute this file.",
            "This planner is not medical advice. Talk to a healthcare professional before making major changes to diet, exercise or sleep.",
        ]
        for i, n in enumerate(notes):
            c.drawString(self.left, self.bottom + 14 - i * 11, n)
        self.end_page()

    def wrap(self, text, x, y, width, leading):
        c = self.c
        line = ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            if c.stringWidth(trial, c._fontname, c._fontsize) > width:
                c.drawString(x, y, line)
                y -= leading
                line = word
            else:
                line = trial
        if line:
            c.drawString(x, y, line)

    def my_habits(self):
        c = self.c
        self.background()
        self.header("My Habits", "Choose your habits and why they matter to you", key="habits")
        n = len(self.habits)
        row_h = min(34, (self.top - self.bottom - 40) / n)
        name_w = 240
        y = self.top - 10
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.col["secondary"])
        c.drawString(self.left + 30, y, "HABIT")
        c.drawString(self.left + 30 + name_w, y, "WHY IT MATTERS TO ME")
        c.drawRightString(self.right, y, "WHEN / WHERE")
        y -= 10
        for i, habit in enumerate(self.habits):
            yy = y - (i + 1) * row_h
            c.setFillColor(self.col["tint"] if i % 2 == 0 else self.col["background"])
            c.rect(self.left, yy, self.right - self.left, row_h, stroke=0, fill=1)
            c.setFillColor(self.col["secondary"])
            c.setFont(FONT_BOLD, 10)
            c.drawString(self.left + 8, yy + row_h / 2 - 4, f"{i + 1:02d}")
            c.setFillColor(self.col["text"])
            c.setFont(FONT, 11)
            c.drawString(self.left + 30, yy + row_h / 2 - 4, habit)
            c.setStrokeColor(self.col["line"])
            c.setLineWidth(0.5)
            if not habit:
                c.line(self.left + 30, yy + 8, self.left + name_w - 10, yy + 8)
            c.line(self.left + 30 + name_w, yy + 8, self.right - 130, yy + 8)
            c.line(self.right - 110, yy + 8, self.right - 4, yy + 8)
        self.end_page()

    def year_overview(self):
        c = self.c
        self.background()
        self.header(f"{self.year} at a Glance", "Tap any month to jump straight to it", key="year")
        cols, rows = 4, 3
        gap = 18
        cw = (self.right - self.left - gap * (cols - 1)) / cols
        ch = (self.top - self.bottom - gap * (rows - 1)) / rows
        for m in range(1, 13):
            col, row = (m - 1) % cols, (m - 1) // cols
            x = self.left + col * (cw + gap)
            y_top = self.top - row * (ch + gap)
            self.mini_month(m, x, y_top, cw, ch)
            c.linkRect("", f"m{m}", (x, y_top - ch, x + cw, y_top), thickness=0)
        self.end_page("year")

    def mini_month(self, m, x, y_top, w, h):
        c = self.c
        c.setFillColor(white)
        c.setStrokeColor(self.col["line"])
        c.setLineWidth(0.8)
        c.roundRect(x, y_top - h, w, h, 8, stroke=1, fill=1)
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_BOLD, 10)
        c.drawString(x + 10, y_top - 17, MONTHS[m - 1].upper())
        cell_w = (w - 20) / 7
        weeks = self.cal.monthdayscalendar(self.year, m)
        cell_h = (h - 40) / 7
        c.setFont(FONT_BOLD, 7)
        c.setFillColor(self.col["secondary"])
        for i, d in enumerate(self.weekday_labels):
            c.drawCentredString(x + 10 + cell_w * (i + 0.5), y_top - 32, d)
        c.setFont(FONT, 8)
        c.setFillColor(self.col["text"])
        for r, week in enumerate(weeks):
            for i, day in enumerate(week):
                if day:
                    c.drawCentredString(x + 10 + cell_w * (i + 0.5), y_top - 32 - cell_h * (r + 1), str(day))

    def year_in_pixels(self):
        c = self.c
        self.background()
        self.header("Year in Pixels", "Colour one square a day to match your mood", key="pixels")
        legend_w = 120
        grid_left = self.left + 22
        grid_right = self.right - legend_w - 20
        grid_top = self.top - 16
        cell_w = (grid_right - grid_left) / 12
        cell_h = (grid_top - self.bottom) / 31
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(self.col["secondary"])
        for m in range(12):
            c.drawCentredString(grid_left + cell_w * (m + 0.5), grid_top + 4, MONTH_ABBR[m])
        c.setFont(FONT, 6.5)
        for d in range(31):
            c.setFillColor(self.col["muted"])
            c.drawRightString(grid_left - 5, grid_top - cell_h * (d + 1) + cell_h / 2 - 2, str(d + 1))
        c.setLineWidth(0.5)
        for m in range(12):
            days = calendar.monthrange(self.year, m + 1)[1]
            for d in range(31):
                x = grid_left + cell_w * m
                y = grid_top - cell_h * (d + 1)
                if d < days:
                    c.setFillColor(white)
                    c.setStrokeColor(self.col["line"])
                    c.rect(x + 1, y + 1, cell_w - 2, cell_h - 2, stroke=1, fill=1)
        lx = self.right - legend_w
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_BOLD, 9)
        c.drawString(lx, grid_top, "MOOD KEY")
        for i, (label, color) in enumerate(self.mood.items()):
            y = grid_top - 30 - i * 30
            c.setFillColor(color)
            c.roundRect(lx, y, 22, 18, 4, stroke=0, fill=1)
            c.setFillColor(self.col["text"])
            c.setFont(FONT, 10)
            c.drawString(lx + 30, y + 5, label)
        self.end_page("year")

    def month_calendar(self, m):
        c = self.c
        self.background()
        name = MONTHS[m - 1]
        self.header(f"{name} {self.year}", "Monthly calendar", key=f"m{m}", month=m)
        c.addOutlineEntry(name, f"m{m}", level=0)
        c.addOutlineEntry("Calendar", f"m{m}", level=1)

        side_w = 170
        self.lined_box(self.left, self.top, side_w, 120, "This month I intend to…")
        self.lined_box(self.left, self.top - 134, side_w, 130, "Focus habits")
        self.lined_box(self.left, self.top - 278, side_w, self.top - 278 - self.bottom, "Notes")

        gx = self.left + side_w + 16
        gw = self.right - gx
        weeks = self.cal.monthdayscalendar(self.year, m)
        cw = gw / 7
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(self.col["secondary"])
        full_days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        if self.weekday_labels[0] == "M":
            full_days = full_days[1:] + full_days[:1]
        for i, d in enumerate(full_days):
            c.drawCentredString(gx + cw * (i + 0.5), self.top - 6, d)
        gtop = self.top - 14
        ch = (gtop - self.bottom) / len(weeks)
        c.setLineWidth(0.6)
        for r, week in enumerate(weeks):
            for i, day in enumerate(week):
                x = gx + cw * i
                y = gtop - ch * (r + 1)
                c.setStrokeColor(self.col["line"])
                c.setFillColor(white if day else self.col["tint"])
                c.rect(x, y, cw, ch, stroke=1, fill=1)
                if day:
                    c.setFillColor(self.col["primary"])
                    c.setFont(FONT_BOLD, 11)
                    c.drawString(x + 6, y + ch - 15, str(day))
                    # "all habits done" circle
                    c.setStrokeColor(self.col["secondary"])
                    c.circle(x + cw - 11, y + ch - 11, 5, stroke=1, fill=0)
        c.setFont(FONT, 7.5)
        c.setFillColor(self.col["muted"])
        c.drawRightString(self.right, self.bottom - 12, "Fill the corner circle on days you complete every habit.")
        self.end_page(f"m{m}")

    def habit_tracker(self, m):
        c = self.c
        self.background()
        name = MONTHS[m - 1]
        self.header(f"{name} Habits", "Fill a circle for every habit you complete", key=f"m{m}h", month=m)
        c.addOutlineEntry("Habit tracker", f"m{m}h", level=1)

        days = calendar.monthrange(self.year, m)[1]
        name_w = 150
        total_w = 38
        dx = (self.right - self.left - name_w - total_w) / 31
        rows = self.habits + ["Mood (1–5)", "Energy (1–5)", "Water (glasses)", "Sleep (hours)"]
        head_h = 30
        row_h = min(26, (self.top - self.bottom - head_h) / len(rows))
        y0 = self.top
        # column header: weekday letter + day number
        for d in range(1, days + 1):
            x = self.left + name_w + dx * (d - 1)
            wd = calendar.weekday(self.year, m, d)  # Mon=0
            weekend = wd >= 5
            if weekend:
                c.setFillColor(self.col["tint"])
                c.rect(x, y0 - head_h - row_h * len(rows), dx, head_h + row_h * len(rows), stroke=0, fill=1)
            c.setFillColor(self.col["secondary"])
            c.setFont(FONT_BOLD, 6.5)
            c.drawCentredString(x + dx / 2, y0 - 10, "MTWTFSS"[wd])
            c.setFillColor(self.col["primary"])
            c.setFont(FONT_BOLD, 8)
            c.drawCentredString(x + dx / 2, y0 - 22, str(d))
        c.setFillColor(self.col["secondary"])
        c.setFont(FONT_BOLD, 7)
        c.drawCentredString(self.right - total_w / 2, y0 - 22, "TOTAL")
        c.drawString(self.left + 4, y0 - 22, "HABIT")

        r = min(dx, row_h) * 0.30
        for i, label in enumerate(rows):
            y = y0 - head_h - row_h * (i + 1)
            is_metric = i >= len(self.habits)
            c.setStrokeColor(self.col["line"])
            c.setLineWidth(0.5)
            c.line(self.left, y, self.right, y)
            c.setFillColor(self.col["text"] if not is_metric else self.col["muted"])
            c.setFont(FONT if not is_metric else FONT_SERIF_ITALIC, 9 if not is_metric else 10)
            if label:
                c.drawString(self.left + 4, y + row_h / 2 - 3, label)
            else:
                c.line(self.left + 4, y + 6, self.left + name_w - 10, y + 6)
            for d in range(1, days + 1):
                cx = self.left + name_w + dx * (d - 0.5)
                cy = y + row_h / 2
                if is_metric:
                    continue  # blank cell to write a number in
                c.setStrokeColor(self.col["secondary"])
                c.setFillColor(white)
                c.circle(cx, cy, r, stroke=1, fill=1)
            if not is_metric:
                c.setStrokeColor(self.col["line"])
                c.roundRect(self.right - total_w + 6, y + 4, total_w - 10, row_h - 8, 4, stroke=1, fill=0)
        # thin vertical guides on metric rows so numbers line up
        metric_top = y0 - head_h - row_h * len(self.habits)
        metric_bottom = y0 - head_h - row_h * len(rows)
        c.setStrokeColor(self.col["line"])
        c.setLineWidth(0.3)
        for d in range(days + 1):
            x = self.left + name_w + dx * d
            c.line(x, metric_top, x, metric_bottom)
        c.setStrokeColor(self.col["secondary"])
        c.setLineWidth(1)
        c.line(self.left, metric_top, self.right, metric_top)
        self.end_page(f"m{m}")

    def reflection(self, m):
        c = self.c
        self.background()
        name = MONTHS[m - 1]
        self.header(f"{name} Reflection", "Look back, celebrate, adjust", key=f"m{m}r", month=m)
        c.addOutlineEntry("Reflection", f"m{m}r", level=1)

        gap = 16
        cw = (self.right - self.left - gap * 2) / 3
        top = self.top
        h1 = (top - self.bottom - gap - 70) / 2
        prompts = [
            "Wins I'm proud of",
            "What got in the way",
            "What I learned about myself",
            "Habits to keep",
            "Habits to change or drop",
            "Next month I will…",
        ]
        for i, p in enumerate(prompts):
            col, row = i % 3, i // 3
            self.lined_box(self.left + col * (cw + gap), top - row * (h1 + gap), cw, h1, p)

        # rating strip
        y = self.bottom + 20
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_BOLD, 9)
        c.drawString(self.left, y + 22, "RATE THIS MONTH")
        for i in range(10):
            cx = self.left + 12 + i * 30
            c.setStrokeColor(self.col["secondary"])
            c.setFillColor(white)
            c.circle(cx, y + 2, 11, stroke=1, fill=1)
            c.setFillColor(self.col["muted"])
            c.setFont(FONT, 8)
            c.drawCentredString(cx, y - 1, str(i + 1))
        bx = self.left + 340
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_BOLD, 9)
        c.drawString(bx, y + 22, "HABIT COMPLETION")
        c.setStrokeColor(self.col["line"])
        c.setFillColor(white)
        c.roundRect(bx, y - 10, 90, 26, 6, stroke=1, fill=1)
        c.setFillColor(self.col["muted"])
        c.setFont(FONT, 12)
        c.drawRightString(bx + 82, y - 2, "%")
        c.setFillColor(self.col["primary"])
        c.setFont(FONT_BOLD, 9)
        c.drawString(bx + 120, y + 22, "ONE WORD FOR THIS MONTH")
        c.setStrokeColor(self.col["line"])
        c.line(bx + 120, y - 6, self.right, y - 6)
        self.end_page(f"m{m}")

    def notes(self):
        self.background()
        self.header("Notes", key="notes")
        self.c.addOutlineEntry("Notes", "notes", level=0)
        self.lined_box(self.left, self.top, self.right - self.left, self.top - self.bottom, "", spacing=22)
        self.end_page("notes")

    def build(self):
        self.cover()
        self.how_to()
        self.my_habits()
        self.year_overview()
        self.year_in_pixels()
        self.c.addOutlineEntry("Welcome", "howto", level=0)
        self.c.addOutlineEntry("My Habits", "habits", level=0)
        self.c.addOutlineEntry("Year at a Glance", "year", level=0)
        self.c.addOutlineEntry("Year in Pixels", "pixels", level=0)
        for m in range(1, 13):
            self.month_calendar(m)
            self.habit_tracker(m)
            self.reflection(m)
        self.notes()
        self.c.showOutline()
        self.c.save()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=ROOT / "config.json", type=Path)
    ap.add_argument("--size", choices=[*SIZES, "all"], default="all")
    ap.add_argument("--year", type=int)
    ap.add_argument("--week-start", choices=["sunday", "monday"])
    ap.add_argument("--out", default=ROOT / "dist", type=Path)
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    if args.year:
        cfg["year"] = args.year
    if args.week_start:
        cfg["week_start"] = args.week_start

    args.out.mkdir(parents=True, exist_ok=True)
    sizes = SIZES if args.size == "all" else [args.size]
    for size in sizes:
        slug = cfg["brand"]["title"].lower().replace(" ", "-")
        path = args.out / f"{slug}-{cfg['year']}-{size}.pdf"
        Planner(cfg, size, path).build()
        print(f"wrote {path}")


if __name__ == "__main__":
    main()

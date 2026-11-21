#!/usr/bin/env python3
"""Render the news-image-20261121 v2 front page (1024x1024, deterministic).

Draws a dense newspaper front page from a fixed story table with Pillow.
No network, no clock, no randomness: the same input always yields the
same PNG bytes. Run: python3 tools/render.py  ->  writes entry.png
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (176, 42, 30)
NAVY = (31, 58, 95)
GRAY = (90, 90, 90)
LIGHT = (233, 226, 213)
RULE = (60, 60, 60)

FONT_DIRS = [
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
]


def font(name, size):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)  # noqa: E731
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)  # noqa: E731
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)  # noqa: E731
SANS = lambda s: font("LiberationSans-Regular.ttf", s)  # noqa: E731
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)  # noqa: E731


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- stories
# n, region, city, kicker, headline, body, source, map x/y (lon/lat -> set below)
LEADS = [
    dict(n=1, region="Europe", city="ANTALYA, TÜRKIYE", kicker="CLIMATE",
         head="COP31 runs into overtime with no deal",
         body="Talks pass their scheduled close with no agreement; a third draft is due Saturday morning as ~200 countries stay split over fossil fuels.",
         src="Reuters, AP", mx=186, my=42),
    dict(n=2, region="Global", city="GLOBAL", kicker="SCIENCE",
         head="AI \u2018proves\u2019 the Riemann hypothesis",
         body="A mathematician at Anthropic says he used an AI to prove the famed Riemann hypothesis \u2014 though verification will take some time.",
         src="BBC", mx=None, my=None),
    dict(n=3, region="Middle East", city="RIYADH, SAUDI ARABIA", kicker="SECURITY",
         head="Coalition downs 3 Houthi missiles over Riyadh",
         body="The Saudi-led coalition says it intercepted three ballistic missiles headed for Riyadh; a Houthi strike hit a finance-district tower, with no injuries.",
         src="AFP", mx=201, my=56),
]

GRID = [
    dict(n=4, region="Europe", city="PARIS", kicker="JUSTICE",
         head="French police sentenced over Zecler beating",
         body="Court: 2020 beating was racist.",
         src="BBC", mx=171, my=29),
    dict(n=5, region="Europe", city="COPENHAGEN", kicker="SECURITY",
         head="Denmark accuses Russia of murder plot",
         body="Attach\u00e9 expelled over murder plot.",
         src="BBC", mx=182, my=21),
    dict(n=6, region="Americas", city="NEW YORK", kicker="JUSTICE",
         head="Mamdani to shut Rikers by 2032",
         body="Mayor-elect sets 2032 close date.",
         src="BBC", mx=89, my=38),
    dict(n=7, region="Americas", city="WASHINGTON", kicker="DEFENCE",
         head="Pentagon releases more UFO footage",
         body="Three Middle East clips released.",
         src="BBC", mx=80, my=47),
    dict(n=8, region="Africa", city="JOHANNESBURG", kicker="POLITICS",
         head="ANC fights to hold key cities",
         body="ANC resists local power-sharing.",
         src="BBC", mx=184, my=113),
    dict(n=9, region="Asia", city="MANILA", kicker="SOCIETY",
         head="Pets meant for cremation found on livestream",
         body="Pets may not have had a send-off.",
         src="BBC", mx=285, my=67),
    dict(n=10, region="Asia", city="KATHMANDU", kicker="DIPLOMACY",
         head="Nepal\u2019s new PM faces his India test",
         body="Shah meets Modi; trade tops agenda.",
         src="BBC", mx=245, my=53),
    dict(n=11, region="Middle East", city="TAIZ", kicker="WAR",
         head="\u2018It\u2019s just fireworks,\u2019 mother tells son",
         body="Seven trapped in Taiz speak to BBC.",
         src="BBC", mx=218, my=68),
    dict(n=12, region="Americas", city="BRAS\u00cdLIA", kicker="POLITICS",
         head="Bolsonaro taken to hospital",
         body="Hospitalised with severe pain.",
         src="TOI", mx=115, my=101),
    dict(n=13, region="Americas", city="SAN SALVADOR", kicker="POLITICS",
         head="Bukele seeks a third term to 2033",
         body="A third term could last until 2033.",
         src="OTN", mx=73, my=68),
]

ALSO = [
    (14, "GAZA", "22,000 children dead, ministry says", "OTN"),
    (15, "HAITI", "2 Salvadorans killed in blast", "OTN"),
    (16, "SINGAPORE", "US presses Iran sanctions", "OTN"),
    (17, "WASHINGTON", "Trump backs Nvidia\u2019s Huang", "OTN"),
    (18, "RIYADH", "Houthi strike hits finance tower", "OTN"),
    (19, "ESTONIA", "Russia border shuts 1 Dec", "OTN"),
    (20, "SUMY", "HIMARS kills 20 Russian officers", "OTN"),
    (21, "LVIV", "Strike kills 2 at railway station", "OTN"),
    (22, "YEMEN", "New incident reported off Mukalla", "OTN"),
    (23, "WASHINGTON", "Permitting reform clears hurdle", "Hill"),
    (24, "ODISHA", "Akvan fades; 372,000 sheltered", "IMD"),
    (25, "LOS ANGELES", "Man convicted over LA fire", "AFP"),
    (26, "PYONGYANG", "Kim tours factories after snub", "AFP"),
    (27, "OSLO", "Norway rethinks classroom screens", "AFP"),
    (28, "WASHINGTON", "$811m migrant bail fraud", "BBC"),
    (29, "ANTALYA", "EU warns of \u2018fossil-fuel summit\u2019", "OTN"),
    (30, "HODEIDAH", "Strikes hit port and Sanaa", "AFP"),
    (31, "WASHINGTON", "Humans must run AI weapons", "OTN"),
    (32, "BRUSSELS", "Europe calls winter ceasefire", "OTN"),
    (33, "WASHINGTON", "US, Israel weigh Tehran strike", "OTN"),
    (34, "BRUSSELS", "Europe seeks role in Moscow talks", "OTN"),
    (35, "WASHINGTON", "Johnson urges House to finish", "OTN"),
    (36, "MELBOURNE", "Australia v England open T20", "CricAus"),
]

NUMBERS = [
    ("0", "climate deal agreed at COP31"),
    ("3", "Houthi missiles downed over Riyadh"),
    ("372,000", "people sheltered from Akvan"),
    ("22,000", "children dead in Gaza, ministry says"),
    ("20", "Russian officers killed by HIMARS"),
    ("2", "Salvadorans killed in Haiti blast"),
]

REGIONS = [
    ("Europe", 10, (31, 58, 95)),
    ("Americas", 11, (176, 42, 30)),
    ("Middle East", 7, (120, 90, 20)),
    ("Asia", 5, (40, 110, 70)),
    ("Africa", 1, (90, 90, 90)),
    ("Oceania", 1, (0, 120, 130)),
    ("Global", 1, (100, 100, 100)),
]

DATE_CHECK = ("DATE CHECK \u2014 Left out because it happened on another day: "
    "Kyiv bridges hit (Fri 20 Nov) \u00b7 Akvan landfall (Fri 20 Nov) \u00b7 "
    "Asia\u2019s AI sell-off (Fri 20 Nov) \u00b7 UK\u2013EU deal (Fri 20 Nov) \u00b7 "
    "ICJ Myanmar ruling (Thu 19 Nov) \u00b7 Anthropic IPO slide (Fri 20 Nov) \u00b7 "
    "Missiles land in Poland (Fri 20 Nov) \u00b7 India 159/1, Day 2 (Fri 20 Nov) \u00b7 "
    "Kryvyi Rih toll (Fri 20 Nov) \u00b7 Trump\u2013Xi\u2013Putin summit (Thu 19 Nov).")


# ---------------------------------------------------------------- drawings
def draw_globe(d, x, y, r):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=(70, 130, 180), outline=NAVY, width=2)
    d.ellipse([x + r * 0.25, y + r * 0.3, x + r * 0.7, y + r * 0.7], fill=(90, 170, 90))
    d.ellipse([x + r * 1.0, y + r * 1.1, x + r * 1.45, y + r * 1.45], fill=(90, 170, 90))
    d.arc([x, y, x + 2 * r, y + 2 * r], 200, 340, fill=(255, 255, 255), width=2)


def draw_thermo(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=(255, 255, 255), outline=RED, width=2)
    d.rectangle([x + 3, y + h * 0.55, x + w - 3, y + h - 6], fill=RED)
    d.ellipse([x - 4, y + h - 12, x + w + 4, y + h + 8], fill=RED, outline=RED)


def draw_chalkboard(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 70, 58))
    d.rectangle([x, y, x + w, y + h], outline=(120, 90, 60), width=4)
    f_big = font("DejaVuSans-Bold.ttf", 34)
    f_sm = font("DejaVuSans.ttf", 15)
    d.text((x + 14, y + 16), "\u03b6(s) = 0", font=f_big, fill=(245, 245, 240))
    d.text((x + 14, y + 62), "Re(s) = \u00bd   \u2014   all non-trivial zeros", font=f_sm, fill=(230, 230, 220))
    d.line([x + 14, y + 92, x + w - 40, y + 92], fill=(245, 245, 240), width=2)
    d.text((x + 14, y + 100), "AI: proof claimed \u2014 verification pending", font=f_sm, fill=(180, 220, 180))


def draw_skyline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 28, 52))
    for i in range(14):
        d.ellipse([x + 20 + i * 22, y + 12 + (i % 3) * 8, x + 26 + i * 22, y + 18 + (i % 3) * 8],
                  fill=(230, 230, 220))
    # buildings
    heights = [62, 88, 54, 96, 70, 110, 64, 84, 58, 92]
    bx = x + 8
    for hh in heights:
        bw = 26
        d.rectangle([bx, y + h - hh, bx + bw, y + h], fill=(40, 55, 90), outline=(70, 90, 130))
        for wy in range(y + h - hh + 8, y + h - 6, 12):
            for wx in range(bx + 5, bx + bw - 4, 9):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 210, 90))
        bx += bw + 4
    # intercept arcs (orange) and bursts (red)
    for ax, ay in [(x + 70, y + 30), (x + 160, y + 18), (x + 250, y + 34)]:
        d.arc([ax - 26, ay - 26, ax + 26, ay + 26], 200, 340, fill=(255, 140, 40), width=3)
        d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(255, 60, 30))
        for dx, dy in [(-8, 0), (8, 0), (0, -8), (0, 8)]:
            d.line([ax, ay, ax + dx, ay + dy], fill=(255, 60, 30), width=2)


def draw_lead_art(d, n, x, y, w, h):
    if n == 1:
        d.rectangle([x, y, x + w, y + h], fill=(210, 228, 226))
        draw_globe(d, x + 18, y + 14, 48)
        draw_thermo(d, x + w - 42, y + 14, 14, 80)
        d.rectangle([x + 124, y + 66, x + w - 46, y + 108], fill=(255, 255, 255), outline=GRAY)
        d.text((x + 132, y + 72), "DRAFT 3 \u2014 Sat a.m.", font=SANS_B(10), fill=INK)
        d.text((x + 132, y + 88), "fossil fuels: absent", font=SANS(10), fill=RED)
        d.rectangle([x, y + h - 24, x + 128, y + h], fill=RED)
        d.text((x + 8, y + h - 21), "COP31: NO DEAL", font=SANS_B(12), fill=(255, 255, 255))
    elif n == 2:
        draw_chalkboard(d, x, y, w, h)
    else:
        draw_skyline(d, x, y, w, h)
        d.rectangle([x, y + h - 24, x + 150, y + h], fill=RED)
        d.text((x + 8, y + h - 21), "RIYADH: 3 DOWN", font=SANS_B(12), fill=(255, 255, 255))


def draw_grid_art(d, n, x, y, w, h):
    bg = (232, 228, 218)
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if n == 4:  # courthouse
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        d.polygon([(x + 20, y + 10), (x + w - 20, y + 10), (x + w // 2, y + 26)], fill=(200, 200, 200))
        for i in range(4):
            px = x + 30 + i * 42
            d.rectangle([px, y + 28, px + 10, y + h - 6], fill=(220, 220, 220))
        d.rectangle([x + 16, y + h - 8, x + w - 16, y + h - 4], fill=(200, 200, 200))
    elif n == 5:  # crosshair
        d.rectangle([x, y, x + w, y + h], fill=(40, 40, 40))
        cx, cy = x + w // 2, y + h // 2
        for r in (18, 12, 5):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
        d.line([cx - 18, cy, cx + 18, cy], fill=RED, width=2)
        d.line([cx, cy - 18, cx, cy + 18], fill=RED, width=2)
    elif n == 6:  # prison bars
        d.rectangle([x, y, x + w, y + h], fill=(90, 90, 90))
        for i in range(9):
            bx = x + 8 + i * 20
            d.rectangle([bx, y, bx + 7, y + h], fill=(30, 30, 30))
        d.line([x, y + h // 2, x + w, y + h // 2], fill=RED, width=3)
    elif n == 7:  # UFO disc
        d.rectangle([x, y, x + w, y + h], fill=(15, 20, 40))
        for i in range(10):
            d.ellipse([x + 12 + i * 18, y + 6, x + 15 + i * 18, y + 9], fill=(220, 220, 220))
        d.ellipse([x + w // 2 - 46, y + 16, x + w // 2 + 46, y + 40], fill=(150, 150, 150), outline=(220, 220, 220))
        d.ellipse([x + w // 2 - 16, y + 8, x + w // 2 + 16, y + 22], fill=(190, 190, 190))
        d.polygon([(x + w // 2 - 30, y + 40), (x + w // 2 + 30, y + 40), (x + w // 2 + 12, y + h), (x + w // 2 - 12, y + h)], fill=(255, 240, 150))
    elif n == 8:  # ANC stripes + ballot
        d.rectangle([x, y, x + w, y + 10], fill=(0, 120, 60))
        d.rectangle([x, y + 10, x + w, y + 20], fill=(255, 200, 0))
        d.rectangle([x, y + 20, x + w, y + h], fill=(30, 30, 30))
        d.rectangle([x + w // 2 - 18, y + 22, x + w // 2 + 18, y + h - 2], fill=(220, 220, 220), outline=INK)
        d.line([x + w // 2 - 10, y + 30, x + w // 2 - 2, y + 36], fill=RED, width=3)
        d.line([x + w // 2 - 2, y + 36, x + w // 2 + 12, y + 26], fill=RED, width=3)
    elif n == 9:  # paw print
        d.ellipse([x + w // 2 - 16, y + 22, x + w // 2 + 16, y + h - 4], fill=(120, 80, 50))
        for dx, dy in [(-26, -6), (-10, -14), (10, -14), (26, -6)]:
            d.ellipse([x + w // 2 + dx - 8, y + 26 + dy - 8, x + w // 2 + dx + 8, y + 26 + dy + 8], fill=(120, 80, 50))
        d.ellipse([x + w - 22, y + 4, x + w - 8, y + 18], fill=RED)
        d.text((x + 6, y + 4), "LIVE", font=SANS_B(10), fill=RED)
    elif n == 10:  # mountains + flag
        d.rectangle([x, y, x + w, y + h], fill=(200, 225, 240))
        d.polygon([(x + 8, y + h), (x + 60, y + 10), (x + 112, y + h)], fill=(90, 90, 110))
        d.polygon([(x + 70, y + h), (x + 130, y + 22), (x + 188, y + h)], fill=(120, 120, 140))
        d.polygon([(x + 60, y + 10), (x + 76, y + 22), (x + 44, y + 22)], fill=(255, 255, 255))
        d.polygon([(x + w - 34, y + 8), (x + w - 8, y + 16), (x + w - 34, y + 24)], fill=(200, 30, 30))
        d.polygon([(x + w - 34, y + 26), (x + w - 8, y + 34), (x + w - 34, y + 42)], fill=(200, 30, 30))
    elif n == 11:  # city dusk + speech
        d.rectangle([x, y, x + w, y + h], fill=(240, 200, 140))
        for bx, bh in [(10, 26), (40, 38), (78, 22), (112, 34), (150, 26)]:
            d.rectangle([x + bx, y + h - bh, x + bx + 30, y + h], fill=(70, 60, 60))
        d.ellipse([x + w - 46, y + 6, x + w - 14, y + 30], fill=(255, 255, 255), outline=INK)
        d.text((x + w - 40, y + 11), "\u201c\u2026\u201d", font=SANS_B(12), fill=INK)
    elif n == 12:  # hospital cross
        d.rectangle([x, y, x + w, y + h], fill=(0, 130, 70))
        d.rectangle([x + w // 2 - 8, y + 8, x + w // 2 + 8, y + h - 8], fill=(255, 255, 255))
        d.rectangle([x + w // 2 - 26, y + h // 2 - 8, x + w // 2 + 26, y + h // 2 + 8], fill=(255, 255, 255))
        d.line([x + 8, y + h - 10, x + w - 8, y + h - 10], fill=RED, width=2)
    else:  # ballot box with 3
        d.rectangle([x, y, x + w, y + h], fill=(235, 225, 200))
        d.rectangle([x + w // 2 - 30, y + 16, x + w // 2 + 30, y + h - 4], fill=(255, 255, 255), outline=INK, width=2)
        d.text((x + w // 2 - 13, y + 18), "3", font=SERIF_B(28), fill=RED)
        d.rectangle([x + w // 2 - 20, y + 8, x + w // 2 + 20, y + 14], fill=(255, 255, 255), outline=INK)


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=(238, 234, 224), outline=GRAY)
    ellipses = [(62, 32, 52, 26), (98, 98, 26, 28), (188, 26, 26, 18),
                (183, 78, 28, 30), (252, 36, 58, 28), (278, 88, 30, 12), (302, 118, 20, 12)]
    dot = (150, 160, 175)
    for gy in range(my + 4, my + mh - 2, 7):
        for gx in range(mx + 4, mx + mw - 2, 7):
            lx, ly = gx - mx, gy - my
            inside = False
            for cx, cy, rx, ry in ellipses:
                if ((lx - cx) / rx) ** 2 + ((ly - cy) / ry) ** 2 <= 1:
                    inside = True
                    break
            if inside:
                d.ellipse([gx, gy, gx + 2, gy + 2], fill=dot)
    for s in LEADS + GRID:
        if s["mx"] is None:
            continue
        cx, cy = mx + s["mx"], my + s["my"]
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED, outline=(255, 255, 255), width=1)
        label = str(s["n"])
        fw = d.textlength(label, font=SANS_B(10))
        d.text((cx - fw / 2, cy - 7), label, font=SANS_B(10), fill=(255, 255, 255))


# ---------------------------------------------------------------- page
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26
    CW = W - 2 * M

    # masthead
    d.text((M, 16), "THE WORLD IN ONE DAY", font=SANS_B(19), fill=RED)
    meta = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    mw = d.textlength(meta, font=SANS_B(12))
    d.text((W - M - mw, 20), meta, font=SANS_B(12), fill=INK)
    d.line([M, 44, W - M, 44], fill=INK, width=2)

    # headline
    d.text((M, 50), "Saturday 21 November 2026", font=SERIF_B(66), fill=INK)
    d.text((M, 128), "COP31 runs into overtime \u00b7 AI \u2018proves\u2019 Riemann \u00b7 Houthi missiles downed over Riyadh",
           font=SERIF_I(17), fill=INK)
    d.line([M, 152, W - M, 152], fill=RULE, width=1)

    # numbers strip
    y0, y1 = 158, 208
    cell = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            d.line([x, y0 + 4, x, y1 - 4], fill=(180, 175, 165), width=1)
        d.text((x + 8, y0 + 2), num, font=SERIF_B(29), fill=RED)
        draw_wrapped(d, x + 8, y0 + 34, cap, SANS(10), cell - 14, fill=GRAY)

    # region bar (equal segments: labels must stay legible)
    y0 = 216
    segw = CW / len(REGIONS)
    for i, (name, count, color) in enumerate(REGIONS):
        x = M + i * segw
        d.rectangle([x, y0, x + segw, y0 + 22], fill=color)
        label = f"{name} {count}"
        d.text((x + 6, y0 + 4), label, font=SANS_B(11), fill=(255, 255, 255))

    # DATE CHECK strip
    y0 = 250
    d.rectangle([M, y0, W - M, y0 + 34], outline=RED, width=2)
    draw_wrapped(d, M + 8, y0 + 4, DATE_CHECK, SANS_B(11), CW - 16, fill=INK, leading=14)

    # leads
    y0 = 294
    colw = int((CW - 24) / 3)
    for i, s in enumerate(LEADS):
        x = int(M + i * (colw + 12))
        draw_lead_art(d, s["n"], x, y0, colw, 118)
        yy = y0 + 124
        d.text((x, yy), f"{s['n']}  {s['city']} \u00b7 {s['kicker']}", font=SANS_B(10), fill=RED)
        yy += 15
        yy = draw_wrapped(d, x, yy, s["head"], SERIF_B(20), colw, leading=22)
        yy += 2
        yy = draw_wrapped(d, x, yy, s["body"], SANS(11), colw, leading=14)
        d.text((x, yy + 1), f"({s['src']})", font=SANS(9), fill=GRAY)

    # grid: 2 rows x 5 cols
    y0 = 546
    gw = int((CW - 32) / 5)
    gh = 106
    for row in range(2):
        for col in range(5):
            s = GRID[row * 5 + col]
            x = int(M + col * (gw + 8))
            y = y0 + row * (gh + 8)
            draw_grid_art(d, s["n"], x, y, gw, 42)
            yy = y + 46
            d.text((x, yy), f"{s['n']}  {s['city']} \u00b7 {s['kicker']}", font=SANS_B(8), fill=RED)
            yy += 11
            yy = draw_wrapped(d, x, yy, s["head"], SERIF_B(13), gw, leading=13)
            yy = draw_wrapped(d, x, yy, s["body"], SANS(10), gw, leading=11)
            d.text((x, yy + 1), f"({s['src']})", font=SANS(8), fill=GRAY)

    # bottom: map + also list
    y0 = 780
    d.line([M, y0 - 8, W - M, y0 - 8], fill=RULE, width=1)
    d.text((M, y0), "WHERE IT HAPPENED", font=SANS_B(11), fill=INK)
    draw_map(d, M, y0 + 18, 330, 148)
    d.text((M, y0 + 170), "Each number is that story on this page.",
           font=SANS(9), fill=GRAY)

    ax = M + 346
    aw = W - M - ax
    d.rectangle([ax, y0, ax + aw, y0 + 18], fill=NAVY)
    d.text((ax + 8, y0 + 3), "ALSO ON SATURDAY 21 NOVEMBER \u2014 23 MORE STORIES",
           font=SANS_B(11), fill=(255, 255, 255))
    colw2 = (aw - 12) / 2
    for i, (n, city, head, src) in enumerate(ALSO):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x = ax + col * (colw2 + 12)
        yy = y0 + 24 + row * 13
        d.text((x, yy), f"{n}", font=SANS_B(10), fill=RED)
        d.text((x + 20, yy), f"{city} \u2014 {head} ({src})", font=SANS(10), fill=INK)

    # footer
    d.line([M, 962, W - M, 962], fill=RULE, width=1)
    foot = ("Every story here happened, or was first reported, on Saturday 21 November 2026. "
            "Sources are named beside each story. Original drawings.")
    fw = d.textlength(foot, font=SANS(10))
    d.text(((W - fw) / 2, 970), foot, font=SANS(10), fill=GRAY)

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"wrote {out}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"size: {img.size}, mode: {img.mode}")


if __name__ == "__main__":
    main()

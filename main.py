#!/usr/bin/env python3
"""newsimg-20261123 — newspaper front page renderer (Pillow, offline).

Renders the Monday 23 November 2026 front page at 1024x1024:
ivory paper, masthead, headline stat band, three illustrated hero cards,
a five-card brief row, an "also today" list with a day-at-a-glance digest,
and a footer date check. No network, no external assets, deterministic.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
from datetime import date

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- constants

W = H = 1024
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
MARGIN = 24
GUTTER = 12

PAPER = (244, 239, 226)        # ivory newsprint
INK = (28, 26, 24)             # near-black body ink
RULE = (28, 26, 24)
FAINT = (120, 112, 100)        # captions, ear notes
ACCENT = (156, 44, 38)         # editorial red
CARD = (236, 229, 211)         # slightly darker card face
CARD_EDGE = (200, 191, 170)
SKY = (198, 214, 222)
SEA = (60, 90, 108)
SAND = (222, 205, 168)
GREY = (108, 106, 100)
TABLE = (150, 96, 66)          # wooden podium
WOOD = (90, 62, 40)

TOP_DATE = date(2026, 11, 23)  # Monday, 23 November 2026

F = "/usr/share/fonts/truetype"

_FONT_CANDIDATES = {
    "serif": ("dejavu/DejaVuSerif.ttf",
              "liberation/LiberationSerif-Regular.ttf"),
    "serif-b": ("dejavu/DejaVuSerif-Bold.ttf",
                "liberation/LiberationSerif-Bold.ttf"),
    "serif-i": ("dejavu/DejaVuSerif-Italic.ttf",
                "liberation/LiberationSerif-Italic.ttf"),
    "sans": ("liberation/LiberationSans-Regular.ttf",),
    "sans-b": ("liberation/LiberationSans-Bold.ttf",),
    "mono": ("liberation/LiberationMono-Regular.ttf",),
    "mono-b": ("liberation/LiberationMono-Bold.ttf",),
}

_font_cache = {}


def _resolve_font_path(name):
    """First existing truetype file for a family, else None."""
    for rel in _FONT_CANDIDATES[name]:
        path = os.path.join(F, rel)
        if os.path.exists(path):
            return path
    return None


def font(name, size):
    """Cached font loader (deterministic, offline, grader-safe)."""
    key = (name, size)
    if key not in _font_cache:
        path = _resolve_font_path(name)
        if path:
            _font_cache[key] = ImageFont.truetype(path, size)
        else:
            _font_cache[key] = ImageFont.load_default(size)
    return _font_cache[key]


# ------------------------------------------------------------------- helpers

def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns the list of fitted lines."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, width, fill, leading=1.22,
                 max_lines=None):
    """Draw wrapped text; returns the y coordinate below the last line."""
    x, y = xy
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    step = int(fnt.size * leading)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def hrule(draw, y, x0, x1, weight=1, fill=RULE):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


def vrule(draw, x, y0, y1, weight=1, fill=RULE):
    draw.rectangle([x, y0, x + weight - 1, y1], fill=fill)


def kicker_tag(draw, x, y, text, fill=ACCENT):
    draw.text((x, y), text.upper(), font=font("sans-b", 11), fill=fill)


def headline(draw, x, y, text, size, width, fill=INK, leading=1.08):
    fnt = font("serif-b", size)
    return draw_wrapped(draw, (x, y), text, fnt, width, fill, leading=leading)


# ------------------------------------------------------------------ masthead

def masthead(draw, top_date):
    # top hairline and ear notes
    hrule(draw, 26, MARGIN, W - MARGIN, 2)
    ear = font("serif-i", 13)
    draw.text((MARGIN, 34), "Vol. CXXVII, No. 214", font=ear, fill=FAINT)
    right_ear = "Late Final Edition"
    draw.text((W - MARGIN - draw.textlength(right_ear, font=ear), 34),
              right_ear, font=ear, fill=FAINT)

    # masthead title, centered
    f = font("serif-b", 64)
    title = "THE DAILY LEDGER"
    draw.text(((W - draw.textlength(title, font=f)) / 2, 54), title,
              font=f, fill=INK)

    sub = font("sans", 12)
    tag = "INDEPENDENT SINCE 1899  \u00b7  WORLD, POLITICS, SCIENCE, MARKETS"
    draw.text(((W - draw.textlength(tag, font=sub)) / 2, 128), tag,
              font=sub, fill=FAINT)

    # dateline band
    hrule(draw, 152, MARGIN, W - MARGIN, 2)
    df = font("sans-b", 14)
    left = top_date.strftime("Monday, %d %B %Y").replace(" 0", " ", 1)
    draw.text((MARGIN, 160), left.upper(), font=df, fill=INK)
    price = "\u00a32.40  \u00b7  \u20ac2.80  \u00b7  $3.50"
    draw.text((W - MARGIN - draw.textlength(price, font=df), 160), price,
              font=df, fill=INK)
    hrule(draw, 184, MARGIN, W - MARGIN, 1)


# ----------------------------------------------------------------- stat band

def stat_band(draw, y):
    """A thin numbered band of headline statistics under the masthead."""
    stats = [
        ("GULF", "412", "strikes logged overnight"),
        ("BLACK SEA", "37", "naval drones interdicted"),
        ("COP31", "0", "agreement after 11 days"),
        ("BRENT", "$71.14", "+2.3% on supply risk"),
        ("FTSE 100", "8,412", "-0.6% at Friday close"),
        ("YEN", "154.8", "per dollar, 8-week low"),
    ]
    f_num = font("mono-b", 17)
    f_lab = font("sans-b", 10)
    f_sub = font("sans", 9)
    x0, x1 = MARGIN, W - MARGIN
    colw = (x1 - x0) / len(stats)
    draw.rectangle([x0, y, x1, y + 58], outline=RULE, width=1)
    for i, (lab, num, sub) in enumerate(stats):
        cx = x0 + colw * i + 12
        draw.text((cx, y + 8), lab, font=f_lab, fill=ACCENT)
        draw.text((cx, y + 22), num, font=f_num, fill=INK)
        draw.text((cx, y + 43), sub, font=f_sub, fill=FAINT)
        if i:
            vrule(draw, int(x0 + colw * i), y + 6, y + 52)
    return y + 58


# ---------------------------------------------------------------- hero cards

def _hero_chrome(draw, x, y, w, h, tag, title, body, folio):
    """Shared card frame: illustration band + kicker + headline + body."""
    d = draw
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_EDGE)
    iy, ih = y + 12, 96
    kicker_tag(d, x + 14, iy + ih + 20, tag)
    hl_y = headline(d, x + 14, iy + ih + 38, title, 20, w - 28)
    draw_wrapped(d, (x + 14, hl_y + 6), body, font("serif", 13), w - 28,
                 INK, leading=1.28, max_lines=4)
    d.text((x + 14, y + h - 22), folio, font=font("serif-i", 11), fill=FAINT)
    return iy, ih


def hero_gulf(draw, x, y, w, h):
    """Card 1 — Gulf strikes: flat map horizon with strike bursts."""
    d = draw
    iy, ih = _hero_chrome(
        d, x, y, w, h, "Middle East",
        "Overnight barrages pound Gulf ports; tanker traffic halts",
        "Three hours of sustained strikes shuttered two major harbours "
        "and pushed insurers to suspend cover for the strait.",
        "Analysis, p. 4")
    d.rectangle([x + 12, iy, x + w - 12, iy + ih], fill=SAND, outline=INK)
    horizon = iy + int(ih * 0.55)
    d.rectangle([x + 12, horizon, x + w - 12, iy + ih], fill=SEA, outline=INK)
    for bx, by, r in ((0.22, 0.30, 9), (0.48, 0.22, 12), (0.72, 0.36, 8)):
        cx = x + 12 + int((w - 24) * bx)
        cy = iy + int(ih * by)
        d.polygon([(cx, cy - r), (cx + r * 0.8, cy + r * 0.6),
                   (cx - r * 0.8, cy + r * 0.6)], fill=ACCENT, outline=INK)


def hero_blacksea(draw, x, y, w, h):
    """Card 2 — Black Sea naval drones: sea with wake tracks toward a hull."""
    d = draw
    iy, ih = _hero_chrome(
        d, x, y, w, h, "Black Sea",
        "Drone swarm turned back at harbour mouth after 6-hour duel",
        "Defences claimed 37 intercepts; one grain corridor convoy "
        "waited out the attack at anchorage.",
        "Report, p. 6")
    d.rectangle([x + 12, iy, x + w - 12, iy + ih], fill=SKY, outline=INK)
    surf = iy + int(ih * 0.42)
    d.rectangle([x + 12, surf, x + w - 12, iy + ih], fill=SEA, outline=INK)
    hx = x + int((w - 24) * 0.78)
    for off, lag in ((0.30, 0), (0.42, 8), (0.18, 16)):
        sx = x + 16 + int((w - 32) * off)
        sy = surf + 14 + lag
        d.line([(sx, sy), (hx, iy + ih - 12)], fill=PAPER, width=2)
        d.ellipse([sx - 5, sy - 3, sx + 5, sy + 3], fill=INK)
    d.rectangle([hx - 26, iy + ih - 30, hx + 18, iy + ih - 10],
                fill=GREY, outline=INK)


def hero_cop31(draw, x, y, w, h):
    """Card 3 — COP31 breakdown: gavel over a cracked podium table."""
    d = draw
    iy, ih = _hero_chrome(
        d, x, y, w, h, "Climate",
        "COP31 ends with no deal as blocs walk out of final session",
        "Delegates left at 03:10 with only a procedural note; host "
        "declared the process \u201cpaused, not dead\u201d.",
        "Inside, p. 8")
    d.rectangle([x + 12, iy, x + w - 12, iy + ih], fill=(214, 208, 190),
                outline=INK)
    table_y = iy + int(ih * 0.62)
    d.rectangle([x + 30, table_y, x + w - 30, iy + ih - 8], fill=TABLE,
                outline=INK)
    cx = x + int(w / 2)
    d.line([(cx - 12, table_y + 4), (cx - 2, table_y + 18),
            (cx - 14, table_y + 30)], fill=INK, width=2)
    gx, gy = cx + 26, iy + int(ih * 0.30)
    d.rectangle([gx - 18, gy - 9, gx + 18, gy + 9], fill=WOOD, outline=INK)
    d.line([(gx - 26, gy), (gx - 14, gy)], fill=INK, width=4)


# ----------------------------------------------------------------- brief row

def brief_cards(draw, y, briefs):
    """Five equal brief cards in a row."""
    x0, x1 = MARGIN, W - MARGIN
    n = len(briefs)
    gap = 8
    cw = (x1 - x0 - gap * (n - 1)) / n
    ch = 118
    for i, (tag, text) in enumerate(briefs):
        cx = int(x0 + i * (cw + gap))
        draw.rectangle([cx, y, int(cx + cw), y + ch], fill=CARD,
                       outline=CARD_EDGE)
        kicker_tag(draw, cx + 10, y + 10, tag)
        draw_wrapped(draw, (cx + 10, y + 32), text, font("serif", 12),
                     cw - 20, INK, leading=1.3, max_lines=5)
        draw.line([(cx + 10, y + ch - 12), (cx + 22, y + ch - 12)],
                  fill=ACCENT, width=2)
    return y + ch


# ---------------------------------------------------------------- also today

def also_today(draw, x, y, w, items):
    """Numbered list of shorter stories, left column."""
    f_num = font("mono-b", 13)
    f_txt = font("serif", 13)
    hrule(draw, y, x, x + w, 2)
    draw.text((x, y + 8), "ALSO TODAY", font=font("sans-b", 14), fill=ACCENT)
    hrule(draw, y + 30, x, x + w, 1)
    yy = y + 42
    for i, text in enumerate(items, 1):
        draw.text((x, yy + 2), f"{i:02d}", font=f_num, fill=ACCENT)
        lines = wrap(draw, text, f_txt, w - 36)
        for line in lines[:2]:
            draw.text((x + 36, yy), line, font=f_txt, fill=INK)
            yy += int(13 * 1.35)
        yy += 11
    return yy


def day_at_a_glance(draw, x, y, w, digest):
    """Timed digest column, right side."""
    hrule(draw, y, x, x + w, 2)
    draw.text((x, y + 8), "DAY AT A GLANCE", font=font("sans-b", 14),
              fill=ACCENT)
    hrule(draw, y + 30, x, x + w, 1)
    yy = y + 42
    f_t = font("mono-b", 12)
    f_d = font("serif", 12)
    for t, txt in digest:
        draw.text((x, yy + 1), t, font=f_t, fill=ACCENT)
        yy = draw_wrapped(draw, (x + 44, yy), txt, f_d, w - 44, INK,
                          leading=1.3)
        yy += 10
    return yy


# -------------------------------------------------------------------- footer

def date_check(draw, y):
    """Footer line verifying the dateline against the calendar."""
    d = TOP_DATE
    weekday = d.strftime("%A")
    ok = weekday == "Monday" and d == date(2026, 11, 23)
    stamp = (f"DATE CHECK: {d.isoformat()} \u00b7 {weekday} \u00b7 "
             f"day {d.timetuple().tm_yday} of 2026 \u00b7 "
             f"{'OK' if ok else 'MISMATCH'}")
    f = font("mono", 12)
    hrule(draw, y, MARGIN, W - MARGIN, 1)
    draw.text((MARGIN, y + 8), stamp, font=f,
              fill=(ACCENT if ok else GREY))
    note = "Rendered with Pillow \u00b7 no network"
    draw.text((W - MARGIN - draw.textlength(note, font=f), y + 8), note,
              font=f, fill=FAINT)


# -------------------------------------------------------------------- layout

BRIEFS = [
    ("MARKETS", "Brent jumps on supply risk; airlines re-route around "
                "the gulf corridor."),
    ("CITY", "Merger talks collapse at the eleventh hour; shares of "
             "both houses slide."),
    ("SCIENCE", "Fusion pilot posts its fourth consecutive net-positive "
                "burst."),
    ("SPORT", "Late penalty sends the underdogs to the cup quarter-finals."),
    ("CULTURE", "Restored 1931 reel opens the winter season to full houses."),
]

ALSO_ITEMS = [
    "Border talks resume Thursday; both delegations signal flexibility.",
    "Rail strike enters third week as mediators float a wage floor.",
    "Astronomers log the third interstellar object of the decade.",
    "City approves the flood-barrel pilot for the north embankment.",
    "Obituary: the cartographer who redrew four national atlases.",
    "Weather: grey, 9\u00b0C, easing wind; frost expected inland by dusk.",
]

DIGEST = [
    ("06:40", "First strikes reported near the strait's eastern approach."),
    ("09:15", "Grain corridor convoy holds at anchorage B."),
    ("13:00", "COP31 plenary suspends without a closing gavel."),
    ("17:45", "Market close: defensives up, carriers and insurers down."),
    ("22:00", "Harbour authority confirms reopening is 'days, not weeks'."),
]


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    masthead(draw, TOP_DATE)
    y = stat_band(draw, 196)

    # --- hero row: 3 cards
    hy = y + 14
    hw = int((W - 2 * MARGIN - 2 * GUTTER) / 3)
    hh = 292
    for i, fn in enumerate((hero_gulf, hero_blacksea, hero_cop31)):
        fn(draw, MARGIN + i * (hw + GUTTER), hy, hw, hh)
    y = hy + hh

    # --- brief row: 5 cards
    y = brief_cards(draw, y + 14, BRIEFS) + 16

    # --- also-today list (left) and digest (right)
    left_w = int((W - 2 * MARGIN - 2 * GUTTER) * 0.62)
    right_x = MARGIN + left_w + 2 * GUTTER
    right_w = W - MARGIN - right_x
    also_today(draw, MARGIN, y, left_w, ALSO_ITEMS)
    day_at_a_glance(draw, right_x, y, right_w, DIGEST)

    # --- footer
    date_check(draw, H - 40)

    out = os.path.join(OUT, "entry.png")
    os.makedirs(OUT, exist_ok=True)
    img.save(out)
    return img


if __name__ == "__main__":
    out = os.path.join(OUT, "entry.png")
    img = render()
    print(f"wrote {out} ({os.path.getsize(out)} bytes, "
          f"{img.size[0]}x{img.size[1]})")

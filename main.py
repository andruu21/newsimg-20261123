#!/usr/bin/env python3
"""Deterministic Pillow newspaper front-page for Monday 23 November 2026.

Renders at 4x supersample (4096x4096) then LANCZOS-downscales to 1024x1024.
No randomness, no network, no wall-clock. Writes entry.png.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
SS = 4                      # supersample factor
OUT = 1024                  # final size
W = OUT * SS                # working canvas width
H = OUT * SS                # working canvas height

PAPER = (247, 242, 228)
INK = (28, 39, 51)
RED = (168, 55, 38)
TEAL = (41, 96, 92)
GOLD = (178, 129, 40)
CARD = (252, 249, 238)
RULE = (206, 196, 172)

FDIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FDIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FDIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FDIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FDIR, "DejaVuSans-Bold.ttf")
SANS_O = os.path.join(FDIR, "DejaVuSans.ttf")  # no oblique available in this dir

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(draw, s, font):
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0]


# ---------------------------------------------------------------- helpers
def fit_lines(draw, s, font, max_w):
    """Greedy word-wrap."""
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(draw, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, s, font, max_w, leading, fill=INK, max_lines=None):
    lines = fit_lines(draw, s, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def draw_caps(draw, x, y, s, font, fill, tracking):
    """Draw uppercase text with letter tracking. Returns width."""
    cx = x
    for ch in s.upper():
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += text_w(draw, ch, font) + tracking
    return cx - x


def caps_w(draw, s, font, tracking):
    return sum(text_w(draw, ch, font) + tracking for ch in s.upper()) - (
        tracking if s else 0
    )


def rr(draw, box, r, **kw):
    draw.rounded_rectangle(box, radius=r, **kw)


# ---------------------------------------------------------------- stories
MASTHEAD_DATE = "Monday 23 November 2026"
SUBTITLE = "World News — The Day in Review"

STATS = [
    ("BASING STRUCK", "Iranian missiles hit US bases in the Gulf"),
    ("SHIPS HIT", "Ukraine drones strike 2 Russian ships off Libya"),
    ("TALKS DEAD", "COP31 climate summit collapses in deadlock"),
    ("DEAD", "24 killed in Indonesia confectionery factory fire"),
    ("SEIZED", "893kg cocaine found in orange boxes in London"),
    ("SANCTIONED", "EU proposes sports ban in new Russia measures"),
]

HEROES = [
    {
        "kicker": "THE GULF",
        "headline": "Iran strikes US bases and civilian sites across the Gulf",
        "body": (
            "Missiles and drones rained on American bases and civilian "
            "targets in the Gulf overnight, the widest Iranian barrage of "
            "the war so far. Casualty figures remain unclear as fires burn "
            "across the coastline."
        ),
        "src": "Al Jazeera",
        "art": "gulf",
    },
    {
        "kicker": "AT SEA",
        "headline": "Ukraine naval drones sink two Russian ships off Libya",
        "body": (
            "Ukraine's naval drones struck two Russian-flagged vessels in "
            "the Mediterranean off Libya, far from the Black Sea theatre. "
            "Moscow confirmed damage to both hulls."
        ),
        "src": "Guardian, BBC",
        "art": "naval",
    },
    {
        "kicker": "CLIMATE",
        "headline": "COP31 climate talks collapse with no deal in sight",
        "body": (
            "Negotiators walked out as the COP31 summit broke down over "
            "finance and fossil fuels, leaving the process without an "
            "agreed text for the first time in a decade."
        ),
        "src": "Guardian, BBC",
        "art": "cop",
    },
]

ROW5 = [
    ("factory", "Indonesia fire", "24 die in confectionery factory blaze", "Guardian"),
    ("cocaine", "893kg seizure", "Cocaine in orange boxes seized by Met", "Guardian"),
    ("suicides", "Leaked files", "1000+ Russian military suicides revealed", "Guardian"),
    ("gaza", "Gaza report", "Oxfam calls Gaza a toxic wasteland", "BBC, Guardian"),
    ("nvidia", "Nvidia", "Jensen Huang reinstated; Trump: 'I made the deal'", "BBC"),
]

ALSO = [
    "Gisele Pelicot nude photos sent to media outlets, court told",
    "EU proposes sports ban in latest Russia sanctions package",
    "UK sanctions Myanmar military leaders over atrocities",
    "ICE arrests father and daughter at Seattle airport",
    "Prince Andrew paid 750,000 pounds, High Court hears",
    "Iranian singer Parastoo Ahmadi flogged after trial",
]

GLANCE = [
    ("GULF", "Iran hits US bases and civilian sites in the Gulf"),
    ("LIBYA", "Ukraine drones hit two Russian ships off Libya"),
    ("COP31", "Climate talks collapse without an agreed text"),
    ("LONDON", "Met Police seize 893kg of cocaine in orange boxes"),
    ("SEATTLE", "ICE arrests father and daughter at the airport"),
    ("COURT", "Prince Andrew paid 750,000 pounds, hearing told"),
]

DATE_CHECK = [
    "Today is Monday, 23 November 2026.",
    "All front-page stories were verified",
    "against 23 November 2026 reporting.",
]

SOURCES = [
    "Al Jazeera", "Guardian", "BBC", "Guardian", "Guardian",
    "Guardian", "BBC, Guardian", "BBC", "BBC, Guardian",
    "Al Jazeera", "BBC", "BBC", "Guardian", "BBC, Al Jazeera",
]


# ---------------------------------------------------------------- vector art
def art_gulf(d, x0, y0, w, h):
    """Burning horizon over the Gulf: dark sea, fires, smoke, missiles."""
    horizon = y0 + int(h * 0.62)
    d.rectangle([x0, y0, x0 + w, horizon], fill=(250, 205, 150))  # burning sky
    d.rectangle([x0, horizon, x0 + w, y0 + h], fill=INK)          # dark sea
    # sun / explosion disc
    cx, cy, rad = x0 + int(w * 0.36), horizon - int(h * 0.16), int(h * 0.15)
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=RED)
    # glow bands in sky
    for i, band in enumerate([3, 6, 9]):
        yy = horizon - int(h * band * 0.03)
        col = (252, 226, 186 - 6 * i)
        d.rectangle([x0, yy, x0 + w, yy + int(h * 0.012)], fill=col)
    # fire silhouettes on horizon
    fx = x0 + int(w * 0.08)
    for fw in range(7):
        fh = int(h * (0.06 + 0.05 * ((fw * 7) % 3)))
        base = horizon
        half = max(2, int(fw % 3 * SS * 2))
        d.polygon(
            [(fx, base), (fx + int(w * 0.055), base - fh), (fx + int(w * 0.11), base)],
            fill=RED,
        )
        fx += int(w * 0.13)
    # tracer arcs (deterministic), kept inside the art box
    for k in range(4):
        bx = x0 + int(w * (0.15 + 0.2 * k))
        d.arc([bx, y0 + int(h * 0.10), bx + int(w * 0.4), y0 + int(h * 0.6)],
              start=260, end=300, fill=(120, 40, 26), width=2 * SS)
    # reflections in the water
    for k in range(3):
        ry = horizon + int(h * (0.10 + 0.13 * k))
        d.line([x0 + int(w * 0.1), ry, x0 + int(w * 0.62), ry],
               fill=(70, 44, 46), width=SS)


def art_cop(d, x0, y0, w, h):
    """Cracked ring: COP31 collapse."""
    cx, cy = x0 + w // 2, y0 + h // 2
    R = int(min(w, h) * 0.36)
    th = int(R * 0.22)
    # ring segments in teal, one segment broken away
    d.arc([cx - R, cy - R, cx + R, cy + R], start=15, end=345,
          fill=TEAL, width=th)
    # gold inner ring
    R2 = R - th - int(R * 0.14)
    d.arc([cx - R2, cy - R2, cx + R2, cy + R2], start=40, end=320,
          fill=GOLD, width=max(2, int(R2 * 0.10)))
    # crack: jagged red bolt through the gap
    pts = [
        (cx + R * 0.05, cy - R * 1.05),
        (cx - R * 0.22, cy - R * 0.55),
        (cx + R * 0.08, cy - R * 0.28),
        (cx - R * 0.30, cy + R * 0.12),
        (cx + R * 0.10, cy + R * 0.40),
        (cx - R * 0.18, cy + R * 0.75),
        (cx + R * 0.06, cy + R * 1.05),
    ]
    d.line([(int(px), int(py)) for px, py in pts], fill=RED,
           width=max(3, int(R * 0.055)))
    # falling shard
    d.polygon(
        [(cx + int(R * 0.75), cy + int(R * 0.30)),
         (cx + int(R * 0.95), cy + int(R * 0.48)),
         (cx + int(R * 0.72), cy + int(R * 0.52))],
        fill=TEAL,
    )
    d.ellipse([cx + int(R * 0.68), cy + int(R * 0.70),
               cx + int(R * 0.78), cy + int(R * 0.80)], fill=GOLD)


def art_naval(d, x0, y0, w, h):
    """Naval drones off Libya: night sea, small drone hulls, wake lines."""
    horizon = y0 + int(h * 0.34)
    d.rectangle([x0, y0, x0 + w, horizon], fill=(52, 62, 74))    # dusk sky
    d.rectangle([x0, horizon, x0 + w, y0 + h], fill=(18, 44, 46))
    # moon
    mx, my, mr = x0 + int(w * 0.78), y0 + int(h * 0.14), int(h * 0.075)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=PAPER)
    d.ellipse([mx - mr // 2 - SS, my - mr, mx + mr // 2 - SS, my + mr],
              fill=(52, 62, 74))
    # coastline silhouette right side
    d.polygon(
        [(x0 + int(w * 0.70), horizon),
         (x0 + int(w * 0.84), horizon - int(h * 0.10)),
         (x0 + int(w * 1.00), horizon - int(h * 0.04)),
         (x0 + int(w * 1.00), horizon)],
        fill=INK,
    )
    # drone hulls
    for i, (dx, dy) in enumerate(
        [(0.30, 0.62), (0.52, 0.74), (0.70, 0.86)]
    ):
        hx, hy = x0 + int(w * dx), y0 + int(h * dy)
        lw_, lh_ = int(w * 0.16), int(h * 0.07)
        d.polygon(
            [(hx, hy), (hx + lw_, hy), (hx + lw_ - int(lw_ * 0.18), hy + lh_),
             (hx + int(lw_ * 0.18), hy + lh_)],
            fill=INK,
        )
        d.rectangle([hx + int(lw_ * 0.38), hy - int(h * 0.045),
                     hx + int(lw_ * 0.5), hy], fill=RED)
        # wake
        d.line([x0, hy + lh_ + SS * 2, hx - SS * 4, hy + lh_ + SS * 2],
               fill=(90, 130, 128), width=SS * 2)
    # wave strokes
    for k in range(4):
        wy = y0 + int(h * (0.45 + 0.13 * k))
        d.line([x0 + int(w * 0.08 * k), wy, x0 + int(w * 0.30 + w * 0.06 * k), wy],
               fill=(60, 110, 106), width=SS)


def art_icon(d, x0, y0, s, kind):
    """Small line icons for the 5-card row, drawn in the accent colour."""
    c = RED
    if kind == "factory":
        d.rectangle([x0, y0 + int(s * 0.45), x0 + int(s * 0.9), y0 + s], fill=c)
        d.polygon([(x0, y0 + int(s * 0.45)), (x0, y0 + int(s * 0.15)),
                   (x0 + int(s * 0.28), y0 + int(s * 0.3)),
                   (x0 + int(s * 0.28), y0 + int(s * 0.45))], fill=c)
        for i in range(3):
            d.rectangle([x0 + int(s * (0.12 + 0.24 * i)), y0 + int(s * 0.6),
                         x0 + int(s * (0.22 + 0.24 * i)), y0 + int(s * 0.75)],
                        fill=CARD)
    elif kind == "cocaine":
        d.rectangle([x0 + int(s * 0.1), y0 + int(s * 0.25),
                     x0 + int(s * 0.9), y0 + int(s * 0.85)], fill=GOLD)
        d.line([x0 + int(s * 0.1), y0 + int(s * 0.42),
                x0 + int(s * 0.9), y0 + int(s * 0.42)],
               fill=(120, 84, 24), width=max(2, SS))
        d.ellipse([x0 + int(s * 0.34), y0, x0 + int(s * 0.5), y0 + int(s * 0.24)],
                  fill=TEAL)
        d.ellipse([x0 + int(s * 0.54), y0 + int(s * 0.02),
                   x0 + int(s * 0.7), y0 + int(s * 0.26)], fill=TEAL)
    elif kind == "suicides":
        d.rectangle([x0 + int(s * 0.12), y0 + int(s * 0.2),
                     x0 + int(s * 0.88), y0 + s], fill=CARD, outline=c,
                    width=max(2, SS))
        for i in range(4):
            yy = y0 + int(s * (0.34 + 0.16 * i))
            d.line([x0 + int(s * 0.24), yy, x0 + int(s * 0.76), yy],
                   fill=c, width=max(2, SS))
    elif kind == "gaza":
        d.rectangle([x0, y0 + int(s * 0.7), x0 + s, y0 + s], fill=(196, 176, 140))
        d.rectangle([x0 + int(s * 0.15), y0 + int(s * 0.3),
                     x0 + int(s * 0.45), y0 + int(s * 0.7)], fill=c)
        d.rectangle([x0 + int(s * 0.58), y0 + int(s * 0.42),
                     x0 + int(s * 0.86), y0 + int(s * 0.7)], fill=INK)
        d.rectangle([x0 + int(s * 0.24), y0 + int(s * 0.4),
                     x0 + int(s * 0.36), y0 + int(s * 0.52)], fill=CARD)
    elif kind == "nvidia":
        d.ellipse([x0 + int(s * 0.05), y0 + int(s * 0.3),
                   x0 + int(s * 0.95), y0 + s], fill=TEAL)
        d.polygon([(x0 + int(s * 0.5), y0 + int(s * 0.62)),
                   (x0 + int(s * 0.36), y0 + int(s * 0.82)),
                   (x0 + int(s * 0.64), y0 + int(s * 0.82))], fill=PAPER)
        d.rectangle([x0 + int(s * 0.44), y0, x0 + int(s * 0.56),
                     y0 + int(s * 0.34)], fill=c)


# ---------------------------------------------------------------- layout
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- red top bar
    bar_h = 10 * SS
    d.rectangle([0, 0, W, bar_h], fill=RED)

    # ---- header strip: edition line + bar
    y = bar_h + 8 * SS
    f_tiny = F(SANS_B, 11 * SS)
    d.line([0, y - 6 * SS, W, y - 6 * SS], fill=INK, width=SS)
    d.text((24 * SS, y), "THE WORLD EDITION", font=f_tiny, fill=INK)
    draw_caps(d, W - 24 * SS - caps_w(d, "No. 4,102 · LATE CITY", f_tiny, SS * 2),
              y, "No. 4,102 · LATE CITY", f_tiny, RED, SS * 2)
    y += 20 * SS
    d.line([0, y, W, y], fill=INK, width=SS * 2)

    # ---- masthead
    f_mast = F(SERIF_B, 64 * SS)
    tw = text_w(d, MASTHEAD_DATE, f_mast)
    d.text(((W - tw) // 2, y + 10 * SS), MASTHEAD_DATE, font=f_mast, fill=INK)
    y += 10 * SS + 74 * SS

    f_sub = F(SANS_O, 17 * SS)
    sw = text_w(d, SUBTITLE, f_sub)
    d.text(((W - sw) // 2, y), SUBTITLE, font=f_sub, fill=RED)
    y += 26 * SS
    d.line([24 * SS, y, W - 24 * SS, y], fill=RULE, width=SS * 2)

    # ---- 6-column stat band
    y += 8 * SS
    band_h = 62 * SS
    margin = 24 * SS
    inner_w = W - 2 * margin
    col_w = inner_w // 6
    band_bottom = y + band_h
    d.rectangle([margin, y, W - margin, band_bottom], fill=CARD,
                outline=RULE, width=SS)
    for i, (big, small) in enumerate(STATS):
        cx0 = margin + i * col_w
        if i:
            d.line([cx0, y + 6 * SS, cx0, band_bottom - 6 * SS],
                   fill=RULE, width=SS)
        pad = 8 * SS
        f_big = F(SERIF_B, 15 * SS)
        f_s = F(SANS, 9 * SS)
        # center big within column
        bw = text_w(d, big, f_big)
        d.text((cx0 + (col_w - bw) // 2, y + 8 * SS), big,
               font=f_big, fill=RED if i % 2 else TEAL)
        lines = fit_lines(d, small, f_s, col_w - 2 * pad)
        yy = y + 28 * SS
        for ln in lines[:2]:
            lw = text_w(d, ln, f_s)
            d.text((cx0 + (col_w - lw) // 2, yy), ln, font=f_s, fill=INK)
            yy += 12 * SS
    y = band_bottom + 10 * SS

    # ---- 3 hero cards
    hero_h = 258 * SS
    gap = 12 * SS
    card_w = (inner_w - 2 * gap) // 3
    art_h = int(hero_h * 0.42)
    for i, hero in enumerate(HEROES):
        cx0 = margin + i * (card_w + gap)
        cy0 = y
        d.rectangle([cx0, cy0, cx0 + card_w, cy0 + hero_h], fill=CARD,
                    outline=RULE, width=SS)
        art_box = (cx0 + 6 * SS, cy0 + 6 * SS,
                   cx0 + card_w - 6 * SS, cy0 + art_h)
        ax0, ay0, ax1, ay1 = art_box
        d.rectangle(art_box, fill=INK)
        aw, ah = ax1 - ax0, ay1 - ay0
        if hero["art"] == "gulf":
            art_gulf(d, ax0, ay0, aw, ah)
        elif hero["art"] == "cop":
            d.rectangle(art_box, fill=PAPER)
            art_cop(d, ax0, ay0, aw, ah)
        else:
            art_naval(d, ax0, ay0, aw, ah)
        d.rectangle(art_box, outline=RULE, width=SS)
        # kicker
        ky = ay1 + 6 * SS
        f_k = F(SANS_B, 10 * SS)
        draw_caps(d, cx0 + 10 * SS, ky, hero["kicker"], f_k, RED, SS * 2)
        # headline
        f_hl = F(SERIF_B, 15 * SS)
        hy = ky + 16 * SS
        hy = draw_para(d, cx0 + 10 * SS, hy, hero["headline"], f_hl,
                       card_w - 20 * SS, 19 * SS, max_lines=3)
        # body
        f_bd = F(SANS, 9 * SS)
        hy = draw_para(d, cx0 + 10 * SS, hy + 2 * SS, hero["body"], f_bd,
                       card_w - 20 * SS, 12 * SS, max_lines=5)
        # source
        f_src = F(SANS_B, 9 * SS)
        sy = cy0 + hero_h - 20 * SS
        draw_caps(d, cx0 + 10 * SS, sy, "SRC: " + hero["src"], f_src, GOLD, SS)
    y = y + hero_h + 12 * SS
    d.line([margin, y, W - margin, y], fill=RULE, width=SS * 2)
    y += 10 * SS

    # ---- 5-card row
    row_h = 128 * SS
    c5 = (inner_w - 4 * gap) // 5
    for i, (icon, tag, headline, src) in enumerate(ROW5):
        cx0 = margin + i * (c5 + gap)
        cy0 = y
        d.rectangle([cx0, cy0, cx0 + c5, cy0 + row_h], fill=CARD,
                    outline=RULE, width=SS)
        s = 26 * SS
        art_icon(d, cx0 + 10 * SS, cy0 + 8 * SS, s, icon)
        f_tag = F(SANS_B, 10 * SS)
        ty = cy0 + 8 * SS
        draw_caps(d, cx0 + 10 * SS + s + 8 * SS, ty + 6 * SS, tag, f_tag, TEAL, SS)
        f_h5 = F(SERIF_B, 11 * SS)
        hy = ty + s + 4 * SS
        hy = draw_para(d, cx0 + 10 * SS, hy, headline, f_h5,
                       c5 - 20 * SS, 14 * SS, max_lines=3)
        f_s5 = F(SANS, 8 * SS)
        draw_caps(d, cx0 + 10 * SS, cy0 + row_h - 16 * SS, src, f_s5, GOLD, SS)
    y = y + row_h + 12 * SS
    d.line([margin, y, W - margin, y], fill=RULE, width=SS * 2)
    y += 10 * SS

    # ---- bottom zone: also-today (2 columns, left ~60%) + glance panel
    bottom_top = y
    bottom_h = H - bottom_top - 24 * SS   # leave footer strip
    glance_w = int(inner_w * 0.38)
    also_w = inner_w - glance_w - gap

    # also-today
    f_at = F(SANS_B, 12 * SS)
    draw_caps(d, margin, bottom_top, "Also Today", f_at, RED, SS * 2)
    f_li = F(SERIF, 12 * SS)
    yy = bottom_top + 20 * SS
    half = (len(ALSO) + 1) // 2
    col_gap = 16 * SS
    sub_w = (also_w - col_gap) // 2
    for i, item in enumerate(ALSO):
        col = 0 if i < half else 1
        ix = margin + col * (sub_w + col_gap)
        iy = bottom_top + 20 * SS + (i % half) * 24 * SS
        # bullet
        d.ellipse([ix, iy + 5 * SS, ix + 5 * SS, iy + 10 * SS], fill=GOLD)
        lines = fit_lines(d, item, f_li, sub_w - 14 * SS)
        for j, ln in enumerate(lines[:2]):
            d.text((ix + 12 * SS, iy + j * 13 * SS), ln, font=f_li, fill=INK)
    d.line([margin + also_w + gap // 2, bottom_top,
            margin + also_w + gap // 2, bottom_top + bottom_h - 8 * SS],
           fill=RULE, width=SS)

    # day-at-a-glance panel
    gx = margin + also_w + gap
    gw = glance_w
    gy = bottom_top
    gh = bottom_h - 8 * SS
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=CARD, outline=RULE, width=SS)
    d.rectangle([gx, gy, gx + gw, gy + 4 * SS], fill=TEAL)
    f_g = F(SANS_B, 12 * SS)
    draw_caps(d, gx + 12 * SS, gy + 12 * SS, "Day at a Glance", f_g, TEAL, SS * 2)
    f_gl = F(SANS, 9 * SS)
    yy = gy + 34 * SS
    avail = gh - 34 * SS - 84 * SS
    step = avail // len(GLANCE)
    for tag, item in GLANCE:
        f_gt = F(SANS_B, 9 * SS)
        draw_caps(d, gx + 12 * SS, yy, tag, f_gt, RED, SS)
        lines = fit_lines(d, item, f_gl, gw - 24 * SS - text_w(d, tag, f_gt) - 6 * SS)
        for j, ln in enumerate(lines[:1]):
            d.text((gx + 12 * SS + caps_w(d, tag, f_gt, SS) + 8 * SS, yy + j * 11 * SS),
                   ln, font=f_gl, fill=INK)
        yy += step
        d.line([gx + 12 * SS, yy - 4 * SS, gx + gw - 12 * SS, yy - 4 * SS],
               fill=RULE, width=SS)
    # DATE CHECK box inside glance panel
    dc_h = 72 * SS
    dc_y = gy + gh - dc_h - 8 * SS
    rr(d, [gx + 8 * SS, dc_y, gx + gw - 8 * SS, dc_y + dc_h], 4 * SS,
       fill=PAPER, outline=GOLD, width=SS * 2)
    f_dc = F(SANS_B, 10 * SS)
    draw_caps(d, gx + 18 * SS, dc_y + 8 * SS, "Date Check", f_dc, GOLD, SS * 2)
    f_dcl = F(SANS, 9 * SS)
    yy = dc_y + 24 * SS
    for ln in DATE_CHECK:
        d.text((gx + 18 * SS, yy), ln, font=f_dcl, fill=INK)
        yy += 13 * SS

    # ---- footer
    f_f = F(SANS, 8 * SS)
    foot = "The World Edition  ·  Monday 23 November 2026  ·  Page One"
    d.line([margin, H - 20 * SS, W - margin, H - 20 * SS], fill=RULE, width=SS)
    fw = text_w(d, foot, f_f)
    d.text(((W - fw) // 2, H - 16 * SS), foot, font=f_f, fill=INK)

    # ---- downscale
    final = img.resize((OUT, OUT), Image.LANCZOS)
    final.save("entry.png", optimize=True)
    return final


if __name__ == "__main__":
    im = render()
    print("wrote entry.png", im.size)

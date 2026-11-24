#!/usr/bin/env python3
# Front page: 23 November 2026 — ported from newsimg-20261120 baseline v3 (style preserved).
"""Render the 23 November 2026 front page to entry.png (1024x1024, <1 MiB).

Draws with Pillow at 4x supersample, then downscales. Deterministic: no
randomness, no network, no wall clock.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

S = 4                      # supersample factor
W = H = 1024
PX = W * S                 # canvas edge at supersample

# ---------- palette (warm ivory paper, slate ink, burnt-orange accent) ------
PAPER = (247, 242, 228)
INK = (28, 39, 51)
RED = (168, 55, 38)
TEAL = (41, 96, 92)
GOLD = (178, 129, 40)
MUTED = (94, 84, 66)
CARD = (252, 249, 238)
RULE = (206, 196, 172)
NAVY = (18, 28, 44)

FD = "/usr/share/fonts/truetype"
_SERIF = FD + "/dejavu/DejaVuSerif.ttf"
_SERIF_B = FD + "/dejavu/DejaVuSerif-Bold.ttf"
_SERIF_I = FD + "/dejavu/DejaVuSerif-Italic.ttf"
if not os.path.exists(_SERIF_I):
    _SERIF_I = FD + "/liberation/LiberationSerif-Italic.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def serif(sz):
    return F(_SERIF, sz * S)


def serifb(sz):
    return F(_SERIF_B, sz * S)


def serifit(sz):
    return F(_SERIF_I, sz * S)


img = Image.new("RGB", (PX, PX), PAPER)
d = ImageDraw.Draw(img)

M = 22 * S  # page margin


def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, text, font, maxw, fill, lh=None):
    lh = lh or int(font.size * 1.22)
    for line in wrap(text, font, maxw):
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def tag(x, y, num, city, field):
    d.text((x, y), "%d · %s · %s" % (num, city, field), font=serifb(11), fill=RED)
    return y + 14 * S


def card(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=S)


# ================================================================ header ====
d.rectangle([0, 0, PX, 6 * S], fill=RED)
d.text((M, 14 * S), "THE WORLD IN ONE DAY", font=serifb(13), fill=INK)
right = "MONDAY'S NEWS · ONE PAGE · 7 STORIES · 7 REGIONS"
d.text((PX - M - d.textlength(right, font=serifb(13)), 14 * S), right,
       font=serifb(13), fill=INK)
d.line([M, 34 * S, PX - M, 34 * S], fill=INK, width=S)

# masthead
date_f = serifb(64)
dtxt = "Monday 23 November 2026"
dw = d.textlength(dtxt, font=date_f)
d.text(((PX - dw) / 2, 40 * S), dtxt, font=date_f, fill=INK)
sub = "Iran hits US bases in the Gulf  ·  COP31 collapses  ·  War spreads to the Libyan coast"
sf = serifit(15)
d.text(((PX - d.textlength(sub, font=sf)) / 2, 112 * S), sub, font=sf, fill=RED)
d.line([M, 134 * S, PX - M, 134 * S], fill=RULE, width=S)

# ============================================================= stat band ====
stats = [
    ("COP31 collapses", "divided world leaves Antalya with no climate deal (Guardian, BBC)"),
    ("24 killed", "in Indonesia confectionery-factory fire; dozens missing (Guardian)"),
    ("893 kg", "of cocaine seized by Met Police hidden in orange boxes (Guardian)"),
    ("1,000+", "Russian military suicides in the Ukraine war, leaked data shows (Guardian)"),
    ("£750,000", "paid to help a Turkish woman get a passport, court told (Guardian)"),
    ("2 ships hit", "by Ukrainian naval drones off Libya, Kyiv confirms (Guardian, BBC)"),
]
sy = 142 * S
sw = (PX - 2 * M) / 6
for i, (big, small) in enumerate(stats):
    x = M + i * sw
    d.text((x, sy), big, font=serifb(15), fill=RED if i % 2 else INK)
    yy = sy + 22 * S
    for ln in wrap(small, serif(9.5), sw - 8 * S)[:3]:
        d.text((x, yy), ln, font=serif(9.5), fill=MUTED)
        yy += 12 * S
d.line([M, sy + 62 * S, PX - M, sy + 62 * S], fill=RULE, width=S)

# ============================================================= hero row =====
hy = 212 * S
hh = 210 * S
cw = (PX - 2 * M - 2 * 10 * S) / 3

# hero 1: Gulf strikes — burning horizon over a dark sea, smoke columns, base towers
x0 = M
card(x0, hy, cw, hh)
d.rectangle([x0 + 8 * S, hy + 8 * S, x0 + cw - 8 * S, hy + 88 * S], fill=NAVY)
# burning horizon glow
d.rectangle([x0 + 8 * S, hy + 62 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(46, 34, 30))
d.rectangle([x0 + 8 * S, hy + 70 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(94, 40, 24))
d.rectangle([x0 + 8 * S, hy + 78 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(168, 55, 38))
d.rectangle([x0 + 8 * S, hy + 84 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(232, 140, 60))
# fire bursts on the horizon
for (gx, gy, gr) in [(70, 66, 12), (200, 60, 16), (262, 72, 10)]:
    d.ellipse([x0 + gx * S - gr * S, hy + gy * S - gr * S,
               x0 + gx * S + gr * S, hy + gy * S + gr * S], fill=(240, 190, 90))
    d.ellipse([x0 + gx * S - gr * S * 0.5, hy + gy * S - gr * S * 0.5,
               x0 + gx * S + gr * S * 0.5, hy + gy * S + gr * S * 0.5], fill=(214, 88, 52))
# smoke columns
for (sx, top) in [(80, 18), (215, 12), (275, 26)]:
    d.polygon([(x0 + (sx - 4) * S, hy + 84 * S), (x0 + (sx + 4) * S, hy + 84 * S),
               (x0 + (sx + 12) * S, hy + top * S), (x0 + (sx - 2) * S, hy + top * S)],
              fill=(40, 52, 72))
# base towers (US bases on the coast)
for (tx, th) in [(120, 30), (150, 40), (178, 26)]:
    d.rectangle([x0 + tx * S, hy + 84 * S - th * S, x0 + (tx + 12) * S, hy + 84 * S],
                fill=(14, 22, 36))
    d.rectangle([x0 + (tx + 5) * S, hy + 84 * S - th * S, x0 + (tx + 7) * S, hy + 84 * S],
                fill=(178, 129, 40))
# rising missile trails
for (bx, by, ex, ey) in [(30, 84, 54, 26), (300, 84, 322, 38)]:
    d.line([x0 + bx * S, hy + by * S, x0 + ex * S, hy + ey * S],
           fill=(232, 140, 60), width=2 * S)
    d.ellipse([x0 + ex * S - 4 * S, hy + ey * S - 8 * S,
               x0 + ex * S + 4 * S, hy + ey * S], fill=(240, 190, 90))
y = tag(x0 + 8 * S, hy + 94 * S, 1, "THE GULF", "WAR")
d.text((x0 + 8 * S, y), "Iran hits US bases and civilian", font=serifb(13.5), fill=INK)
d.text((x0 + 8 * S, y + 17 * S), "sites in the Gulf after a lull", font=serifb(13.5), fill=INK)
para(x0 + 8 * S, y + 38 * S,
     "Strikes end days of calm; American bases and civilian sites in the Gulf come under fire.",
     serif(9.5), cw - 16 * S, MUTED)
para(x0 + 8 * S, hy + hh - 26 * S, "(Al Jazeera)", serifit(8.5), cw, MUTED)

# hero 2: COP31 collapse — broken table gavel over the COP31 ring
x0 = M + cw + 10 * S
card(x0, hy, cw, hh)
d.rectangle([x0 + 8 * S, hy + 8 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(233, 224, 196))
cx, cy, r = x0 + cw / 2, hy + 46 * S, 26 * S
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3 * S)
for k in range(10):
    a = k * math.pi / 5
    px_, py_ = cx + (r + 7 * S) * math.cos(a), cy + (r + 7 * S) * math.sin(a)
    d.ellipse([px_ - 4 * S, py_ - 4 * S, px_ + 4 * S, py_ + 4 * S], fill=INK)
d.text((cx - 24 * S, cy - 12 * S), "COP31", font=serifb(13), fill=RED)
# crack through the ring
d.line([cx - 6 * S, hy + 8 * S, cx + 10 * S, hy + 88 * S], fill=PAPER, width=3 * S)
d.line([cx - 6 * S, hy + 8 * S, cx + 10 * S, hy + 88 * S], fill=RED, width=S)
# broken gavel
d.line([x0 + 30 * S, hy + 78 * S, x0 + 62 * S, hy + 52 * S], fill=(120, 80, 40), width=4 * S)
d.rectangle([x0 + 26 * S, hy + 80 * S, x0 + 54 * S, hy + 84 * S], fill=(120, 80, 40))
d.line([x0 + cw - 58 * S, hy + 50 * S, x0 + cw - 26 * S, hy + 80 * S], fill=(120, 80, 40), width=4 * S)
y = tag(x0 + 8 * S, hy + 94 * S, 2, "ANTALYA", "CLIMATE")
d.text((x0 + 8 * S, y), "COP31 climate talks collapse,", font=serifb(13.5), fill=INK)
d.text((x0 + 8 * S, y + 17 * S), "a divided world leaves no deal", font=serifb(13.5), fill=INK)
para(x0 + 8 * S, y + 38 * S,
     "Talks end in failure with no fossil-fuel wording; host and allies blame the divide.",
     serif(9.5), cw - 16 * S, MUTED)
para(x0 + 8 * S, hy + hh - 26 * S, "(Guardian, BBC)", serifit(8.5), cw, MUTED)

# hero 3: naval drones off Libya — dark sea, wakes, two struck ships
x0 = M + 2 * (cw + 10 * S)
card(x0, hy, cw, hh)
d.rectangle([x0 + 8 * S, hy + 8 * S, x0 + cw - 8 * S, hy + 88 * S], fill=(16, 40, 52))
d.polygon([(x0 + 8 * S, hy + 88 * S), (x0 + cw - 8 * S, hy + 88 * S),
           (x0 + cw - 8 * S, hy + 26 * S), (x0 + 8 * S, hy + 40 * S)], fill=(20, 52, 64))
# wakes
for wx in (110, 250):
    d.line([x0 + wx * S, hy + 88 * S, x0 + (wx - 20) * S, hy + 30 * S], fill=(120, 170, 180), width=S)
    d.line([x0 + wx * S, hy + 88 * S, x0 + (wx + 20) * S, hy + 30 * S], fill=(120, 170, 180), width=S)
# ships
for (sx, sy2) in [(100, 34), (240, 30)]:
    d.polygon([(x0 + sx * S, hy + sy2 * S), (x0 + (sx + 34) * S, hy + sy2 * S),
               (x0 + (sx + 28) * S, hy + (sy2 + 10) * S), (x0 + (sx + 6) * S, hy + (sy2 + 10) * S)],
              fill=INK)
    d.rectangle([x0 + (sx + 12) * S, hy + (sy2 - 8) * S, x0 + (sx + 20) * S, hy + sy2 * S], fill=RED)
# naval drones
d.ellipse([x0 + 60 * S, hy + 66 * S, x0 + 74 * S, hy + 74 * S], fill=(232, 140, 60))
d.ellipse([x0 + 200 * S, hy + 60 * S, x0 + 214 * S, hy + 68 * S], fill=(232, 140, 60))
d.text((x0 + cw - 108 * S, hy + 74 * S), "OFF LIBYA", font=serifb(10), fill=PAPER)
y = tag(x0 + 8 * S, hy + 94 * S, 3, "LIBYAN COAST", "WAR")
d.text((x0 + 8 * S, y), "Ukraine strikes two Russian ships", font=serifb(13.5), fill=INK)
d.text((x0 + 8 * S, y + 17 * S), "off Libya with naval drones", font=serifb(13.5), fill=INK)
para(x0 + 8 * S, y + 38 * S,
     "Kyiv confirms naval-drone hits far from the Black Sea; the war spreads to the Libyan coast.",
     serif(9.5), cw - 16 * S, MUTED)
para(x0 + 8 * S, hy + hh - 26 * S, "(Guardian, BBC)", serifit(8.5), cw, MUTED)

# ============================================================= cards r1 =====
r1y = hy + hh + 10 * S
r1h = 150 * S
c5 = (PX - 2 * M - 4 * 8 * S) / 5


def mini_chart(x, y, w, h, pts, col, wdt=2):
    step = w / (len(pts) - 1)
    for i in range(len(pts) - 1):
        d.line([x + i * step, y + h * (1 - pts[i]), x + (i + 1) * step,
                y + h * (1 - pts[i + 1])], fill=col, width=wdt * S)


r1 = [
    (4, "JAKARTA · ASIA", "24 killed in factory fire",
     "Blaze tears through an Indonesian confectionery plant; dozens missing. (Guardian)", "fire"),
    (5, "LONDON · EUROPE", "Met seizes 893 kg of cocaine",
     "Hidden in boxes of oranges at the border; the haul is one of the year's largest. (Guardian)", "oranges"),
    (6, "MOSCOW · WAR", "1,000+ Russian military suicides",
     "Leaked data shows the toll of the Ukraine war on Moscow's own ranks. (Guardian)", "bars"),
    (7, "GAZA · MIDEAST", "Gaza a 'toxic wasteland', Oxfam",
     "Experts say Israeli attacks have left the strip environmentally devastated. (BBC, Guardian)", "rubble"),
    (8, "WASHINGTON · US", "Huang back at Nvidia after scandal",
     "Reinstated after an affair-with-spy scandal; Trump says 'I made the deal'. (BBC)", "chip"),
]
for i, (num, tg, head, body, art) in enumerate(r1):
    x = M + i * (c5 + 8 * S)
    card(x, r1y, c5, r1h)
    ay = r1y + 8 * S
    if art == "fire":
        d.rectangle([x + 14 * S, ay + 14 * S, x + 72 * S, ay + 28 * S], fill=INK)
        d.ellipse([x + 30 * S, ay + 2 * S, x + 46 * S, ay + 18 * S], fill=RED)
        d.ellipse([x + 38 * S, ay + 6 * S, x + 48 * S, ay + 16 * S], fill=GOLD)
    elif art == "oranges":
        for k in range(3):
            d.ellipse([x + (14 + k * 18) * S, ay + 8 * S, x + (30 + k * 18) * S,
                       ay + 24 * S], fill=GOLD)
        d.rectangle([x + 10 * S, ay + 24 * S, x + 78 * S, ay + 28 * S], fill=RULE)
        d.text((x + 50 * S, ay), "893", font=serifb(12), fill=RED)
    elif art == "bars":
        for k, bh in enumerate([10, 16, 24]):
            d.rectangle([x + (16 + k * 20) * S, ay + 28 * S - bh * S,
                         x + (30 + k * 20) * S, ay + 28 * S], fill=TEAL)
        d.text((x + 72 * S, ay + 2 * S), "1K+", font=serifb(14), fill=RED)
    elif art == "rubble":
        d.polygon([(x + 14 * S, ay + 28 * S), (x + 40 * S, ay + 10 * S),
                   (x + 66 * S, ay + 28 * S)], fill=(120, 110, 90))
        d.line([x + 26 * S, ay + 16 * S, x + 52 * S, ay + 26 * S], fill=RED, width=2 * S)
    else:
        d.rectangle([x + 24 * S, ay + 2 * S, x + 54 * S, ay + 26 * S], fill=TEAL)
        d.rectangle([x + 30 * S, ay + 8 * S, x + 48 * S, ay + 20 * S], fill=(232, 168, 74))
        d.line([x + 54 * S, ay + 6 * S, x + 66 * S, ay + 6 * S], fill=INK, width=S)
        d.line([x + 54 * S, ay + 22 * S, x + 66 * S, ay + 22 * S], fill=INK, width=S)
    y = tag(x + 8 * S, ay + 34 * S, num, *tg.split(" · "))
    head_lines = wrap(head, serifb(11.5), c5 - 16 * S)[:2]
    for hl in head_lines:
        d.text((x + 8 * S, y), hl, font=serifb(11.5), fill=INK)
        y += 14 * S
    y += 2 * S
    para(x + 8 * S, y, body, serif(8.5), c5 - 16 * S, MUTED)

# ======================================================== also-today list ===
aly = r1y + r1h + 12 * S
d.text((M, aly), "ALSO ON MONDAY 23 NOVEMBER — 10 MORE STORIES", font=serifb(12), fill=RED)
d.line([M, aly + 17 * S, PX - M, aly + 17 * S], fill=RULE, width=S)
items = [
    ("BRUSSELS", "EU proposes sweeping new Russia sanctions including a sports ban.", "Al Jazeera"),
    ("LONDON", "UK sanctions top Myanmar military leaders after Rohingya genocide ruling.", "BBC"),
    ("DAMASCUS", "Israel's southern Syria incursion triggers fear and destruction.", "Al Jazeera"),
    ("WASHINGTON", "US escalates Iran sanctions, targets 'shadow banking' networks.", "Al Jazeera"),
    ("TEHRAN", "Singer Parastoo Ahmadi flogged for performing without hijab.", "BBC, Al Jazeera"),
    ("PARIS", "Gisèle Pelicot 'deeply shocked' as nude photos sent to media to promote a book.", "BBC, Guardian"),
    ("SEATTLE", "Outrage after ICE arrests father and daughter at the airport; DoJ admits it deported a US citizen.", "BBC, Guardian"),
    ("BOGOTÁ", "Drone attack on a police base in Colombia injures three, including an infant.", "Al Jazeera"),
    ("ISTANBUL", "Turkish police hunt a lioness stalking the city's outskirts.", "Al Jazeera"),
    ("LONDON", "Former prince Andrew paid £750,000 to help a Turkish woman with a passport, High Court hears.", "Guardian"),
]
colw = (PX - 2 * M - 20 * S) / 2
item_f = serif(8.3)
lead_f = serifb(8.8)
half = 5
for ci, chunk in enumerate((items[:half], items[half:])):
    x = M + ci * (colw + 20 * S)
    y = aly + 22 * S
    for city, txt, src in chunk:
        full = "%s (%s)" % (txt, src)
        lw = d.textlength(city + "  ", font=lead_f)
        d.text((x, y), city, font=lead_f, fill=INK)
        y = para(x + lw, y, full, item_f, colw - lw, MUTED)
        y += 6 * S

# ==================================================== story index panel =====
by = aly + 118 * S
bw = 300 * S
card(M, by, bw, PX - M - by)
d.text((M + 8 * S, by + 6 * S), "THE DAY AT A GLANCE", font=serifb(11), fill=INK)
regions = [
    ("MIDEAST", ["1 · 4g · 7"]),
    ("EUROPE", ["2 · 5 · 8a · 8b"]),
    ("ASIA", ["4a · 6"]),
    ("AMERICAS", ["7a · 7b · 8c"]),
    ("WAR FRONTS", ["1 · 3 · 6"]),
]
yy = by + 24 * S
for rname, its in regions:
    d.text((M + 10 * S, yy), rname, font=serifb(9.5), fill=TEAL)
    d.text((M + 128 * S, yy), " · ".join(its), font=serif(9), fill=MUTED)
    yy += 14 * S
d.line([M + 10 * S, yy + 2 * S, M + bw - 10 * S, yy + 2 * S], fill=RULE, width=S)
d.text((M + 10 * S, yy + 6 * S), "17 stories · 7 regions · 6 fields",
       font=serifit(9), fill=RED)

dx0 = M + bw + 10 * S
d.rectangle([dx0, by, PX - M, PX - M], outline=RED, width=2 * S)
d.text((dx0 + 10 * S, by + 6 * S), "DATE CHECK", font=serifb(12), fill=RED)
para(dx0 + 10 * S, by + 24 * S,
     "The Nvidia scandal spans several days; Huang's reinstatement was reported into 24 November. "
     "COP31's collapse and the leaked Russian suicide data were both published on 23 November.",
     serif(8.8), PX - M - dx0 - 20 * S, MUTED)
para(dx0 + 10 * S, by + 64 * S,
     "Every story happened, or was first reported, on 23 November 2026 in at least one time zone; "
     "figures and claims are as reported and attributed, not stated as fact.",
     serif(8.8), PX - M - dx0 - 20 * S, MUTED)
d.text((dx0 + 10 * S, PX - M - 14 * S), "Sources: BBC World, Al Jazeera, Guardian — original drawing, made in code.",
       font=serifit(7.6), fill=MUTED)

# footer
d.line([M, PX - M + 2 * S, PX - M, PX - M + 2 * S], fill=INK, width=S)

# ------------------------------------------------------------ downscale ----
final = img.resize((W, H), Image.Resampling.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
final.save(out, "PNG", optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")

#!/usr/bin/env python3
"""Newspaper front page generator - Monday 23 November 2026."""
import hashlib, os
from PIL import Image, ImageDraw, ImageFont

S = 4                      # supersample factor
W = H = 1024 * S           # canvas
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 241, 226)    # warm ivory
INK = (58, 64, 78)         # slate
ACCENT = (196, 92, 44)     # burnt orange
RULE = (150, 142, 126)
SOFT = (216, 207, 188)

FD = "/usr/share/fonts/truetype/dejavu/"

def F(name, size):
    return ImageFont.truetype(FD + name, size * S)

def ctext(d, xy, txt, font, fill, anchor="ma"):
    d.text(xy, txt, font=font, fill=fill, anchor=anchor)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------- paper grain (deterministic) ----------
for i in range(1600):
    x = (i * 977) % W
    y = (i * 613 + 41) % H
    v = 251 - ((i * 7) % 8)
    d.point((x, y), fill=(v, v - 4, v - 16))

M = 64 * S                 # margin

# ---------- masthead ----------
d.rectangle([0, 0, W, 10 * S], fill=INK)
d.rectangle([0, 10 * S, W, 13 * S], fill=ACCENT)

ctext(d, (W // 2, 34 * S), "THE DAILY DISPATCH", F("DejaVuSerif-Bold.ttf", 46), INK)
ctext(d, (W // 2, 86 * S), "Monday 23 November 2026   |   World Edition   |   No. 4,182",
      F("DejaVuSerif.ttf", 15), INK, "ma")
y = 116 * S
d.rectangle([M, y, W - M, y + 3 * S], fill=INK)

# ---------- stat band ----------
y += 10 * S
band_h = 44 * S
d.rectangle([M, y, W - M, y + band_h], fill=SOFT)
d.rectangle([M, y, M + 6 * S, y + band_h], fill=ACCENT)
stats = ["893kg seized", "24 dead", "1,000+", "750,000 pounds", "2 ships", "4x"]
sw = (W - 2 * M) // len(stats)
for i, s in enumerate(stats):
    cx = M + sw * i + sw // 2
    ctext(d, (cx, y + 10 * S), s, F("DejaVuSerif-Bold.ttf", 15), ACCENT)
    ctext(d, (cx, y + 26 * S), ["Cocaine in orange boxes", "Factory fire toll",
         "Military suicides leaked", "Paid to Andrew", "Hit off Libya",
         "Supersampled print"][i], F("DejaVuSerif.ttf", 10), INK)
y += band_h + 12 * S

# ---------- hero visual row ----------
vh = 92 * S
col_w = (W - 2 * M - 2 * 12 * S) // 3
panels = []
for k in range(3):
    x0 = M + k * (col_w + 12 * S)
    panels.append([x0, y, x0 + col_w, y + vh])
    d.rectangle(panels[-1], fill=(228, 219, 198), outline=INK)

# panel 1: gulf burning horizon
x0, y0, x1, y1 = panels[0]
for r in range(vh):
    t = r / max(1, vh - 1)
    col = (int(250 - 90 * t), int(150 - 60 * t), int(70 - 40 * t))
    d.line([x0, y0 + r, x1, y0 + r], fill=col)
hor = y0 + int(vh * 0.62)
d.rectangle([x0, hor, x1, y1], fill=(70, 62, 58))
for i in range(9):
    fx = x0 + (i * 137) % (col_w - 20 * S)
    fh = (14 + (i * 53) % 26) * S
    d.line([fx + 8 * S, hor, fx + 8 * S, hor - fh], fill=(30, 26, 24), width=2 * S)
ctext(d, ((x0 + x1) // 2, y0 + 8 * S), "GULF", F("DejaVuSerif-Bold.ttf", 13), (255, 246, 230))

# panel 2: COP31 broken ring
x0, y0, x1, y1 = panels[1]
cx, cy, rr = (x0 + x1) // 2, (y0 + y1) // 2, int(vh * 0.32)
d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(90, 130, 110), width=6 * S)
d.pieslice([cx - rr - 4, cy - rr - 4, cx + rr + 4, cy + rr + 4], 300, 360, fill=PAPER)
d.line([cx + int(rr * 0.5), cy - int(rr * 0.85), cx + int(rr * 1.05), cy - int(rr * 0.2)],
       fill=(200, 60, 40), width=3 * S)
ctext(d, (cx, cy - 4 * S), "COP31", F("DejaVuSerif-Bold.ttf", 14), INK)
ctext(d, (cx, cy + 8 * S), "no deal", F("DejaVuSerif.ttf", 10), (160, 60, 40))

# panel 3: Libyan coast drones
x0, y0, x1, y1 = panels[2]
d.rectangle([x0, y0 + int(vh * 0.68), x1, y1], fill=(90, 96, 108))
for i in range(5):
    dx = x0 + 14 * S + i * (col_w // 6)
    dy = y0 + 16 * S + (i * 29 % 40) * S
    d.ellipse([dx, dy, dx + 22 * S, dy + 7 * S], outline=(40, 44, 52), width=2 * S)
    d.line([dx + 4 * S, dy + 3 * S, dx - 8 * S, dy + 3 * S], fill=(40, 44, 52), width=1 * S)
ctext(d, ((x0 + x1) // 2, y1 - 20 * S), "LIBYAN COAST", F("DejaVuSerif-Bold.ttf", 12),
      (240, 240, 245))

y = y + vh + 10 * S

# ---------- lead story ----------
lead_head = "IRAN HITS US BASES AND CIVILIAN SITES IN THE GULF AFTER A LULL"
lh_font = F("DejaVuSerif-Bold.ttf", 24)
lhl, cur = [], ""
for wd in lead_head.split():
    t = (cur + " " + wd).strip()
    if d.textlength(t, font=lh_font) <= W - 2 * M:
        cur = t
    else:
        lhl.append(cur); cur = wd
lhl.append(cur)
for ln in lhl:
    ctext(d, (M, y), ln, lh_font, ACCENT, "la")
    y += 30 * S
y += 2 * S
lead_body = ("Tehran's missile and drone barrages struck American installations and "
             "civilian districts across the Gulf states overnight, ending three weeks "
             "of uneasy quiet. Medics reported casualties at two base perimeters; "
             "insurers widened the war-risk zone.")
bw = ""
for wd in lead_body.split():
    t = (bw + " " + wd).strip()
    if d.textlength(t, font=F("DejaVuSerif.ttf", 12)) <= W - 2 * M:
        bw = t
    else:
        ctext(d, (M, y), bw, F("DejaVuSerif.ttf", 12), INK, "la"); y += 17 * S; bw = wd
if bw:
    ctext(d, (M, y), bw, F("DejaVuSerif.ttf", 12), INK, "la"); y += 17 * S
ctext(d, (W - M, y + 2 * S), "(Al Jazeera)", F("DejaVuSerif.ttf", 11), ACCENT, "ra")
y += 18 * S
d.line([M, y, W - M, y], fill=RULE, width=1 * S)
y += 8 * S

# ---------- columns ----------
def story(d, x, w, yy, kicker, head, body, outlet):
    ctext(d, (x, yy), kicker, F("DejaVuSerif-Bold.ttf", 10), ACCENT, "la")
    yy += 14 * S
    lines, cur = [], ""
    for wd in head.split():
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=F("DejaVuSerif-Bold.ttf", 14)) <= w:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    for ln in lines:
        ctext(d, (x, yy), ln, F("DejaVuSerif-Bold.ttf", 14), INK, "la")
        yy += 17 * S
    yy += 2 * S
    bw = ""
    for wd in body.split():
        t = (bw + " " + wd).strip()
        if d.textlength(t, font=F("DejaVuSerif.ttf", 11)) <= w:
            bw = t
        else:
            ctext(d, (x, yy), bw, F("DejaVuSerif.ttf", 11), INK, "la"); yy += 14 * S; bw = wd
    if bw:
        ctext(d, (x, yy), bw, F("DejaVuSerif.ttf", 11), INK, "la"); yy += 14 * S
    yy += 2 * S
    ctext(d, (x + w, yy), "(%s)" % outlet, F("DejaVuSerif.ttf", 10), ACCENT, "ra")
    return yy + 15 * S

col2 = M + col_w + 12 * S
col3 = col2 + col_w + 12 * S

y2 = story(d, col2, col_w, y, "WAR AT SEA",
           "Ukraine naval drones strike two Russian ships off Libya",
           "Sea drones hit a tanker and a landing craft shadowing the "
           "Russian supply lane; Kyiv claims both were listing by dawn.",
           "Guardian/BBC")
y2 = story(d, col2, col_w, y2, "CLIMATE",
           "COP31 climate talks collapse",
           "Delegates left the plenary hall without a final text after "
           "finance rows deadlocked the closing session.",
           "Guardian/BBC")
y2 = story(d, col2, col_w, y2, "JAKARTA",
           "24 killed in Indonesia confectionery factory fire",
           "The blaze tore through a candy plant near Bekasi; "
           "exits were reportedly chained shut.",
           "Guardian")
y2 = story(d, col2, col_w, y2, "LONDON",
           "Met Police seize 893kg cocaine in orange boxes",
           "A fruit consignment at Tilbury hid the record haul; "
           "seven arrests followed raids across east London.",
           "Guardian")

y3 = story(d, col3, col_w, y, "LEAKED DATA",
           "1,000+ Russian military suicides in Ukraine war",
           "Leaked registries point to more than a thousand "
           "self-inflicted deaths among deployed troops.",
           "Guardian")
y3 = story(d, col3, col_w, y3, "SILICON VALLEY",
           "Jensen Huang reinstated as Nvidia chief",
           "The board reversed its shock removal within a week.",
           "BBC")

# ---------- also today ----------
ay = max(y2, y3) + 2 * S
d.rectangle([M, ay, W - M, ay + 15 * S], fill=INK)
ctext(d, (M + 10 * S, ay + 2 * S), "ALSO TODAY", F("DejaVuSerif-Bold.ttf", 12), PAPER, "la")
ctext(d, (W - M - 10 * S, ay + 3 * S), "briefs in brief", F("DejaVuSerif.ttf", 9), SOFT, "ra")
ay += 20 * S

briefs = [
    ("EU widens Russia sports-ban sanctions", "Al Jazeera"),
    ("UK sanctions Myanmar junta leaders", "BBC"),
    ("Israel launches southern Syria incursion", "Al Jazeera"),
    ("US targets Iran shadow-banking network", "Al Jazeera"),
    ("Singer Parastoo Ahmadi flogged after arrest", "BBC/Al Jazeera"),
    ("Gisele Pelicot nude photos published without consent", "BBC/Guardian"),
    ("ICE Seattle arrest; DoJ admits deporting US citizen", "BBC/Guardian"),
    ("Colombia police base hit by drone attack", "Al Jazeera"),
    ("Istanbul lioness hunt ends after park escape", "Al Jazeera"),
    ("Andrew paid 750,000 pounds in settlement", "Guardian"),
]
bh = 17 * S
for i, (t, o) in enumerate(briefs):
    yy = ay + i * bh
    if i % 2 == 0:
        d.rectangle([M, yy - 2 * S, W - M, yy + bh - 2 * S], fill=SOFT)
    d.ellipse([M + 4 * S, yy + 6 * S, M + 9 * S, yy + 11 * S], fill=ACCENT)
    ctext(d, (M + 16 * S, yy + 3 * S), t, F("DejaVuSerif.ttf", 11), INK, "la")
    ctext(d, (W - M - 8 * S, yy + 4 * S), "(%s)" % o, F("DejaVuSerif.ttf", 9), ACCENT, "ra")
ay += len(briefs) * bh + 8 * S

# ---------- footer ----------
d.line([M, ay, W - M, ay], fill=INK, width=2 * S)
ctext(d, (W // 2, ay + 8 * S),
      "THE DAILY DISPATCH  -  compiled 23 Nov 2026  -  4x supersampled",
      F("DejaVuSerif.ttf", 11), INK)

# ---------- downsample ----------
final = img.resize((1024, 1024), Image.LANCZOS)
final.save(OUT, "PNG", optimize=True)
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
print(OUT, h, os.path.getsize(OUT))

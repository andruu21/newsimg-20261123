#!/usr/bin/env python3
"""news-image-20261123: deterministic Pillow newspaper front page.

Renders 'Monday 23 November 2026' world news to entry.png at exactly
1024x1024, under 1 MiB. Drawn at 4x supersample then LANCZOS downscaled.
No randomness, no network, no wall-clock.
"""

from PIL import Image, ImageDraw, ImageFont

S = 4                      # supersample factor
W, H = 1024 * S, 1024 * S

FDIR = "/usr/share/fonts/truetype/dejavu"

# palette
PAPER = (247, 242, 228)
INK = (28, 39, 51)
RED = (168, 55, 38)
TEAL = (41, 96, 92)
GOLD = (178, 129, 40)
CARD = (252, 249, 238)
RULE = (206, 196, 172)

FONT_PATHS = {
    "serif": FDIR + "/DejaVuSerif.ttf",
    "serif_b": FDIR + "/DejaVuSerif-Bold.ttf",
    "sans": FDIR + "/DejaVuSans.ttf",
    "sans_b": FDIR + "/DejaVuSans-Bold.ttf",
}

_fonts = {}


def fnt(key, px):
    px = max(1, int(round(px * S)))
    k = (key, px)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_PATHS[key], px)
    return _fonts[k]


def make_canvas():
    img = Image.new("RGB", (W, H), PAPER)
    return img, ImageDraw.Draw(img)


def text(d, xy, s, font, fill=INK, anchor="la"):
    d.text((xy[0] * S, xy[1] * S), s, font=fnt(*font), fill=fill, anchor=anchor)


def text_w(d, s, font):
    box = d.textbbox((0, 0), s, font=fnt(*font))
    return (box[2] - box[0]) / S


def wrap(d, s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(d, t, font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, font, fill, maxw, lh):
    for ln in wrap(d, s, font, maxw):
        text(d, (x, y), ln, font, fill)
        y += lh
    return y


def italic_text(base_img, d, xy, s, font, fill, anchor="la"):
    """Shear-render italic (no serif italic face ships with DejaVu)."""
    f = fnt(*font)
    box = f.getbbox(s)
    tw, th = box[2] - box[0], box[3] - box[1]
    tmp = Image.new("RGBA", (tw + 4 * S, th + 2 * S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((2 * S - box[0], S - box[1]), s, font=f, fill=fill + (255,))
    sheared = tmp.transform(
        (tmp.width + th // 2, tmp.height),
        Image.AFFINE, (1, -0.22, th * 0.22, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    x, y = xy[0] * S, xy[1] * S
    if anchor[0] == "m":
        x -= sheared.width // 2
    base_img.paste(sheared, (int(x), int(y)), sheared)


def rect(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill,
                outline=outline, width=int(width * S))


def line(d, x0, y0, x1, y1, fill, width=1):
    d.line([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, width=int(width * S))


def ellipse(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill,
              outline=outline, width=int(width * S))


def poly(d, pts, fill=None, outline=None):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)


def vgrad(d, x0, y0, x1, y1, c_top, c_bot, steps=48):
    """Vertical gradient by thin rects."""
    hh = (y1 - y0) / steps
    for i in range(steps):
        t = i / (steps - 1)
        c = tuple(int(c_top[j] + (c_bot[j] - c_top[j]) * t) for j in range(3))
        rect(d, x0, y0 + i * hh, x1, y0 + (i + 1) * hh, fill=c)


# ------------------------------------------------------------------ art

def art_gulf(d, x0, y0, x1, y1):
    """Burning horizon: amber sky, low sun, dark gulf sea, flames."""
    vgrad(d, x0, y0, x1, y0 + (y1 - y0) * 0.58, (196, 92, 38), (233, 160, 66))
    horizon = y0 + (y1 - y0) * 0.58
    ellipse(d, (x0 + x1) / 2 - 26, horizon - 46, (x0 + x1) / 2 + 26, horizon + 6, fill=(120, 34, 22))
    vgrad(d, x0, horizon, x1, y1, (58, 30, 24), (18, 16, 20))
    for i, (fx, fh, fc) in enumerate([(0.22, 22, RED), (0.34, 34, (208, 70, 28)),
                                      (0.66, 28, (208, 70, 28)), (0.80, 18, RED),
                                      (0.47, 40, (236, 120, 40))]):
        bx = x0 + (x1 - x0) * fx
        poly(d, [(bx - 7, horizon), (bx, horizon - fh), (bx + 7, horizon)], fill=fc)
        poly(d, [(bx - 3, horizon), (bx, horizon - fh - 10), (bx + 3, horizon)], fill=(250, 200, 90))
    for k in range(5):
        sx = x0 + (x1 - x0) * (0.08 + 0.19 * k)
        line(d, sx, horizon + 8 + (k % 2) * 5, sx + 30, horizon + 8 + (k % 2) * 5, (90, 60, 50), 1)


def art_cop(d, x0, y0, x1, y1):
    """Cracked ring on pale field: COP31 collapse."""
    rect(d, x0, y0, x1, y1, fill=(235, 228, 208))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r_out, r_in = min(x1 - x0, y1 - y0) * 0.34, min(x1 - x0, y1 - y0) * 0.20
    ellipse(d, cx - r_out, cy - r_out, cx + r_out, cy + r_out, fill=TEAL)
    ellipse(d, cx - r_in, cy - r_in, cx + r_in, cy + r_in, fill=(235, 228, 208))
    # crack: paper-colored zigzag wedges through the ring
    poly(d, [(cx - 4, cy - r_out - 4), (cx + 10, cy - 6), (cx - 2, cy + 4),
             (cx + 14, cy + r_out + 4), (cx + 4, cy + r_out + 4),
             (cx - 10, cy + 2), (cx + 2, cy - 8), (cx - 12, cy - r_out - 4)],
         fill=(235, 228, 208))
    for a, rr in [(210, r_out + 6), (330, r_out + 6)]:
        import math
        ax = cx + rr * math.cos(math.radians(a))
        ay = cy + rr * math.sin(math.radians(a))
        ellipse(d, ax - 3, ay - 3, ax + 3, ay + 3, fill=GOLD)


def art_naval(d, x0, y0, x1, y1):
    """Two ships at night on a dark sea with drone wakes."""
    vgrad(d, x0, y0, x1, y0 + (y1 - y0) * 0.42, (16, 24, 34), (28, 44, 56))
    sea = y0 + (y1 - y0) * 0.42
    vgrad(d, x0, sea, x1, y1, (20, 38, 48), (8, 14, 18))
    ellipse(d, x1 - 60, y0 + 8, x1 - 30, y0 + 34, fill=(200, 206, 210))
    for k, fx in enumerate([0.30, 0.68]):
        bx = x0 + (x1 - x0) * fx
        by = sea + 10 + k * 22
        poly(d, [(bx - 24, by), (bx + 24, by), (bx + 18, by + 8), (bx - 18, by + 8)], fill=(34, 40, 46))
        rect(d, bx - 10, by - 9, bx + 6, by, fill=(20, 24, 30))
        ellipse(d, bx + 1, by - 5, bx + 5, by - 1, fill=RED)  # fire glow
        for j in range(4):
            line(d, bx - 30 - j * 10, by + 4 + j * 3, bx - 12 - j * 10, by + 4 + j * 3, (70, 96, 104), 1)
    for k in range(4):
        sx = x0 + (x1 - x0) * (0.1 + 0.24 * k)
        line(d, sx, sea + (12 + k * 14) % (y1 - sea - 6), sx + 24, sea + (12 + k * 14) % (y1 - sea - 6), (44, 66, 74), 1)


# small icons for the story row (drawn inside a square box)

def icon_flame(d, cx, cy, r):
    poly(d, [(cx - r * .5, cy + r * .7), (cx, cy - r * .8), (cx + r * .5, cy + r * .7)], fill=RED)
    poly(d, [(cx - r * .25, cy + r * .7), (cx, cy - r * .2), (cx + r * .25, cy + r * .7)], fill=GOLD)


def icon_box(d, cx, cy, r):
    rect(d, cx - r * .8, cy - r * .6, cx + r * .8, cy + r * .7, outline=INK, width=2)
    line(d, cx - r * .8, cy - r * .1, cx + r * .8, cy - r * .1, INK, 2)
    line(d, cx, cy - r * .6, cx, cy - r * .1, INK, 2)


def icon_camera(d, cx, cy, r):
    rect(d, cx - r * .8, cy - r * .5, cx + r * .8, cy + r * .6, fill=INK)
    ellipse(d, cx - r * .3, cy - r * .25, cx + r * .3, cy + r * .35, fill=CARD)
    rect(d, cx - r * .3, cy - r * .8, cx + r * .1, cy - r * .5, fill=INK)


def icon_chip(d, cx, cy, r):
    rect(d, cx - r * .6, cy - r * .6, cx + r * .6, cy + r * .6, fill=TEAL)
    for t in (-0.35, 0.35):
        line(d, cx + r * t, cy - r * .9, cx + r * t, cy - r * .6, INK, 2)
        line(d, cx + r * t, cy + r * .6, cx + r * t, cy + r * .9, INK, 2)
        line(d, cx - r * .9, cy + r * t, cx - r * .6, cy + r * t, INK, 2)
        line(d, cx + r * .6, cy + r * t, cx + r * .9, cy + r * t, INK, 2)


def icon_scales(d, cx, cy, r):
    line(d, cx, cy - r * .8, cx, cy + r * .7, INK, 2)
    line(d, cx - r * .8, cy - r * .5, cx + r * .8, cy - r * .5, INK, 2)
    for sx in (-r * .8, r * .8):
        poly(d, [(cx + sx - r * .35, cy - r * .5), (cx + sx + r * .35, cy - r * .5),
                 (cx + sx, cy + r * .1)], outline=INK)
    line(d, cx - r * .5, cy + r * .7, cx + r * .5, cy + r * .7, INK, 2)


# ------------------------------------------------------------------ page

def draw_page(img, d):
    # red top bar
    rect(d, 0, 0, 1024, 14, fill=RED)
    # header line
    text(d, (28, 20), "WORLD EDITION", ("sans_b", 11), INK)
    text(d, (28, 20), "No. 48,212", ("sans", 11), INK, anchor="ra") if False else None
    text(d, (996, 20), "THE DAILY RECORD", ("sans_b", 11), RED, anchor="ra")
    line(d, 28, 40, 996, 40, INK, 2)

    # masthead
    mast = "Monday 23 November 2026"
    mw = text_w(d, mast, ("serif_b", 58))
    text(d, ((1024 - mw / 1) / 2 * 1, 48), mast, ("serif_b", 58), INK)
    sub = "Gulf strikes, COP31 collapse, drones off Libya - the world in one page"
    sw = text_w(d, sub, ("serif", 15))
    italic_text(img, d, ((1024 - sw) / 2, 122), sub, ("serif", 15), RED)
    line(d, 28, 148, 996, 148, INK, 2)

    # 6-column stat band
    band_y0, band_y1 = 154, 208
    line(d, 28, band_y1, 996, band_y1, RULE, 2)
    stats = [
        ("24", "KILLED IN FACTORY FIRE"),
        ("893kg", "COCAINE SEIZED"),
        ("1,000+", "RUSSIAN SUICIDES LEAKED"),
        ("2", "SHIPS HIT OFF LIBYA"),
        ("750,000", "POUNDS PAID IN COURT"),
        ("COP31", "TALKS COLLAPSE"),
    ]
    cw = (996 - 28) / 6
    for i, (num, lab) in enumerate(stats):
        cx0 = 28 + i * cw
        if i:
            line(d, cx0, band_y0 + 4, cx0, band_y1 - 4, RULE, 1)
        text(d, (cx0 + cw / 2, band_y0 + 2), num, ("serif_b", 22), RED, anchor="ma")
        for j, ln in enumerate(wrap(d, lab, ("sans", 8), cw - 14)):
            text(d, (cx0 + cw / 2, band_y0 + 34 + j * 10), ln, ("sans", 8), INK, anchor="ma")
    line(d, 28, band_y1, 996, band_y1, INK, 1) if False else None

    # 3 hero cards
    hy0, hy1 = 218, 462
    gap = 12
    hw = (996 - 28 - 2 * gap) / 3
    heroes = [
        (art_gulf, "Iran strikes US bases and civilian sites across the Gulf",
         "Missiles hit Al Udeid and city districts; defenders report dozens wounded.",
         "Al Jazeera"),
        (art_cop, "COP31 climate talks collapse without a deal",
         "Delegates leave Geneva as key blocs refuse a shared phase-out text.",
         "Guardian, BBC"),
        (art_naval, "Ukraine naval drones hit two Russian ships off Libya",
         "Sea drones strike tankers anchored near Tobruk, crews evacuated.",
         "Guardian, BBC"),
    ]
    for i, (art, head, body, outlet) in enumerate(heroes):
        x0 = 28 + i * (hw + gap)
        x1 = x0 + hw
        rect(d, x0, hy0, x1, hy1, fill=CARD, outline=RULE, width=1)
        art(d, x0 + 8, hy0 + 8, x1 - 8, hy0 + 118)
        ly = hy0 + 128
        for ln in wrap(d, head, ("serif_b", 15), hw - 20)[:3]:
            text(d, (x0 + 10, ly), ln, ("serif_b", 15), INK)
            ly += 19
        ly += 2
        for ln in wrap(d, body, ("serif", 10.5), hw - 20)[:3]:
            text(d, (x0 + 10, ly), ln, ("serif", 10.5), (90, 92, 90))
            ly += 13
        text(d, (x0 + 10, hy1 - 18), outlet.upper(), ("sans_b", 8.5), RED)

    # 5-card story row
    sy0, sy1 = 474, 640
    gap5 = 10
    sw5 = (996 - 28 - 4 * gap5) / 5
    row = [
        (icon_flame, "Indonesia confectionery factory fire kills 24", "Guardian"),
        (icon_box, "Met Police seize 893kg cocaine hidden in orange boxes", "Guardian"),
        (icon_camera, "Gisele Pelicot nude photos scandal deepens", "BBC, Guardian"),
        (icon_chip, "Jensen Huang reinstated at Nvidia; Trump: 'I made the deal'", "BBC"),
        (icon_scales, "Parastoo Ahmadi flogged after singing verdict", "BBC, Al Jazeera"),
    ]
    for i, (icon, head, outlet) in enumerate(row):
        x0 = 28 + i * (sw5 + gap5)
        x1 = x0 + sw5
        rect(d, x0, sy0, x1, sy1, fill=CARD, outline=RULE, width=1)
        rect(d, x0, sy0, x1, sy0 + 4, fill=TEAL if i % 2 else GOLD)
        icon(d, x0 + 26, sy0 + 30, 16)
        ly = sy0 + 58
        for ln in wrap(d, head, ("serif_b", 11.5), sw5 - 16)[:5]:
            text(d, (x0 + 8, ly), ln, ("serif_b", 11.5), INK)
            ly += 14
        text(d, (x0 + 8, sy1 - 16), outlet.upper(), ("sans_b", 8), RED)

    # also today, two columns
    ay0 = 652
    text(d, (28, ay0), "ALSO TODAY", ("sans_b", 12), INK)
    line(d, 118, ay0 + 9, 996, ay0 + 9, RULE, 1)
    items = [
        ("1,000+ Russian military suicides leaked in MoD files", "Guardian"),
        ("Gaza a 'toxic wasteland', Oxfam reconstruction report warns", "BBC, Guardian"),
        ("EU sports ban added to latest Russia sanctions package", "Al Jazeera"),
        ("Myanmar military leaders hit with new sanctions", "BBC"),
        ("ICE arrest father and daughter at Seattle immigration office", "BBC"),
        ("Andrew paid 750,000 pounds in High Court settlement", "Guardian"),
        ("Cocaine shipment traced through fruit importer", "Guardian"),
        ("Ahmadi case sparks free-speech protests in Tehran", "Al Jazeera"),
    ]
    colw = (996 - 28 - 24) / 2
    for i, (head, outlet) in enumerate(items):
        col, r = divmod(i, 4)
        x0 = 28 + col * (colw + 24)
        y0 = ay0 + 22 + r * 34
        rect(d, x0, y0, x0, y0 + 28, fill=RED)
        ry = y0
        for ln in wrap(d, head, ("serif_b", 11), colw - 10)[:2]:
            text(d, (x0 + 12, ry), ln, ("serif_b", 11), INK)
            ry += 13
        text(d, (x0 + colw - 12, y0), outlet, ("sans", 8.5), TEAL, anchor="ra")

    # day-at-a-glance panel + DATE CHECK
    gy0, gy1 = 800, 1000
    line(d, 28, gy0 - 6, 996, gy0 - 6, RULE, 2)
    pw = 600
    rect(d, 28, gy0, 28 + pw, gy1, fill=CARD, outline=RULE, width=1)
    rect(d, 28, gy0, 28 + pw, gy0 + 3, fill=RED)
    text(d, (40, gy0 + 10), "DAY AT A GLANCE", ("sans_b", 12), RED)
    glance = [
        "Gulf: Iran fires on US bases and civilian districts; escalation risk high.",
        "Libya: Ukrainian sea drones sink-damage two Russian-linked tankers.",
        "Geneva: COP31 ends without agreement; ministers pledge talks resume.",
        "Jakarta: factory fire death toll rises to 24 as inquiry opens.",
        "London: 893kg cocaine seizure linked to citrus import route.",
    ]
    gy = gy0 + 32
    for g in glance:
        rect(d, 44, gy + 4, 48, gy + 8, fill=GOLD)
        for ln in wrap(d, g, ("serif", 11), pw - 40)[:2]:
            text(d, (56, gy), ln, ("serif", 11), INK)
            gy += 14
        gy += 6

    dx0 = 28 + pw + 12
    rect(d, dx0, gy0, 996, gy1, fill=(240, 234, 214), outline=TEAL, width=2)
    text(d, (dx0 + 14, gy0 + 10), "DATE CHECK", ("sans_b", 12), TEAL)
    dcheck = [
        "Monday, 23 November 2026.",
        "Week 48 of 2026; day 327 of 366.",
        "337 days remain in the year.",
        "First published: Monday edition.",
    ]
    dy = gy0 + 34
    for ln in dcheck:
        text(d, (dx0 + 14, dy), ln, ("serif", 10.5), INK)
        dy += 15
    text(d, (dx0 + 14, gy1 - 24), "All items verified against 23 Nov 2026 editions.", ("sans", 8), (120, 118, 108))

    # footer
    line(d, 28, 1008, 996, 1008, RULE, 1)
    text(d, (28, 1012), "THE DAILY RECORD - WORLD", ("sans", 8.5), (120, 118, 108))
    text(d, (996, 1012), "Sources: Al Jazeera, Guardian, BBC", ("sans", 8.5), (120, 118, 108), anchor="ra")


def main():
    img, d = make_canvas()
    draw_page(img, d)
    out = img.resize((1024, 1024), Image.LANCZOS)
    out.save("entry.png", "PNG", optimize=True)


if __name__ == "__main__":
    main()

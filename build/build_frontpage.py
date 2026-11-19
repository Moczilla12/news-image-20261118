#!/usr/bin/env python3
"""Render the make.fun news-image-20261118 front page (1024x1024 JPEG), v2.

Newspaper front page for Wednesday 18 November 2026: 43 verified stories.
Three large leads with rich AI illustrations (APEC Shenzhen, Iran drones
in the Gulf, Peltola's Alaska win), ten medium stories in two rows of five
(all ten with AI illustrations), a region bar counting all 43 stories, a
world map with story dots, a day-in-numbers strip, and 30 briefs.
All facts verified against reporting dated 18 Nov 2026; nothing invented.
Output is deterministic.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

REPO = "/home/hatch/workspace/makefun/news-image-20261118"
OUT_JPG = REPO + "/front-page.jpg"
GEO = "/tmp/countries.geo.json"
ASSETS = REPO + "/assets"

W, H = 1024, 1024
PAPER = (247, 242, 230)
INK = (24, 24, 24)
RED = (176, 32, 28)
BLUE = (28, 74, 116)
GREEN = (44, 120, 68)
ORANGE = (214, 110, 24)
BROWN = (146, 106, 38)
TEAL = (0, 122, 122)
GREY = (104, 104, 104)
WORLD = (110, 90, 160)
SEA = (206, 226, 235)
LAND = (233, 221, 193)
COAST = (182, 164, 120)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_KICK = font("DejaVuSans-Bold.ttf", 12)
F_DATE = font("DejaVuSerif-Bold.ttf", 48)
F_TAG = font("DejaVuSans.ttf", 11)
F_REG = font("DejaVuSans-Bold.ttf", 9)
F_LEAD_KICK = font("DejaVuSans-Bold.ttf", 11)
F_LEAD_HEAD = font("DejaVuSerif-Bold.ttf", 17)
F_LEAD_FACT = font("DejaVuSans.ttf", 11)
F_MED_KICK = font("DejaVuSans-Bold.ttf", 9)
F_MED_HEAD = font("DejaVuSerif-Bold.ttf", 12)
F_MED_FACT = font("DejaVuSans.ttf", 10)
F_SEC = font("DejaVuSans-Bold.ttf", 13)
F_BRIEF = font("DejaVuSans.ttf", 9)
F_FOOT = font("DejaVuSans.ttf", 9)
F_MAP_LAB = font("DejaVuSans-Bold.ttf", 9)
F_NUM = font("DejaVuSans-Bold.ttf", 16)
F_NUM_LAB = font("DejaVuSans.ttf", 8)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def wrap(text, f, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, lines, f, fill=INK, leading=None):
    """Draw lines top-down; returns the y just below the last line."""
    if leading is None:
        leading = int(f.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def num_badge(cx, cy, r, n, fill=RED):
    """Numbered circle badge."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    s = str(n)
    f = font("DejaVuSans-Bold.ttf", max(8, int(r * 1.05)))
    tw = d.textlength(s, font=f)
    d.text((cx - tw / 2, cy - f.size / 2 - 1), s, font=f, fill=(255, 255, 255))


def hline(x0, x1, y, width=1, fill=INK):
    d.rectangle([x0, y, x1, y + width - 1], fill=fill)


def load_ai(fname, w, h, focus=0.5):
    """Load an AI illustration, crop to the w:h aspect (focus 0=top, 1=bottom),
    and resize. PIL reads WEBP fine."""
    im = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
    iw, ih = im.size
    target = w / h
    src = iw / ih
    if src > target:
        nw = int(ih * target)
        x0 = (iw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / target)
        y0 = int((ih - nh) * focus)
        im = im.crop((0, y0, iw, y0 + nh))
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- header
d.text((28, 8), "THE WORLD'S NEWS IN ONE PICTURE", font=F_KICK, fill=RED)
right = "43 STORIES  ·  6 CONTINENTS  ·  13 ILLUSTRATED  ·  ALL FROM WEDNESDAY"
d.text((W - 28 - d.textlength(right, font=F_KICK), 8), right, font=F_KICK, fill=INK)
d.text((28, 26), "Wednesday 18 November 2026", font=F_DATE, fill=INK)
d.text((28, 80), "The day in one image — every story happened on 18 November 2026",
       font=F_TAG, fill=GREY)
hline(28, W - 28, 96, 2)
hline(28, W - 28, 100, 1)

# ---------------------------------------------------------------- region bar
# Story counts per region, counted from the 43 stories below:
# Americas 9, Africa 8, Asia 7, Europe 6, Middle East 6, World 6, Oceania 1.
REGIONS = [
    ("Americas", 9, RED),
    ("Africa", 8, BROWN),
    ("Asia", 7, GREEN),
    ("Europe", 6, BLUE),
    ("Mideast", 6, ORANGE),
    ("World", 6, WORLD),
    ("Oceania", 1, TEAL),
]
assert sum(c for _, c, _ in REGIONS) == 43, "region counts must sum to 43"
BAR_X0, BAR_X1, BAR_Y, BAR_H = 28, W - 28, 106, 18
bar_w = BAR_X1 - BAR_X0
x = BAR_X0
for name, count, col in REGIONS:
    seg = int(round(bar_w * count / 43))
    if x + seg > BAR_X1:
        seg = BAR_X1 - x
    d.rectangle([x, BAR_Y, x + seg - 1, BAR_Y + BAR_H - 1], fill=col)
    label = f"{name} {count}"
    tw = d.textlength(label, font=F_REG)
    if tw <= seg - 6:
        d.text((x + (seg - tw) / 2, BAR_Y + 4), label, font=F_REG,
               fill=(255, 255, 255))
    x += seg

# ---------------------------------------------------------------- top row: 3 large leads
LEADS = [
    dict(n=1, kick="ASIA  ·  APEC SUMMIT", col=BLUE,
         fname="media-generation-apec-xi-trump-v2-0-0d5b684b-a01a-465d-a490-179d9b9133d8.webp",
         focus=0.4,
         head="Xi greets Trump at APEC; trio summit set",
         fact="Xi met Trump at Air Force One in Shenzhen; first Trump–Xi–Putin "
              "talks set for Thursday."),
    dict(n=2, kick="MIDDLE EAST  ·  IRAN WAR", col=RED,
         fname="media-generation-iran-drones-gulf-0-f98decaa-7bee-486e-a82b-32b9034af108.webp",
         focus=0.5,
         head="Iran drones strike US base in Kuwait",
         fact="Drones hit Ali Al Salem base and Bahrain; retaliation for the US "
              "strike on Qeshm Island."),
    dict(n=3, kick="US  ·  SENATE", col=GREEN,
         fname="media-generation-peltola-alaska-0-5c509f6c-1324-44dc-9c54-f336329b80b6.webp",
         focus=0.5,
         head="Peltola wins Alaska; Democrats take Senate",
         fact="Peltola 50.1% beats Sullivan 45.8%; Democrats lead 56–44, their "
              "ninth midterm flip."),
]
LEAD_W = 312
LEAD_Y = 132
LEAD_IMG_H = 140
for i, s in enumerate(LEADS):
    x = 28 + i * (LEAD_W + 8)
    y = LEAD_Y
    im_ai = load_ai(s["fname"], LEAD_W, LEAD_IMG_H, focus=s["focus"])
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + LEAD_W - 1, y + LEAD_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 13, y + 13, 10, s["n"], fill=s["col"])
    ky = y + LEAD_IMG_H + 8
    d.text((x, ky), s["kick"], font=F_LEAD_KICK, fill=s["col"])
    hy = ky + 16
    hl = wrap(s["head"], F_LEAD_HEAD, LEAD_W)
    hy = text_block(x, hy, hl[:2], F_LEAD_HEAD, leading=20)
    fl = wrap(s["fact"], F_LEAD_FACT, LEAD_W)
    text_block(x, hy + 3, fl[:3], F_LEAD_FACT, fill=(70, 70, 70), leading=14)
hline(28, W - 28, 388, 1)

# ---------------------------------------------------------------- rows: 10 medium stories (2 rows x 5)
MEDS = [
    dict(n=4, kick="EUROPE  ·  UKRAINE", col=BLUE, ai="kerch",
         head="Kerch Bridge span in the sea",
         fact="227 m road arch fell after two nights of strikes."),
    dict(n=5, kick="OCEANIA  ·  STORM", col=TEAL, ai="cyclone",
         head="Cyclone Xavier batters Cooks",
         fact="Cat 5, 220 km/h winds; a November record."),
    dict(n=6, kick="AFRICA  ·  HEALTH", col=GREEN, ai="ebola",
         head="Ebola passes 11,000 cases",
         fact="11,376 cases, 5,568 deaths in DR Congo."),
    dict(n=7, kick="US  ·  BUSINESS", col=BROWN, ai="nvidia",
         head="Nvidia sales double to $115.8bn",
         fact="Revenue up 103%; board will not reinstate Huang."),
    dict(n=8, kick="ISRAEL  ·  POLITICS", col=ORANGE, ai="knesset",
         head="Kahana wins Knesset 66–52",
         fact="66–52 speaker vote; a blow to Netanyahu."),
    dict(n=9, kick="MIDDLE EAST  ·  GAZA", col=RED, ai="gaza",
         head="Board faults Israel and Hamas",
         fact="Peace board says truce at risk; 1.4m face acute hunger."),
    dict(n=10, kick="WORLD  ·  SPACE", col=WORLD, ai="voyager",
         head="Voyager 1 reaches one light-day from Earth",
         fact="25.9bn km at 10:16 UTC — first object that far; signal takes 24h."),
    dict(n=11, kick="EUROPE  ·  UKRAINE WAR", col=BLUE, ai="russia-drones",
         head="Russia fires 141 drones at Ukraine; 126 downed",
         fact="Hits at seven sites; 4 killed in Donetsk, 5 dead, 15 hurt."),
    dict(n=12, kick="ASIA  ·  LABOUR", col=GREEN, ai="bangladesh",
         head="Bangladesh wage protests shut ~535 factories",
         fact="~300 arrested; 20,000 workers blocked the Dhaka–Aricha highway."),
    dict(n=13, kick="EUROPE  ·  ECONOMY", col=BLUE, ai="uk-inflation",
         head="UK inflation climbs to 3.6%, a one-year high",
         fact="CPI up from 3.5% in September; motor fuel +33.2% year on year."),
]

# AI illustrations for medium stories: filename + vertical focus (0=top, 1=bottom).
AI_MED = {
    "kerch": ("media-generation-kerch-bridge-0-e9538b4f-a59d-427e-b527-9cd05c40ae09.webp", 0.5),
    "cyclone": ("media-generation-cyclone-xavier-0-a6ce5951-5950-47a3-9da3-be3ab44c1a01.webp", 0.4),
    "ebola": ("media-generation-ebola-congo-0-799a6ff4-2c95-407a-9ef4-633d8572dbc5.webp", 0.5),
    "nvidia": ("media-generation-nvidia-chip-0-2642ac14-7763-4ec7-986a-fa57b459742c.webp", 0.75),
    "knesset": ("media-generation-knesset-gaza-0-08787f5a-8976-4c31-b177-139bde160522.webp", 0.3),
    "gaza": ("media-generation-gaza-aid-0-a34c1b88-3103-4328-91de-e1e83174d033.webp", 0.5),
    "voyager": ("media-generation-voyager-1-0-49edb854-a1ba-4b0e-b0fa-05f321a6e184.webp", 0.5),
    "russia-drones": ("media-generation-russia-drones-0-cca0fce2-b38a-4e28-9131-cc74fc34234c.webp", 0.5),
    "bangladesh": ("media-generation-bangladesh-garment-0-67c0545f-ea96-43ed-b5c0-cd161c456cfc.webp", 0.5),
    "uk-inflation": ("media-generation-uk-inflation-0-b7724f1a-9818-4d4d-99ef-f49ac6d35848.webp", 0.5),
}

MED_W = 187
MED_IMG_H = 70
MED_Y1 = 396
ROW_H = 150
for i, s in enumerate(MEDS):
    row = i // 5
    col = i % 5
    x = 28 + col * (MED_W + 8)
    y = MED_Y1 + row * ROW_H
    fname, focus = AI_MED[s["ai"]]
    im_ai = load_ai(fname, MED_W, MED_IMG_H, focus=focus)
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + MED_W - 1, y + MED_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 11, y + 11, 9, s["n"], fill=s["col"])
    ky = y + MED_IMG_H + 6
    d.text((x, ky), s["kick"], font=F_MED_KICK, fill=s["col"])
    hy = ky + 13
    hl = wrap(s["head"], F_MED_HEAD, MED_W)
    hy = text_block(x, hy, hl[:2], F_MED_HEAD, leading=15)
    fl = wrap(s["fact"], F_MED_FACT, MED_W)
    text_block(x, hy + 1, fl[:2], F_MED_FACT, fill=(70, 70, 70), leading=12)
hline(28, W - 28, 696, 1)

# ---------------------------------------------------------------- bottom: map + numbers + briefs
d.text((28, 704), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
d.text((524, 704), "ALSO ON 18 NOVEMBER", font=F_SEC, fill=INK)
MAP = (28, 722, 498, 882)
d.rectangle(MAP, fill=SEA, outline=(170, 180, 170))

geo = json.load(open(GEO))


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    lat = max(-60.0, min(85.0, lat))
    lon = max(-180.0, min(180.0, lon))
    fx = (lon + 180.0) / 360.0
    fy = (85.0 - lat) / 145.0
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))


def draw_poly(coords, box):
    pts = [project(lon, lat, box) for lon, lat in coords]
    if len(pts) >= 3:
        d.polygon(pts, fill=LAND, outline=COAST)


for feat in geo["features"]:
    if feat.get("id") == "ATA":
        continue
    g = feat["geometry"]
    if g["type"] == "Polygon":
        for ring in g["coordinates"]:
            draw_poly(ring, MAP)
    elif g["type"] == "MultiPolygon":
        for poly in g["coordinates"]:
            for ring in poly:
                draw_poly(ring, MAP)

REG = {"americas": RED, "europe": BLUE, "mideast": ORANGE,
       "asia": GREEN, "africa": BROWN, "oceania": TEAL, "world": WORLD}
NUMBERED = [
    (1, 113.8, 22.5, "asia"), (2, 47.5, 29.3, "mideast"),
    (3, -150.0, 64.0, "americas"), (4, 36.5, 45.3, "europe"),
    (5, -162.0, -13.0, "oceania"), (6, 23.0, -3.0, "africa"),
    (7, -122.0, 37.4, "americas"), (8, 35.2, 31.8, "mideast"),
    (9, 34.5, 31.5, "mideast"), (10, -120.0, -40.0, "world"),
    (11, 31.0, 49.0, "europe"), (12, 90.4, 23.8, "asia"),
    (13, -0.1, 51.5, "europe"),
]
OFFSETS = {2: (26, 6), 8: (-8, 14), 9: (14, 22), 1: (14, 10),
           3: (14, -12), 7: (-14, 10), 4: (24, -8), 11: (-24, 10),
           12: (-14, 12), 13: (-24, -16)}
for n, lon, lat, reg in NUMBERED:
    x, y = project(lon, lat, MAP)
    dx, dy = OFFSETS.get(n, (0, 0))
    if dx or dy:
        d.line([x, y, x + dx, y + dy], fill=(90, 90, 90), width=1)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=REG[reg])
        x, y = x + dx, y + dy
    num_badge(x, y, 8, n, fill=REG[reg])
BRIEF_DOTS = [
    (-97.0, 38.0, "americas"), (80.5, 15.5, "asia"),
    (4.35, 50.85, "europe"), (44.2, 15.35, "mideast"), (45.0, 24.0, "mideast"),
    (-122.4, 37.8, "americas"), (8.5, 47.4, "europe"), (36.8, -1.3, "africa"),
    (32.5, 15.6, "africa"), (39.0, 14.5, "africa"), (3.4, 6.5, "africa"),
    (12.0, 36.0, "europe"), (4.3, 52.1, "europe"), (96.2, 19.7, "asia"),
    (116.4, 39.9, "asia"), (121.0, 14.6, "asia"), (30.5, 50.4, "europe"),
    (-0.1, 51.5, "europe"), (56.5, 26.8, "mideast"), (-77.0, 38.9, "americas"),
    (-74.0, 40.7, "americas"), (34.8, 31.3, "mideast"), (4.7, 50.6, "europe"),
    (28.0, -26.2, "africa"), (-23.5, 15.1, "africa"), (31.6, 4.85, "africa"),
    (-46.6, -23.5, "americas"), (-52.0, -10.0, "americas"),
    (-121.0, 37.0, "americas"), (-76.0, 39.0, "americas"),
]
for lon, lat, reg in BRIEF_DOTS:
    x, y = project(lon, lat, MAP)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=REG[reg], outline=(255, 255, 255))

d.text((28, 886), "Numbers 1–13 are the big stories; dots are the briefs.",
       font=F_TAG, fill=GREY)

# day in numbers (left column, under the map)
d.text((28, 902), "THE DAY IN NUMBERS", font=F_SEC, fill=INK)
STATS = [
    ("56–44", "Democrats' Senate majority", RED),
    ("220 km/h", "Cyclone Xavier's top winds", TEAL),
    ("11,376", "Ebola cases in DR Congo", GREEN),
    ("$115.8bn", "Nvidia's quarterly sales", BROWN),
]
for i, (num, lab, col) in enumerate(STATS):
    x = 28 + i * (113 + 6)
    y = 918
    d.rectangle([x, y, x + 113, y + 70], fill=(238, 234, 222),
                outline=(200, 192, 170))
    d.rectangle([x, y, x + 113, y + 3], fill=col)
    nw = d.textlength(num, font=F_NUM)
    d.text((x + (113 - nw) / 2, y + 10), num, font=F_NUM, fill=col)
    ll = wrap(lab, F_NUM_LAB, 100)
    text_block(x + 7, y + 34, ll[:2], F_NUM_LAB, fill=(70, 70, 70), leading=11)

# briefs list (right side, two columns of 15; numbers 14–43)
BRIEFS = [
    (14, "US loses measles-free status"),
    (15, "Cyclone Akvan nears Andhra coast"),
    (16, "Eurozone inflation hits 4.0%"),
    (17, "Saudi coalition hits 60 Houthi targets"),
    (18, "Houthis claim drones hit Saudi pipeline"),
    (19, "OpenAI launches GPT-6.2 Astra and Sol"),
    (20, "FIFA rankings: Spain stays No. 1"),
    (21, "Six teams book AFCON 2027 spots"),
    (22, "UN counts 2,230 Sudan civilian deaths"),
    (23, "Ethiopia, Eritrea mass troops"),
    (24, "Nigeria busts Europe-bound cocaine gang"),
    (25, "2,500 dead or missing on sea routes"),
    (26, "World Court to rule on Myanmar case"),
    (27, "Myanmar junta to review ASEAN ties"),
    (28, "South Korea's Lee courts Beijing"),
    (29, "Trump meets Marcos in Manila"),
    (30, "Putin 'not ready' for Ukraine talks"),
    (31, "US officer held over alleged spying"),
    (32, "Oil falls on US stock build"),
    (33, "Fed minutes hawkish; December hike likely"),
    (34, "US housing starts up 9.9%"),
    (35, "Gaza winter floods tents; 1.4m hungry"),
    (36, "NATO unveils new comms strategy"),
    (37, "SA mercenary accused in court"),
    (38, "Cabo Verde vote peaceful, ECOWAS says"),
    (39, "Machar testifies; South Sudan votes 22 Dec"),
    (40, "Latin America steel imports up 47%"),
    (41, "Brazil wind slows; Mexico plans 6.9 GW"),
    (42, "OpenAI models found Nginx code flaws"),
    (43, "Trump takes dirty-bomb report seriously"),
]
for i, (n, txt) in enumerate(BRIEFS):
    col = i // 15
    row = i % 15
    x = 524 + col * 236
    y = 722 + row * 17
    num_badge(x + 7, y + 6, 7, n, fill=GREEN)
    d.text((x + 19, y), txt, font=F_BRIEF, fill=INK)

# ---------------------------------------------------------------- footer
hline(28, W - 28, 992, 1)
d.text((28, 998), "Every story here happened or was first reported on Wednesday 18 November 2026. "
                  "Contested claims are marked as claims.", font=F_FOOT, fill=GREY)
src = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings."
d.text((W - 28 - d.textlength(src, font=F_FOOT), 998), src, font=F_FOOT, fill=GREY)

img.save(OUT_JPG, "JPEG", quality=88)
print("saved", OUT_JPG)
print("bytes:", os.path.getsize(OUT_JPG))
print("size:", img.size)

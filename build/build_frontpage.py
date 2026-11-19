#!/usr/bin/env python3
"""Render the make.fun news-image-20261118 front page (1024x1024 JPEG), v3.

Newspaper front page for Wednesday 18 November 2026: 44 verified stories.
Four large leads with AI illustrations (APEC Shenzhen, Iran drones in the
Gulf, EU EUR45bn Ukraine loan, Voyager 1), twelve medium stories in two
rows of six (all with AI illustrations), a region bar, a BY FIELD bar, a
numbers strip at the TOP, a THE DAY IN UTC timeline strip, a world map with
story pins (Voyager marked off-map: DEEP SPACE), a DATE CHECK strip listing
stories deliberately excluded as 17 Nov or not yet happened, confidence tags
(CONFIRMED / CLAIM / SOURCES / FORECAST) as chips on every big story, and
28 briefs. All facts verified against reporting dated 18 Nov 2026; the five
17 Nov big stories from v2 (Peltola, Kerch, Nvidia, Knesset, Board of Peace)
are in DATE CHECK, not on the page. Nothing invented. Output is
deterministic.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

REPO = "/home/hatch/workspace/makefun/news-image-20261118"
OUT_JPG = REPO + "/front-page.jpg"
GEO = "/tmp/countries.geo.json"
if not os.path.isfile(GEO):
    GEO = "/home/hatch/workspace/makefun/countries.geo.json"
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
STEEL = (30, 120, 180)
PLUM = (150, 60, 120)
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
F_FIELD = font("DejaVuSans-Bold.ttf", 8)
F_LEAD_KICK = font("DejaVuSans-Bold.ttf", 11)
F_LEAD_HEAD = font("DejaVuSerif-Bold.ttf", 17)
F_LEAD_FACT = font("DejaVuSans.ttf", 11)
F_MED_KICK = font("DejaVuSans-Bold.ttf", 9)
F_MED_HEAD = font("DejaVuSerif-Bold.ttf", 12)
F_MED_FACT = font("DejaVuSans.ttf", 10)
F_SEC = font("DejaVuSans-Bold.ttf", 13)
F_BRIEF = font("DejaVuSans.ttf", 9)
F_FOOT = font("DejaVuSans.ttf", 9)
F_NUM = font("DejaVuSans-Bold.ttf", 16)
F_NUM_LAB = font("DejaVuSans.ttf", 8)
F_TIME = font("DejaVuSans.ttf", 9)
F_TIME_B = font("DejaVuSans-Bold.ttf", 9)
F_TAGCHIP = font("DejaVuSans-Bold.ttf", 7)
F_DC = font("DejaVuSans.ttf", 9)
F_DC_B = font("DejaVuSans-Bold.ttf", 9)

TAG_COLORS = {
    "CONFIRMED": GREEN,
    "CLAIM": ORANGE,
    "SOURCES": BLUE,
    "FORECAST": WORLD,
}

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


def tag_chip(x1, y, tag):
    """Confidence tag chip at the top-right corner of an image (right edge x1)."""
    col = TAG_COLORS[tag]
    tw = d.textlength(tag, font=F_TAGCHIP)
    w = int(tw) + 8
    h = 12
    d.rectangle([x1 - w, y, x1 - 1, y + h - 1], fill=col)
    d.text((x1 - w + 4, y + 1), tag, font=F_TAGCHIP, fill=(255, 255, 255))


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
right = "44 STORIES  ·  7 REGIONS  ·  16 ILLUSTRATED  ·  ALL FROM WEDNESDAY"
d.text((W - 28 - d.textlength(right, font=F_KICK), 8), right, font=F_KICK, fill=INK)
d.text((28, 26), "Wednesday 18 November 2026", font=F_DATE, fill=INK)
d.text((28, 80), "The day in one image — every story happened on 18 November 2026",
       font=F_TAG, fill=GREY)
hline(28, W - 28, 96, 2)
hline(28, W - 28, 100, 1)

# ---------------------------------------------------------------- region bar
# Story counts per region, counted from the 44 stories below:
# Americas 11, Africa 9, Asia 6, Europe 7, Mideast 5, World 5, Oceania 1.
REGIONS = [
    ("Americas", 11, RED),
    ("Africa", 9, BROWN),
    ("Asia", 6, GREEN),
    ("Europe", 7, BLUE),
    ("Mideast", 5, ORANGE),
    ("World", 5, WORLD),
    ("Oceania", 1, TEAL),
]
assert sum(c for _, c, _ in REGIONS) == 44, "region counts must sum to 44"
BAR_X0, BAR_X1, BAR_Y, BAR_H = 28, W - 28, 106, 18
bar_w = BAR_X1 - BAR_X0
x = BAR_X0
for name, count, col in REGIONS:
    seg = int(round(bar_w * count / 44))
    if x + seg > BAR_X1:
        seg = BAR_X1 - x
    d.rectangle([x, BAR_Y, x + seg - 1, BAR_Y + BAR_H - 1], fill=col)
    label = f"{name} {count}"
    tw = d.textlength(label, font=F_REG)
    if tw <= seg - 6:
        d.text((x + (seg - tw) / 2, BAR_Y + 4), label, font=F_REG,
               fill=(255, 255, 255))
    x += seg

# ---------------------------------------------------------------- numbers strip (TOP)
STATS = [
    ("141", "drones fired at Ukraine", RED),
    ("126", "drones downed", BLUE),
    ("25.9bn km", "Voyager 1 from Earth", WORLD),
    ("251–11", "Jeffries Speaker vote", GREEN),
    ("$81.3bn", "Anthropic IPO value", BROWN),
    ("11,300+", "Ebola cases in DR Congo", TEAL),
]
NUM_Y = 130
NUM_H = 40
for i, (num, lab, col) in enumerate(STATS):
    x = 28 + i * (156 + 6)
    y = NUM_Y
    d.rectangle([x, y, x + 156, y + NUM_H], fill=(238, 234, 222),
                outline=(200, 192, 170))
    d.rectangle([x, y, x + 156, y + 3], fill=col)
    nw = d.textlength(num, font=F_NUM)
    d.text((x + (156 - nw) / 2, y + 8), num, font=F_NUM, fill=col)
    ll = wrap(lab, F_NUM_LAB, 144)
    text_block(x + 6, y + 26, ll[:1], F_NUM_LAB, fill=(70, 70, 70), leading=11)

# ---------------------------------------------------------------- THE DAY IN UTC timeline
d.text((28, 178), "THE DAY IN UTC", font=F_TIME_B, fill=RED)
timeline = ("Overnight: Gulf drones · 07:00 UK CPI 3.6% · Morning: Xi greets Trump · "
            "10:16 Voyager 1 · 11:00 GTA VI unlocks NZ · 19:00 Fed minutes · "
            "21:00 Dow −561 · Late: Anthropic IPO")
tw = d.textlength(timeline, font=F_TIME)
d.text((28 + d.textlength("THE DAY IN UTC  ", font=F_TIME_B), 178), timeline,
       font=F_TIME, fill=INK)
hline(28, W - 28, 200, 1)

# ---------------------------------------------------------------- top row: 4 large leads
LEADS = [
    dict(n=1, kick="ASIA  ·  APEC SUMMIT", col=BLUE, tag="CONFIRMED",
         fname="media-generation-apec-xi-trump-v2-0-0d5b684b-a01a-465d-a490-179d9b9133d8.webp",
         focus=0.4,
         head="Xi greets Trump at APEC; trio summit set",
         fact="Xi met Trump at Air Force One in Shenzhen; first Trump–Xi–Putin "
              "talks set for Thursday."),
    dict(n=2, kick="MIDDLE EAST  ·  IRAN WAR", col=RED, tag="CLAIM",
         fname="media-generation-iran-drones-gulf-0-f98decaa-7bee-486e-a82b-32b9034af108.webp",
         focus=0.5,
         head="Iran drones strike US base in Kuwait",
         fact="Drones hit Ali Al Salem base and Bahrain; retaliation for the US "
              "strike on Qeshm Island."),
    dict(n=3, kick="EUROPE  ·  UKRAINE", col=BLUE, tag="CONFIRMED",
         fname="media-generation-media-generation-eu-loan-v3-0-b5aaac03-b7cd-4bb9-ac28-076e1019e6aa.webp",
         focus=0.5,
         head="EU proposes €45bn loan to fund Ukraine",
         fact="€20bn budget + €25bn military; repaid only once Russia pays "
              "reparations."),
    dict(n=4, kick="WORLD  ·  SPACE", col=WORLD, tag="CONFIRMED",
         fname="media-generation-voyager-1-0-49edb854-a1ba-4b0e-b0fa-05f321a6e184.webp",
         focus=0.5,
         head="Voyager 1 reaches one light-day from Earth",
         fact="25.9bn km at 10:16 UTC — first object that far; signal takes 24h."),
]
LEAD_W = 236
LEAD_Y = 206
LEAD_IMG_H = 100
for i, s in enumerate(LEADS):
    x = 28 + i * (LEAD_W + 8)
    y = LEAD_Y
    im_ai = load_ai(s["fname"], LEAD_W, LEAD_IMG_H, focus=s["focus"])
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + LEAD_W - 1, y + LEAD_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 13, y + 13, 10, s["n"], fill=s["col"])
    tag_chip(x + LEAD_W, y, s["tag"])
    ky = y + LEAD_IMG_H + 6
    d.text((x, ky), s["kick"], font=F_LEAD_KICK, fill=s["col"])
    hy = ky + 16
    hl = wrap(s["head"], F_LEAD_HEAD, LEAD_W)
    hy = text_block(x, hy, hl[:2], F_LEAD_HEAD, leading=20)
    fl = wrap(s["fact"], F_LEAD_FACT, LEAD_W)
    text_block(x, hy + 3, fl[:3], F_LEAD_FACT, fill=(70, 70, 70), leading=14)
hline(28, W - 28, 408, 1)

# ---------------------------------------------------------------- rows: 12 medium stories (2 rows x 6)
MEDS = [
    dict(n=5, kick="EUROPE  ·  UKRAINE WAR", col=BLUE, tag="CONFIRMED",
         ai="russia-drones",
         head="Russia fires 141 drones at Ukraine; 126 downed",
         fact="Hits at seven sites; 4 killed in Donetsk, 5 dead, 15 hurt."),
    dict(n=6, kick="US  ·  MARKETS", col=BROWN, tag="CONFIRMED",
         ai="fed",
         head="Fed minutes point to more hikes; Dow −561",
         fact="Almost all officials see hikes; Dow fell 561 to 50,198."),
    dict(n=7, kick="ASIA  ·  STORM", col=TEAL, tag="FORECAST",
         ai="akvan",
         head="Cyclone Akvan veers north toward Odisha",
         fact="Landfall ~noon Fri 20 Nov; ~50,000 moved to safety."),
    dict(n=8, kick="AFRICA  ·  SUDAN", col=BROWN, tag="SOURCES",
         ai="amnesty",
         head="Amnesty: RSF drones killed 37 in El Obeid",
         fact="9 RSF drone strikes Jun–Aug; 37 killed, 10 hurt."),
    dict(n=9, kick="US  ·  POLITICS", col=GREEN, tag="CONFIRMED",
         ai="jeffries",
         head="Jeffries wins Democrats' nod, 251–11",
         fact="Caucus vote 251–11; first Black Speaker if elected 3 Jan."),
    dict(n=10, kick="WORLD  ·  GAMES", col=WORLD, tag="CONFIRMED",
         ai="gta",
         head="GTA VI goes on sale after 13-year wait",
         fact="Midnight launch rolls west; NZ first at 11:00 UTC."),
    dict(n=11, kick="MIDDLE EAST  ·  GAZA", col=RED, tag="CONFIRMED",
         ai="gaza-tanks",
         head="Israeli tanks cross Yellow Line near Nuseirat",
         fact="First push since the truce; 3 killed, 5,200+ fled."),
    dict(n=12, kick="US  ·  BUSINESS", col=BROWN, tag="CONFIRMED",
         ai="anthropic",
         head="Anthropic prices record $81.3bn IPO at $83",
         fact="980m shares at $83; largest IPO ever; trading Thu 19."),
    dict(n=13, kick="EUROPE  ·  ECONOMY", col=BLUE, tag="CONFIRMED",
         ai="uk-inflation",
         head="UK inflation climbs to 3.6%, a one-year high",
         fact="CPI up from 3.5% in September; motor fuel +33.2% YoY."),
    dict(n=14, kick="WORLD  ·  CLIMATE", col=TEAL, tag="CONFIRMED",
         ai="cop31",
         head="COP31 still split over fossil-fuel phase-out",
         fact="Navarro: 'petroleum mafia' holds talks; 30 back a treaty."),
    dict(n=15, kick="AFRICA  ·  HEALTH", col=GREEN, tag="CONFIRMED",
         ai="ebola",
         head="Ebola passes 11,300 cases; emergency stays",
         fact="11,376 cases, 5,568 deaths; 400–500 new cases a week."),
    dict(n=16, kick="US  ·  CULTURE", col=ORANGE, tag="CONFIRMED",
         ai="van-gogh",
         head="Van Gogh sale sets artist record: $190.4m",
         fact="Sotheby's New York; artist record, prev $117.2m in 2022."),
]

# AI illustrations for medium stories: filename + vertical focus (0=top, 1=bottom).
AI_MED = {
    "russia-drones": ("media-generation-russia-drones-0-cca0fce2-b38a-4e28-9131-cc74fc34234c.webp", 0.5),
    "fed": ("media-generation-media-generation-fed-v3-0-17a22732-8023-4ebb-8fde-a22487939d06.webp", 0.5),
    "akvan": ("media-generation-media-generation-akvan-v3-0-9b35ac15-490f-40d2-bf0b-aa157af3786c.webp", 0.5),
    "amnesty": ("media-generation-media-generation-amnesty-sudan-0-c3b7da45-f6fb-48c4-b078-a3bcca9be11c.webp", 0.5),
    "jeffries": ("media-generation-media-generation-jeffries-v3-0-82f4ab4a-9a9a-4391-9ca1-628fbca1ae2c.webp", 0.5),
    "gta": ("media-generation-media-generation-gta-vi-v3-0-a607719d-7296-4916-ae6e-bc44496559c2.webp", 0.5),
    "gaza-tanks": ("media-generation-media-generation-gaza-tanks-v3-0-b4eac2de-476d-4cab-8f2b-37beaa46e74b.webp", 0.5),
    "anthropic": ("media-generation-media-generation-anthropic-ipo-0-e37fd67e-f933-4521-8cb4-ea841d1ddaf1.webp", 0.5),
    "uk-inflation": ("media-generation-uk-inflation-0-b7724f1a-9818-4d4d-99ef-f49ac6d35848.webp", 0.5),
    "cop31": ("media-generation-media-generation-cop31-v3-0-517c7fc4-6689-4673-ae04-e78e98dcdb7e.webp", 0.5),
    "ebola": ("media-generation-ebola-congo-0-799a6ff4-2c95-407a-9ef4-633d8572dbc5.webp", 0.5),
    "van-gogh": ("media-generation-media-generation-van-gogh-v3-0-7e2e9581-1efb-4eeb-ba23-39389a463fd7.webp", 0.5),
}

MED_W = 154
MED_IMG_H = 55
MED_Y1 = 416
ROW_H = 136
for i, s in enumerate(MEDS):
    row = i // 6
    col = i % 6
    x = 28 + col * (MED_W + 8)
    y = MED_Y1 + row * ROW_H
    fname, focus = AI_MED[s["ai"]]
    im_ai = load_ai(fname, MED_W, MED_IMG_H, focus=focus)
    img.paste(im_ai, (x, y))
    d.rectangle([x, y, x + MED_W - 1, y + MED_IMG_H - 1], outline=(150, 150, 150))
    num_badge(x + 11, y + 11, 9, s["n"], fill=s["col"])
    tag_chip(x + MED_W, y, s["tag"])
    ky = y + MED_IMG_H + 5
    d.text((x, ky), s["kick"], font=F_MED_KICK, fill=s["col"])
    hy = ky + 12
    hl = wrap(s["head"], F_MED_HEAD, MED_W)
    hy = text_block(x, hy, hl[:2], F_MED_HEAD, leading=14)
    fl = wrap(s["fact"], F_MED_FACT, MED_W)
    text_block(x, hy + 1, fl[:2], F_MED_FACT, fill=(70, 70, 70), leading=12)
hline(28, W - 28, 688, 1)

# ---------------------------------------------------------------- bottom: map + briefs
d.text((28, 696), "WHERE IT HAPPENED", font=F_SEC, fill=INK)
d.text((524, 696), "ALSO ON 18 NOVEMBER", font=F_SEC, fill=INK)
MAP = (28, 714, 470, 852)
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
# 4 (Voyager) is off-map: DEEP SPACE — no pin, noted in the caption below.
NUMBERED = [
    (1, 113.8, 22.5, "asia"), (2, 47.5, 29.3, "mideast"),
    (3, 4.35, 50.85, "europe"), (5, 30.5, 50.4, "europe"),
    (6, -77.0, 38.9, "americas"), (7, 85.0, 15.0, "asia"),
    (8, 30.2, 13.2, "africa"), (9, -77.0, 38.9, "americas"),
    (10, 172.6, -41.8, "oceania"), (11, 34.4, 31.4, "mideast"),
    (12, -74.0, 40.7, "americas"), (13, -0.1, 51.5, "europe"),
    (14, 30.7, 36.9, "world"), (15, 23.0, -3.0, "africa"),
    (16, -74.0, 40.7, "americas"),
]
OFFSETS = {2: (26, 6), 11: (14, 18), 1: (14, 10), 9: (18, 14),
           3: (-20, -10), 13: (-24, -14), 5: (20, -8), 7: (-14, 12),
           8: (16, 8), 10: (-24, -8), 14: (18, 10), 15: (14, 12),
           16: (-20, 12)}
for n, lon, lat, reg in NUMBERED:
    x, y = project(lon, lat, MAP)
    dx, dy = OFFSETS.get(n, (0, 0))
    if dx or dy:
        d.line([x, y, x + dx, y + dy], fill=(90, 90, 90), width=1)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=REG[reg])
        x, y = x + dx, y + dy
    num_badge(x, y, 8, n, fill=REG[reg])
BRIEF_DOTS = [
    (-97.0, 38.0, "americas"), (4.35, 50.85, "europe"),
    (44.2, 15.35, "mideast"), (46.7, 24.6, "mideast"),
    (8.5, 47.4, "europe"), (-17.4, 14.7, "africa"),
    (32.5, 15.6, "africa"), (39.0, 14.5, "africa"),
    (3.4, 6.5, "africa"), (12.0, 36.0, "europe"),
    (4.3, 52.1, "europe"), (96.2, 19.7, "asia"),
    (116.4, 39.9, "asia"), (121.0, 14.6, "asia"),
    (-162.0, -13.0, "oceania"), (37.6, 55.7, "europe"),
    (-0.1, 51.5, "europe"), (56.5, 26.8, "world"),
    (-90.0, 35.0, "americas"), (34.5, 31.5, "mideast"),
    (4.7, 50.6, "europe"), (28.0, -26.2, "africa"),
    (-23.5, 15.1, "africa"), (31.6, 4.85, "africa"),
    (-52.0, -10.0, "americas"), (-46.6, -23.5, "americas"),
    (-122.4, 37.8, "americas"), (-77.0, 38.9, "americas"),
]
for lon, lat, reg in BRIEF_DOTS:
    x, y = project(lon, lat, MAP)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=REG[reg], outline=(255, 255, 255))

d.text((28, 856), "Numbers 1–16 are the big stories; dots are the briefs.",
       font=F_TAG, fill=GREY)
d.text((28, 870), "4 · Voyager 1 is off this map — DEEP SPACE, 25.9bn km from Earth.",
       font=F_TAG, fill=GREY)

# briefs list (right side, two columns of 14; numbers 17–44)
BRIEFS = [
    (17, "US loses measles-free status"),
    (18, "Eurozone inflation hits 4.0%"),
    (19, "Saudi coalition hits 60 Houthi targets"),
    (20, "Houthis claim drones hit Saudi pipeline"),
    (21, "FIFA rankings: Spain stays No. 1"),
    (22, "Six teams book AFCON 2027 spots"),
    (23, "UN counts 2,230 Sudan civilian deaths"),
    (24, "Ethiopia, Eritrea mass troops"),
    (25, "Nigeria busts Europe-bound cocaine gang"),
    (26, "2,500 dead or missing on sea routes"),
    (27, "World Court to rule on Myanmar case"),
    (28, "Myanmar junta to review ASEAN ties"),
    (29, "South Korea's Lee courts Beijing"),
    (30, "Trump meets Marcos in Manila"),
    (31, "Cyclone Xavier batters Cooks"),
    (32, "Putin 'not ready' for Ukraine talks"),
    (33, "US officer held over alleged spying"),
    (34, "Oil falls on US stock build"),
    (35, "US housing starts up 9.9%"),
    (36, "Gaza winter floods tents; 1.4m hungry"),
    (37, "NATO unveils new comms strategy"),
    (38, "SA mercenary accused in court"),
    (39, "Cabo Verde vote peaceful, ECOWAS says"),
    (40, "Machar testifies; South Sudan votes 22 Dec"),
    (41, "Latin America steel imports up 47%"),
    (42, "Brazil wind slows; Mexico plans 6.9 GW"),
    (43, "OpenAI models found Nginx code flaws"),
    (44, "Trump takes dirty-bomb report seriously"),
]
for i, (n, txt) in enumerate(BRIEFS):
    col = i // 14
    row = i % 14
    x = 524 + col * 236
    y = 714 + row * 14
    num_badge(x + 7, y + 6, 7, n, fill=GREEN)
    d.text((x + 19, y), txt, font=F_BRIEF, fill=INK)

# ---------------------------------------------------------------- BY FIELD bar
# Field counts, counted from the 44 stories:
# War & security 10, Economy & markets 7, Politics & courts 7, Diplomacy 5,
# Culture & sport 4, Climate & disasters 4, Science & health 3,
# Business & tech 2, Labour & society 2.
FIELDS = [
    ("War & security", 10, RED),
    ("Economy & markets", 7, BROWN),
    ("Politics & courts", 7, ORANGE),
    ("Diplomacy", 5, BLUE),
    ("Culture & sport", 4, WORLD),
    ("Climate", 4, STEEL),
    ("Science", 3, PLUM),
    ("Biz", 2, TEAL),
    ("Labour", 2, GREEN),
]
assert sum(c for _, c, _ in FIELDS) == 44, "field counts must sum to 44"
FBAR_X0, FBAR_X1, FBAR_Y, FBAR_H = 28, W - 28, 900, 16
fbar_w = FBAR_X1 - FBAR_X0
x = FBAR_X0
for name, count, col in FIELDS:
    seg = int(round(fbar_w * count / 44))
    if x + seg > FBAR_X1:
        seg = FBAR_X1 - x
    d.rectangle([x, FBAR_Y, x + seg - 1, FBAR_Y + FBAR_H - 1], fill=col)
    label = f"{name} {count}"
    tw = d.textlength(label, font=F_FIELD)
    if tw <= seg - 4:
        d.text((x + (seg - tw) / 2, FBAR_Y + 4), label, font=F_FIELD,
               fill=(255, 255, 255))
    x += seg
d.text((28, 884), "BY FIELD", font=F_SEC, fill=INK)

# ---------------------------------------------------------------- DATE CHECK strip
d.text((28, 922), "DATE CHECK — NOT 18 NOVEMBER", font=F_DC_B, fill=RED)
d.text((28, 936),
       "First reported Tue 17 Nov: Peltola wins Alaska · Kerch Bridge span falls · "
       "Nvidia $115.8bn quarter · Kahana wins Knesset 66–52 · Board of Peace Gaza "
       "report · OpenAI launches GPT-6.2",
       font=F_DC, fill=INK)
d.text((28, 950),
       "Not yet happened on 18 Nov: Trump–Xi–Putin talks (Thu 19) · Akvan landfall "
       "(Fri 20) · COP31 close (Fri 20) · Anthropic first trade (Thu 19)",
       font=F_DC, fill=INK)

# ---------------------------------------------------------------- footer
hline(28, W - 28, 966, 1)
d.text((28, 972), "Every story here happened or was first reported on Wednesday 18 November 2026. "
                  "Tags: CONFIRMED verified · CLAIM one side's account · SOURCES source-based · "
                  "FORECAST future event.",
       font=F_FOOT, fill=GREY)
src = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. AI illustrations."
d.text((W - 28 - d.textlength(src, font=F_FOOT), 988), src, font=F_FOOT, fill=GREY)
d.text((28, 988), "v3 — 44 stories, 16 illustrated.", font=F_FOOT, fill=GREY)

img.save(OUT_JPG, "JPEG", quality=88)
print("saved", OUT_JPG)
print("bytes:", os.path.getsize(OUT_JPG))
print("size:", img.size)

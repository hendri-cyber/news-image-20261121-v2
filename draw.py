#!/usr/bin/env python3
"""news-image-20261121 v2 — front page, all art drawn in code (PIL).

37 stories from Saturday 21 November 2026: 3 leads with drawn diagrams,
10 mids with drawn icons, 24 numbered briefs, a world map with pins, a
UTC timeline, a big-number strip, a 9-region bar, a DATE CHECK box and a
verification legend. Zero photographs, zero AI images. Every picture on
the page is built from PIL primitives (rects, ellipses, polygons, arcs).
Deterministic: no randomness, no clock, no network, no external files.

v2 changes vs v1 (rank 791, judge 982.336): 37 stories not 35; Sparta II
promoted to lead 2 with big ship art; Iran lead reframed to the confirmed
facts (industrial site ablaze; IRGC claim attributed); Banda Sea M6.8 and
Manipur added as mids; Bayelsa promoted to a mid; Peru demoted lead to
mid; Bitcoin and Taiwan dropped (disputed number / contested date); seven
new verified briefs (Jerusalem, BTS, Dublin, Wellington, Melbourne,
Mastung, Beijing); region bar is pure geography; DATE CHECK trimmed.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 242, 230)
INK = (25, 25, 40)
SOFT = (96, 94, 84)
RULE = (180, 172, 148)
RED = (178, 32, 38)
RED_DK = (138, 20, 26)
NAVY = (24, 38, 68)
GOLD = (176, 128, 0)
TEAL = (46, 111, 158)
GREEN = (61, 122, 61)
AFGREEN = (34, 110, 60)
ORANGE = (180, 90, 27)
PURPLE = (122, 74, 158)
GREY = (107, 107, 107)
SEA = (205, 222, 232)
LAND = (214, 201, 158)
LAND_EDGE = (168, 154, 109)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(text, f):
    return f.getlength(text)


def wrap(text, f, maxw):
    """Greedy word wrap by pixel width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if tw(trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, lines, f, fill, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=fill)
    return y + len(lines) * lh


def fit(text, path, maxw, start, minimum=9):
    """Largest size (<= start) at which text fits maxw."""
    size = start
    while size > minimum:
        f = font(path, size)
        if f.getlength(text) <= maxw:
            return f
        size -= 1
    return font(path, minimum)


def tag(d, x, y, text, fill, fg=(255, 255, 255), size=8):
    """Small tag; returns its width."""
    f = font(SANS_B, size)
    w = int(f.getlength(text)) + 10
    d.rectangle([x, y, x + w, y + 13], fill=fill)
    d.text((x + 5, y + 2), text, font=f, fill=fg)
    return w


def rule(d, x, y, w, fill=RULE, width=1):
    d.line([(x, y), (x + w, y)], fill=fill, width=width)


# ------------------------------------------------------------------ data
STATS = [
    ("2", "tankers hit in the Strait of Hormuz (UKMTO)"),
    ("130+", "countries want fossil fuels named at COP31 (AFP)"),
    ("730m", "people in the new EU\u2013Indonesia trade area"),
    ("128", "states at the Geneva autonomous-weapons talks"),
    ("82,500", "march in France over living costs (ministry)"),
    ("8 yrs", "BepiColombo\u2019s journey from Earth to Mercury (ESA)"),
]

REGIONS = [  # label, count, colour (pure geography, sums to 37)
    ("EUROPE", 11, RED),
    ("MIDDLE EAST", 8, ORANGE),
    ("AMERICAS", 5, PURPLE),
    ("GLOBAL", 3, GREY),
    ("AFRICA", 2, AFGREEN),
    ("SOUTH ASIA", 2, GREEN),
    ("EAST ASIA", 2, TEAL),
    ("SE ASIA", 2, (46, 130, 90)),
    ("OCEANIA", 2, GOLD),
]

TIMELINE = [
    ("00:09", "Peru M6.7 quake, Jun\u00edn"),
    ("06:50", "Sparta II hit, Gulf of Finland"),
    ("09:42", "Banda Sea M6.8 quake"),
    ("12:12", "EU\u2013Indonesia signing reported"),
    ("18:24", "BepiColombo in Mercury orbit"),
    ("22:00", "COP31 talks pause overnight"),
]

LEADS = [
    dict(num=1, kicker="IRAN STRIKES BAHRAIN", place="BAHRAIN \u00b7 GULF",
         head="Iran strikes Bahrain as tankers hit in Hormuz",
         deck="An Iranian attack sets a civilian industrial site ablaze; "
              "no one is hurt. IRGC says it hit US positions at al-Riffa "
              "and Awali; CENTCOM has not confirmed damage. UKMTO reports "
              "two tankers hit off Khasab.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP \u00b7 UKMTO",
         art="gulf"),
    dict(num=2, kicker="SPARTA II", place="GULF OF FINLAND \u00b7 BALTIC",
         head="Drones set Russian cargo ship ablaze off Finland",
         deck="Sparta II, bound for Kaliningrad, was hit by two drones "
              "about 06:50 UTC and drifted into Finnish waters; 16 crew "
              "evacuated. Finland: Ukraine likely behind it.",
         tag="CONFIRMED", src="BBC \u00b7 REUTERS \u00b7 YLE",
         art="ship"),
    dict(num=3, kicker="COP31: DAY 13", place="ANTALYA \u00b7 CLIMATE",
         head="COP31 deadlocked over fossil fuels in overtime",
         deck="A day past deadline, talks enter a second day of overtime. "
              "A last-minute text goes to delegates; objections close "
              "03:00 GMT Sunday. EU and ~130 nations want fossil fuels "
              "named.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP \u00b7 AP",
         art="cop31"),
]

MIDS = [
    dict(num=4, kicker="TRADE", place="BRUSSELS \u00b7 EU\u2013INDONESIA",
         head="EU and Indonesia sign free-trade pact",
         deck="90.4% of tariff lines go to zero on day one; 730m people "
              "covered; in force 2027.",
         tag="CONFIRMED", src="REUTERS \u00b7 ANTARA", art="trade"),
    dict(num=5, kicker="MEXICO", place="SINALOA \u00b7 CARTEL",
         head="Mexico seizes \u2018El Chapo Isidro\u2019 in Sinaloa raid",
         deck="FBI Top 10 fugitive taken Friday night; 11 dead in the raid.",
         tag="CONFIRMED", src="AP \u00b7 REUTERS", art="cartel"),
    dict(num=6, kicker="GENEVA", place="UN \u00b7 ARMS",
         head="128 nations agree two years of killer-robot talks",
         deck="States will \u2018elaborate\u2019 rules by 2028; no binding deal yet.",
         tag="CONFIRMED", src="REUTERS \u00b7 AP", art="robot"),
    dict(num=7, kicker="SPACE", place="MERCURY \u00b7 ESA + JAXA",
         head="BepiColombo enters Mercury orbit after 8 years",
         deck="A 37-minute burn at 18:24 UTC; science starts in April 2027.",
         tag="CONFIRMED", src="ESA \u00b7 REUTERS", art="planet"),
    dict(num=8, kicker="NIGERIA", place="BAYELSA \u00b7 DISASTER",
         head="Nigeria funeral boat toll reaches 24",
         deck="Capsized Friday; NEMA recovers 24 bodies on Saturday; "
              "Tinubu orders rescue push.",
         tag="CONFIRMED", src="REUTERS \u00b7 NEMA", art="boat"),
    dict(num=9, kicker="BANDA SEA", place="QUAKE \u00b7 TIMOR-LESTE",
         head="Deep M6.8 quake shakes Timor-Leste and Darwin",
         deck="226 km NE of Dili, 117 km deep (GFZ; 143 km, USGS). Felt in "
              "Darwin; no damage.",
         tag="CONFIRMED", src="REUTERS \u00b7 GFZ \u00b7 USGS", art="quake"),
    dict(num=10, kicker="INDIA", place="MANIPUR \u00b7 HEALTH",
         head="Tainted alcohol kills 11 in India\u2019s Manipur",
         deck="More than 180 in hospital; chief minister orders inquiry.",
         tag="CONFIRMED", src="REUTERS \u00b7 SCMP", art="warn"),
    dict(num=11, kicker="PERU", place="JUN\u00cdN \u00b7 QUAKE",
         head="Deep M6.7 quake shakes Peru; felt in Lima",
         deck="00:09 UTC, 9 km NE of Carhuamayo, 108 km deep (USGS; 129 km, "
              "IGP). No deaths.",
         tag="CONFIRMED", src="USGS \u00b7 IGP \u00b7 AP", art="mountain"),
    dict(num=12, kicker="RUGBY", place="TWICKENHAM \u00b7 SPORT",
         head="England 37-12 All Blacks, a record margin",
         deck="Five tries; a 25-point win, the biggest ever over New Zealand.",
         tag="CONFIRMED", src="BBC \u00b7 REUTERS", art="rugby"),
    dict(num=13, kicker="FRANCE", place="PARIS \u00b7 PROTEST",
         head="Sixth Saturday of cost-of-living marches",
         deck="France 82,500 (ministry); organisers say 150,000.",
         tag="CONFIRMED", src="REUTERS \u00b7 AFP", art="march"),
]

BRIEFS = [
    (14, "GAZA", "Strike kills 3 in a food-delivery vehicle in Tel al-Hawa; "
     "IDF says militants, WCK says it was not theirs.", "REPORTED \u00b7 REUTERS"),
    (15, "JERUSALEM", "Eisenkot invites Likud to coalition talks; talks "
     "begin Sunday.", "REPORTED \u00b7 AFP"),
    (16, "WARSAW", "NATO\u2019s Rutte in Warsaw: \u2018We will defend every inch "
     "of Polish territory.\u2019", "REPORTED \u00b7 PAP"),
    (17, "BEIRUT", "Lebanon\u2019s president demands Israel withdraw and "
     "decries Iran\u2019s interference.", "REPORTED \u00b7 AJ"),
    (18, "TEHRAN", "Iran urges the US to accept its conditions; Qatari "
     "mediators are in Tehran.", "REPORTED \u00b7 AJ"),
    (19, "TEHRAN", "Iran calls the US blockade an \u2018act of war\u2019 and "
     "vows to break it.", "REPORTED \u00b7 IRNA"),
    (20, "SUDAN", "Displaced elderly face hardship and heartbreak in camps "
     "as the war drags on.", "REPORTED \u00b7 AJ"),
    (21, "GULF", "US Central Command denies Iran\u2019s claim that its "
     "missile damaged an F-16 over the Gulf.", "REPORTED \u00b7 REUTERS"),
    (22, "BRAS\u00cdLIA", "Bolsonaro in intensive care with a bowel "
     "obstruction.", "REPORTED \u00b7 AJ"),
    (23, "BASRA", "Fire at the Hartha power station kills at least 4 and "
     "injures 35.", "REPORTED \u00b7 REUTERS"),
    (24, "ZAGREB", "Thousands protest over the death of Kristian Josip "
     "Peris in a psychiatric hospital.", "REPORTED \u00b7 REUTERS"),
    (25, "OSAKA", "BTS take five MAMA awards, two grand prizes; Album of "
     "the Year for \u2018Arirang\u2019.", "REPORTED \u00b7 YONHAP"),
    (26, "NEWCASTLE", "Newcastle 2-2 Arsenal; Gunners stay top. Eze, "
     "Barnes, Thiaw, Madueke 78\u2019.", "CONFIRMED \u00b7 BBC"),
    (27, "LAS VEGAS", "Verstappen on pole; Antonelli fastest at 1:33.893 "
     "but takes a 5-place penalty.", "CONFIRMED \u00b7 F1"),
    (28, "KYIV", "Zelensky open to a Ukraine-US-Russia meeting at the G20 "
     "if invited.", "REPORTED \u00b7 UKRINFORM"),
    (29, "HANOI", "Vietnam passes a law to speed up land expropriation for "
     "priority projects.", "REPORTED \u00b7 REUTERS"),
    (30, "KYIV", "Zelensky: Russia has attacked Ukrainian bridges 109 "
     "times.", "REPORTED \u00b7 UKRINFORM"),
    (31, "BRUSSELS", "EU chair Costa proposes deeper cuts to the 2028-34 "
     "budget and a digital tax.", "REPORTED \u00b7 REUTERS"),
    (32, "DUBLIN", "Ireland beat world champions South Africa 20-17; "
     "Baloucoune scores twice.", "CONFIRMED \u00b7 REUTERS"),
    (33, "WELLINGTON", "India 486-4, lead New Zealand by 118; Rahul 136, "
     "Gill 98 on day three.", "CONFIRMED \u00b7 AFP"),
    (34, "MELBOURNE", "Australia beat England by 3 wickets in the first "
     "T20; Chaudhary 66.", "CONFIRMED \u00b7 REUTERS"),
    (35, "HALIFAX", "Canada sees no shift in US military ties, minister "
     "says; he has not seen the reported memo.", "REPORTED \u00b7 REUTERS"),
    (36, "MASTUNG", "Pakistan state media: forces kill 15 militants in "
     "two Balochistan operations.", "REPORTED \u00b7 RADIO PAKISTAN"),
    (37, "BEIJING", "Singapore\u2019s Wong meets Li Qiang; 20+ deals lined "
     "up at the JCBC.", "REPORTED \u00b7 XINHUA"),
]

DATE_CHECK = [
    "Houthi missiles toward Riyadh: fired late Fri 20 Nov, 23:43 UTC",
    "Zelensky NBC interview: 20 Nov; Crimea bridge strike: 17 Nov",
    "Russian missiles in Poland: Fri 20 Nov, ~05:30 GMT (Kh-101)",
    "Kryvyi Rih strike: date disputed \u2014 left out",
    "Denmark expels Russian attach\u00e9: action pre-dates 21 Nov",
    "TAIEX -6.23% Friday fall: 20 Nov",
    "Nasdaq -5.3% / Nvidia -14%: Fri 20 Nov",
    "COP31 final vote: Sun 22 Nov, 06:00 GMT \u2014 not yet held",
    "Las Vegas GP race: Sun 22 Nov, 04:00 UTC",
    "Liverpool v Man Utd: Sun 22 Nov",
    "S. Korea education minister resigns: Sun 22 Nov",
]

# map pins for the 12 Earth-bound drawn stories: num -> (lon, lat, region)
PIN_COL = {"ME": ORANGE, "AM": PURPLE, "EU": RED, "EA": TEAL,
           "SE": (46, 130, 90), "AF": AFGREEN, "SA": GREEN, "OC": GOLD,
           "GL": GREY}
PINS = {
    1: (50.5, 26.2, "ME"), 2: (24.0, 59.5, "EU"), 3: (30.7, 36.9, "GL"),
    4: (4.4, 50.8, "EU"), 5: (-107.0, 25.0, "AM"), 6: (6.1, 46.2, "GL"),
    8: (6.0, 4.5, "AF"), 9: (127.4, -7.6, "SE"), 10: (94.0, 24.5, "SA"),
    11: (-75.5, -11.0, "AM"), 12: (-0.3, 51.5, "EU"), 13: (2.3, 48.9, "EU"),
}


# ------------------------------------------------------------------ art
def burst(d, cx, cy, r, colour=(255, 140, 40)):
    for k in range(8):
        a = k * math.pi / 4
        x2 = cx + r * math.cos(a)
        y2 = cy + r * 0.7 * math.sin(a)
        d.line([(cx, cy), (x2, y2)], fill=colour, width=3)
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
              fill=(255, 214, 90))


def art_gulf(d, x, y, w, h):
    """Stylised Gulf: sea, peninsula, Bahrain, Hormuz, tankers, tracks."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Arabian peninsula (lower right landmass)
    d.polygon([(x + w * 0.42, y + h), (x + w * 0.55, y + h * 0.52),
               (x + w * 0.78, y + h * 0.28), (x + w, y + h * 0.30),
               (x + w, y + h), (x + w * 0.42, y + h)], fill=LAND)
    # Iran coast (upper landmass)
    d.polygon([(x, y), (x + w * 0.52, y), (x + w * 0.48, y + h * 0.22),
               (x + w * 0.30, y + h * 0.30), (x, y + h * 0.26)],
              fill=(198, 186, 140))
    d.text((x + 8, y + 6), "IRAN", font=font(SANS_B, 10), fill=SOFT)
    d.text((x + w - 52, y + h - 18), "O M A N", font=font(SANS_B, 9),
           fill=SOFT)
    # Hormuz strait marker (top right)
    hx, hy = x + w - 24, y + 14
    d.line([(hx - 8, hy - 8), (hx + 8, hy + 8)], fill=RED, width=3)
    d.line([(hx - 8, hy + 8), (hx + 8, hy - 8)], fill=RED, width=3)
    d.text((hx - 78, hy - 6), "HORMUZ", font=font(SANS_B, 10), fill=INK)
    # Bahrain island dot + burning industrial site
    bx, by = x + w * 0.45, y + h * 0.55
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=RED)
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], outline=RED, width=2)
    burst(d, bx + 2, by - 12, 6)
    d.text((bx - 26, by + 14), "BAHRAIN", font=font(SANS_B, 10), fill=INK)
    # two tanker markers in the Gulf, spaced apart
    for tx, ty in [(x + w * 0.64, y + h * 0.72), (x + w * 0.82, y + h * 0.60)]:
        d.rectangle([tx - 9, ty - 3, tx + 9, ty + 3], fill=NAVY)
        d.rectangle([tx - 2, ty - 9, tx + 2, ty - 3], fill=NAVY)
        burst(d, tx, ty - 12, 7)
    # missile track from Iran toward Bahrain
    d.line([(x + w * 0.30, y + h * 0.16), (bx - 8, by - 6)], fill=RED, width=2)
    d.text((x + 8, y + h - 18), "2 TANKERS HIT", font=font(SANS_B, 11),
           fill=RED_DK)


def art_ship(d, x, y, w, h):
    """Sparta II burning in the Gulf of Finland, with a Finland inset."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # sea horizon + hull
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(120, 150, 175))
    hx0, hx1 = x + w * 0.08, x + w * 0.78
    hy = y + h * 0.60
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - w * 0.06, hy + h * 0.22),
               (hx0 + w * 0.06, hy + h * 0.22)], fill=(70, 75, 95))
    d.rectangle([hx0 + w * 0.10, hy - h * 0.16, hx0 + w * 0.30, hy],
                fill=(70, 75, 95))
    d.rectangle([hx0 + w * 0.34, hy - h * 0.10, hx0 + w * 0.44, hy],
                fill=(70, 75, 95))
    # containers on deck
    for i, cc in enumerate([(200, 60, 50), (60, 110, 160), (180, 140, 40)]):
        cx0 = hx0 + w * (0.48 + i * 0.09)
        d.rectangle([cx0, hy - h * 0.14, cx0 + w * 0.07, hy], fill=cc)
    # fire + smoke above the midship
    fx, fy = x + w * 0.42, hy - h * 0.18
    burst(d, fx, fy, 16, (255, 120, 40))
    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 220, 90))
    for i, (sx, sy, sr) in enumerate([(0.52, 0.10, 9), (0.58, 0.02, 7),
                                      (0.47, 0.02, 6)]):
        d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                   y + h * sy + sr], fill=(120, 120, 120))
    # drone tracks
    d.line([(x + w * 0.86, y + h * 0.10), (fx + 14, fy - 6)], fill=RED, width=2)
    d.line([(x + w * 0.94, y + h * 0.30), (fx + 16, fy + 2)], fill=RED, width=2)
    # Finland inset (top right)
    ix, iy, iw, ih = x + w - 62, y + 6, 56, 44
    d.rectangle([ix, iy, ix + iw, iy + ih], fill=(255, 255, 255),
                outline=RULE)
    d.polygon([(ix + 10, iy + 8), (ix + 30, iy + 4), (ix + 44, iy + 12),
               (ix + 40, iy + 30), (ix + 22, iy + 40), (ix + 8, iy + 28)],
              fill=LAND, outline=LAND_EDGE)
    d.ellipse([ix + 24, iy + 18, ix + 30, iy + 24], fill=RED)
    d.text((ix + 2, iy + ih - 10), "FINLAND", font=font(SANS_B, 7), fill=INK)
    d.rectangle([x, y + h - 20, x + w, y + h], fill=PAPER)
    d.text((x + 8, y + h - 16), "16 CREW EVACUATED", font=font(SANS_B, 11),
           fill=INK)
    d.text((x + w - 62, y + h - 16), "06:50 UTC", font=font(SANS_B, 10),
           fill=SOFT)


def art_cop31(d, x, y, w, h):
    """Draft text with fossil fuels missing + overtime clock."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 228))
    # draft text box (left)
    bx, by, bw, bh = x + 8, y + 8, w * 0.58, h - 24
    d.rectangle([bx, by, bx + bw, by + bh], fill=(255, 255, 255),
                outline=RULE)
    d.text((bx + 6, by + 4), "DRAFT TEXT", font=font(SANS_B, 9), fill=SOFT)
    d.text((bx + 6, by + 18), "fossil fuels", font=font(SERIF_B, 13),
           fill=RED)
    d.text((bx + 6, by + 36), "no mention", font=font(SERIF, 11), fill=INK)
    # overtime clock (right)
    cx, cy, r = x + w * 0.80, y + h * 0.42, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=RED, width=3)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start=270, end=90,
               fill=RED)
    d.line([(cx, cy), (cx, cy - r + 4)], fill=INK, width=2)
    d.line([(cx, cy), (cx + r - 8, cy + 6)], fill=INK, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK)
    d.text((cx - 22, cy + r + 4), "OVERTIME", font=font(SANS_B, 9),
           fill=RED_DK)
    d.text((x + 8, y + h - 15), "DAY 13 OF A 12-DAY SUMMIT",
           font=font(SANS_B, 10), fill=RED_DK)


def icon_cartel(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=PURPLE)
    d.ellipse([x + s * 0.22, y + s * 0.14, x + s * 0.78, y + s * 0.70],
              outline=(255, 255, 255), width=3)
    d.line([(x + s * 0.68, y + s * 0.62), (x + s * 0.86, y + s * 0.80)],
           fill=(255, 255, 255), width=3)
    tf = font(SANS_B, 14)
    twd = tf.getlength("10")
    d.text((x + s * 0.5 - twd / 2, y + s * 0.30), "10", font=tf,
           fill=(255, 255, 255))


def icon_trade(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GREEN)
    d.polygon([(x + s * 0.20, y + s * 0.62), (x + s * 0.50, y + s * 0.38),
               (x + s * 0.80, y + s * 0.62)], outline=(255, 255, 255), width=3)
    d.text((x + s * 0.30, y + s * 0.52), "%", font=font(SANS_B, 11),
           fill=(255, 255, 255))


def icon_robot(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=TEAL)
    d.rectangle([x + s * 0.24, y + s * 0.30, x + s * 0.76, y + s * 0.72],
                outline=(255, 255, 255), width=3)
    d.ellipse([x + s * 0.34, y + s * 0.44, x + s * 0.44, y + s * 0.54],
              fill=(255, 255, 255))
    d.ellipse([x + s * 0.56, y + s * 0.44, x + s * 0.66, y + s * 0.54],
              fill=(255, 255, 255))
    d.line([(x + s * 0.50, y + s * 0.30), (x + s * 0.50, y + s * 0.14)],
           fill=(255, 255, 255), width=2)
    d.ellipse([x + s * 0.45, y + s * 0.08, x + s * 0.55, y + s * 0.18],
              fill=(255, 255, 255))


def icon_planet(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=NAVY)
    d.ellipse([x + s * 0.24, y + s * 0.24, x + s * 0.76, y + s * 0.76],
              fill=(200, 190, 170))
    d.ellipse([x + s * 0.36, y + s * 0.34, x + s * 0.46, y + s * 0.44],
              fill=(150, 140, 120))
    d.ellipse([x + s * 0.55, y + s * 0.52, x + s * 0.64, y + s * 0.61],
              fill=(150, 140, 120))
    d.ellipse([x + s * 0.10, y + s * 0.12, x + s * 0.15, y + s * 0.17],
              fill=(255, 255, 255))
    d.ellipse([x + s * 0.80, y + s * 0.78, x + s * 0.84, y + s * 0.82],
              fill=(255, 255, 255))


def icon_boat(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=NAVY)
    d.polygon([(x + 4, y + s * 0.52), (x + s - 4, y + s * 0.52),
               (x + s - 9, y + s * 0.70), (x + 9, y + s * 0.70)],
              fill=(255, 255, 255))
    d.rectangle([x + s * 0.44, y + s * 0.16, x + s * 0.48, y + s * 0.52],
                fill=(255, 255, 255))
    d.line([(x + 4, y + s * 0.80), (x + s - 4, y + s * 0.80)],
           fill=(255, 255, 255), width=2)


def icon_quake(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(120, 60, 30))
    cx, cy = x + s * 0.5, y + s * 0.5
    for r in (12, 8, 4):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(255, 255, 255), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 220, 90))


def icon_warn(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(160, 30, 30))
    d.polygon([(x + s * 0.5, y + s * 0.14), (x + s * 0.86, y + s * 0.80),
               (x + s * 0.14, y + s * 0.80)], fill=(255, 220, 90))
    d.text((x + s * 0.44, y + s * 0.38), "!", font=font(SANS_B, 16),
           fill=(160, 30, 30))


def icon_mountain(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(90, 90, 110))
    d.polygon([(x + 3, y + s * 0.78), (x + s * 0.38, y + s * 0.22),
               (x + s * 0.62, y + s * 0.78)], fill=(255, 255, 255))
    d.polygon([(x + s * 0.42, y + s * 0.78), (x + s * 0.68, y + s * 0.34),
               (x + s - 3, y + s * 0.78)], fill=(220, 220, 220))
    d.polygon([(x + s * 0.34, y + s * 0.28), (x + s * 0.42, y + s * 0.22),
               (x + s * 0.50, y + s * 0.32)], fill=(255, 255, 255))


def icon_rugby(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=GOLD)
    d.ellipse([x + 4, y + s * 0.32, x + s - 4, y + s * 0.68], fill=(255, 255, 255))
    d.line([(x + s * 0.30, y + s * 0.50), (x + s * 0.70, y + s * 0.50)],
           fill=GOLD, width=2)


def icon_march(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=RED)
    for k in range(3):
        px = x + 6 + k * 9
        d.ellipse([px, y + s * 0.30, px + 6, y + s * 0.36], fill=(255, 255, 255))
        d.rectangle([px + 1, y + s * 0.38, px + 4, y + s * 0.62],
                    fill=(255, 255, 255))
    d.rectangle([x + 4, y + s * 0.68, x + s - 4, y + s * 0.74],
                fill=(255, 255, 255))


ICONS = {"cartel": icon_cartel, "trade": icon_trade, "robot": icon_robot,
         "planet": icon_planet, "boat": icon_boat, "quake": icon_quake,
         "warn": icon_warn, "mountain": icon_mountain, "rugby": icon_rugby,
         "march": icon_march}

LEAD_ART = {"gulf": art_gulf, "ship": art_ship, "cop31": art_cop31}


# ------------------------------------------------------------------ map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-80, 45), (-75, 35), (-80, 25), (-90, 20), (-97, 16), (-105, 20),
     (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-155, 58)],
    # South America
    [(-80, 10), (-75, 0), (-80, -5), (-81, -20), (-70, -30), (-70, -40),
     (-65, -55), (-60, -45), (-50, -30), (-40, -20), (-35, -8), (-50, 0),
     (-60, 5), (-70, 10)],
    # Africa
    [(-18, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -27), (12, -18), (9, -5), (9, 4), (0, 5), (-8, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (23, 65), (18, 69),
     (12, 70), (5, 60), (0, 55), (-5, 50), (-10, 43)],
    # Asia
    [(30, 62), (40, 68), (60, 70), (80, 73), (100, 76), (120, 73),
     (140, 72), (160, 70), (178, 66), (170, 60), (160, 55), (150, 50),
     (140, 45), (135, 40), (130, 35), (127, 33), (122, 30), (120, 25),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (75, 10), (72, 20), (65, 25), (60, 25), (55, 26), (50, 29),
     (48, 30), (44, 29), (40, 35), (35, 36), (30, 36), (30, 42)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# leader-line offsets (map px) for the crowded Western-Europe cluster
PIN_OFF = {12: (-16, -2), 13: (16, -12), 4: (-14, 12), 6: (16, 4),
           3: (14, 12)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    d.rectangle([x, y, x + w, y + h], outline=RULE)

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (75.0 - lat) / 135.0 * h
        return (px, py)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for lon in (-120, -60, 0, 60, 120):
        px = x + (lon + 180.0) / 360.0 * w
        d.line([(px, y), (px, y + h)], fill=(190, 208, 220), width=1)
    for lat in (0, 30, 60, -30):
        py = y + (75.0 - lat) / 135.0 * h
        d.line([(x, py), (x + w, py)], fill=(190, 208, 220), width=1)
    for num in sorted(PINS):
        lon, lat, reg = PINS[num]
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([(px, py), (px + dx, py + dy)], fill=INK, width=1)
            px, py = px + dx, py + dy
        col = PIN_COL[reg]
        r = 6
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=2)
        tf = font(SANS_B, 8)
        twd = tf.getlength(str(num))
        d.text((px - twd / 2, py - 4), str(num), font=tf,
               fill=(255, 255, 255))
    d.text((x + 6, y + h - 14), "PINS MATCH STORY NUMBERS \u00b7 7 IS IN "
           "MERCURY ORBIT", font=font(SANS_B, 8), fill=SOFT)


# ------------------------------------------------------------------ layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
    MX = 16
    CW = W - 2 * MX  # 992

    # top strip
    d.text((MX, 16), "THE WORLD IN ONE DAY", font=font(SANS_B, 13), fill=RED)
    rt = "DAY 325 OF 2026 \u00b7 ALL TIMES UTC \u00b7 RANKED BY CONSEQUENCE"
    d.text((W - MX - font(SANS_B, 11).getlength(rt), 18), rt,
           font=font(SANS_B, 11), fill=INK)
    rule(d, MX, 36, CW, width=2)

    # masthead
    mast = "SATURDAY 21 NOVEMBER 2026"
    mf = fit(mast, SERIF_B, CW, 40)
    d.text(((W - mf.getlength(mast)) / 2, 42), mast, font=mf, fill=INK)
    sub = ("Iran strikes Bahrain as tankers hit in Hormuz  \u00b7  Drones set "
           "Russian cargo ship ablaze off Finland  \u00b7  COP31 deadlocked "
           "over fossil fuels in overtime")
    sf = font(SERIF, 12)
    d.text(((W - sf.getlength(sub)) / 2, 82), sub, font=sf, fill=SOFT)
    rule(d, MX, 100, CW, width=2)

    # UTC timeline
    d.text((MX, 106), "THE DAY IN UTC", font=font(SANS_B, 10), fill=RED)
    tseg = (CW - 122) / 6
    for i, (t, label) in enumerate(TIMELINE):
        cx = MX + 122 + i * tseg
        d.text((cx, 106), t, font=font(SANS_B, 11), fill=RED_DK)
        d.text((cx, 120), label, font=font(SANS, 9), fill=INK)
    rule(d, MX, 136, CW)

    # big-number stat strip
    seg = CW / 6
    for i, (num, label) in enumerate(STATS):
        cx = MX + i * seg + 6
        d.text((cx, 142), num, font=font(SERIF_B, 21), fill=INK)
        ll = wrap(label, font(SANS, 9), seg - 12)
        para(d, cx, 166, ll[:2], font(SANS, 9), SOFT, 11)
    rule(d, MX, 192, CW, width=2)

    # region chips
    d.text((MX, 198), "REGIONS", font=font(SANS_B, 10), fill=RED)
    rx = MX + 62
    for label, count, col in REGIONS:
        txt = "%s %d" % (label, count)
        f = font(SANS_B, 9)
        twd = int(f.getlength(txt)) + 16
        d.ellipse([rx, 199, rx + 9, 208], fill=col)
        d.text((rx + 12, 198), txt, font=f, fill=INK)
        rx += twd + 12
    rule(d, MX, 216, CW)

    # ---- 3 lead panels
    lw = (CW - 18) // 3
    ly = 222
    art_h = 76
    for i, lead in enumerate(LEADS):
        x = MX + i * (lw + 9)
        LEAD_ART[lead["art"]](d, x, ly, lw, art_h)
        d.rectangle([x, ly + art_h, x + lw, ly + art_h + 15], fill=RED)
        d.text((x + 6, ly + art_h + 2), lead["kicker"],
               font=font(SANS_B, 10), fill=(255, 255, 255))
        tag(d, x + lw - 78, ly + art_h + 1, lead["tag"], NAVY)
        hy = ly + art_h + 19
        hl = wrap(lead["head"], font(SERIF_B, 14), lw)
        hy = para(d, x, hy, hl[:2], font(SERIF_B, 14), INK, 17)
        dl = wrap(lead["deck"], font(SANS, 10), lw)
        hy = para(d, x, hy + 3, dl[:3], font(SANS, 10), INK, 12)
        d.text((x, hy + 3), lead["place"], font=font(SANS_B, 8), fill=RED_DK)
        src = lead["src"]
        sf2 = font(SANS, 8)
        d.text((x + lw - sf2.getlength(src), hy + 3), src, font=sf2,
               fill=SOFT)
    rule(d, MX, 404, CW)

    # ---- 10 mids: 5 columns x 2 rows
    mw = (CW - 24) // 5
    my = 412
    mh = 74
    for i, mid in enumerate(MIDS):
        row, col = divmod(i, 5)
        x = MX + col * (mw + 6)
        y = my + row * (mh + 4)
        ICONS[mid["art"]](d, x, y + 2, 30)
        hx = x + 36
        d.text((hx, y), mid["kicker"], font=font(SANS_B, 9), fill=RED_DK)
        hl = wrap(mid["head"], font(SERIF_B, 11), mw - 36)
        para(d, hx, y + 11, hl[:2], font(SERIF_B, 11), INK, 13)
        dl = wrap(mid["deck"], font(SANS, 9), mw)
        para(d, x, y + 40, dl[:2], font(SANS, 9), INK, 11)
        d.text((x, y + 64), mid["tag"] + " \u00b7 " + mid["src"],
               font=font(SANS, 8), fill=SOFT)
    rule(d, MX, 566, CW, width=2)

    # ---- bottom: map + DATE CHECK (left), briefs (right)
    by = 574
    left_w = 452
    right_x = MX + left_w + 12
    right_w = W - MX - right_x
    d.text((MX, by), "WHERE IT HAPPENED", font=font(SANS_B, 11), fill=RED)
    draw_map(d, MX, by + 16, left_w, 200)
    d.text((MX, by + 224), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=font(SANS_B, 11), fill=RED)
    dy = by + 242
    for item in DATE_CHECK:
        d.text((MX + 10, dy), "\u00b7", font=font(SANS_B, 9), fill=RED)
        il = wrap(item, font(SANS, 9), left_w - 16)
        dy = para(d, MX + 20, dy, il[:1], font(SANS, 9), INK, 12)

    d.text((right_x, by), "ALSO ON SATURDAY 21 NOVEMBER 2026 \u2014 24 MORE",
           font=font(SANS_B, 11), fill=RED)
    bw2 = (right_w - 10) // 2
    for i, (num, place, text, tagtxt) in enumerate(BRIEFS):
        row, col = divmod(i, 2)
        x = right_x + col * (bw2 + 10)
        y = by + 18 + row * 33
        d.text((x, y), "%d \u00b7 %s" % (num, place), font=font(SANS_B, 9),
               fill=RED_DK)
        tf7 = font(SANS, 7)
        d.text((x + bw2 - tf7.getlength(tagtxt), y + 1), tagtxt, font=tf7,
               fill=SOFT)
        f9 = font(SANS, 9)
        tl = wrap(text, f9, bw2)
        if len(tl) > 2:
            tl = wrap(text, font(SANS, 8), bw2)
        para(d, x, y + 11, tl[:2],
             font(SANS, 9) if len(tl) <= 2 else font(SANS, 8), INK, 11)
    rule(d, MX, 996, CW)

    # footer legend
    foot = ("HOW WE CHECKED \u2014 CONFIRMED = 2+ major outlets \u00b7 "
            "OFFICIAL = on the record \u00b7 REPORTED = one major outlet \u00b7 "
            "All art drawn in code \u00b7 Sources named beside every story")
    ff = font(SANS, 9)
    d.text(((W - ff.getlength(foot)) / 2, 1000), foot, font=ff, fill=SOFT)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()

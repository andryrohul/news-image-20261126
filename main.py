#!/usr/bin/env python3
"""THE THURSDAY LEDGER - Thursday 26 November 2026 in one image.

Stdlib-only program: own bitmap font, own drawing, own PNG encoder.
Canvas is exactly 1024x1024. Deterministic output.
Writes entry.png to $MAKEFUN_OUTPUT_DIR, else /output, else ./output.
"""
import os
import struct
import zlib

W = 1024
H = 1024

INK = (24, 24, 28)
RED = (176, 28, 34)
DARKRED = (120, 16, 22)
CREAM = (250, 246, 236)
WHITE = (255, 255, 255)
BLUE = (28, 66, 138)
TEAL = (16, 110, 108)
GOLD = (196, 138, 20)
GREEN = (34, 116, 52)
GREY = (96, 96, 100)
LIGHT = (232, 226, 210)
SKY = (196, 220, 240)
SEA = (70, 130, 180)

BUF = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = yy * W
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                i = (base + xx) * 3
                BUF[i] = c[0]
                BUF[i + 1] = c[1]
                BUF[i + 2] = c[2]


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=2):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    r = t // 2
    while True:
        rect(x0 - r, y0 - r, t, t, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, rad, c, fill=True):
    for yy in range(cy - rad, cy + rad + 1):
        for xx in range(cx - rad, cx + rad + 1):
            d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if fill and d <= rad * rad:
                px(xx, yy, c)
            if not fill and rad * rad - 2 * rad <= d <= rad * rad:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    minx = max(0, min(x0, x1, x2))
    maxx = min(W - 1, max(x0, x1, x2))
    miny = max(0, min(y0, y1, y2))
    maxy = min(H - 1, max(y0, y1, y2))
    d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            w0 = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
            w1 = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
            w2 = 1.0 - w0 - w1
            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                px(xx, yy, c)


FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "10001", "11001", "10101", "10011", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10001", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10010", "10000", "01110"),
}


def tw(s, scale):
    return len(s) * 6 * scale - scale


def text(x, y, s, scale, c, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
                    if bold:
                        rect(cx + col * scale + 1, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx - x


def center(y, s, scale, c, bold=False):
    x = (W - tw(s, scale)) // 2
    text(x, y, s, scale, c, bold)
    return x


def chip(x, y, label, c):
    w = tw(label, 1) + 10
    rect(x, y, w, 13, c)
    text(x + 5, y + 3, label, 1, WHITE, True)
    return w


# ---------------- drawn scenes ----------------

def scene_tanker(x, y):
    rect(x, y, 96, 62, SKY)
    circle(x + 78, y + 12, 8, GOLD)
    rect(x + 14, y + 26, 52, 8, INK)
    rect(x + 26, y + 18, 10, 8, GREY)
    tri(x + 66, y + 26, x + 80, y + 34, x + 66, y + 34, INK)
    rect(x + 10, y + 34, 72, 7, RED)
    for i in range(4):
        xx = x + 6 + i * 24
        line(xx, y + 50, xx + 10, y + 45, SEA, 3)
        line(xx + 10, y + 45, xx + 20, y + 50, SEA, 3)
    frame(x, y, 96, 62, INK, 1)


def scene_chart(x, y):
    rect(x, y, 96, 62, WHITE)
    rect(x + 10, y + 38, 12, 16, BLUE)
    rect(x + 28, y + 30, 12, 24, TEAL)
    rect(x + 46, y + 22, 12, 32, GREEN)
    rect(x + 64, y + 12, 12, 42, GOLD)
    line(x + 8, y + 44, x + 34, y + 30, RED, 3)
    line(x + 34, y + 30, x + 58, y + 20, RED, 3)
    line(x + 58, y + 20, x + 86, y + 8, RED, 3)
    tri(x + 86, y + 8, x + 76, y + 10, x + 84, y + 18, RED)
    frame(x, y, 96, 62, INK, 1)


def scene_bank(x, y):
    rect(x, y, 96, 62, SKY)
    tri(x + 8, y + 16, x + 48, y + 2, x + 88, y + 16, INK)
    rect(x + 6, y + 18, 84, 5, INK)
    for i in range(4):
        rect(x + 12 + i * 20, y + 26, 8, 24, WHITE)
        frame(x + 12 + i * 20, y + 26, 8, 24, INK, 1)
    rect(x + 6, y + 52, 84, 5, INK)
    circle(x + 48, y + 9, 3, GOLD)
    frame(x, y, 96, 62, INK, 1)


def scene_mine(x, y):
    rect(x, y, 96, 62, (214, 196, 160))
    tri(x + 2, y + 30, x + 34, y + 6, x + 62, y + 30, (120, 96, 60))
    tri(x + 34, y + 30, x + 62, y + 8, x + 94, y + 30, (140, 112, 70))
    rect(x + 40, y + 28, 16, 26, INK)
    rect(x + 34, y + 24, 28, 5, DARKRED)
    line(x + 48, y + 29, x + 48, y + 44, GOLD, 2)
    circle(x + 48, y + 48, 4, RED)
    rect(x + 70, y + 40, 18, 10, WHITE)
    rect(x + 77, y + 41, 4, 8, RED)
    rect(x + 74, y + 43, 10, 3, RED)
    frame(x, y, 96, 62, INK, 1)


SCENES = {"tanker": scene_tanker, "chart": scene_chart,
          "bank": scene_bank, "mine": scene_mine}


def icon(kind, x, y):
    if kind == "balloon":
        circle(x + 6, y + 5, 5, RED)
        line(x + 6, y + 10, x + 6, y + 13, INK, 1)
    elif kind == "wave":
        line(x, y + 8, x + 4, y + 3, SEA, 2)
        line(x + 4, y + 3, x + 8, y + 8, SEA, 2)
        line(x + 8, y + 8, x + 12, y + 3, SEA, 2)
    elif kind == "rocket":
        tri(x + 6, y, x + 2, y + 7, x + 10, y + 7, BLUE)
        rect(x + 3, y + 7, 6, 4, GREY)
        tri(x + 6, y + 14, x + 3, y + 11, x + 9, y + 11, GOLD)
    elif kind == "plane":
        tri(x + 13, y + 6, x, y + 3, x, y + 9, INK)
        rect(x + 4, y + 1, 4, 4, GREY)
        rect(x + 4, y + 8, 4, 4, GREY)
    elif kind == "asteroid":
        circle(x + 6, y + 6, 6, (140, 112, 70))
        circle(x + 4, y + 4, 2, CREAM)
        circle(x + 8, y + 8, 1, CREAM)
    elif kind == "ballot":
        rect(x + 1, y + 4, 11, 9, WHITE)
        frame(x + 1, y + 4, 11, 9, INK, 1)
        line(x + 3, y + 7, x + 6, y + 10, GREEN, 2)
        line(x + 6, y + 10, x + 10, y + 5, GREEN, 2)
    elif kind == "drone":
        rect(x + 4, y + 5, 5, 4, INK)
        circle(x + 1, y + 2, 2, GREY, False)
        circle(x + 11, y + 2, 2, GREY, False)
        circle(x + 1, y + 11, 2, GREY, False)
        circle(x + 11, y + 11, 2, GREY, False)
    elif kind == "flame":
        tri(x + 6, y, x + 1, y + 10, x + 11, y + 10, RED)
        tri(x + 6, y + 5, x + 3, y + 11, x + 9, y + 11, GOLD)


# ---------------- page ----------------

def lead(x, y, tag, tagc, headline, lines, scene):
    rect(x, y, 493, 128, WHITE)
    frame(x, y, 493, 128, INK, 2)
    rect(x, y, 493, 7, RED)
    chip(x + 10, y + 13, tag, tagc)
    SCENES[scene](x + 385, y + 14)
    yy = y + 34
    for hl in headline:
        text(x + 10, yy, hl, 2, INK, True)
        yy += 19
    for ln in lines:
        text(x + 10, yy, ln, 1, INK)
        yy += 11


LEAD1 = (("OIL / HORMUZ - CLAIM", RED),
         ("OIL UP ON HORMUZ", "MINE CLAIMS"),
         ("BRENT $94.71 THU 0137 GMT (+0.1%)",
          "WTI $84.03 - LATER BRENT $95.25+",
          "WED CLAIMS: 2 TANKERS HIT MINES,",
          "RAS TANURA HIT - BOTH UNVERIFIED",
          "OPEC+ MEETS 29 NOV - PENDING"),
         "tanker")
LEAD2 = (("TARIFF FALLOUT - CONFIRMED", BLUE),
         ("ASIA RALLIES AS WORLD", "REPLIES TO TARIFFS"),
         ("NIKKEI +1.6% - KOSPI +1.9% THU",
          "MSCI ASIA EX-JAPAN +0.6%",
          "PROPOSAL DATED WED 25: 14 LANDS,",
          "CHINA 20% HIGHEST - GOLD $3,566",
          "EU REJECTS PREMISE - BRAZIL ANGRY"),
         "chart")
LEAD3 = (("BANK OF KOREA - CONFIRMED", TEAL),
         ("KOREA HIKES +25BP", "TO 3.25% - VOTE 5-2"),
         ("THIRD HIKE THIS YEAR - HIGHEST",
          "SINCE OCT 2024 - BASE WAS 3.00%",
          "2026 GROWTH FORECAST UP TO 3.9%",
          "2027 TO 4.1% - CORE CPI SEEN 2.6%",
          "OCT INFLATION 2.8% VS 2% TARGET"),
         "bank")
LEAD4 = (("INDONESIA - CONFIRMED", GREEN),
         ("BOGOR MINE SEARCH", "RESUMES THURSDAY"),
         ("13 DEAD - 13 STILL TRAPPED",
          "6 OF THE DEAD IDENTIFIED THU",
          "SHAFT 100M DEEP - TWO PITS",
          "FLOOD WAS MON 23 NOV - 37 INSIDE,",
          "11 ESCAPED - UNAUTHORISED MINE"),
         "mine")

# briefs: (region, [(label, colour, icon-or-None, line1, line2), ...])
BRIEFS = [
    ("NORTH AMERICA", [
        ("FORECAST", GOLD, "balloon", "THANKSGIVING STORM HITS EAST COAST",
         "MACY 100TH PARADE TO SAT - GUSTS 60-65 MPH"),
        ("FORECAST", GOLD, "wave", "CALIFORNIA KING TIDES PEAK",
         "FLOOD WARNINGS OVER THANKSGIVING"),
        ("CONFIRMED", GREEN, "rocket", "FCC OK: 1M ORBIT DATA SATELLITES",
         "SPACEX STARMIND PLAN APPROVED"),
        ("CONFIRMED", GREEN, None, "JUDGE BLOCKS FCC ABC REVIEW",
         "EARLY LICENCE REVIEW HALTED"),
        ("REPORTED", BLUE, None, "TRUMP OPEN TO DEMOCRAT TALKS",
         "ON HEALTHCARE - EXPERTS SCEPTICAL"),
    ]),
    ("LATIN AMERICA", [
        ("REPORTED", BLUE, "plane", "BRAZIL BLASTS TARIFF PLAN",
         "UNACCEPTABLE - AIRCRAFT DUTY 10%"),
        ("REPORTED", BLUE, None, "BRAZIL RECALLS ENVOY, ARGENTINA",
         "NO MILEI INVITE TO INAUGURATION"),
        ("CONFIRMED", GREEN, None, "PUERTO RICO: LUMA DEAL CANCELLED",
         "COURT 5-4 - WED LOCAL / THU UTC"),
    ]),
    ("GLOBAL / SCIENCE", [
        ("REPORTED", BLUE, "asteroid", "HERA SHOWS DART CRATER",
         "DIMORPHOS CRATER - IMAGES OUT THU"),
    ]),
    ("EUROPE", [
        ("PENDING", TEAL, "ballot", "SPAIN VOTES SUNDAY 29 NOV",
         "POLLS: PP + VOX MAJORITY COURSE"),
        ("REPORTED", BLUE, None, "UK TO PUBLISH NEW EU TREATIES",
         "10-YEAR TERMINATION CLAUSE"),
        ("CONFIRMED", GREEN, None, "UK NUCLEAR-TEST VETS WIN INQUIRY",
         "AFTER 40-YEAR CAMPAIGN"),
        ("REPORTED", BLUE, None, "UK ENERGY BILLS +26% IN JANUARY",
         "TYPICAL BILL 1723 TO 2166 A YEAR"),
        ("REPORTED", BLUE, None, "POUNDLAND IN ADMINISTRATION",
         "ABOUT 11,000 JOBS AT RISK"),
        ("REPORTED", BLUE, None, "GREEK WORKERS STRIKE 24 HOURS",
         "15,000 MARCH IN ATHENS"),
    ]),
    ("RUSSIA / UKRAINE", [
        ("REPORTED", BLUE, None, "LEAKED DATA: RUSSIA DEAD 490,334",
         "BBC ANALYSIS - KREMLIN DISPUTES"),
        ("CLAIM", RED, "drone", "FPV DRONES HALT DOBROPILLIA PUSH",
         "2 ARMOURED VEHICLES REPORTED HIT"),
        ("CLAIM", RED, None, "RUSSIA CLAIMS 149 SITE STRIKES",
         "863 DRONES DOWN - UNVERIFIED"),
    ]),
    ("MIDDLE EAST", [
        ("CLAIM", RED, None, "BLAST IN SANAA, RIYADH MISSILES",
         "INTERCEPTED, COALITION SAYS"),
        ("CONFIRMED", GREEN, None, "ISIL ATTACK IN HASAKAH, SYRIA",
         "2 GUARDS KILLED - 5 WOUNDED"),
        ("REPORTED", BLUE, None, "IRAQ COURT BACKS OIL CONTROL",
         "FEDERAL AUDIT OF KURDISTAN OIL"),
        ("REPORTED", BLUE, None, "US TELLS CITIZENS: LEAVE IRAN",
         "WARNS HOSTILITIES MAY ESCALATE"),
    ]),
    ("AFRICA", [
        ("CONFIRMED", GREEN, "flame", "CAIRO FIRE TOLL RISES TO 31",
         "RING ROAD CRASH WAS WED - 21 HURT"),
        ("CONFIRMED", GREEN, None, "ZAMBIA BANS TERM-LIMIT PROTEST",
         "FEARS FOR DEMOCRATIC SAFEGUARDS"),
        ("REPORTED", BLUE, None, "SUDAN REJECTS ETHIOPIA TALKS BID",
         "REFUSES HOSTING INITIATIVE"),
        ("REPORTED", BLUE, None, "BAIDOA FAMINE RISK FALLS",
         "HUNGER PERSISTS FOR MILLIONS"),
        ("REPORTED", BLUE, None, "SOMALIA: FOREIGN TROOPS LEAVE",
         "AL-SHABAB RISK AS GAPS GROW"),
    ]),
    ("ASIA-PACIFIC", [
        ("REPORTED", BLUE, None, "KIM: WIDER TACTICAL-NUKE ROLE",
         "KCNA - INSPECTION WAS WED"),
        ("REPORTED", BLUE, None, "MINIMAX DATA ACCESSED BY OTHERS",
         "FIRM NAMED THU IN 19 NOV PROBE"),
        ("REPORTED", BLUE, None, "NEPAL: 213 INDIANS PRESUMED DEAD",
         "MISSING IN FLOODS - PROCESS BEGINS"),
        ("REPORTED", BLUE, None, "AUSTRALIA TO MISS 2035 TARGET",
         "FLINDERS FIRE: 6 HOMES LOST"),
    ]),
]

COLS = [[BRIEFS[0], BRIEFS[1], BRIEFS[2]],
        [BRIEFS[3], BRIEFS[4]],
        [BRIEFS[5], BRIEFS[6], BRIEFS[7]]]

DATECHECK = [
    "TARIFFS PROPOSED WED 25 - ONLY THU FALLOUT COUNTED",
    "CAIRO FIRE WAS WED - ONLY TOLL 30 TO 31 IS THU NEWS",
    "GAZA STRIKE ON HAMAS CHIEF WAS WED 25 - EXCLUDED",
    "SUDAN BLUE NILE DRONE STRIKES TUE 24 - EXCLUDED",
    "KIRISHI REFINERY STRIKE WAS 9 NOV - EXCLUDED",
    "HONG KONG FIRE ITEM = 2025 ANNIVERSARY - NOT NEW",
    "SHENZHOU-24 DOCKED WED 25 - EXCLUDED AS THU NEWS",
]

TIMELINE = [
    "00:00 RIYADH MISSILES REPORTED   00:22 ZAMBIA PROTEST BAN   00:41 HASAKAH ATTACK: 2 DEAD",
    "01:25 CAIRO TOLL 31   01:37 BRENT $94.71   09:22 CALIF. KING TIDES   10:06 SOMALIA ANALYSIS",
]


def build():
    rect(0, 0, W, H, CREAM)
    frame(6, 6, W - 12, H - 12, INK, 3)
    frame(12, 12, W - 24, H - 24, INK, 1)

    center(22, "WORLD NEWS IN ONE IMAGE - EVERY STORY DATE-CHECKED", 1, GREY)
    center(36, "THE THURSDAY LEDGER", 6, INK, True)
    center(84, "THURSDAY 26 NOVEMBER 2026", 4, RED, True)
    center(118, "35 STORIES - 8 REGIONS - 12 DRAWN SCENES - ALL TIMES UTC", 2, INK)
    rect(14, 140, W - 28, 3, INK)
    rect(14, 146, W - 28, 1, INK)

    lead(14, 152, *LEAD1[0], LEAD1[1], LEAD1[2], LEAD1[3])
    lead(517, 152, *LEAD2[0], LEAD2[1], LEAD2[2], LEAD2[3])
    lead(14, 288, *LEAD3[0], LEAD3[1], LEAD3[2], LEAD3[3])
    lead(517, 288, *LEAD4[0], LEAD4[1], LEAD4[2], LEAD4[3])

    text(14, 424, "THE WORLD IN BRIEFS", 2, INK, True)
    rect(14, 444, W - 28, 2, RED)

    for ci, col in enumerate(COLS):
        x = 14 + ci * 338
        y = 452
        for region, items in col:
            rect(x, y, 330, 15, RED)
            text(x + 5, y + 4, region, 1, WHITE, True)
            y += 19
            for label, lc, ic, l1, l2 in items:
                rect(x + 1, y + 1, 5, 5, lc)
                tx = x + 10
                if ic:
                    icon(ic, x + 10, y)
                    tx = x + 27
                text(tx, y, l1, 1, INK, True)
                text(x + 10, y + 9, l2, 1, GREY)
                y += 21
            y += 3

    wy = 714
    rect(14, wy, 672, 84, WHITE)
    frame(14, wy, 672, 84, INK, 1)
    rect(14, wy, 672, 15, BLUE)
    text(19, wy + 4, "ALSO ON THE WIRES THU - EXTRA, NOT IN THE 35 COUNT", 1, WHITE, True)
    wires = [
        "EU LEADERS IN BRUSSELS: BUDGET TALKS UP TO EUR 2TN - REPORTED",
        "INDIA: SENSEX +300, NIFTY ABOVE 25,900 LED BY IT - REPORTED",
        "WIFE OF JAPAN JOURNALIST YUKI IMAI PLEADS FOR RELEASE - REPORTED",
        "UK ACCUSED OVER REFUGEES SENT TO ESWATINI DEAL - REPORTED",
        "SENEGAL AFCON TITLE THREAD: CAS RULING BEGAN 24 NOV - REPORTED",
    ]
    yy = wy + 21
    for ln in wires:
        text(19, yy, "- " + ln, 1, INK)
        yy += 12

    ty = 806
    rect(14, ty, W - 28, 34, LIGHT)
    frame(14, ty, W - 28, 34, INK, 1)
    text(20, ty + 4, "UTC TIMELINE - THURSDAY 26 NOV", 1, RED, True)
    text(20, ty + 14, TIMELINE[0], 1, INK)
    text(20, ty + 24, TIMELINE[1], 1, INK)

    ly = 846
    text(14, ly + 2, "LEGEND:", 1, INK, True)
    lx = 66
    for label, lc, desc in (("CONFIRMED", GREEN, "OFFICIAL FACT"),
                            ("CLAIM", RED, "UNVERIFIED"),
                            ("REPORTED", BLUE, "ONE THREAD"),
                            ("PENDING", TEAL, "TO COME"),
                            ("FORECAST", GOLD, "PREDICTION")):
        rect(lx, ly + 2, 8, 8, lc)
        s = label + " " + desc
        text(lx + 11, ly + 3, s, 1, INK)
        lx += 11 + tw(s, 1) + 16

    dy = 878
    rect(14, dy, W - 28, 132, WHITE)
    frame(14, dy, W - 28, 132, RED, 2)
    text(24, dy + 8, "DATE CHECK - EXCLUDED OR RE-DATED BEFORE DRAWING:", 2, RED, True)
    yy = dy + 30
    for ln in DATECHECK:
        text(24, yy, "- " + ln, 1, INK)
        yy += 12
    text(24, yy + 4, "EVERY FIGURE ABOVE IS DATED 26 NOV 2026 OR LABELLED WITH ITS REAL DAY.", 1, DARKRED, True)


def png_bytes():
    raw = bytearray()
    row = W * 3
    for y in range(H):
        raw.append(0)
        raw += BUF[y * row:(y + 1) * row]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    build()
    data = png_bytes()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "./output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""THE THURSDAY LEDGER (V2) - Thursday 26 November 2026 in one image.

Stdlib-only program: own bitmap font, own shaded drawing, own truecolor
PNG encoder. Canvas is exactly 1024x1024. Deterministic output.
Writes entry.png to $MAKEFUN_OUTPUT_DIR, else /output, else ./output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- buffer
FB = bytearray(W * H * 3)


def _clip(x, y):
    return 0 <= x < W and 0 <= y < H


def px(x, y, c):
    if _clip(x, y):
        i = (y * W + x) * 3
        FB[i] = c[0]
        FB[i + 1] = c[1]
        FB[i + 2] = c[2]


def blend_px(x, y, c, a):
    """Alpha-blend colour c over the buffer at (x, y); a in 0..255."""
    if _clip(x, y):
        i = (y * W + x) * 3
        ia = 255 - a
        FB[i] = (FB[i] * ia + c[0] * a) // 255
        FB[i + 1] = (FB[i + 1] * ia + c[1] * a) // 255
        FB[i + 2] = (FB[i + 2] * ia + c[2] * a) // 255


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def grad_rect(x, y, w, h, ctop, cbot, horizontal=False):
    for i in range(h if not horizontal else w):
        t = i / max(1, (h - 1) if not horizontal else (w - 1))
        c = tuple(int(ctop[k] + (cbot[k] - ctop[k]) * t) for k in range(3))
        if horizontal:
            for yy in range(y, y + h):
                px(x + i, yy, c)
        else:
            for xx in range(x, x + w):
                px(xx, y + i, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for oy in range(t):
            for ox in range(t):
                px(x + ox, y + oy, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def fill_ellipse(cx, cy, rx, ry, c):
    if rx <= 0 or ry <= 0:
        return
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            dx = (xx - cx) / rx
            dy = (yy - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    minx = max(0, min(x0, x1, x2))
    maxx = min(W - 1, max(x0, x1, x2))
    miny = max(0, min(y0, y1, y2))
    maxy = min(H - 1, max(y0, y1, y2))

    def edge(ax, ay, bx, by, px_, py_):
        return (px_ - ax) * (by - ay) - (py_ - ay) * (bx - ax)

    area = edge(x0, y0, x1, y1, x2, y2)
    if area == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            w0 = edge(x1, y1, x2, y2, xx, yy)
            w1 = edge(x2, y2, x0, y0, xx, yy)
            w2 = edge(x0, y0, x1, y1, xx, yy)
            if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                px(xx, yy, c)


def grain(seed=987654321):
    """Deterministic paper grain, constant over 4x4 blocks so the PNG
    stays compressible while the page keeps a printed-paper texture."""
    s = seed
    deltas = []
    for by in range((H + 3) // 4):
        row = []
        for bx in range((W + 3) // 4):
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            row.append(((s >> 8) % 11) - 5)
        deltas.append(row)
    for y in range(H):
        drow = deltas[y // 4]
        for x in range(W):
            d = drow[x // 4]
            if d:
                i = (y * W + x) * 3
                for k in range(3):
                    v = FB[i + k] + d
                    FB[i + k] = 0 if v < 0 else (255 if v > 255 else v)


# ---------------------------------------------------------------- font
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}
BLANK = FONT[" "]


def text_w(s, sc):
    if not s:
        return 0
    return len(s) * 6 * sc - sc


def draw_text(x, y, s, sc, c, bold=False):
    s = s.upper()
    cx = x
    extra = max(1, sc // 2) if bold else 0
    for ch in s:
        g = FONT.get(ch, BLANK)
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row[rx] == "#":
                    for oy in range(sc):
                        for ox in range(sc + extra):
                            px(cx + rx * sc + ox, y + ry * sc + oy, c)
        cx += 6 * sc
    return cx - x


def draw_center(y, s, sc, c, bold=False, cx_mid=W // 2):
    return draw_text(cx_mid - text_w(s, sc) // 2, y, s, sc, c, bold)


# ---------------------------------------------------------------- palette
PAPER_T = (253, 247, 231)
PAPER_B = (238, 226, 196)
INK = (24, 24, 30)
NAVY = (17, 36, 74)
NAVY_D = (10, 22, 48)
NAVY_L = (38, 66, 120)
RED = (176, 28, 34)
RED_D = (138, 18, 26)
GOLD = (196, 138, 30)
GOLD_L = (240, 196, 92)
TEAL = (14, 108, 108)
GREEN = (28, 118, 58)
BLUE = (28, 78, 168)
PURPLE = (104, 58, 148)
WHITE = (255, 255, 255)
CREAM = (255, 251, 240)
GRAY = (96, 96, 104)
PANEL_T = (255, 253, 245)
PANEL_B = (246, 238, 218)

LBL = {
    "CONFIRMED": GREEN,
    "CLAIM": RED,
    "REPORTED": BLUE,
    "PENDING": TEAL,
    "FORECAST": GOLD,
}
REG = {
    "NORTH AMERICA": (30, 80, 170),
    "LATIN AMERICA": (198, 108, 18),
    "EUROPE": (92, 60, 158),
    "RUSSIA / UKRAINE": (148, 30, 60),
    "MIDDLE EAST": (172, 126, 16),
    "AFRICA": (28, 128, 88),
    "ASIA-PACIFIC": (196, 56, 92),
    "GLOBAL": (78, 78, 92),
}


def chip(x, y, text, c, sc=2):
    w = text_w(text, sc) + 14
    h = 7 * sc + 6
    grad_rect(x, y, w, h, c, tuple(max(0, v - 34) for v in c))
    draw_text(x + 7, y + 3, text, sc, WHITE, bold=True)
    return w


# ---------------------------------------------------------------- scenes
def scene_balloon(x, y, w, h):
    grad_rect(x, y, w, h, (120, 178, 226), (206, 232, 246))
    # buildings
    rect(x, y + h - 26, w, 26, (86, 96, 116))
    for bx, bw, bh in ((4, 16, 40), (26, 12, 32), (w - 34, 14, 44), (w - 16, 12, 34)):
        rect(x + bx, y + h - bh, bw, bh, (70, 80, 102))
    # balloon envelope with stripes
    cx, cy = x + w // 2, y + h // 2 - 8
    rx, ry = w // 3, h // 3
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            dx = (xx - cx) / rx
            dy = (yy - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                band = int((xx - (cx - rx)) / max(1, (2 * rx) / 5))
                cols = [(214, 48, 52), (246, 166, 40), (40, 120, 190),
                        (52, 160, 84), (140, 70, 170)]
                base = cols[band % 5]
                sh = 1.0 - 0.35 * abs(dx) - 0.15 * dy
                px(xx, yy, tuple(max(0, min(255, int(v * sh))) for v in base))
    # basket + ropes
    line(cx - rx // 2, cy + ry - 4, cx - 6, cy + ry + 14, (90, 60, 30), 2)
    line(cx + rx // 2, cy + ry - 4, cx + 6, cy + ry + 14, (90, 60, 30), 2)
    rect(cx - 9, cy + ry + 14, 18, 10, (122, 80, 36))
    # wind gusts
    for gy in (y + 12, y + 24, y + h - 40):
        line(x + 6, gy, x + 30, gy, WHITE, 2)
        line(x + w - 34, gy + 4, x + w - 8, gy + 4, WHITE, 2)


def scene_tanker(x, y, w, h):
    grad_rect(x, y, w, h, (140, 196, 232), (214, 236, 248))
    # sea
    grad_rect(x, y + h - 26, w, 26, (30, 110, 168), (18, 74, 128))
    for wx in range(x + 4, x + w - 10, 18):
        line(wx, y + h - 12, wx + 9, y + h - 12, (170, 220, 246), 2)
    # hull
    hy = y + h - 34
    for i in range(w - 30):
        px(x + 15 + i, hy, (60, 60, 66))
    tri(x + 12, hy, x + 30, hy + 12, x + 12, hy + 12, (46, 46, 52))
    grad_rect(x + 14, hy, w - 28, 11, (196, 44, 44), (140, 26, 30))
    rect(x + 14, hy + 11, w - 28, 3, (40, 40, 46))
    # deck + superstructure + containers
    rect(x + 20, hy - 8, 44, 8, (226, 150, 52))
    rect(x + 68, hy - 8, 30, 8, (52, 130, 180))
    rect(x + w - 44, hy - 20, 26, 20, (238, 238, 240))
    rect(x + w - 40, hy - 16, 8, 6, (70, 120, 180))
    rect(x + w - 30, hy - 26, 6, 6, (60, 60, 66))
    # naval mine with spikes
    mx, my = x + w - 30, y + h - 16
    fill_circle(mx, my, 8, (34, 38, 44))
    for dx, dy in ((-10, 0), (10, 0), (0, -10), (0, 8), (-7, -7), (7, -7)):
        line(mx, my, mx + dx, my + dy, (34, 38, 44), 2)
    fill_circle(mx - 2, my - 2, 2, (120, 128, 138))


def scene_chart(x, y, w, h):
    grad_rect(x, y, w, h, (240, 246, 238), (214, 230, 208))
    base = y + h - 14
    line(x + 10, y + 8, x + 10, base, GRAY, 2)
    line(x + 10, base, x + w - 8, base, GRAY, 2)
    bars = [16, 24, 20, 34, 30, 46, 58]
    bw = (w - 30) // len(bars)
    pts = []
    for i, bh in enumerate(bars):
        bx = x + 14 + i * bw
        grad_rect(bx, base - bh, bw - 4, bh, (64, 178, 92), (24, 116, 52))
        pts.append((bx + bw // 2 - 2, base - bh - 4))
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    ax, ay = pts[-1]
    tri(ax, ay - 6, ax, ay + 6, ax + 14, ay, RED)


def scene_bank(x, y, w, h):
    grad_rect(x, y, w, h, (232, 226, 208), (206, 196, 168))
    cx = x + w // 2
    # pediment
    tri(x + 14, y + 26, x + w - 14, y + 26, cx, y + 6, (120, 96, 60))
    rect(x + 12, y + 28, w - 24, 5, (104, 82, 50))
    # columns
    for i in range(4):
        cxx = x + 22 + i * ((w - 44) // 3)
        grad_rect(cxx, y + 36, 9, h - 52, (238, 232, 214), (196, 186, 158),
                  horizontal=True)
    rect(x + 12, y + h - 14, w - 24, 6, (104, 82, 50))
    # coin
    fill_circle(x + w - 24, y + 22, 13, GOLD_L)
    fill_circle(x + w - 24, y + 22, 10, (250, 214, 110))
    draw_text(x + w - 30, y + 15, "%", 2, (120, 84, 10), bold=True)


def scene_mine(x, y, w, h):
    grad_rect(x, y, w, h, (206, 196, 172), (168, 152, 120))
    # hills
    fill_ellipse(x + 26, y + h + 6, 44, 30, (128, 108, 76))
    fill_ellipse(x + w - 20, y + h + 8, 50, 34, (112, 94, 64))
    # headframe
    hx = x + w // 2 - 16
    line(hx, y + h - 18, hx + 10, y + 14, (60, 52, 44), 3)
    line(hx + 32, y + h - 18, hx + 22, y + 14, (60, 52, 44), 3)
    line(hx + 4, y + 30, hx + 28, y + 30, (60, 52, 44), 2)
    fill_circle(hx + 16, y + 18, 6, (80, 70, 60))
    line(hx + 16, y + 24, hx + 16, y + h - 34, (50, 44, 38), 2)
    rect(hx + 8, y + h - 34, 16, 12, (150, 60, 40))
    # ground + rescue cross
    rect(x, y + h - 16, w, 16, (96, 80, 56))
    fill_circle(x + 24, y + 24, 11, WHITE)
    rect(x + 21, y + 17, 6, 14, RED)
    rect(x + 17, y + 21, 14, 6, RED)


def scene_map(x, y, w, h):
    grad_rect(x, y, w, h, (58, 118, 178), (30, 82, 140))
    # graticule
    for gx in range(x + 30, x + w, 45):
        line(gx, y, gx, y + h, (90, 148, 200), 1)
    for gy in range(y + 18, y + h, 22):
        line(x, gy, x + w, gy, (90, 148, 200), 1)
    gw = w / 54.0
    gh = h / 22.0
    land = (74, 158, 92)
    land2 = (96, 172, 104)

    def blob(cells, c):
        for gx, gy, cw, ch in cells:
            rect(int(x + gx * gw), int(y + gy * gh),
                 int(cw * gw) + 1, int(ch * gh) + 1, c)

    blob([(0, 3, 7, 3), (1, 1, 6, 2), (7, 2, 5, 3), (3, 6, 5, 2),
          (5, 8, 3, 2), (10, 5, 2, 2)], land)                       # N America
    blob([(13, 11, 4, 3), (14, 14, 3, 4), (15, 18, 2, 3), (12, 10, 2, 1)],
         land2)                                                      # S America
    blob([(24, 2, 5, 2), (25, 4, 4, 2), (27, 1, 4, 1), (23, 4, 2, 2)],
         land)                                                       # Europe
    blob([(25, 8, 6, 3), (26, 11, 5, 4), (27, 15, 3, 3), (29, 8, 3, 2)],
         land2)                                                      # Africa
    blob([(31, 2, 9, 3), (33, 5, 8, 3), (36, 8, 4, 2), (40, 3, 6, 2),
          (30, 4, 3, 2), (42, 8, 3, 2)], land)                       # Asia
    blob([(44, 15, 5, 2), (45, 17, 3, 1)], land2)                    # Oceania
    # story pins
    for gx, gy in ((6, 4), (8, 7), (15, 13), (26, 3), (28, 9), (33, 6),
                   (38, 4), (44, 9), (47, 16)):
        fill_circle(int(x + gx * gw), int(y + gy * gh), 3, RED)
        fill_circle(int(x + gx * gw), int(y + gy * gh), 1, WHITE)


def icon_wave(x, y):
    grad_rect(x, y, 22, 22, (120, 190, 230), (50, 120, 190))
    line(x + 2, y + 15, x + 8, y + 8, WHITE, 2)
    line(x + 8, y + 8, x + 13, y + 13, WHITE, 2)
    line(x + 13, y + 13, x + 20, y + 7, WHITE, 2)
    line(x + 3, y + 19, x + 19, y + 19, (190, 226, 248), 2)


def icon_rocket(x, y):
    grad_rect(x, y, 22, 22, (30, 44, 84), (16, 24, 52))
    fill_ellipse(x + 11, y + 9, 4, 7, (232, 236, 240))
    tri(x + 7, y + 14, x + 4, y + 19, x + 8, y + 18, RED)
    tri(x + 15, y + 14, x + 18, y + 19, x + 14, y + 18, RED)
    tri(x + 9, y + 18, x + 13, y + 18, x + 11, y + 22, GOLD_L)
    fill_circle(x + 11, y + 8, 2, (70, 130, 200))


def icon_ballot(x, y):
    grad_rect(x, y, 22, 22, (238, 232, 214), (214, 202, 168))
    rect(x + 6, y + 2, 10, 9, WHITE)
    frame(x + 6, y + 2, 10, 9, GRAY, 1)
    rect(x + 3, y + 12, 16, 3, (90, 90, 98))
    rect(x + 2, y + 15, 18, 6, (120, 96, 60))


def icon_bolt(x, y):
    grad_rect(x, y, 22, 22, (250, 226, 130), (240, 190, 70))
    pts = [(12, 2), (6, 12), (10, 12), (9, 20), (16, 9), (12, 9)]
    for i in range(len(pts) - 1):
        line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
             y + pts[i + 1][1], (150, 96, 10), 2)
    line(x + pts[-1][0], y + pts[-1][1], x + pts[0][0], y + pts[0][1],
         (150, 96, 10), 2)


def icon_drone(x, y):
    grad_rect(x, y, 22, 22, (150, 178, 208), (104, 140, 178))
    for cx, cy in ((5, 5), (17, 5), (5, 17), (17, 17)):
        fill_ellipse(x + cx, y + cy, 4, 2, (50, 54, 62))
        line(x + cx, y + cy, x + 11, y + 11, (50, 54, 62), 1)
    rect(x + 8, y + 9, 6, 4, (40, 44, 52))
    fill_circle(x + 11, y + 11, 1, RED)


def icon_asteroid(x, y):
    grad_rect(x, y, 22, 22, (24, 28, 54), (12, 14, 34))
    fill_circle(x + 3, y + 4, 1, WHITE)
    fill_circle(x + 19, y + 16, 1, WHITE)
    fill_ellipse(x + 12, y + 12, 7, 6, (150, 138, 120))
    fill_circle(x + 9, y + 10, 2, (110, 100, 84))
    fill_circle(x + 15, y + 14, 2, (110, 100, 84))
    rect(x + 2, y + 2, 4, 3, (210, 214, 220))


def icon_kidney(x, y):
    grad_rect(x, y, 22, 22, (240, 226, 226), (226, 198, 198))
    fill_ellipse(x + 12, y + 11, 7, 8, (196, 84, 104))
    fill_ellipse(x + 15, y + 11, 4, 6, (240, 226, 226))
    fill_ellipse(x + 12, y + 11, 4, 5, (214, 104, 124))


ICONS = {
    "wave": icon_wave,
    "rocket": icon_rocket,
    "ballot": icon_ballot,
    "bolt": icon_bolt,
    "drone": icon_drone,
    "asteroid": icon_asteroid,
    "kidney": icon_kidney,
}

# ---------------------------------------------------------------- layout
MX = 14
CW = W - 2 * MX


def panel(x, y, w, h, border):
    grad_rect(x, y, w, h, PANEL_T, PANEL_B)
    frame(x, y, w, h, border, 3)


def lead(x, y, w, h, region, label, headline, body, scene):
    panel(x, y, w, h, REG[region])
    cw_ = chip(x + 8, y + 7, label, LBL[label])
    draw_text(x + 16 + cw_, y + 10, region, 2, REG[region], bold=True)
    sy = y + 32
    for ln in headline:
        draw_text(x + 10, sy, ln, 3, INK, bold=True)
        sy += 24
    by = sy + 4
    for ln in body:
        draw_text(x + 10, by, ln, 2, (52, 52, 60))
        by += 16
    scene(x + w - 128, y + 30, 120, h - 38)


def brief(colx, y, label, icon, lines):
    """One brief: label square (or icon), bold first line, plain rest."""
    if icon:
        ICONS[icon](colx, y)
        tx = colx + 28
    else:
        rect(colx + 1, y + 2, 11, 11, LBL[label])
        tx = colx + 18
    ly = y
    for i, ln in enumerate(lines):
        draw_text(tx, ly, ln, 2, INK if i == 0 else (58, 58, 66),
                  bold=(i == 0))
        ly += 14
    return y + 14 * len(lines) + 2


def region_bar(x, y, w, name):
    c = REG[name]
    grad_rect(x, y, w, 19, c, tuple(max(0, v - 30) for v in c))
    draw_text(x + 7, y + 3, name, 2, WHITE, bold=True)
    return y + 22


def build():
    # paper
    grad_rect(0, 0, W, H, PAPER_T, PAPER_B)

    # ---- header
    draw_center(10, "WORLD NEWS IN ONE IMAGE - EVERY STORY DATE-CHECKED",
                2, NAVY, bold=True)
    draw_center(30, "THE THURSDAY LEDGER", 7, NAVY_D, bold=True)
    draw_center(84, "THURSDAY 26 NOVEMBER 2026", 4, RED, bold=True)
    grad_rect(MX, 116, CW, 22, NAVY, NAVY_D)
    draw_center(120, "35 STORIES - 8 REGIONS - 13 DRAWN SCENES - WORLD MAP - UTC TIMES",
                2, WHITE, bold=True)

    # ---- leads (2 x 2)
    lw = (CW - 12) // 2
    lead(MX, 146, lw, 128, "NORTH AMERICA", "FORECAST",
         ["MACY'S 100TH PARADE", "PUT OFF TO SATURDAY"],
         ["THANKSGIVING STORM: GUSTS OF", "60-65 MPH, RAIN 1-3 IN, NJ",
          "EMERGENCY - DECIDED WED"],
         scene_balloon)
    lead(MX + lw + 12, 146, lw, 128, "MIDDLE EAST", "CLAIM",
         ["OIL UP ON HORMUZ", "MINE CLAIMS"],
         ["BRENT $94.71 THU, +0.1%", "WED CLAIMS: TANKERS MINED,",
          "RAS TANURA HIT - UNVERIFIED"],
         scene_tanker)
    lead(MX, 282, lw, 128, "ASIA-PACIFIC", "CONFIRMED",
         ["ASIA RALLIES, WORLD", "REPLIES TO TARIFFS"],
         ["NIKKEI +1.6%, KOSPI +1.9%", "PLAN WAS WED: 14 LANDS,",
          "CHINA 20% - EU, BRAZIL ANGRY"],
         scene_chart)
    lead(MX + lw + 12, 282, lw, 128, "ASIA-PACIFIC", "CONFIRMED",
         ["KOREA HIKES +25BP", "TO 3.25% - VOTE 5-2"],
         ["THIRD HIKE OF 2026, HIGHEST", "SINCE OCT 2024 - GROWTH",
          "SEEN 3.9% 2026, 4.1% 2027"],
         scene_bank)

    # ---- map + Bogor row
    panel(MX, 418, 560, 92, NAVY)
    draw_text(MX + 10, 423, "THE WORLD ON ONE PAGE - STORY MAP", 2, NAVY,
              bold=True)
    scene_map(MX + 10, 441, 540, 62)
    bx = MX + 572
    bw = CW - 572
    panel(bx, 418, bw, 92, REG["ASIA-PACIFIC"])
    cw_ = chip(bx + 8, 423, "CONFIRMED", LBL["CONFIRMED"])
    draw_text(bx + 16 + cw_, 426, "INDONESIA", 2, REG["ASIA-PACIFIC"],
              bold=True)
    scene_mine(bx + bw - 118, 441, 110, 62)
    draw_text(bx + 10, 441, "BOGOR MINE SEARCH", 2, INK, bold=True)
    draw_text(bx + 10, 458, "RESUMES THU", 2, INK, bold=True)
    draw_text(bx + 10, 477, "13 DEAD, 13 TRAPPED", 2, (52, 52, 60))
    draw_text(bx + 10, 492, "6 KNOWN, FLOOD MON 23", 2, (52, 52, 60))

    # ---- UTC timeline
    grad_rect(MX, 518, CW, 42, NAVY_D, NAVY)
    draw_text(MX + 10, 525, "UTC TIMELINE", 2, GOLD_L, bold=True)
    draw_text(MX + 10, 541, "THU 26 NOV", 2, GOLD_L, bold=True)
    events = [
        "00:00 RIYADH MISSILES", "00:41 HASAKAH: 2 DEAD", "01:25 CAIRO TOLL 31",
        "01:37 BRENT $94.71", "09:22 KING TIDES", "10:06 SOMALIA TROOPS",
    ]
    ex = MX + 168
    ecol = (CW - 168) // 3
    for i, ev in enumerate(events):
        draw_text(ex + (i % 3) * ecol, 525 + (i // 3) * 16, ev, 2, WHITE)

    # ---- briefs in 3 columns
    colw = (CW - 20) // 3
    xs = [MX, MX + colw + 10, MX + 2 * (colw + 10)]
    y = 564
    # column 1
    yy = region_bar(xs[0], y, colw, "NORTH AMERICA")
    yy = brief(xs[0], yy, "FORECAST", "wave",
               ["KING TIDES FLOOD CALIF.", "ROADS - PEAK THU"])
    yy = brief(xs[0], yy, "CONFIRMED", "rocket",
               ["FCC OK: SPACEX PLAN 1M", "ORBIT DATA SATELLITES"])
    yy = brief(xs[0], yy, "CONFIRMED", None,
               ["JUDGE BLOCKS FCC EARLY", "REVIEW OF ABC LICENCE"])
    yy = brief(xs[0], yy, "REPORTED", "kidney",
               ["PIG-KIDNEY PATIENT:", "1 YEAR OFF DIALYSIS"])
    yy = region_bar(xs[0], yy + 2, colw, "LATIN AMERICA")
    yy = brief(xs[0], yy, "REPORTED", None,
               ["BRAZIL: TARIFF PLAN IS", "'UNACCEPTABLE' - 10% JETS"])
    yy = brief(xs[0], yy, "REPORTED", None,
               ["BRAZIL PULLS ENVOY FROM", "ARGENTINA, SNUBS MILEI"])
    yy = brief(xs[0], yy, "CONFIRMED", None,
               ["PUERTO RICO: LUMA POWER", "DEAL AXED 5-4 WED LOCAL"])
    yy = region_bar(xs[0], yy + 2, colw, "ASIA-PACIFIC")
    yy = brief(xs[0], yy, "REPORTED", None,
               ["KIM: WIDER TACTICAL-NUKE", "ROLE - KCNA VIA THU"])
    yy = brief(xs[0], yy, "REPORTED", None,
               ["MINIMAX DATA ACCESSED BY", "OTHERS, FIRM NAMED THU"])
    yy = brief(xs[0], yy, "REPORTED", None,
               ["AUSTRALIA TO MISS 2035", "GOAL; FIRE BURNS 6 HOMES"])
    # column 2
    yy = region_bar(xs[1], y, colw, "EUROPE")
    yy = brief(xs[1], yy, "PENDING", "ballot",
               ["SPAIN VOTES SUNDAY:", "PP+VOX LEAD POLLS"])
    yy = brief(xs[1], yy, "REPORTED", None,
               ["UK TO PUBLISH NEW EU", "TREATIES, 10-YEAR CLAUSE"])
    yy = brief(xs[1], yy, "CONFIRMED", None,
               ["UK NUKE VETS WIN INQUIRY"])
    yy = brief(xs[1], yy, "REPORTED", "bolt",
               ["UK ENERGY BILLS +26%", "JAN: 1723 TO 2166"])
    yy = brief(xs[1], yy, "REPORTED", None,
               ["POUNDLAND: 11K JOBS RISK"])
    yy = brief(xs[1], yy, "REPORTED", None,
               ["GREEK STRIKE: 15K MARCH"])
    yy = region_bar(xs[1], yy + 2, colw, "RUSSIA / UKRAINE")
    yy = brief(xs[1], yy, "REPORTED", None,
               ["LEAKED DATA: RUSSIA DEAD", "NEAR 490,334 - BBC STUDY"])
    yy = brief(xs[1], yy, "REPORTED", "drone",
               ["FPV DRONES HALT ASSAULT", "NEAR DOBROPILLIA"])
    yy = brief(xs[1], yy, "CLAIM", None,
               ["RUSSIA CLAIMS STRIKES ON", "149 DRONE SITES - CLAIM"])
    yy = region_bar(xs[1], yy + 2, colw, "GLOBAL")
    yy = brief(xs[1], yy, "CONFIRMED", None,
               ["NVIDIA RATING ON WATCH", "FOR DOWNGRADE - S+P"])
    yy = brief(xs[1], yy, "REPORTED", "asteroid",
               ["HERA SHOWS DART CRATER", "DIMORPHOS IMAGES THU"])
    # column 3
    yy = region_bar(xs[2], y, colw, "MIDDLE EAST")
    yy = brief(xs[2], yy, "REPORTED", None,
               ["BLAST IN SANAA, MISSILES", "OVER RIYADH INTERCEPTED"])
    yy = brief(xs[2], yy, "CONFIRMED", None,
               ["ISIL ATTACK IN HASAKAH:", "2 KILLED, 5 WOUNDED"])
    yy = brief(xs[2], yy, "REPORTED", None,
               ["IRAQ COURT BACKS FEDERAL", "CONTROL OF KURD OIL"])
    yy = brief(xs[2], yy, "REPORTED", None,
               ["US TELLS CITIZENS:", "LEAVE IRAN NOW"])
    yy = region_bar(xs[2], yy + 2, colw, "AFRICA")
    yy = brief(xs[2], yy, "CONFIRMED", None,
               ["CAIRO FIRE TOLL RISES", "TO 31 - FIRE WAS WED"])
    yy = brief(xs[2], yy, "CONFIRMED", None,
               ["ZAMBIA BANS PROTEST ON", "TERM-LIMIT PUSH"])
    yy = brief(xs[2], yy, "REPORTED", None,
               ["SUDAN REJECTS ETHIOPIA", "OFFER TO HOST TALKS"])
    yy = brief(xs[2], yy, "REPORTED", None,
               ["BAIDOA FAMINE RISK FALLS,", "HUNGER STILL GRIPS MANY"])
    yy = brief(xs[2], yy, "REPORTED", None,
               ["SOMALIA: TROOPS LEAVE -", "AL-SHABAB FEARS GROW"])

    # ---- legend
    ly = 948
    draw_text(MX, ly + 2, "LEGEND:", 2, INK, bold=True)
    lx = MX + 92
    for name in ("CONFIRMED", "CLAIM", "REPORTED", "PENDING", "FORECAST"):
        rect(lx, ly + 2, 12, 12, LBL[name])
        draw_text(lx + 16, ly + 2, name, 2, INK)
        lx += 16 + text_w(name, 2) + 22

    # ---- date check
    dy = 968
    grad_rect(MX, dy, CW, 54, (252, 244, 226), (248, 232, 206))
    frame(MX, dy, CW, 54, RED, 2)
    draw_text(MX + 10, dy + 4, "DATE CHECK - EXCLUDED OR RE-DATED BEFORE DRAWING:",
              2, RED_D, bold=True)
    draw_text(MX + 10, dy + 21,
              "TARIFFS WED 25 (THU FALLOUT ONLY) - CAIRO FIRE WED, TOLL 31 THU - GAZA WED",
              2, (70, 44, 40))
    draw_text(MX + 10, dy + 37,
              "SUDAN BLUE NILE TUE 24 - KIRISHI 9 NOV - SHENZHOU-24 WED - HK FIRE = 2025 ANNIV.",
              2, (70, 44, 40))

    grain()


# ---------------------------------------------------------------- png out
def encode_png():
    raw = bytearray()
    stride = W * 3
    prev = bytearray(stride)
    for yy in range(H):
        row = FB[yy * stride:(yy + 1) * stride]
        # filter type 1 (Sub) - good on gradients and flat panels alike
        filt = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            filt[i] = (row[i] - left) & 0xFF
        raw.append(1)
        raw.extend(filt)
        prev = row
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    build()
    data = encode_png()
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

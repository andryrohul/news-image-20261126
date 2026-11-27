#!/usr/bin/env python3
"""
THE THURSDAY LEDGER - V3 (picture-led edition)
Sum up 26 November 2026's world news in one image.

A picture-led front page: a big drawn hero scene (the Macy's 100th parade
balloon held down by a Thanksgiving storm), three medium drawn scenes
(Hormuz tanker + mine, Asia rally chart, Bank of Korea), a drawn world map
strip with the Bogor mine rescue beside it, and the remaining stories as
short captions in four columns. Every story is date-checked against the
brief and carries its CONFIRMED / CLAIM / REPORTED / PENDING / FORECAST
label. Pure Python 3.13 standard library: own RGB PNG encoder, own bitmap
font, own drawing. Deterministic - no randomness, no clock, no network.
Writes entry.png to $MAKEFUN_OUTPUT_DIR, else /output, else ./output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER   = (243, 238, 224)
PAPER_D = (232, 224, 203)
INK     = (24, 26, 34)
GRAY    = (96, 96, 100)
RED     = (178, 30, 38)
NAVY    = (18, 38, 74)
WHITE   = (250, 250, 246)
GOLD    = (196, 148, 32)

LBL = {
    "CONFIRMED": (22, 128, 57),
    "CLAIM":     (198, 40, 40),
    "REPORTED":  (30, 90, 200),
    "PENDING":   (10, 138, 128),
    "FORECAST":  (214, 116, 6),
}
REG = {
    "NORTH AMERICA": (30, 90, 200),
    "LATIN AMERICA": (0, 148, 108),
    "EUROPE":        (110, 60, 180),
    "RUSSIA/UKRAINE": (160, 30, 30),
    "MIDDLE EAST":   (220, 120, 0),
    "AFRICA":        (150, 100, 20),
    "ASIA-PACIFIC":  (200, 40, 120),
    "GLOBAL":        (92, 92, 92),
}

# ---------------------------------------------------------------- font 5x7
_G = {
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
"N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
"2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
"3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
"'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
"%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
"$": ("..#..", ".####", "#.#.#", ".###.", ".#.#.", "####.", "..#.."),
"#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
"(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
"&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
"*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def blend(self, x, y, c, a):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = int(self.px[i] * (1 - a) + c[0] * a)
            self.px[i + 1] = int(self.px[i + 1] * (1 - a) + c[1] * a)
            self.px[i + 2] = int(self.px[i + 2] * (1 - a) + c[2] * a)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def grad_v(self, x, y, w, h, top, bot):
        for j in range(h):
            t = j / max(1, h - 1)
            c = (int(top[0] + (bot[0] - top[0]) * t),
                 int(top[1] + (bot[1] - top[1]) * t),
                 int(top[2] + (bot[2] - top[2]) * t))
            self.rect(x, y + j, w, 1, c)
            for xx in range(x, x + w):
                d = (((xx * 73856093) ^ ((y + j) * 19349663)) % 5) - 2
                if d:
                    i = ((y + j) * self.w + xx) * 3
                    self.px[i] = max(0, min(255, self.px[i] + d))
                    self.px[i + 1] = max(0, min(255, self.px[i + 1] + d))
                    self.px[i + 2] = max(0, min(255, self.px[i + 2] + d))

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for oy in range(t):
                for ox in range(t):
                    self.set(x + ox, y + oy, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(int(x0 + (yy - y0) * (x1 - x0) / (y1 - y0)))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, c)

# ---------------------------------------------------------------- text
def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0

def draw_text(cv, s, x, y, scale, c, bold=False):
    cx = x
    for ch in s.upper():
        g = _G.get(ch, _G[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "#":
                    cv.rect(cx + col * scale, y + r * scale, scale, scale, c)
                    if bold:
                        cv.rect(cx + col * scale + max(1, scale // 2),
                                y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx

def text_c(cv, s, cx, y, scale, c, bold=False):
    draw_text(cv, s, cx - text_w(s, scale) // 2, y, scale, c, bold)

def chip(cv, label, x, y, scale=1):
    col = LBL[label]
    w = text_w(label, scale) + 8
    h = 7 * scale + 6
    cv.rect(x, y, w, h, col)
    draw_text(cv, label, x + 4, y + 3, scale, WHITE, bold=(scale >= 2))
    return w

def grain(cv, x, y, w, h, amp=5):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            v = ((xx * 73856093) ^ (yy * 19349663)) % 1000
            d = (v % (2 * amp + 1)) - amp
            if d and 0 <= xx < cv.w and 0 <= yy < cv.h:
                i = (yy * cv.w + xx) * 3
                cv.px[i] = max(0, min(255, cv.px[i] + d))
                cv.px[i + 1] = max(0, min(255, cv.px[i + 1] + d))
                cv.px[i + 2] = max(0, min(255, cv.px[i + 2] + d))

def shade_mul(cv, x, y, w, h, f):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < cv.w and 0 <= yy < cv.h:
                i = (yy * cv.w + xx) * 3
                cv.px[i] = int(cv.px[i] * f)
                cv.px[i + 1] = int(cv.px[i + 1] * f)
                cv.px[i + 2] = int(cv.px[i + 2] * f)

# ---------------------------------------------------------------- scenes
def cloud(cv, cx, cy, s, base):
    dark = tuple(int(v * 0.72) for v in base)
    cv.ellipse(cx, cy + int(4 * s), int(46 * s), int(15 * s), dark)
    cv.ellipse(cx - int(30 * s), cy + int(2 * s), int(30 * s), int(13 * s), base)
    cv.ellipse(cx + int(28 * s), cy + int(2 * s), int(32 * s), int(14 * s), base)
    cv.ellipse(cx, cy - int(6 * s), int(30 * s), int(15 * s), base)
    cv.ellipse(cx - int(8 * s), cy - int(10 * s), int(18 * s), int(11 * s),
               tuple(min(255, int(v * 1.12)) for v in base))

def balloon(cv, cx, cy, rx, ry):
    stripes = [(198, 40, 40), (232, 124, 22), (240, 192, 40), (52, 160, 74),
               (36, 100, 190), (110, 60, 180), (220, 70, 130)]
    for yy in range(cy - ry, cy + ry + 1):
        t = (yy - cy) / ry
        hw = rx * (1 - t * t) ** 0.5 if abs(t) < 1 else 0
        for xx in range(cx - rx, cx + rx + 1):
            if abs(xx - cx) <= hw:
                nx = (xx - cx) / rx
                band = int((nx + 1.0) / 2.0 * len(stripes))
                band = max(0, min(len(stripes) - 1, band))
                base = stripes[band]
                f = 1.0 - 0.38 * nx - 0.10 * t
                if nx < -0.45 and abs(t) < 0.45:
                    f += 0.16
                cv.set(xx, yy, (min(255, int(base[0] * f)),
                                min(255, int(base[1] * f)),
                                min(255, int(base[2] * f))))
    for k in range(5):
        a = -0.5 + k * 0.25
        cv.line(cx + int(rx * a * 0.9), cy + int(ry * 0.92),
                cx + int(rx * a * 0.28), cy + ry + 16, (60, 44, 30), 2)
    cv.poly([(cx - 13, cy + ry + 16), (cx + 13, cy + ry + 16),
             (cx + 10, cy + ry + 30), (cx - 10, cy + ry + 30)], (122, 82, 40))
    cv.frame(cx - 13, cy + ry + 16, 26, 14, (84, 56, 26), 2)

def person(cv, x, y, s, c):
    cv.disc(x, y, max(2, s // 2), c)
    cv.line(x, y + s // 2, x, y + s + s // 2, c, 2)
    cv.line(x, y + s + s // 2, x - s // 2, y + 2 * s, c, 2)
    cv.line(x, y + s + s // 2, x + s // 2, y + 2 * s, c, 2)

def hero_scene(cv, x, y, w, h):
    cv.grad_v(x, y, w, h, (52, 66, 96), (126, 140, 168))
    cloud(cv, x + 150, y + 26, 0.9, (104, 110, 126))
    cloud(cv, x + 520, y + 18, 1.15, (92, 99, 118))
    cloud(cv, x + 880, y + 30, 0.95, (108, 114, 132))
    cloud(cv, x + 330, y + 44, 0.7, (120, 126, 144))
    for i in range(26):
        rx0 = x + (i * 173) % w
        ry0 = y + 34 + (i * 37) % 60
        for k in range(4):
            cv.blend(rx0 + k * 3, ry0 + k * 5, (210, 220, 238), 0.5)
    for i in range(7):
        wy = y + 30 + i * 16
        for k in range(46):
            cv.blend(x + 40 + i * 130 + k * 2, wy + (k % 5) - 2,
                     (225, 232, 244), 0.35)
    rng = [61210247]
    def rnd(n):
        rng[0] = (rng[0] * 1103515245 + 12345) % 2147483648
        return rng[0] % n
    bx = x
    while bx < x + w - 30:
        bw = 26 + rnd(30)
        bh = 26 + rnd(30)
        cv.rect(bx, y + h - 20 - bh, bw, bh, (26, 32, 50))
        for wy in range(y + h - 16 - bh, y + h - 24, 8):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rnd(3) == 0:
                    cv.rect(wx, wy, 3, 4, (250, 214, 120))
        bx += bw + 3
    cv.rect(x, y + h - 20, w, 20, (34, 36, 44))
    cv.rect(x, y + h - 20, w, 2, (70, 72, 82))
    balloon(cv, x + 300, y + 56, 36, 44)
    balloon(cv, x + 620, y + 58, 62, 54)
    for hx, hc in ((x + 470, (30, 90, 200)), (x + 520, (198, 40, 40)),
                   (x + 760, (22, 128, 57)), (x + 800, (110, 60, 180))):
        cv.line(hx, y + h - 20, x + 620 + (hx - x - 620) // 6, y + 122,
                (52, 44, 34), 2)
        person(cv, hx, y + h - 38, 9, hc)
    cv.rect(x + 96, y + h - 46, 268, 24, WHITE)
    cv.frame(x + 96, y + h - 46, 268, 24, RED, 2)
    draw_text(cv, "POSTPONED TO SATURDAY", x + 110, y + h - 38, 2, RED, bold=True)

def tanker_scene(cv, x, y, w, h):
    cv.grad_v(x, y, w, h // 2, (168, 200, 226), (196, 218, 238))
    cv.grad_v(x, y + h // 2, w, h - h // 2, (36, 96, 150), (22, 64, 110))
    for i in range(9):
        wy = y + h // 2 + 6 + i * 5
        for k in range(12):
            cv.blend(x + (i * 53 + k * 24) % w, wy, (210, 232, 250), 0.4)
    hx, hy = x + 18, y + h // 2 - 4
    cv.poly([(hx, hy), (hx + 150, hy), (hx + 138, hy + 16), (hx + 12, hy + 16)],
            (150, 34, 30))
    cv.rect(hx + 8, hy - 8, 140, 8, (52, 56, 66))
    cols = [(198, 40, 40), (232, 124, 22), (36, 100, 190), (52, 160, 74)]
    for i in range(4):
        cv.rect(hx + 14 + i * 26, hy - 20, 22, 12, cols[i])
    cv.rect(hx + 122, hy - 30, 18, 22, (238, 238, 232))
    cv.rect(hx + 126, hy - 26, 10, 6, (36, 96, 150))
    mx, my = x + w - 52, y + h // 2 + 12
    for a in range(8):
        import math
        dx = int(13 * math.cos(a * 0.785))
        dy = int(13 * math.sin(a * 0.785))
        cv.line(mx, my, mx + dx, my + dy, (30, 30, 36), 3)
    cv.disc(mx, my, 10, (38, 38, 46))
    cv.disc(mx - 3, my - 3, 3, (110, 110, 122))
    for k in range(3):
        cv.line(mx - 8 + k * 2, my + 10 + k * 3, mx - 6 + k * 2, my + 12 + k * 3,
                (90, 90, 100), 2)

def chart_scene(cv, x, y, w, h):
    cv.rect(x, y, w, h, (238, 244, 238))
    for gx in range(x + 20, x + w - 8, 26):
        cv.line(gx, y + 6, gx, y + h - 16, (206, 216, 206), 1)
    for gy in range(y + 8, y + h - 14, 16):
        cv.line(x + 14, gy, x + w - 10, gy, (206, 216, 206), 1)
    cv.line(x + 14, y + 6, x + 14, y + h - 14, INK, 2)
    cv.line(x + 14, y + h - 14, x + w - 10, y + h - 14, INK, 2)
    pts = [(x + 16, y + h - 30), (x + 52, y + h - 24), (x + 88, y + h - 38),
           (x + 124, y + h - 34), (x + 160, y + h - 52), (x + 196, y + h - 48),
           (x + 232, y + h - 66), (x + 262, y + 16)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                (22, 150, 60), 4)
    ax, ay = pts[-1]
    cv.poly([(ax, ay), (ax - 14, ay + 2), (ax - 2, ay + 12)], (22, 150, 60))
    bars = [(x + 30, 20, (198, 40, 40)), (x + 66, 28, (22, 150, 60)),
            (x + 102, 24, (22, 150, 60)), (x + 138, 34, (22, 150, 60)),
            (x + 174, 30, (22, 150, 60)), (x + 210, 40, (22, 150, 60))]
    for bx, bh, bc in bars:
        cv.rect(bx, y + h - 14 - bh, 16, bh, bc)

def bank_scene(cv, x, y, w, h):
    cv.grad_v(x, y, w, h, (226, 232, 244), (196, 206, 228))
    cv.poly([(x + 26, y + 22), (x + 120, y + 2), (x + 214, y + 22)], NAVY)
    cv.rect(x + 20, y + 24, 200, 5, NAVY)
    for i in range(4):
        cx0 = x + 36 + i * 46
        cv.rect(cx0, y + 33, 13, 23, (240, 240, 234))
        cv.rect(cx0 - 2, y + 31, 17, 3, (200, 200, 192))
        cv.rect(cx0 - 2, y + 55, 17, 3, (200, 200, 192))
    cv.rect(x + 20, y + 59, 200, 4, NAVY)
    cv.rect(x + 14, y + 63, 212, 3, (120, 128, 150))
    cx, cy, r = x + w - 42, y + 24, 21
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if d2 <= r * r:
                f = 1.0 - 0.30 * ((xx - cx) / r) - 0.12 * ((yy - cy) / r)
                cv.set(xx, yy, (min(255, int(240 * f)), min(255, int(196 * f)),
                                min(255, int(60 * f))))
    text_c(cv, "%", cx, cy - 11, 3, (120, 84, 10), bold=True)

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70), (-85, 66),
     (-80, 62), (-76, 58), (-70, 45), (-75, 38), (-80, 32), (-81, 26),
     (-84, 30), (-90, 29), (-97, 26), (-97, 22), (-94, 17), (-86, 13),
     (-83, 9), (-90, 14), (-105, 20), (-110, 23), (-114, 29), (-120, 34),
     (-124, 40), (-124, 47), (-130, 55), (-150, 60), (-165, 60)],
    [(-80, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -20), (-48, -26), (-52, -33), (-58, -39),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -46),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-81, -4),
     (-80, 1)],
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (38, 22),
     (40, 15), (43, 12), (48, 11), (51, 12), (46, 5), (42, -2), (40, -10),
     (38, -18), (36, -22), (33, -26), (28, -33), (20, -35), (17, -32),
     (15, -27), (13, -18), (12, -10), (9, -1), (9, 4), (4, 6), (-3, 5),
     (-8, 5), (-13, 8), (-17, 12), (-17, 15), (-16, 20), (-15, 25),
     (-13, 28), (-10, 31)],
    [(-9, 43), (-2, 44), (-1, 46), (-5, 48), (-2, 50), (2, 51), (8, 55),
     (8, 57), (5, 60), (10, 59), (18, 56), (21, 55), (24, 58), (28, 60),
     (30, 62), (25, 66), (20, 70), (30, 70), (40, 68), (45, 66), (48, 64),
     (44, 60), (40, 55), (38, 50), (35, 46), (30, 46), (28, 41), (23, 40),
     (22, 37), (19, 40), (15, 38), (12, 42), (10, 44), (7, 44), (3, 42),
     (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (-2, 54), (-4, 51)],
    [(30, 70), (50, 70), (70, 72), (90, 75), (110, 74), (130, 72),
     (150, 70), (170, 66), (178, 65), (170, 60), (160, 55), (155, 50),
     (142, 45), (140, 40), (135, 35), (128, 33), (122, 30), (120, 25),
     (115, 23), (108, 18), (105, 9), (103, 5), (100, 8), (98, 12),
     (95, 16), (92, 16), (89, 22), (86, 20), (80, 13), (77, 8), (72, 20),
     (68, 23), (61, 25), (57, 26), (51, 28), (48, 30), (44, 29), (40, 31),
     (36, 36), (36, 42), (40, 46), (44, 50), (48, 55), (50, 60), (45, 66),
     (40, 68)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 44), (138, 38), (135, 34), (131, 32)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -30), (153, -25), (150, -22), (146, -19), (142, -11), (142, -14),
     (139, -17), (136, -15), (135, -12), (132, -11), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]
PINS = [(-74, 41), (56, 27), (127, 38), (139, 36), (107, -7), (31, 30),
        (31, 50), (24, 38), (-48, -16), (151, -34), (-66, 18), (-122, 37)]

def map_strip(cv, x, y, w, h):
    cv.grad_v(x, y, w, h, (20, 52, 96), (14, 38, 74))
    for gx in range(0, 13):
        lx = x + gx * w // 12
        cv.line(lx, y, lx, y + h, (30, 66, 116), 1)
    for gy in range(0, 5):
        ly = y + gy * h // 4
        cv.line(x, ly, x + w, ly, (30, 66, 116), 1)
    def proj(lon, lat):
        return (x + int((lon + 180) / 360.0 * w),
                y + int((85 - lat) / 160.0 * h))
    land = (74, 148, 84)
    for cont in CONTINENTS:
        cv.poly([proj(lon, lat) for lon, lat in cont], land)
    for cx0, cy0, r in ((104, -2, 5), (113, -3, 4), (119, -4, 4), (99, 3, 3)):
        px, py = proj(cx0, cy0)
        cv.disc(px, py, r, land)
    for lon, lat in PINS:
        px, py = proj(lon, lat)
        cv.disc(px, py, 4, RED)
        cv.disc(px, py, 2, WHITE)

def bogor_scene(cv, x, y, w, h):
    cv.grad_v(x, y, w, h, (196, 214, 200), (150, 176, 148))
    cv.poly([(x, y + h), (x + 26, y + 30), (x + 54, y + h)], (122, 94, 58))
    cv.poly([(x + 26, y + 30), (x + w - 2, y + h), (x + 54, y + h)],
            (140, 110, 66))
    cv.ellipse(x + 40, y + 68, 10, 7, (16, 12, 10))
    cv.line(x + w - 16, y + 12, x + w - 16, y + 46, (70, 70, 76), 3)
    cv.line(x + w - 16, y + 12, x + 44, y + 24, (70, 70, 76), 2)
    cv.line(x + 50, y + 26, x + 50, y + 40, (70, 70, 76), 1)
    cv.rect(x + 45, y + 40, 10, 7, (196, 148, 32))
    cv.poly([(x + w - 30, y + h), (x + w - 16, y + 54), (x + w - 2, y + h)],
            WHITE)
    cv.rect(x + w - 18, y + 64, 4, 11, RED)
    cv.rect(x + w - 22, y + 68, 12, 4, RED)
    person(cv, x + 14, y + h - 26, 8, (232, 124, 22))
    person(cv, x + 26, y + h - 24, 8, (232, 124, 22))
    cv.rect(x, y + h - 4, w, 4, (96, 76, 48))

# ---------------------------------------------------------------- briefs
# (region, label, line1, line2)
BRIEFS = [
    ("NORTH AMERICA", "FORECAST", "KING TIDES FLOOD", "CALIF. ROADS THU"),
    ("NORTH AMERICA", "CONFIRMED", "FCC OK SPACEX PLAN", "1M ORBIT DATA SATS"),
    ("NORTH AMERICA", "CONFIRMED", "JUDGE BLOCKS FCC", "EARLY ABC REVIEW"),
    ("NORTH AMERICA", "REPORTED", "TRUMP OPEN TO DEMS", "HEALTHCARE TALKS"),
    ("NORTH AMERICA", "REPORTED", "PIG-KIDNEY PATIENT", "1 YR OFF DIALYSIS"),
    ("LATIN AMERICA", "REPORTED", "BRAZIL TARIFF PLAN", "'UNACCEPTABLE' 10%"),
    ("LATIN AMERICA", "REPORTED", "BRAZIL PULLS ENVOY", "FROM ARGENTINA"),
    ("LATIN AMERICA", "CONFIRMED", "PUERTO RICO: LUMA", "AXED 5-4 WED LOCAL"),
    ("EUROPE", "PENDING", "SPAIN VOTES SUNDAY", "PP+VOX LEAD POLLS"),
    ("EUROPE", "REPORTED", "UK-EU TREATIES DUE", "10-YR EXIT CLAUSE"),
    ("EUROPE", "CONFIRMED", "UK NUKE VETS WIN", "40-YEAR INQUIRY"),
    ("EUROPE", "REPORTED", "UK ENERGY BILLS UP", "+26% JAN: 1723>2166"),
    ("EUROPE", "REPORTED", "POUNDLAND COLLAPSE", "11K JOBS AT RISK"),
    ("EUROPE", "REPORTED", "GREEK STRIKE: 15K", "MARCH IN ATHENS"),
    ("RUSSIA/UKRAINE", "REPORTED", "LEAKED DATA: RUSSIA", "DEAD NEAR 490,334"),
    ("RUSSIA/UKRAINE", "REPORTED", "FPV DRONES HALT", "DOBROPILLIA ASSAULT"),
    ("RUSSIA/UKRAINE", "CLAIM", "RUSSIA CLAIMS HITS", "ON 149 DRONE SITES"),
    ("MIDDLE EAST", "REPORTED", "BLAST IN SANAA;", "MISSILES ON RIYADH"),
    ("MIDDLE EAST", "CONFIRMED", "ISIL ATTACK HASAKAH", "2 DEAD, 5 WOUNDED"),
    ("MIDDLE EAST", "REPORTED", "IRAQ COURT BACKS", "FED. KURD OIL AUDIT"),
    ("MIDDLE EAST", "REPORTED", "US TELLS CITIZENS:", "LEAVE IRAN NOW"),
    ("AFRICA", "CONFIRMED", "CAIRO FIRE TOLL 31", "- FIRE WAS WED"),
    ("AFRICA", "CONFIRMED", "ZAMBIA PROTEST BAN", "ON TERM-LIMIT PUSH"),
    ("AFRICA", "REPORTED", "SUDAN: NO TO TALKS", "ETHIOPIA OFFER"),
    ("AFRICA", "REPORTED", "BAIDOA FAMINE RISK", "FALLS, HUNGER STAYS"),
    ("AFRICA", "REPORTED", "SOMALIA: TROOPS GO", "SHABAB FEARS GROW"),
    ("ASIA-PACIFIC", "REPORTED", "KIM WIDER TACTICAL", "NUKE ROLE - KCNA"),
    ("ASIA-PACIFIC", "REPORTED", "MINIMAX DATA HIT:", "ACCESSED BY OTHERS"),
    ("ASIA-PACIFIC", "REPORTED", "213 INDIANS MISSING", "PRESUMED DEAD"),
    ("ASIA-PACIFIC", "REPORTED", "AUSTRALIA TO MISS", "2035 EMISSIONS GOAL"),
    ("GLOBAL", "REPORTED", "HERA SHOWS DART", "CRATER ON DIMORPHOS"),
]
COLS = [BRIEFS[0:8], BRIEFS[8:16], BRIEFS[16:24], BRIEFS[24:31]]

# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    grain(cv, 0, 0, W, H, 4)

    # ---- masthead
    text_c(cv, "WORLD NEWS IN ONE IMAGE - EVERY STORY DATE-CHECKED", 512, 8, 1,
           GRAY)
    text_c(cv, "THE THURSDAY LEDGER", 512, 20, 9, INK)
    cv.rect(12, 86, 1000, 3, INK)
    draw_text(cv, "THURSDAY 26 NOVEMBER 2026", 12, 94, 3, RED, bold=True)
    strap = "35 STORIES - 8 REGIONS - UTC TIMES"
    draw_text(cv, strap, 1012 - text_w(strap, 2), 99, 2, NAVY, bold=True)
    cv.rect(12, 118, 1000, 2, INK)

    # ---- hero
    hero_scene(cv, 12, 126, 1000, 144)
    cv.frame(12, 126, 1000, 144, INK, 2)
    cw = chip(cv, "FORECAST", 12, 278)
    draw_text(cv, "NORTH AMERICA - THANKSGIVING DAY", 12 + cw + 10, 281, 2,
              REG["NORTH AMERICA"], bold=True)
    text_c(cv, "MACY'S 100TH PARADE PUT OFF TO SATURDAY", 512, 300, 4, INK,
           bold=True)
    sub = ("STORM FORECAST: GUSTS 60-65 MPH, RAIN 1-3 IN, NJ EMERGENCY"
           " - DECISION DATED WED")
    text_c(cv, sub, 512, 334, 2, (70, 70, 76))

    # ---- middle band: three scenes
    panels = [
        ("CLAIM", "MIDDLE EAST", tanker_scene,
         ["OIL UP ON HORMUZ", "MINE CLAIMS"],
         ["BRENT $94.71 THU +0.1%", "WED CLAIMS UNVERIFIED"]),
        ("CONFIRMED", "ASIA-PACIFIC", chart_scene,
         ["ASIA RALLIES AS", "WORLD REPLIES TO"],
         ["TARIFFS: NIKKEI +1.6%", "KOSPI +1.9% - PLAN WED"]),
        ("CONFIRMED", "ASIA-PACIFIC", bank_scene,
         ["KOREA HIKES +25BP", "TO 3.25%"],
         ["VOTE 5-2 - 3RD HIKE 2026", "GROWTH SEEN 3.9% IN 2026"]),
    ]
    pw = (1000 - 24) // 3
    for i, (lab, reg, scene, head, subs) in enumerate(panels):
        px = 12 + i * (pw + 12)
        py = 356
        cv.rect(px, py, pw, 184, WHITE)
        cv.frame(px, py, pw, 184, INK, 2)
        cw = chip(cv, lab, px + 8, py + 6)
        draw_text(cv, reg, px + 8 + cw + 8, py + 9, 1, REG[reg], bold=True)
        scene(cv, px + 10, py + 28, pw - 20, 64)
        cv.frame(px + 10, py + 28, pw - 20, 64, (150, 150, 150), 1)
        hy = py + 98
        for ln in head:
            draw_text(cv, ln, px + 10, hy, 3, INK, bold=True)
            hy += 23
        for sline in subs:
            draw_text(cv, sline, px + 10, hy + 1, 2, (70, 70, 76))
            hy += 16

    # ---- map strip + bogor
    my = 548
    cv.rect(12, my, 656, 104, WHITE)
    cv.frame(12, my, 656, 104, INK, 2)
    draw_text(cv, "THE WORLD ON ONE PAGE - STORY MAP", 22, my + 6, 2, NAVY,
              bold=True)
    map_strip(cv, 22, my + 26, 636, 70)
    bx = 680
    cv.rect(bx, my, 332, 104, WHITE)
    cv.frame(bx, my, 332, 104, INK, 2)
    bogor_scene(cv, bx + 8, my + 8, 84, 88)
    tx = bx + 102
    cw = chip(cv, "CONFIRMED", tx, my + 6)
    draw_text(cv, "INDONESIA", tx + cw + 6, my + 9, 1, REG["ASIA-PACIFIC"],
              bold=True)
    draw_text(cv, "BOGOR MINE SEARCH", tx, my + 26, 2, INK, bold=True)
    draw_text(cv, "RESUMES THURSDAY", tx, my + 42, 2, INK, bold=True)
    draw_text(cv, "13 DEAD, 13 TRAPPED", tx, my + 60, 2, (70, 70, 76))
    draw_text(cv, "6 IDENTIFIED - FLOOD WAS MON 23 NOV", tx, my + 80, 1,
              (150, 40, 40))

    # ---- UTC timeline
    ty = 660
    cv.rect(12, ty, 1000, 24, NAVY)
    draw_text(cv, "UTC", 22, ty + 5, 2, GOLD, bold=True)
    tl1 = ("00:00 SANAA BLAST / RIYADH MISSILES - 00:41 HASAKAH: 2 DEAD"
           " - 01:25 CAIRO TOLL 31")
    tl2 = ("01:37 BRENT $94.71 - 09:22 KING TIDES PEAK - 10:06 SOMALIA"
           " TROOPS - THU 26 NOV")
    draw_text(cv, tl1, 76, ty + 2, 1, WHITE)
    draw_text(cv, tl2, 76, ty + 13, 1, WHITE)

    # ---- briefs: short captions, 4 columns
    # left bar = story label (see legend), square = region chip
    by = 696
    colw = 244
    for ci, col in enumerate(COLS):
        cx0 = 12 + ci * (colw + 8)
        if ci:
            cv.line(cx0 - 5, by, cx0 - 5, by + 232, (198, 190, 168), 1)
        for ri, (reg, lab, l1, l2) in enumerate(col):
            ry = by + ri * 30
            cv.rect(cx0, ry + 1, 3, 24, LBL[lab])
            cv.rect(cx0 + 6, ry + 2, 7, 7, REG[reg])
            draw_text(cv, l1, cx0 + 17, ry, 2, INK, bold=True)
            draw_text(cv, l2, cx0 + 17, ry + 15, 2, (70, 70, 76))

    # ---- footer: legend + date check
    fy = 938
    draw_text(cv, "LABEL BAR:", 12, fy + 2, 2, INK, bold=True)
    lx = 12 + text_w("LABEL BAR:", 2) + 10
    for lab in ("CONFIRMED", "CLAIM", "REPORTED", "PENDING", "FORECAST"):
        cv.rect(lx, fy + 3, 10, 10, LBL[lab])
        draw_text(cv, lab, lx + 14, fy + 3, 1, INK)
        lx += 14 + text_w(lab, 1) + 12
    rkey = "NA LATAM EU RU ME AF APAC GLOB = REGION CHIP"
    draw_text(cv, rkey, 1012 - text_w(rkey, 1), fy + 3, 1, GRAY)
    dy = 958
    cv.rect(12, dy, 1000, 58, (250, 244, 232))
    cv.frame(12, dy, 1000, 58, RED, 2)
    draw_text(cv, "DATE CHECK - EXCLUDED OR RE-DATED BEFORE DRAWING:", 22,
              dy + 6, 2, RED, bold=True)
    draw_text(cv, "TARIFF PLAN WED - CAIRO FIRE WED (ONLY TOLL 31 IS THU)"
              " - GAZA STRIKE WED", 22, dy + 24, 2, INK)
    draw_text(cv, "SUDAN BLUE NILE TUE 24 - KIRISHI 9 NOV - SHENZHOU-24 WED"
              " - HK FIRE 2025", 22, dy + 40, 2, INK)
    return cv

# ---------------------------------------------------------------- png out
def write_png(cv, path):
    raw = bytearray()
    row = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * row:(y + 1) * row]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "./output"
    os.makedirs(outdir, exist_ok=True)
    cv = build()
    n = write_png(cv, os.path.join(outdir, "entry.png"))
    print("wrote entry.png", n, "bytes")

if __name__ == "__main__":
    main()

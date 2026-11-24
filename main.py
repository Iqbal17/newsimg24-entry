#!/usr/bin/env python3
"""The World in One Day - Tuesday 24 November 2026.

A program that draws a newspaper front page summing up the day's world
news in a single picture: eight story panels, each with a hand-drawn icon,
a bold headline and a one-line caption, under a masthead that names the
day. Everything is built in code with only the Python standard library:
the PNG encoder, the bitmap letterforms and every icon are defined here,
so the picture is byte-for-byte identical on every run.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (1024x1024, deterministic).
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ------------------------------------------------------------------ colours
PAPER = (250, 246, 236)   # warm newsprint
INK = (26, 26, 30)        # near-black ink
NAVY = (20, 42, 80)       # secondary colour
RED = (182, 32, 38)       # accent colour
GOLD = (196, 146, 30)     # secondary colour
GREY = (120, 116, 106)    # thin rules and frames
WHITE = (255, 255, 255)

# -------------------------------------------------------------------- font
# 5x7 bitmap letterforms, drawn by hand for this entry. Each glyph is 7
# rows of 5 cells; '#' is a filled cell, '.' is empty.
GLYPHS = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#.#.#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
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
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
}


def glyph_width(s, scale):
    """Pixel width of string s rendered at the given scale."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def wrap_text(s, scale, max_w):
    """Greedy word wrap returning lines that each fit inside max_w."""
    words = s.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if glyph_width(trial, scale) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_text(s, scale, max_w):
    """Shorten s by dropping words from the end until it fits max_w."""
    while len(s.split()) > 1 and glyph_width(s, scale) > max_w:
        s = s.rsplit(" ", 1)[0]
    return s


# ------------------------------------------------------------------- sheet
class Sheet:
    """An RGB canvas held as a flat bytearray, drawn pixel by pixel."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def box(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, c)

    def frame(self, x, y, w, h, c, t=2):
        self.box(x, y, w, t, c)
        self.box(x, y + h - t, w, t, c)
        self.box(x, y, t, h, c)
        self.box(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.dot(xx, yy, c)
                elif (r - 2) * (r - 2) < d2 <= r * r:
                    self.dot(xx, yy, c)

    def stroke(self, x0, y0, x1, y1, c, t=2):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        half = t // 2
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            for dy in range(-half, t - half):
                for dx in range(-half, t - half):
                    self.dot(x + dx, y + dy, c)

    def wedge(self, x0, y0, x1, y1, x2, y2, c):
        """Filled triangle, tested point by point against its edges."""
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)

        def side(ax, ay, bx, by, px, py):
            return (px - ax) * (by - ay) - (py - ay) * (bx - ax)

        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                d0 = side(x0, y0, x1, y1, xx, yy)
                d1 = side(x1, y1, x2, y2, xx, yy)
                d2 = side(x2, y2, x0, y0, xx, yy)
                if (d0 >= 0 and d1 >= 0 and d2 >= 0) or \
                        (d0 <= 0 and d1 <= 0 and d2 <= 0):
                    self.dot(xx, yy, c)

    def write(self, x, y, s, scale, c):
        for ch in s.upper():
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.box(x + col * scale, y + row * scale,
                                 scale, scale, c)
            x += 6 * scale
        return x

    def write_centred(self, cx, y, s, scale, c):
        return self.write(cx - glyph_width(s, scale) // 2, y, s, scale, c)


# ------------------------------------------------------------------- icons
# Every icon draws inside a 96x96 tile whose top-left corner is (x, y).
def icon_ship(sh, x, y, c):
    sh.box(x + 46, y + 14, 4, 44, c)                       # mast
    sh.wedge(x + 50, y + 14, x + 50, y + 26, x + 66, y + 20, RED)  # flag
    sh.box(x + 30, y + 44, 26, 12, c)                     # deck cabin
    sh.wedge(x + 10, y + 56, x + 86, y + 56, x + 76, y + 74, c)  # hull
    sh.wedge(x + 10, y + 56, x + 76, y + 74, x + 20, y + 74, c)
    sh.stroke(x + 8, y + 84, x + 28, y + 84, c, 3)        # waves
    sh.stroke(x + 36, y + 84, x + 56, y + 84, c, 3)
    sh.stroke(x + 64, y + 84, x + 88, y + 84, c, 3)


def icon_flame(sh, x, y, c):
    sh.wedge(x + 48, y + 8, x + 28, y + 58, x + 68, y + 58, RED)  # outer
    sh.disc(x + 48, y + 60, 20, RED)
    sh.wedge(x + 48, y + 34, x + 38, y + 62, x + 58, y + 62, GOLD)  # inner
    sh.disc(x + 48, y + 64, 10, GOLD)
    sh.stroke(x + 22, y + 80, x + 74, y + 86, INK, 4)     # crossed logs
    sh.stroke(x + 74, y + 80, x + 22, y + 86, INK, 4)


def icon_city(sh, x, y, c):
    # skyline of apartment blocks under a plume of smoke
    sh.box(x + 12, y + 52, 20, 32, c)
    sh.box(x + 36, y + 36, 20, 48, c)
    sh.box(x + 60, y + 58, 20, 26, c)
    for wx, wy in ((17, 58), (25, 66), (41, 42), (49, 50), (65, 64),
                   (73, 72)):
        sh.box(x + wx, y + wy, 4, 4, PAPER)                 # lit windows
    sh.disc(x + 46, y + 26, 6, GREY)                        # smoke
    sh.disc(x + 56, y + 18, 5, GREY)
    sh.disc(x + 38, y + 20, 4, GREY)
    sh.box(x + 8, y + 84, 80, 4, c)                         # ground


def icon_globe(sh, x, y, c):
    sh.disc(x + 48, y + 48, 34, c, fill=False)            # rim
    sh.stroke(x + 14, y + 48, x + 82, y + 48, c, 2)       # equator
    sh.stroke(x + 48, y + 14, x + 48, y + 82, c, 2)       # meridian
    sh.stroke(x + 22, y + 30, x + 74, y + 30, c, 2)       # latitudes
    sh.stroke(x + 22, y + 66, x + 74, y + 66, c, 2)
    sh.disc(x + 36, y + 36, 7, c)                         # land blobs
    sh.disc(x + 60, y + 58, 6, c)


def icon_gavel(sh, x, y, c):
    # head: a thick bar angled across the top of the tile, with a band
    # across each end; the handle runs diagonally down from the head's
    # middle, so the whole gavel reads at a jaunty angle
    sh.stroke(x + 16, y + 34, x + 64, y + 16, c, 16)          # head
    sh.stroke(x + 12, y + 24, x + 20, y + 44, c, 6)          # left cap
    sh.stroke(x + 60, y + 6, x + 68, y + 26, c, 6)           # right cap
    sh.stroke(x + 40, y + 25, x + 76, y + 76, c, 7)          # handle
    sh.box(x + 16, y + 84, 64, 6, c)                          # sounding block


def icon_trophy(sh, x, y, c):
    sh.box(x + 22, y + 12, 52, 6, GOLD)                   # rim
    sh.wedge(x + 24, y + 18, x + 72, y + 18, x + 60, y + 46, GOLD)  # bowl
    sh.wedge(x + 24, y + 18, x + 60, y + 46, x + 36, y + 46, GOLD)
    sh.disc(x + 20, y + 28, 8, GOLD, fill=False)          # handles
    sh.disc(x + 76, y + 28, 8, GOLD, fill=False)
    sh.box(x + 44, y + 46, 8, 18, GOLD)                   # stem
    sh.box(x + 32, y + 64, 32, 8, GOLD)                   # base
    sh.box(x + 26, y + 72, 44, 8, GOLD)


def icon_chess(sh, x, y, c):
    sh.box(x + 46, y + 8, 4, 14, c)                       # cross
    sh.box(x + 41, y + 12, 14, 4, c)
    sh.disc(x + 48, y + 30, 10, c)                        # head
    sh.box(x + 38, y + 40, 20, 8, c)                      # collar
    sh.wedge(x + 38, y + 76, x + 58, y + 76, x + 48, y + 48, c)  # body
    sh.box(x + 28, y + 76, 40, 8, c)                      # base


def icon_satellite(sh, x, y, c):
    sh.box(x + 6, y + 40, 26, 14, GOLD)                   # solar panels
    sh.box(x + 64, y + 40, 26, 14, GOLD)
    sh.box(x + 38, y + 36, 20, 22, c)                     # body
    sh.stroke(x + 48, y + 36, x + 48, y + 20, c, 3)       # antenna
    sh.disc(x + 48, y + 16, 4, RED)                       # beacon
    sh.disc(x + 48, y + 16, 9, RED, fill=False)           # signal ring
    sh.wedge(x + 48, y + 58, x + 38, y + 72, x + 58, y + 72, c)  # dish


def icon_stadium(sh, x, y, c):
    sh.stroke(x + 12, y + 58, x + 12, y + 22, c, 3)       # floodlights
    sh.stroke(x + 84, y + 58, x + 84, y + 22, c, 3)
    sh.disc(x + 12, y + 18, 5, GOLD)
    sh.disc(x + 84, y + 18, 5, GOLD)
    sh.box(x + 26, y + 34, 44, 10, c)                     # tiers
    sh.box(x + 18, y + 46, 60, 10, c)
    sh.box(x + 10, y + 58, 76, 10, c)
    sh.box(x + 18, y + 72, 60, 8, GOLD)                   # pitch


# ------------------------------------------------------------------ stories
# (kicker, headline, caption, icon, accent)
STORIES = [
    ("UKRAINE - BLACK SEA", "UKRAINE SINKS RUSSIAN WARSHIP",
     "MERKURY SUNK OFF LIBYA", icon_ship, NAVY),
    ("CLIMATE - COP31", "COP31 ENDS WITH NO DEAL",
     "SUMMIT CLOSES WITH NO DEAL", icon_globe, NAVY),
    ("INDONESIA - CANDY FACTORY", "FACTORY FIRE KILLS 24",
     "24 DEAD, DOZENS MISSING", icon_flame, RED),
    ("KYIV REGION - UKRAINE", "14 KILLED IN KYIV STRIKES",
     "DRONE AND MISSILE ATTACKS", icon_city, INK),
    ("THE HAGUE - ICJ", "MYANMAR COMMITTED GENOCIDE",
     "UN COURT RULES ON ROHINGYA", icon_gavel, NAVY),
    ("SPORT - TURIN", "ALCARAZ WINS ATP FINALS",
     "BEATS ZVEREV IN TURIN", icon_trophy, GOLD),
    ("CHESS - GENEVA", "CHESS TITLE DEFENCE BEGINS",
     "GUKESH FACES SINDAROV", icon_chess, INK),
    ("SPACE - NATO", "NATO VOWS SPACE DEFENCE",
     "AFTER SATELLITE REPORT", icon_satellite, RED),
]


def draw():
    sh = Sheet(W, H, PAPER)
    sh.frame(8, 8, W - 16, H - 16, INK, 4)
    sh.frame(20, 20, W - 40, H - 40, INK, 1)

    # Masthead: the paper's name, then the day in a navy band.
    sh.write_centred(W // 2, 40, "THE WORLD IN ONE DAY", 6, INK)
    sh.box(40, 100, W - 80, 3, INK)
    sh.box(40, 108, W - 80, 52, NAVY)
    sh.write_centred(W // 2, 120, "TUESDAY 24 NOVEMBER 2026", 4, WHITE)
    sh.write_centred(W // 2, 170, "EIGHT STORIES - ONE DAY - ONE PICTURE",
                     2, GREY)

    # Story grid: 2 columns x 4 rows.
    gy = 196
    pw, ph = 466, 172
    for i, (kicker, head, caption, icon, accent) in enumerate(STORIES):
        x = 40 + (i % 2) * (pw + 12)
        y = gy + (i // 2) * (ph + 10)
        sh.frame(x, y, pw, ph, INK, 2)
        sh.box(x, y, pw, 6, accent)
        # story number, top right
        sh.box(x + pw - 38, y + 10, 26, 24, NAVY)
        sh.write_centred(x + pw - 25, y + 15, str(i + 1), 2, WHITE)
        # kicker
        sh.write(x + 14, y + 14, kicker, 2, RED)
        # icon tile, left
        sh.frame(x + 14, y + 38, 96, 96, GREY, 1)
        icon(sh, x + 14, y + 38, accent if accent != INK else NAVY)
        # headline (bold, at most two lines) and one-line caption
        tx = x + 124
        lines = wrap_text(head, 3, pw - 124 - 14)
        for j, ln in enumerate(lines[:2]):
            sh.write(tx, y + 40 + j * 26, ln, 3, INK)
        sh.write(tx, y + 100, fit_text(caption, 2, pw - 124 - 14), 2, INK)
        # thin rule near the bottom of the panel
        sh.box(x + 14, y + 150, pw - 28, 2, GREY)

    # Footer: the World Cup host line, then the date line. A tiny stadium
    # motif flanks the host line on both sides.
    sh.box(40, 922, W - 80, 2, INK)
    for sx in (64, 896):
        sh.box(sx + 12, 932, 24, 5, NAVY)
        sh.box(sx + 6, 938, 36, 5, NAVY)
        sh.box(sx, 944, 48, 5, NAVY)
        sh.box(sx + 6, 951, 36, 4, GOLD)
    sh.write_centred(W // 2, 932,
                     "ALSO: UK CONFIRMED AS 2035 WOMEN'S WORLD CUP HOST",
                     2, NAVY)
    sh.write_centred(W // 2, 956, "24 NOVEMBER 2026 - THE WORLD IN ONE DAY",
                     2, INK)
    return sh


def encode_png(sh):
    raw = bytearray()
    for yy in range(sh.h):
        raw.append(0)  # no filter
        start = yy * sh.w * 3
        raw += sh.px[start:start + sh.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", sh.w, sh.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()

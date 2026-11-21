# main.py — draws "The World in One Day: Saturday 21 November 2026" as a
# 1024x1024 editorial news poster and writes it to /output/entry.png.
#
# Pure Python 3 standard library: the PNG is encoded by hand (zlib +
# CRC32), the lettering comes from font5x7.py, and every fact rendered
# comes from stories.py. No network, no third-party library, no clock:
# running it twice writes the same bytes.
#
# Local run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import struct
import sys
import zlib
from binascii import crc32

# The grader runs `python3 -P -s main.py` (safe path: the script's own
# directory is NOT added to sys.path), so make the sibling modules
# importable regardless of the working directory or -P.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import font5x7
import stories

W, H = 1024, 1024

# Palette: newsprint paper, ink, and a few flat poster colours.
PAPER = (248, 244, 236)
INK = (26, 26, 26)
NAVY = (22, 35, 63)
RED = (185, 28, 28)
GOLD = (180, 83, 9)
TEAL = (15, 118, 110)
GREY = (107, 114, 128)
LIGHT = (226, 220, 208)
SKY = (43, 58, 85)
DARK = (20, 28, 43)
FIRE = (249, 115, 22)
FLAME = (250, 204, 21)
WHITE = (255, 255, 255)
BLUE = (59, 130, 246)


class Canvas:
    """A flat RGB canvas with simple vector drawing."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)
        self.fill_rect(x, y + h - thick, w, thick, colour)
        self.fill_rect(x, y, thick, h, colour)
        self.fill_rect(x + w - thick, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x0 + a, y0 + b, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            if abs(yy - cy) > r:
                continue
            half = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, colour)

    def triangle(self, pts, colour):
        (x0, y0), (x1, y1), (x2, y2) = pts
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            for xx in range(min(x0, x1, x2), max(x0, x1, x2) + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, colour)


# ---------------------------------------------------------------- text

def text_width(s, scale):
    """Width in pixels of s at this scale (6 px per glyph cell)."""
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, colour):
    """Draw s with its top-left at (x, y); returns the width drawn."""
    cx = x
    for ch in s:
        rows = font5x7.glyph(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1':
                    cv.fill_rect(cx + rx * scale, y + ry * scale,
                                 scale, scale, colour)
        cx += 6 * scale
    return cx - x - scale if s else 0


def draw_text_centred(cv, cx, y, s, scale, colour):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, colour)


def wrap(s, scale, max_width):
    """Greedy word wrap of s to lines at most max_width pixels wide."""
    words = s.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, s, scale, colour, max_width, line_h):
    lines = wrap(s, scale, max_width)
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * line_h, ln, scale, colour)
    return y + len(lines) * line_h


# ---------------------------------------------------------------- PNG

def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    return out + struct.pack('>I', crc32(kind + data) & 0xffffffff)


def encode_png(cv):
    """Encode the canvas as a whole PNG: header, image data, end."""
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none, on every row
        i = yy * cv.w * 3
        raw += cv.px[i:i + cv.w * 3]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr)
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    return png


# ------------------------------------------------------- illustrations

def draw_kyiv(cv, x, y, w, h):
    """Night skyline over the Dnipro: bridges, bursts, smoke."""
    cv.fill_rect(x, y, w, h, SKY)
    # a few small stars
    for sx, sy in ((30, 22), (90, 48), (170, 18), (250, 40), (330, 26),
                   (130, 66), (300, 70), (60, 88), (210, 84)):
        cv.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    # skyline silhouettes, back row then front row
    for bx, bw, bh in ((0, 46, 120), (52, 34, 150), (92, 58, 100),
                       (156, 40, 165), (202, 52, 118), (260, 38, 148),
                       (304, 56, 104), (366, 30, 132)):
        cv.fill_rect(x + bx, y + h - 84 - bh, bw, bh + 84, DARK)
    # lit windows in the towers
    for wx, wy in ((12, 130), (30, 150), (62, 110), (104, 140), (122, 120),
                   (168, 96), (214, 132), (232, 108), (272, 118),
                   (316, 138), (344, 116), (376, 140), (146, 150)):
        cv.fill_rect(x + wx, y + wy, 5, 7, (245, 197, 66))
    # river band along the bottom
    cv.fill_rect(x, y + h - 84, w, 84, (28, 44, 68))
    for rx in range(0, w, 44):
        cv.fill_rect(x + rx, y + h - 60, 26, 3, (74, 110, 150))
        cv.fill_rect(x + rx + 12, y + h - 34, 26, 3, (74, 110, 150))
    # the bridge: deck, arch and piers across the river
    by = y + h - 84
    cv.fill_rect(x, by - 6, w, 8, (200, 200, 200))
    for px in range(20, w, 56):
        cv.fill_rect(x + px, by - 6, 6, 84, (200, 200, 200))
    cv.line(x + 10, by - 6, x + w // 2, by - 58, (200, 200, 200), 4)
    cv.line(x + w - 10, by - 6, x + w // 2, by - 58, (200, 200, 200), 4)
    # explosion bursts above the skyline
    for cx, cy, r in ((120, 92, 34), (300, 70, 26)):
        cv.disc(x + cx, y + cy, r, FIRE)
        cv.disc(x + cx, y + cy, int(r * 0.62), FLAME)
        cv.disc(x + cx, y + cy, int(r * 0.3), WHITE)
    # smoke drifting from the bursts
    for cx, cy, r in ((150, 60, 16), (176, 44, 12), (326, 44, 13),
                      (348, 30, 10)):
        cv.disc(x + cx, y + cy, r, GREY)


def draw_scales(cv, x, y, s):
    """Scales of justice for the world court's genocide ruling."""
    cv.fill_rect(x, y, s, s, (232, 226, 214))
    cx = x + s // 2
    # central pillar and crossbeam
    cv.fill_rect(cx - 2, y + 10, 4, s - 24, INK)
    cv.fill_rect(cx - 24, y + 14, 48, 4, INK)
    cv.fill_rect(cx - 12, y + s - 14, 24, 4, INK)
    # two hanging pans: shallow trays on short cords
    for side in (-1, 1):
        px = cx + side * 24
        cv.line(px, y + 18, px, y + 32, INK, 2)
        cv.fill_rect(px - 13, y + 32, 26, 3, GOLD)
        cv.fill_rect(px - 10, y + 35, 20, 2, GOLD)
    # a small base block below the pillar
    cv.fill_rect(cx - 12, y + s - 14, 24, 4, INK)


def draw_drone(cv, x, y, s):
    """A drone over a tanker in the Strait of Hormuz."""
    cv.fill_rect(x, y, s, s, (214, 228, 226))
    # sea band along the bottom
    cv.fill_rect(x, y + s - 22, s, 22, BLUE)
    for wx in range(0, s, 18):
        cv.fill_rect(x + wx, y + s - 14, 10, 2, WHITE)
    # tanker: hull, deck and funnel
    cv.fill_rect(x + 6, y + s - 34, s - 12, 12, (90, 96, 110))
    cv.fill_rect(x + 14, y + s - 46, 18, 12, (90, 96, 110))
    cv.fill_rect(x + 46, y + s - 42, 6, 8, RED)
    # the drone: body, wings and rotor arcs
    dx, dy = x + s // 2, y + 18
    cv.fill_rect(dx - 10, dy, 20, 6, INK)
    cv.fill_rect(dx - 2, dy + 6, 4, 8, INK)
    cv.line(dx - 18, dy - 4, dx + 18, dy - 4, INK, 2)
    cv.line(dx - 14, dy + 2, dx - 22, dy + 10, INK, 2)
    cv.line(dx + 14, dy + 2, dx + 22, dy + 10, INK, 2)
    # warning burst where the drone was hit
    cv.disc(dx, dy + 2, 5, FIRE)
    cv.disc(dx, dy + 2, 2, FLAME)


def draw_chart(cv, x, y, s):
    """A falling market chart: bars down, arrow down."""
    cv.fill_rect(x, y, s, s, WHITE)
    cv.rect(x + 8, y + 8, s - 16, s - 16, INK, 2)
    bars = (44, 36, 28, 20, 12)
    for i, bh in enumerate(bars):
        bx = x + 16 + i * 12
        col = RED if i >= 3 else TEAL
        cv.fill_rect(bx, y + s - 18 - bh, 8, bh, col)
    cv.line(x + 14, y + 18, x + s - 14, y + s - 22, RED, 3)
    cv.triangle(((x + s - 14, y + s - 22), (x + s - 24, y + s - 26),
                 (x + s - 20, y + s - 14)), RED)


def draw_globe(cv, x, y, s):
    """A globe for the climate talks, with a green leaf."""
    cv.fill_rect(x, y, s, s, (220, 235, 225))
    cx, cy, r = x + s // 2 - 4, y + s // 2, s // 2 - 8
    cv.disc(cx, cy, r, BLUE)
    cv.disc(cx - 8, cy - 6, 12, TEAL)
    cv.disc(cx + 10, cy + 10, 9, TEAL)
    cv.disc(cx + 12, cy - 12, 6, TEAL)
    for dy in (-r // 2, 0, r // 2):
        cv.line(cx - r + 4, cy + dy, cx + r - 4, cy + dy, WHITE, 2)
    cv.line(cx, cy - r + 2, cx, cy + r - 2, WHITE, 2)
    # leaf
    cv.triangle(((x + s - 22, y + s - 20), (x + s - 4, y + s - 22),
                 (x + s - 8, y + s - 4)), (34, 139, 34))


# ---------------------------------------------------------------- layout

def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 118, NAVY)
    cv.fill_rect(0, 118, W, 4, RED)
    draw_text_centred(cv, W // 2, 22, stories.MASTHEAD, 5, WHITE)
    draw_text_centred(cv, W // 2, 84, stories.TAGLINE, 2, (200, 208, 224))
    draw_text_centred(cv, W // 2, 130, stories.DATE_LINE, 3, RED)
    cv.fill_rect(24, 156, W - 48, 3, INK)


def draw_stat(cv, x, y, w, number, label):
    cv.rect(x, y, w, 92, INK, 2)
    draw_text_centred(cv, x + w // 2, y + 12, number, 4, RED)
    draw_text_centred(cv, x + w // 2, y + 56, label, 2, INK)


def draw_lead(cv):
    x, y, w, h = 24, 164, W - 48, 356
    cv.rect(x, y, w, h, INK, 3)
    draw_kyiv(cv, x + 8, y + 8, 396, h - 16)
    tx = x + 420
    tw = w - 420 - 16
    draw_text(cv, tx, y + 14, stories.LEAD["kicker"], 2, RED)
    draw_text(cv, tx, y + 40, stories.LEAD["headline"], 4, INK)
    draw_text(cv, tx, y + 76, stories.LEAD["subhead"], 3, NAVY)
    cv.fill_rect(tx, y + 108, tw, 2, LIGHT)
    body = " ".join(stories.LEAD["body"])
    draw_wrapped(cv, tx, y + 120, body, 2, INK, tw, 16)
    # key numbers under the body: three adjacent boxes across the text width
    sy = y + h - 104
    stats = (("400+", "DRONES"), ("110", "MISSILES"), ("8+", "KILLED"))
    sw = tw // 3
    for i, (num, lab) in enumerate(stats):
        draw_stat(cv, tx + i * sw, sy, sw, num, lab)


def draw_panel(cv, x, y, w, h, story, icon):
    cv.rect(x, y, w, h, INK, 3)
    pad = 16
    ix = x + w - pad - 76
    iy = y + 12
    icon(cv, ix, iy, 76)
    tx = x + pad
    tw = w - pad * 2 - 88
    draw_text(cv, tx, y + 12, story["kicker"], 2, RED)
    draw_text(cv, tx, y + 36, story["headline"], 3, INK)
    draw_text(cv, tx, y + 62, story["headline2"], 3, INK)
    cv.fill_rect(tx, y + 92, w - pad * 2, 2, LIGHT)
    body = " ".join(story["body"])
    draw_wrapped(cv, tx, y + 104, body, 2, INK, w - pad * 2, 18)


def draw_briefs(cv):
    y = 958
    cv.fill_rect(24, y, W - 48, 3, INK)
    label = "ALSO TODAY: "
    lw = text_width(label, 2)
    # First line shares its row with the label; later lines use the full width.
    lines = []
    cur = ''
    limit = W - 48 - lw
    for word in stories.BRIEFS_TEXT.split(' '):
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, 2) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            limit = W - 48
    if cur:
        lines.append(cur)
    draw_text(cv, 24, y + 10, label, 2, RED)
    for i, ln in enumerate(lines):
        lx = 24 + lw if i == 0 else 24
        draw_text(cv, lx, y + 10 + i * 16, ln, 2, INK)


def build_image():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    # second row: the world court and the Hormuz flashpoint
    draw_panel(cv, 24, 532, 476, 210, stories.COURT, draw_scales)
    draw_panel(cv, 524, 532, 476, 210, stories.HORMUZ, draw_drone)
    # third row: markets and the climate talks
    draw_panel(cv, 24, 754, 476, 196, stories.MARKETS, draw_chart)
    draw_panel(cv, 524, 754, 476, 196, stories.CLIMATE, draw_globe)
    draw_briefs(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    # The output directory may be a mount point on the grader: create it
    # if missing, but never remove it or its contents wholesale.
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build_image())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"wrote {path} ({len(png)} bytes)")


if __name__ == "__main__":
    main()

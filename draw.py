"""Drawing engine for the news-image entry, written from scratch.

Pure Python standard library only: a PNG encoder (zlib + struct),
a 5x7 bitmap font, and raster primitives (rect, line, circle, text).
No third-party modules, no network.
"""

import math
import struct
import zlib


# ---------------------------------------------------------------- font
# 5x7 glyphs. Each glyph is 7 strings of 5 chars; '#' = ink, '.' = blank.
# Uppercase, lowercase, digits and punctuation, all drawn by hand here.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01111", "10000", "10000", "10000", "01111"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11100", "01000", "01000", "01000"),
    'g': ("00000", "00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10001", "01111"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '&': ("01110", "10001", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10100", "10000", "01110"),
    '*': ("00000", "01010", "00100", "01110", "00100", "01010", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}

# Glyphs that need 8 rows (descenders) are stored with 8 rows; the
# renderer uses the glyph's own row count.
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def glyph_rows(ch):
    """Return the row strings for a character (7 rows, or 8 for descenders)."""
    g = FONT.get(ch)
    if g is None:
        return BLANK
    return g


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char, no trailing gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


# ---------------------------------------------------------------- png
def encode_png(width, height, rgb):
    """Encode raw RGB bytes (width*height*3) as a deterministic PNG."""
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    stride = width * 3
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 6)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(bg) * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, with optional thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if thick <= 1:
                self.set(x0, y0, color)
            else:
                r = thick // 2
                self.rect(x0 - r, y0 - r, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                half = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
                self.rect(cx - half, yy, half * 2 + 1, 1, color)
        else:
            steps = max(8, int(2 * math.pi * r))
            for i in range(steps):
                a = 2 * math.pi * i / steps
                self.set(int(cx + r * 0.999 * math.cos(a)),
                         int(cy + r * 0.999 * math.sin(a)), color)

    def ring(self, cx, cy, r, color, thick=2):
        steps = max(12, int(2 * math.pi * r))
        for i in range(steps):
            a = 2 * math.pi * i / steps
            for t in range(thick):
                self.set(int(cx + (r - t) * math.cos(a)),
                         int(cy + (r - t) * math.sin(a)), color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via scanline fill."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.rect(int(lo), y, int(hi) - int(lo) + 1, 1, color)

    # ------------------------------------------------------------ text
    def draw_glyph(self, x, y, ch, scale, color):
        rows = glyph_rows(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + rx * scale, y + ry * scale, scale, scale, color)

    def text(self, x, y, s, scale, color, bold=False):
        """Draw text at scale; bold re-stamps 1px to the right."""
        cx = x
        for ch in s:
            self.draw_glyph(cx, y, ch, scale, color)
            if bold:
                self.draw_glyph(cx + 1, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color, bold=False):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, color, bold)

    def text_right(self, x, y, s, scale, color, bold=False):
        w = text_width(s, scale)
        return self.text(x - w, y, s, scale, color, bold)


def wrap_text(text, scale, max_width):
    """Wrap text into lines that fit max_width pixels. Returns list of lines."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = (cur + ' ' + w) if cur else w
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single word too long: hard-split it.
            while text_width(w, scale) > max_width and len(w) > 1:
                n = max_width // (6 * scale)
                lines.append(w[:n])
                w = w[n:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_kyiv(cv, x, y, w, h):
    """Night sky, a river bridge, an explosion, missile streaks."""
    sky = (38, 52, 84)
    cv.rect(x, y, w, h, sky)
    # stars
    for sx, sy in [(0.12, 0.15), (0.30, 0.08), (0.55, 0.18), (0.78, 0.10),
                   (0.88, 0.28), (0.05, 0.35), (0.42, 0.05), (0.66, 0.30)]:
        cv.rect(x + int(sx * w), y + int(sy * h), 3, 3, (200, 210, 235))
    # missile streaks
    for (mx, my, mdx, mdy) in [(0.08, 0.30, 0.22, -0.10), (0.55, 0.42, 0.20, -0.14),
                               (0.30, 0.55, 0.18, -0.08)]:
        x0 = x + int(mx * w)
        y0 = y + int(my * h)
        x1 = x + int((mx + mdx) * w)
        y1 = y + int((my + mdy) * h)
        cv.line(x0, y0, x1, y1, (255, 240, 200), 2)
        cv.circle(x1, y1, 4, (255, 220, 120))
    # river band
    ry = y + int(h * 0.78)
    cv.rect(x, ry, w, h - int(h * 0.78), (24, 38, 66))
    cv.hline(x, ry, w, (90, 120, 170))
    # bridge deck + towers + cables
    dy = y + int(h * 0.62)
    cv.rect(x + int(w * 0.06), dy, int(w * 0.88), 7, (200, 205, 215))
    for tx in (0.22, 0.70):
        bx = x + int(tx * w)
        cv.rect(bx, y + int(h * 0.30), 8, dy - y - int(h * 0.30) + 7, (170, 178, 195))
        cv.line(bx + 4, y + int(h * 0.30), x + int(w * 0.06), dy, (150, 158, 178), 1)
        cv.line(bx + 4, y + int(h * 0.30), x + int(w * 0.94), dy, (150, 158, 178), 1)
    # explosion starburst over the deck
    ex = x + int(w * 0.48)
    ey = y + int(h * 0.52)
    for k in range(12):
        a = 2 * math.pi * k / 12
        L = 26 if k % 2 == 0 else 16
        cv.line(ex, ey, int(ex + L * math.cos(a)), int(ey + L * math.sin(a)),
                (255, 170, 40), 3)
    cv.circle(ex, ey, 13, (255, 200, 60))
    cv.circle(ex, ey, 7, (255, 240, 170))
    # smoke dots
    for sx, sy, sr in [(0.40, 0.42, 6), (0.56, 0.44, 5), (0.48, 0.36, 4)]:
        cv.circle(x + int(sx * w), y + int(sy * h), sr, (120, 125, 140))


def icon_scales(cv, x, y, w, h):
    """Scales of justice on a deep teal panel."""
    cv.rect(x, y, w, h, (18, 64, 62))
    gold = (232, 196, 106)
    pale = (245, 235, 205)
    cx = x + w // 2
    top = y + int(h * 0.16)
    base = y + int(h * 0.86)
    # post and base
    cv.rect(cx - 4, top, 8, base - top, gold)
    cv.rect(cx - int(w * 0.18), base, int(w * 0.36), 8, gold)
    cv.circle(cx, top - 6, 6, gold)
    # beam
    cv.rect(x + int(w * 0.14), top + 4, int(w * 0.72), 6, gold)
    # pans
    for side in (-1, 1):
        px = cx + side * int(w * 0.30)
        cv.line(px, top + 7, px - 16, top + int(h * 0.42), pale, 2)
        cv.line(px, top + 7, px + 16, top + int(h * 0.42), pale, 2)
        py = top + int(h * 0.42)
        cv.triangle(px - 18, py, px + 18, py, px, py + 16, gold)
        cv.rect(px - 18, py, 36, 3, gold)
    # small stars
    for sx, sy in [(0.10, 0.12), (0.88, 0.16), (0.78, 0.70), (0.14, 0.66)]:
        cv.rect(x + int(sx * w), y + int(sy * h), 3, 3, pale)


def icon_market(cv, x, y, w, h):
    """A market chart falling hard, on a dark red panel."""
    cv.rect(x, y, w, h, (74, 24, 24))
    # grid
    for gy in range(1, 5):
        gyv = y + int(h * gy / 5)
        cv.hline(x + 8, gyv, w - 16, (120, 60, 60))
    # bars
    bx = x + int(w * 0.10)
    for i, bh in enumerate([0.30, 0.42, 0.36, 0.55, 0.48, 0.66, 0.60, 0.80]):
        bw = int(w * 0.075)
        by = y + int(h * 0.88) - int(bh * h * 0.75)
        cv.rect(bx + i * int(w * 0.105), by, bw, int(bh * h * 0.75),
                (200, 70, 60) if i >= 5 else (150, 90, 80))
    # falling line
    pts = [(0.08, 0.22), (0.20, 0.30), (0.32, 0.26), (0.44, 0.45),
           (0.56, 0.42), (0.68, 0.62), (0.80, 0.58), (0.92, 0.82)]
    for i in range(len(pts) - 1):
        x0 = x + int(pts[i][0] * w)
        y0 = y + int(pts[i][1] * h)
        x1 = x + int(pts[i + 1][0] * w)
        y1 = y + int(pts[i + 1][1] * h)
        cv.line(x0, y0, x1, y1, (255, 235, 220), 4)
    for (px, py) in pts:
        cv.circle(x + int(px * w), y + int(py * h), 4, (255, 235, 220))
    # down arrow at the end
    ax = x + int(w * 0.92)
    ay = y + int(h * 0.82)
    cv.triangle(ax - 12, ay - 16, ax + 12, ay - 16, ax, ay + 4, (255, 120, 100))
    cv.rect(ax - 4, ay - 34, 8, 20, (255, 120, 100))

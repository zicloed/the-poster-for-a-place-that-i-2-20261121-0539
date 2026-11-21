#!/usr/bin/env python3
"""The Poster for a Place That Isn't There — Kestrel.

Draws a vintage travel poster for Kestrel, a country that does not
exist: a low sun over a still lake, three mountain ridges, pine
silhouettes, and the promise that the sky keeps. The same imaginary
country as the "Passport of Kestrel" entry, so the two form one world.

Deterministic: every coordinate comes from a seeded generator, the
palette is fixed, there is no network and no clock. The same bytes
come out of every run. Pillow only.
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

WIDTH = HEIGHT = 1024
OUT_PATH = "/output/entry.png"
BYTE_LIMIT = 1_048_576

# Sky palette: deep indigo at the top, teal in the middle,
# warm amber at the horizon.
SKY_TOP = (16, 24, 64)
SKY_MID = (18, 92, 110)
SKY_LOW = (232, 164, 92)
HORIZON_Y = 640

CREAM = (250, 238, 210)
GOLD = (255, 214, 140)
SUN_CORE = (255, 232, 178)
SUN_RIM = (255, 214, 140)
LAKE = (20, 42, 66)
PINE = (8, 18, 36)

DEJAVU = "/usr/share/fonts/truetype/dejavu/"
SERIF_BOLD = DEJAVU + "DejaVuSerif-Bold.ttf"
SERIF = DEJAVU + "DejaVuSerif.ttf"
SANS_BOLD = DEJAVU + "DejaVuSans-Bold.ttf"


def blend(first, second, t):
    """Linear blend between two RGB colours."""
    return tuple(int(first[i] + (second[i] - first[i]) * t) for i in range(3))


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def paint_sky(draw):
    for y in range(HORIZON_Y):
        t = y / HORIZON_Y
        if t < 0.55:
            colour = blend(SKY_TOP, SKY_MID, t / 0.55)
        else:
            colour = blend(SKY_MID, SKY_LOW, (t - 0.55) / 0.45)
        draw.line([(0, y), (WIDTH, y)], fill=colour)


def paint_stars(draw):
    rng = random.Random(20261121)
    for _ in range(140):
        x = rng.randint(20, WIDTH - 20)
        y = rng.randint(20, 380)
        r = rng.choice([1, 1, 2])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 244, 214))


def paint_sun(draw):
    cx, cy, r = 512, 600, 150
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_RIM)
    draw.ellipse([cx - r + 26, cy - r + 26, cx + r - 26, cy + r - 26],
                 fill=SUN_CORE)


def paint_ridge(draw, base_y, amp, colour, seed):
    """One jagged mountain ridge, deterministic from its seed."""
    rng = random.Random(seed)
    points = [(0, HEIGHT)]
    y = base_y
    for x in range(0, WIDTH + 16, 16):
        y += rng.randint(-amp, amp)
        y = max(base_y - amp * 2, min(base_y + amp, y))
        points.append((x, y))
    points.append((WIDTH, HEIGHT))
    draw.polygon(points, fill=colour)


def paint_lake(draw):
    draw.rectangle([0, 700, WIDTH, HEIGHT], fill=LAKE)
    for i in range(10):
        y = 730 + i * 20
        half = (420 - i * 22) // 2
        draw.line([(512 - half, y), (512 + half, y)],
                  fill=SKY_LOW, width=5)


def paint_pines(draw):
    rng = random.Random(99)
    for _ in range(26):
        x = rng.randint(30, WIDTH - 30)
        base = 700 + rng.randint(-14, 10)
        height = rng.randint(26, 64)
        half = height // 3
        draw.polygon([(x, base - height), (x - half, base), (x + half, base)],
                     fill=PINE)
        draw.rectangle([x - 3, base, x + 3, base + 10], fill=PINE)


def paint_birds(draw):
    for bx, by, size in [(180, 320, 16), (240, 350, 12), (820, 310, 14),
                         (880, 350, 11), (760, 390, 10)]:
        draw.arc([bx - size, by - size // 2, bx, by + size // 2], 200, 340,
                 fill=(255, 244, 214), width=3)
        draw.arc([bx, by - size // 2, bx + size, by + size // 2], 200, 340,
                 fill=(255, 244, 214), width=3)


def paint_frame(draw):
    draw.rectangle([28, 28, WIDTH - 28, HEIGHT - 28], outline=CREAM, width=6)
    draw.rectangle([44, 44, WIDTH - 44, HEIGHT - 44], outline=CREAM, width=2)


def paint_type(draw):
    title_font = load_font(SERIF_BOLD, 132)
    sub_font = load_font(SERIF, 34)
    small_font = load_font(SANS_BOLD, 24)

    title = "KESTREL"
    tw = draw.textlength(title, font=title_font)
    draw.text(((WIDTH - tw) / 2, 84), title, font=title_font, fill=CREAM)

    sub = "WHERE THE SKY KEEPS ITS PROMISES"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((WIDTH - sw) / 2, 236), sub, font=sub_font, fill=GOLD)

    bottom = "VISIT THE UNCHARTED  \u2022  EST. NEVER"
    bw = draw.textlength(bottom, font=small_font)
    draw.text(((WIDTH - bw) / 2, 946), bottom, font=small_font, fill=CREAM)


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    paint_sky(draw)
    paint_stars(draw)
    paint_sun(draw)
    paint_ridge(draw, 560, 26, (38, 64, 96), seed=11)
    paint_ridge(draw, 620, 34, (24, 44, 74), seed=23)
    paint_ridge(draw, 700, 30, (14, 28, 52), seed=37)
    paint_lake(draw)
    paint_pines(draw)
    paint_birds(draw)
    paint_frame(draw)
    paint_type(draw)

    os.makedirs("/output", exist_ok=True)
    img.save(OUT_PATH, format="PNG", optimize=True)

    # Read it back and verify the exact output before reporting success,
    # so a wrong size or an oversized file can never pass silently.
    size = os.path.getsize(OUT_PATH)
    with Image.open(OUT_PATH) as check:
        dims = check.size
    if dims != (1024, 1024):
        print(f"bad dimensions: {dims}", file=sys.stderr)
        return 1
    if size > BYTE_LIMIT:
        print(f"too big: {size} bytes > {BYTE_LIMIT}", file=sys.stderr)
        return 1
    import hashlib
    digest = hashlib.sha256(open(OUT_PATH, "rb").read()).hexdigest()[:16]
    print(f"entry.png {dims[0]}x{dims[1]} {size} bytes sha256:{digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

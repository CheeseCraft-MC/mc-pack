"""Skill bar next to the hotbar: slot frame, cooldown overlays, key labels, digits and direction arrows."""
from PIL import Image
from draw import Canvas, hexc, with_alpha

# 3x5 pixel font for key labels
TINY = {
    'F': ['###', '#..', '##.', '#..', '#..'],
    'Q': ['.#.', '#.#', '#.#', '#.#', '.##'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'E': ['###', '#..', '##.', '#..', '###'],
    '^': ['.#.', '###', '.#.', '.#.', '.#.'],   # shift arrow
    '1': ['.#.', '##.', '.#.', '.#.', '###'], '2': ['##.', '..#', '.#.', '#..', '###'],
    '3': ['##.', '..#', '.#.', '..#', '##.'], '4': ['#.#', '#.#', '###', '..#', '..#'],
    '5': ['###', '#..', '##.', '..#', '##.'], '6': ['.##', '#..', '###', '#.#', '###'],
    '7': ['###', '..#', '.#.', '.#.', '.#.'], '8': ['###', '#.#', '###', '#.#', '###'],
    '9': ['###', '#.#', '###', '..#', '##.'], '0': ['###', '#.#', '#.#', '#.#', '###'],
}

# 5x7 digits for the main line (same size as the vanilla font)
DIGITS = {
    '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
    '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['.###.', '#...#', '....#', '..##.', '....#', '#...#', '.###.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
    '6': ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
    '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
    'm': ['.....', '.....', '##.#.', '#.#.#', '#.#.#', '#...#', '#...#'],
    's': ['.....', '.....', '.####', '#....', '.###.', '....#', '####.'],
}


def bitmap(rows, color, outline=None):
    h, w = len(rows), len(rows[0])
    pad = 1 if outline else 0
    c = Canvas(w + 2 * pad, h + 2 * pad)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '#':
                c.px(x + pad, y + pad, color)
    if outline:
        src = c.img.copy()
        for y in range(c.h):
            for x in range(c.w):
                if src.getpixel((x, y))[3]:
                    continue
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < c.w and 0 <= ny < c.h and src.getpixel((nx, ny))[3]:
                            c.px(x, y, outline)
                            break
    return c


def key_label(text):
    """Small label like '^F' (shift + F) with a dark outline."""
    parts = [TINY[ch] for ch in text]
    rows = []
    for y in range(5):
        rows.append('.'.join(p[y] for p in parts))
    return bitmap(rows, hexc('#f4ecd0'), hexc('#1a1410'))


def digit(ch, color='#ffffff'):
    return bitmap(DIGITS[ch], hexc(color))


def slot_frame():
    c = Canvas(22, 22)
    c.rect(0, 0, 21, 21, hexc('#1a1410', 235))
    c.outline_rect(0, 0, 21, 21, hexc('#c9a24a'))
    c.outline_rect(1, 1, 20, 20, hexc('#5a4628'))
    for (x, y) in ((0, 0), (21, 0), (0, 21), (21, 21)):
        c.px(x, y, hexc('#f0d68a'))
    return c


def empty_slot():
    c = Canvas(16, 16)
    c.rect(6, 7, 9, 8, hexc('#5a4628'))
    return c


def cooldown(step, steps=8):
    """Dark overlay covering step/steps of the icon from the top (the rest is still recharging)."""
    c = Canvas(16, 16)
    rows = round(16 * step / steps)
    if rows > 0:
        c.rect(0, 0, 15, rows - 1, (0, 0, 0, 165))
    return c


def no_mana():
    c = Canvas(16, 16)
    c.rect(0, 0, 15, 15, (30, 60, 200, 110))
    return c


def arrow(index):
    """8 directions, 0 = straight ahead (up), clockwise."""
    import math
    c = Canvas(9, 9)
    angle = math.radians(index * 45)
    tip = (4 + math.sin(angle) * 4, 4 - math.cos(angle) * 4)
    left = (4 + math.sin(angle + 2.5) * 3.6, 4 - math.cos(angle + 2.5) * 3.6)
    right = (4 + math.sin(angle - 2.5) * 3.6, 4 - math.cos(angle - 2.5) * 3.6)
    c.poly([tip, left, (4, 4), right], hexc('#ffd040'))
    return c


def arrived():
    c = Canvas(9, 9)
    c.ring(4, 4, 3, hexc('#58d048'))
    c.px(4, 4, hexc('#58d048'))
    return c


def icon16(img):
    return Canvas.of(img.resize((16, 16), Image.LANCZOS))


def bag_frame():
    """Skill-bar slot for the backpack: round leather frame instead of gold."""
    c = Canvas(22, 22)
    c.rect(1, 1, 20, 20, hexc('#1a1008', 235))
    c.outline_rect(1, 1, 20, 20, hexc('#a06c3c'))
    c.outline_rect(2, 2, 19, 19, hexc('#5a3a1e'))
    for (x, y) in ((1, 1), (20, 1), (1, 20), (20, 20)):
        c.px(x, y, (0, 0, 0, 0))
    for x in range(4, 19, 3):
        c.px(x, 1, hexc('#e0c090'))
        c.px(x, 20, hexc('#e0c090'))
    return c


def bag_icon():
    c = Canvas(16, 16)
    c.rect(3, 4, 12, 14, hexc('#8e5e34'))
    c.rect(3, 4, 12, 7, hexc('#a06c3c'))
    c.rect(5, 1, 10, 3, hexc('#5a3a1e'))
    c.rect(7, 6, 8, 8, hexc('#e0b040'))
    c.outline_rect(3, 4, 12, 14, hexc('#4a2a14'))
    return c

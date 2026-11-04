"""Menu backgrounds, menu icons, skill emblems, quest markers, HUD glyphs, tooltip frames and the book."""
import math
import random
from PIL import Image
from draw import Canvas, finish, hexc, lighten, darken, mix, with_alpha, glow, sparkle, noise_fill, grayscale
import art_items as items

GOLD = hexc('#c9a24a')
GOLD_DARK = hexc('#7a5e2a')
GOLD_LIGHT = hexc('#f0d68a')
BG = hexc('#1d1823')
BG_DARK = hexc('#141018')
TITLE = hexc('#2a2131')
SOCKET = hexc('#0e0b12')
RIM = hexc('#4f3e2c')
PARCHMENT = hexc('#d9c49a')
THEME = None

# Menu colour themes. None = neutral (no class yet), otherwise one per class.
THEMES = {
    None: dict(GOLD='#c9a24a', GOLD_DARK='#7a5e2a', GOLD_LIGHT='#f0d68a', BG='#1d1823', TITLE='#2a2131',
               SOCKET='#0e0b12', RIM='#4f3e2c'),
    'warrior': dict(GOLD='#b4b4bc', GOLD_DARK='#6a3030', GOLD_LIGHT='#f0e0d8', BG='#211515', TITLE='#341b1b',
                    SOCKET='#110a0a', RIM='#5a2c2c'),
    'mage': dict(GOLD='#5ab4ec', GOLD_DARK='#2a5486', GOLD_LIGHT='#c4ecff', BG='#141a2b', TITLE='#1c2644',
                 SOCKET='#090d18', RIM='#2c3e62'),
    'assassin': dict(GOLD='#a462d8', GOLD_DARK='#4a2a6c', GOLD_LIGHT='#e0bcff', BG='#18111e', TITLE='#25182f',
                     SOCKET='#0b0710', RIM='#3c2a4c'),
    'archer': dict(GOLD='#8cbc52', GOLD_DARK='#40602a', GOLD_LIGHT='#d4f4ac', BG='#141b13', TITLE='#1d2a1b',
                   SOCKET='#080c07', RIM='#3c4226'),
    'guardian': dict(GOLD='#e0b24a', GOLD_DARK='#6a5428', GOLD_LIGHT='#fff0b8', BG='#1a1a1e', TITLE='#2a2a30',
                     SOCKET='#0c0c10', RIM='#5a5040'),
}


CLASS_COLORS = {'warrior': '#c83a3a', 'mage': '#3ab8e0', 'assassin': '#9a4ad0', 'archer': '#4ab04a',
                'guardian': '#e0a030'}


def set_theme(name):
    """Switches the colours used by all panel functions."""
    global GOLD, GOLD_DARK, GOLD_LIGHT, BG, TITLE, SOCKET, RIM, THEME
    t = THEMES[name]
    GOLD, GOLD_DARK, GOLD_LIGHT = hexc(t['GOLD']), hexc(t['GOLD_DARK']), hexc(t['GOLD_LIGHT'])
    BG, TITLE, SOCKET, RIM = hexc(t['BG']), hexc(t['TITLE']), hexc(t['SOCKET']), hexc(t['RIM'])
    THEME = name


def ornament(c, cx, cy):
    """Class emblem in the middle of the title bar."""
    if THEME == 'warrior':      # crossed swords
        c.line(cx - 5, cy - 4, cx + 5, cy + 4, GOLD_LIGHT)
        c.line(cx + 5, cy - 4, cx - 5, cy + 4, GOLD_LIGHT)
        c.line(cx - 4, cy + 2, cx - 2, cy + 4, GOLD_DARK)
        c.line(cx + 4, cy + 2, cx + 2, cy + 4, GOLD_DARK)
    elif THEME == 'mage':       # four pointed star
        c.poly([(cx, cy - 5), (cx + 1, cy - 1), (cx + 5, cy), (cx + 1, cy + 1), (cx, cy + 5), (cx - 1, cy + 1),
                (cx - 5, cy), (cx - 1, cy - 1)], GOLD)
        c.px(cx, cy, GOLD_LIGHT)
    elif THEME == 'assassin':   # crescent moon
        c.circle(cx, cy, 4, GOLD)
        c.circle(cx + 2, cy - 1, 4, TITLE)
    elif THEME == 'archer':     # arrow
        c.line(cx - 6, cy, cx + 4, cy, GOLD_LIGHT)
        c.poly([(cx + 6, cy), (cx + 3, cy - 3), (cx + 3, cy + 3)], GOLD)
        c.line(cx - 6, cy - 2, cx - 4, cy, GOLD_DARK)
        c.line(cx - 6, cy + 2, cx - 4, cy, GOLD_DARK)
    elif THEME == 'guardian':   # tower shield
        c.poly([(cx - 4, cy - 5), (cx + 4, cy - 5), (cx + 4, cy + 1), (cx, cy + 5), (cx - 4, cy + 1)], GOLD)
        c.line(cx, cy - 4, cx, cy + 3, GOLD_LIGHT)
        c.line(cx - 3, cy - 2, cx + 3, cy - 2, GOLD_DARK)
    else:                       # diamond
        c.poly([(cx - 4, cy), (cx, cy - 4), (cx + 4, cy), (cx, cy + 3)], GOLD)
        c.px(cx, cy, GOLD_LIGHT)

GUI_W = 176


def gui_height(rows):
    return 114 + rows * 18


def slot_pos(slot):
    """Top-left pixel of the 18x18 slot frame of a chest slot."""
    return 7 + (slot % 9) * 18, 17 + (slot // 9) * 18


def socket(c, x, y, special=False):
    rim = GOLD if special else RIM
    c.rect(x, y, x + 17, y + 17, darken(rim, 0.35))
    c.outline_rect(x, y, x + 17, y + 17, rim)
    c.rect(x + 1, y + 1, x + 16, y + 16, SOCKET)
    c.line(x + 1, y + 1, x + 16, y + 1, darken(SOCKET, 0.5) if False else hexc('#08060a'))
    c.line(x + 1, y + 16, x + 16, y + 16, lighten(SOCKET, 0.1))
    for (px, py) in ((x, y), (x + 17, y), (x, y + 17), (x + 17, y + 17)):
        c.px(px, py, GOLD_LIGHT if special else GOLD_DARK)


def panel(rows, sockets=(), special=(), seed=3, draw_inventory=True):
    h = gui_height(rows)
    c = Canvas(GUI_W, h)
    noise_fill(c, 0, 0, GUI_W - 1, h - 1, BG, 5, seed)
    # title bar
    noise_fill(c, 3, 3, GUI_W - 4, 15, TITLE, 4, seed + 1)
    c.line(3, 16, GUI_W - 4, 16, GOLD_DARK)
    # outer frame
    c.outline_rect(0, 0, GUI_W - 1, h - 1, hexc('#0a080c'))
    c.outline_rect(1, 1, GUI_W - 2, h - 2, GOLD)
    c.outline_rect(2, 2, GUI_W - 3, h - 3, GOLD_DARK)
    for (x, y) in ((1, 1), (GUI_W - 2, 1), (1, h - 2), (GUI_W - 2, h - 2)):
        for dx in range(-2, 3):
            c.px(x + dx, y, GOLD_LIGHT)
        for dy in range(-2, 3):
            c.px(x, y + dy, GOLD_LIGHT)
    # center ornament on the title bar
    ornament(c, GUI_W // 2, 16)
    for slot in sockets:
        x, y = slot_pos(slot)
        socket(c, x, y, slot in special)
    if draw_inventory:
        inv_top = rows * 18 + 17 + 13
        c.line(4, rows * 18 + 19, GUI_W - 5, rows * 18 + 19, GOLD_DARK)
        for row in range(3):
            for col in range(9):
                socket(c, 7 + col * 18, inv_top + row * 18)
        for col in range(9):
            socket(c, 7 + col * 18, inv_top + 58)
    return c


def connect(c, a, b, color, width=2):
    """Draws the same path the plugin uses for skill connectors: vertical first, then horizontal."""
    ax, ay = slot_pos(a)
    bx, by = slot_pos(b)
    ax, ay, bx, by = ax + 9, ay + 9, bx + 9, by + 9
    c.line(ax, ay, ax, by, color, width)
    c.line(ax, by, bx, by, color, width)


def skilltree(nodes, links):
    sockets = [45, 46, 47, 48, 49, 50, 51, 52, 53]
    c = panel(6, sockets=sockets, special=[46, 47, 48, 49, 50, 51])
    # starfield behind the tree
    rnd = random.Random(9)
    for _ in range(70):
        x, y = rnd.randint(5, GUI_W - 6), rnd.randint(19, 125)
        c.px(x, y, with_alpha(GOLD_LIGHT, rnd.randint(40, 120)))
    for a, b in links:
        connect(c, a, b, darken(GOLD_DARK, 0.45), 4)
        connect(c, a, b, darken(GOLD, 0.35), 2)
    for slot, ultimate in nodes:
        x, y = slot_pos(slot)
        cx, cy = x + 9, y + 9
        if ultimate:
            glow(c, cx, cy, 14, with_alpha(GOLD_LIGHT, 90))
        c.circle(cx, cy, 9, SOCKET)
        c.ring(cx, cy, 9, GOLD if ultimate else RIM, 1)
    c.line(4, 6 * 18 + 17 - 19, GUI_W - 5, 6 * 18 + 17 - 19, GOLD_DARK)
    return c


def map_background(regions, roads, sites, border):
    """Parchment world map in the 9x5 slot area (slots 0-44)."""
    sockets = [45, 49, 53]
    c = panel(6, sockets=sockets, special=[49])
    x0, y0, w, h = 7, 17, 162, 90
    half = border / 2
    colors = {
        'MEADOW': '#a9c46a', 'FOREST': '#6f9a48', 'DARK_FOREST': '#3f5e34', 'BADLANDS': '#c99a5a', 'VOID': '#47305e',
        'RUINS': '#9a9a7a', 'MOUNTAINS': '#a8a4a0', 'VOLCANIC': '#5a3030', 'WILDS': '#8aa860',
    }
    ordered = sorted(regions, key=lambda r: (-r['priority'], (r['max'][0] - r['min'][0]) * (r['max'][1] - r['min'][1])))
    rnd = random.Random(4)
    for py in range(h):
        for px_ in range(w):
            wx = -half + (px_ + 0.5) / w * border
            wz = -half + (py + 0.5) / h * border
            col = hexc('#c8b48a')
            for r in ordered:
                if r['min'][0] <= wx <= r['max'][0] and r['min'][1] <= wz <= r['max'][1]:
                    col = hexc(colors.get(r['terrain'], '#a0a080'))
                    break
            col = mix(col, PARCHMENT, 0.35)
            n = rnd.randint(-6, 6)
            c.px(x0 + px_, y0 + py, tuple(max(0, min(255, col[i] + n)) for i in range(3)) + (255,))
    def to_px(wx, wz):
        return x0 + (wx + half) / border * w, y0 + (wz + half) / border * h
    for road in roads:
        pts = [to_px(p[0], p[1]) for p in road]
        for i in range(len(pts) - 1):
            c.line(*pts[i], *pts[i + 1], hexc('#7a5a34'), 1)
    for (wx, wz, big) in sites:
        x, y = to_px(wx, wz)
        if big:
            c.rect(x - 2, y - 2, x + 2, y + 2, hexc('#5a3a1e'))
            c.px(x, y, GOLD_LIGHT)
        else:
            c.px(x, y, hexc('#5a3a1e'))
    # vignette and frame of the map
    for i in range(3):
        c.outline_rect(x0 - 1 + i, y0 - 1 + i, x0 + w - i, y0 + h - i, with_alpha(hexc('#3a2a18'), 200 - i * 60))
    c.outline_rect(x0 - 2, y0 - 2, x0 + w + 1, y0 + h + 1, GOLD)
    # compass rose
    cx, cy = x0 + w - 10, y0 + 10
    c.poly([(cx, cy - 7), (cx + 2, cy), (cx, cy + 7), (cx - 2, cy)], hexc('#5a3a1e'))
    c.poly([(cx - 7, cy), (cx, cy - 2), (cx + 7, cy), (cx, cy + 2)], hexc('#8a6a3e'))
    c.px(cx, cy - 7, hexc('#b01e1e'))
    return c


def world_map_image(regions, roads, sites, border, size=128):
    """The world as a 128x128 picture for the map item: terrain colours of the regions, region borders, roads, towns."""
    c = Canvas(size, size)
    half = border / 2
    colors = {
        'MEADOW': '#8fb456', 'FOREST': '#5a8a3a', 'DARK_FOREST': '#36552c', 'BADLANDS': '#c08a4a',
        'RUINS': '#8a8a72', 'MOUNTAINS': '#9a9690', 'VOLCANIC': '#5a2a24', 'WILDS': '#7a9a52', 'VOID': '#3a2450',
    }
    ordered = sorted(regions, key=lambda r: (-r['priority'], (r['max'][0] - r['min'][0]) * (r['max'][1] - r['min'][1])))
    rnd = random.Random(7)

    def region_at(wx, wz):
        for i, r in enumerate(ordered):
            if r['min'][0] <= wx <= r['max'][0] and r['min'][1] <= wz <= r['max'][1]:
                return i, r
        return -1, None

    owner = {}
    for py in range(size):
        for px_ in range(size):
            wx = -half + (px_ + 0.5) / size * border
            wz = -half + (py + 0.5) / size * border
            i, r = region_at(wx, wz)
            owner[(px_, py)] = i
            col = hexc(colors.get(r['terrain'], '#7a9a52')) if r else hexc('#6a8a4a')
            n = rnd.randint(-7, 7)
            c.px(px_, py, tuple(max(0, min(255, col[k] + n)) for k in range(3)) + (255,))
    for (px_, py), i in owner.items():            # region borders
        if any(owner.get((px_ + dx, py + dy), i) != i for dx, dy in ((1, 0), (0, 1))):
            c.px(px_, py, hexc('#3a3020'))

    def to_px(wx, wz):
        return (wx + half) / border * size, (wz + half) / border * size
    for road in roads:
        pts = [to_px(p[0], p[1]) for p in road]
        for i in range(len(pts) - 1):
            c.line(*pts[i], *pts[i + 1], hexc('#d8c088'), 1)
    for (wx, wz, big) in sites:
        x, y = to_px(wx, wz)
        if big:
            c.rect(x - 2, y - 2, x + 2, y + 2, hexc('#6a4a2a'))
            c.rect(x - 1, y - 1, x + 1, y + 1, hexc('#e8c070'))
        else:
            c.rect(x - 1, y - 1, x + 1, y + 1, hexc('#6a4a2a'))
    c.outline_rect(0, 0, size - 1, size - 1, hexc('#3a2a18'))
    return c


# ───────────────────────────── menu icons (32x32) ─────────────────────────────

def _emblem_base(ring_color, fill='#1a1420'):
    c = Canvas(32, 32)
    c.circle(16, 16, 14, hexc(fill))
    c.ring(16, 16, 14, hexc(ring_color), 2)
    c.ring(16, 16, 11, darken(hexc(ring_color), 0.45), 1)
    return c


def icon_character():
    c = Canvas(32, 32)
    c.poly([(9, 14), (16, 4), (23, 14), (23, 20), (9, 20)], hexc('#9aa3ad'))
    c.rect(11, 14, 21, 16, hexc('#2a2a30'))
    c.rect(15, 6, 17, 20, hexc('#c9a24a'))
    c.poly([(5, 28), (9, 21), (23, 21), (27, 28)], hexc('#6a2a2a'))
    return finish(c)


def icon_skills():
    c = _emblem_base('#4fc3e8')
    for i in range(8):
        a = i / 8 * math.pi * 2
        r = 9 if i % 2 == 0 else 5
        c.line(16, 16, 16 + math.cos(a) * r, 16 + math.sin(a) * r, hexc('#bff0ff'), 1)
    c.circle(16, 16, 3, hexc('#ffffff'))
    finish(c, shade=False)
    glow(c, 16, 16, 12, (100, 210, 255, 120))
    return c


def icon_quests():
    c = Canvas(32, 32)
    c.rect(8, 6, 24, 26, hexc('#e6d3a6'))
    c.rect(6, 4, 26, 7, hexc('#b8935a'))
    c.rect(6, 25, 26, 28, hexc('#b8935a'))
    for y in (10, 14, 18, 22):
        c.line(11, y, 21 if y != 22 else 17, y, hexc('#6a5034'), 1)
    c.poly([(20, 18), (26, 12), (28, 14), (22, 20)], hexc('#d0c8b8'))
    c.px(19, 20, hexc('#202020'))
    return finish(c)


def icon_map():
    c = Canvas(32, 32)
    c.poly([(4, 8), (12, 5), (20, 8), (28, 5), (28, 25), (20, 28), (12, 25), (4, 28)], hexc('#d9c49a'))
    c.line(12, 5, 12, 25, hexc('#a8936a'), 1)
    c.line(20, 8, 20, 28, hexc('#a8936a'), 1)
    c.poly([(6, 18), (10, 12), (16, 14), (18, 20), (11, 23)], hexc('#8ab060'))
    c.line(7, 22, 25, 11, hexc('#8a5a2a'), 1)
    c.line(22, 14, 26, 18, hexc('#b01e1e'), 2)
    c.line(26, 14, 22, 18, hexc('#b01e1e'), 2)
    return finish(c)


def icon_dungeons():
    c = Canvas(32, 32)
    c.poly([(5, 29), (5, 12), (16, 3), (27, 12), (27, 29)], hexc('#5a5560'))
    c.poly([(10, 29), (10, 16), (16, 10), (22, 16), (22, 29)], hexc('#120c14'))
    for x in (12, 16, 20):
        c.line(x, 14 if x == 16 else 16, x, 29, hexc('#7a7480'), 1)
    c.circle(16, 21, 3, hexc('#e8e0d0'))
    c.px(15, 21, hexc('#000000'))
    c.px(17, 21, hexc('#000000'))
    finish(c)
    glow(c, 16, 21, 8, (200, 40, 40, 110))
    return c


def icon_equipment():
    c = Canvas(32, 32)
    c.poly([(8, 6), (13, 4), (16, 7), (19, 4), (24, 6), (27, 12), (23, 13), (23, 27), (9, 27), (9, 13), (5, 12)],
           hexc('#9aa3ad'))
    c.line(16, 8, 16, 26, hexc('#c9a24a'), 1)
    c.line(10, 17, 22, 17, hexc('#c9a24a'), 1)
    return finish(c)


def icon_party():
    c = Canvas(32, 32)
    for (x, col) in ((10, '#4a7ad0'), (22, '#c04a4a'), (16, '#4ab05a')):
        c.circle(x, 11, 4, hexc('#e8c8a0'))
        c.poly([(x - 6, 28), (x - 4, 17), (x + 4, 17), (x + 6, 28)], hexc(col))
    return finish(c)


def icon_achievements():
    c = Canvas(32, 32)
    g = hexc('#e2b23a')
    c.poly([(8, 5), (24, 5), (22, 16), (16, 19), (10, 16)], g)
    c.ring(6, 9, 3, g, 2)
    c.ring(26, 9, 3, g, 2)
    c.rect(14, 19, 18, 23, darken(g, 0.2))
    c.rect(10, 23, 22, 27, hexc('#6a4a2a'))
    finish(c)
    sparkle(c, 12, 8, (255, 255, 230, 255))
    return c


def icon_settings():
    c = Canvas(32, 32)
    col = hexc('#a8b0b8')
    for i in range(8):
        a = i / 8 * math.pi * 2
        c.circle(16 + math.cos(a) * 10, 16 + math.sin(a) * 10, 3, col)
    c.circle(16, 16, 9, col)
    c.circle(16, 16, 4, hexc('#2a2a30'))
    return finish(c)


def icon_help():
    c = items.book('#2e4a7a', '#c9a24a', '#ffffff')
    return c


def icon_back():
    c = Canvas(32, 32)
    c.poly([(5, 16), (15, 6), (15, 12), (27, 12), (27, 20), (15, 20), (15, 26)], hexc('#c9a24a'))
    return finish(c)


def icon_next():
    c = Canvas(32, 32)
    c.poly([(27, 16), (17, 6), (17, 12), (5, 12), (5, 20), (17, 20), (17, 26)], hexc('#c9a24a'))
    return finish(c)


def icon_close():
    c = Canvas(32, 32)
    c.line(8, 8, 24, 24, hexc('#c83030'), 4)
    c.line(24, 8, 8, 24, hexc('#c83030'), 4)
    return finish(c)


def icon_heart():
    return items.heart()


def icon_mana():
    c = Canvas(32, 32)
    c.poly([(16, 3), (25, 18), (16, 29), (7, 18)], hexc('#3060e0'))
    c.poly([(16, 6), (21, 17), (16, 25)], hexc('#5a8aff'))
    finish(c)
    glow(c, 16, 17, 13, (80, 130, 255, 110))
    return c


def icon_gold():
    c = Canvas(32, 32)
    for (x, y) in ((11, 20), (21, 20), (16, 12)):
        c.circle(x, y, 6, hexc('#e2b23a'))
        c.ring(x, y, 4, hexc('#a8801e'), 1)
    finish(c)
    sparkle(c, 14, 9, (255, 255, 220, 255))
    return c


def icon_progress():
    c = Canvas(32, 32)
    c.rect(8, 4, 24, 6, hexc('#8a5a2a'))
    c.rect(8, 26, 24, 28, hexc('#8a5a2a'))
    c.poly([(10, 7), (22, 7), (16, 16)], with_alpha(hexc('#cfe6f0'), 200))
    c.poly([(16, 16), (22, 25), (10, 25)], with_alpha(hexc('#cfe6f0'), 200))
    c.poly([(13, 9), (19, 9), (16, 14)], hexc('#e8c070'))
    c.poly([(16, 19), (20, 25), (12, 25)], hexc('#e8c070'))
    return finish(c)


def icon_stats():
    return items.shard('#c060ff')


def icon_plus_orb(col='#e8c040'):
    c = Canvas(32, 32)
    c.circle(16, 16, 11, hexc(col))
    c.rect(14, 8, 18, 24, hexc('#ffffff'))
    c.rect(8, 14, 24, 18, hexc('#ffffff'))
    finish(c)
    glow(c, 16, 16, 15, with_alpha(hexc(col), 100))
    return c


def icon_derived():
    c = Canvas(32, 32)
    c.line(6, 26, 24, 8, hexc('#c8d0dc'), 3)
    c.line(4, 22, 10, 28, hexc('#8a6a3a'), 2)
    c.poly([(14, 12), (28, 12), (28, 20), (21, 28), (14, 20)], hexc('#6a3a2a'))
    c.line(21, 14, 21, 25, hexc('#c9a24a'), 1)
    return finish(c)


def icon_reset():
    c = Canvas(32, 32)
    c.ring(16, 16, 10, hexc('#d05a30'), 3)
    c.rect(18, 4, 28, 12, (0, 0, 0, 0))
    c.poly([(19, 3), (27, 8), (19, 13)], hexc('#d05a30'))
    return finish(c)


def icon_lock():
    c = Canvas(32, 32)
    c.ring(16, 12, 6, hexc('#8a8a90'), 3)
    c.rect(8, 13, 24, 28, hexc('#6a6a72'))
    c.rect(15, 18, 17, 23, hexc('#202024'))
    return finish(c)


def icon_toggle(on):
    c = Canvas(32, 32)
    c.rect(4, 11, 28, 21, hexc('#2a6a2a' if on else '#5a2a2a'))
    c.circle(21 if on else 11, 16, 7, hexc('#e8e8e8'))
    finish(c)
    if on:
        glow(c, 21, 16, 10, (120, 255, 120, 90))
    return c


def icon_connector():
    c = Canvas(32, 32)
    c.circle(16, 16, 5, hexc('#ffd66a'))
    c.circle(16, 16, 2, hexc('#ffffff'))
    glow(c, 16, 16, 13, (255, 210, 110, 170))
    return c


def icon_empty():
    return Canvas(32, 32)


def icon_skillbar():
    c = Canvas(32, 32)
    c.poly([(17, 2), (8, 18), (15, 18), (13, 30), (24, 12), (17, 12)], hexc('#ffd040'))
    finish(c)
    glow(c, 16, 16, 14, (255, 200, 60, 90))
    return c


def icon_tab(kind):
    if kind == 'active':
        c = Canvas(32, 32)
        c.circle(16, 16, 12, hexc('#d8d0c0'))
        c.circle(16, 16, 10, hexc('#2a2a30'))
        c.poly([(16, 6), (19, 16), (16, 26), (13, 16)], hexc('#d02020'))
        c.poly([(16, 16), (19, 16), (16, 26), (13, 16)], hexc('#e8e8e8'))
        return finish(c)
    if kind == 'main':
        c = Canvas(32, 32)
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 13 if i % 2 == 0 else 6
            pts.append((16 + math.cos(a) * r, 16 + math.sin(a) * r))
        c.poly(pts, hexc('#e2b23a'))
        return finish(c)
    if kind == 'side':
        return icon_quests()
    if kind == 'class':
        return items.book('#205a6a', '#c9a24a', '#7ae0ff', glow_rune=True)
    if kind == 'dungeon':
        return icon_dungeons()
    if kind == 'guild':
        return icon_tab_guild()
    if kind == 'daily':
        return icon_progress()
    if kind == 'available':
        return icon_map()
    if kind == 'completed':
        c = Canvas(32, 32)
        c.line(6, 17, 13, 24, hexc('#4ac04a'), 4)
        c.line(13, 24, 26, 9, hexc('#4ac04a'), 4)
        return finish(c)
    raise ValueError(kind)


def icon_tab_guild():
    c = Canvas(32, 32)
    c.rect(14, 2, 16, 30, hexc('#6a4a2a'))
    c.poly([(8, 5), (24, 5), (24, 24), (16, 29), (8, 24)], hexc('#e8e0d0'))
    c.poly([(16, 10), (19, 15), (16, 21), (13, 15)], hexc('#c9a24a'))
    return finish(c)


def icon_class(cls):
    colors = CLASS_COLORS
    c = _emblem_base(colors[cls])
    if cls == 'guardian':
        c.poly([(9, 7), (23, 7), (23, 18), (16, 26), (9, 18)], hexc('#b8bcc8'))
        c.poly([(11, 9), (21, 9), (21, 17), (16, 23), (11, 17)], hexc('#3a4a8a'))
        c.rect(15, 10, 17, 21, hexc('#e2c26a'))
        c.rect(12, 13, 20, 15, hexc('#e2c26a'))
    elif cls == 'warrior':
        c.line(9, 23, 23, 9, hexc('#d8dee6'), 2)
        c.line(9, 9, 23, 23, hexc('#d8dee6'), 2)
        c.line(7, 21, 11, 25, hexc('#c9a24a'), 2)
        c.line(21, 25, 25, 21, hexc('#c9a24a'), 2)
    elif cls == 'mage':
        c.line(10, 24, 20, 12, hexc('#8a5a2e'), 2)
        c.circle(21, 10, 4, hexc('#7fd0ff'))
    elif cls == 'assassin':
        c.line(10, 22, 22, 10, hexc('#d0d0e0'), 2)
        c.poly([(8, 12), (16, 8), (24, 12), (16, 15)], hexc('#2a1a3a'))
        c.px(13, 11, hexc('#ff4040'))
        c.px(19, 11, hexc('#ff4040'))
    else:
        for i in range(12):
            a = math.pi * 0.75 + i / 11 * math.pi * 1.5
            c.px(16 + math.cos(a) * 9, 16 + math.sin(a) * 9, hexc('#a07040'))
        c.line(9, 23, 23, 9, hexc('#e0e0e0'), 1)
        c.poly([(23, 9), (19, 9), (23, 13)], hexc('#e0e0e0'))
    finish(c, shade=False)
    glow(c, 16, 16, 15, with_alpha(hexc(colors[cls]), 70))
    return c


def icon_difficulty(level):
    cols = {'normal': '#4ab04a', 'hard': '#e0a020', 'nightmare': '#b01818', 'mythic': '#c040f0'}
    c = Canvas(32, 32)
    c.poly([(16, 3), (27, 7), (25, 20), (16, 29), (7, 20), (5, 7)], hexc(cols[level]))
    c.poly([(16, 6), (24, 9), (22, 19), (16, 25)], lighten(hexc(cols[level]), 0.2))
    n = {'normal': 1, 'hard': 2, 'nightmare': 3, 'mythic': 4}[level]
    for i in range(n):
        x = 16 + (i - (n - 1) / 2) * 6
        c.circle(x, 15, 2, hexc('#f2ead6'))
    finish(c)
    if level == 'mythic':
        glow(c, 16, 15, 14, (192, 64, 240, 90))
    return c


def icon_fog():
    c = Canvas(32, 32)
    rnd = random.Random(2)
    for _ in range(9):
        c.circle(rnd.randint(4, 28), rnd.randint(6, 26), rnd.randint(4, 8), (40, 34, 46, 235))
    return c


def icon_map_marker(kind):
    c = Canvas(32, 32)
    if kind == 'player':
        c.poly([(16, 5), (24, 25), (16, 20), (8, 25)], hexc('#3ad04a'))
        c.poly([(16, 5), (16, 20), (8, 25)], hexc('#2aa03a'))
    elif kind == 'quest':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 12 if i % 2 == 0 else 5
            pts.append((16 + math.cos(a) * r, 16 + math.sin(a) * r))
        c.poly(pts, hexc('#ffd040'))
    elif kind == 'dungeon':
        c.circle(16, 15, 9, hexc('#e8e0d0'))
        c.rect(12, 22, 20, 27, hexc('#e8e0d0'))
        c.circle(12, 14, 2, hexc('#200a0a'))
        c.circle(20, 14, 2, hexc('#200a0a'))
        c.line(13, 24, 13, 27, hexc('#200a0a'), 1)
        c.line(16, 24, 16, 27, hexc('#200a0a'), 1)
        c.line(19, 24, 19, 27, hexc('#200a0a'), 1)
    elif kind == 'waypoint':
        c.rect(9, 4, 10, 28, hexc('#5a3a1e'))
        c.poly([(10, 4), (25, 8), (10, 14)], hexc('#e02828'))
        c.poly([(10, 6), (20, 8), (10, 11)], hexc('#ff5a4a'))
        c.circle(10, 28, 3, hexc('#ffd040'))
    elif kind == 'town':
        c.poly([(6, 16), (16, 6), (26, 16)], hexc('#b04030'))
        c.rect(9, 16, 23, 27, hexc('#e0d0b0'))
        c.rect(14, 20, 18, 27, hexc('#6a4a2a'))
    finish(c)
    if kind in ('player', 'quest', 'waypoint'):
        glow(c, 16, 16, 15, (255, 240, 140, 90) if kind == 'quest' else (100, 255, 120, 80))
    return c


# ───────────────────────────── skill emblems ─────────────────────────────



def element_color(skill):
    text = (skill.get('name', '') + ' ' + str(skill.get('params', {}).get('particle', ''))).lower()
    if any(k in text for k in ('feuer', 'flame', 'meteor', 'erdbeben', 'explosiv')):
        return '#ff8a2a'
    if any(k in text for k in ('eis', 'frost', 'snow')):
        return '#9ae8ff'
    if any(k in text for k in ('blitz', 'stern')):
        return '#ffe24a'
    if any(k in text for k in ('gift', 'jagd', 'wind')):
        return '#8ae04a'
    if any(k in text for k in ('blut', 'wut', 'berserk', 'todes')):
        return '#ff4a4a'
    if any(k in text for k in ('schatten', 'tarn', 'meuchel', 'arkan', 'mana', 'teleport')):
        return '#c88aff'
    return '#e8e8f0'


def skill_emblem(skill):
    ring = CLASS_COLORS.get(skill.get('class'), '#c9a24a')
    el = hexc(element_color(skill))
    mech = skill.get('mechanic', 'PASSIVE')
    c = Canvas(32, 32)
    c.circle(16, 16, 15, hexc('#130f18'))
    for r in range(13, 0, -1):
        c.circle(16, 16, r, mix(hexc('#221a2c'), darken(hexc(ring), 0.55), (13 - r) / 13 * 0.6))
    if mech == 'STRIKE':
        c.line(8, 24, 22, 10, el, 3)
        c.line(9, 24, 23, 10, lighten(el, 0.5), 1)
        c.poly([(22, 10), (26, 6), (24, 12)], lighten(el, 0.4))
        c.line(6, 20, 12, 26, hexc('#c9a24a'), 2)
    elif mech == 'AREA':
        c.ring(16, 16, 9, el, 2)
        c.ring(16, 16, 5, lighten(el, 0.3), 1)
        for i in range(4):
            a = i * math.pi / 2 + 0.6
            c.line(16 + math.cos(a) * 9, 16 + math.sin(a) * 9, 16 + math.cos(a + 0.6) * 12, 16 + math.sin(a + 0.6) * 12, el, 2)
    elif mech == 'DASH':
        for off in (-6, 0, 6):
            c.line(9 + off, 9, 15 + off, 16, el, 2)
            c.line(15 + off, 16, 9 + off, 23, el, 2)
    elif mech == 'BUFF':
        c.poly([(16, 6), (25, 16), (20, 16), (20, 26), (12, 26), (12, 16), (7, 16)], el)
        c.line(16, 9, 16, 24, lighten(el, 0.5), 1)
    elif mech == 'SHIELD':
        c.poly([(16, 6), (25, 9), (24, 18), (16, 26), (8, 18), (7, 9)], el)
        c.poly([(16, 9), (22, 11), (21, 17), (16, 23)], lighten(el, 0.35))
    elif mech == 'TAUNT':
        c.rect(14, 6, 18, 19, el)
        c.rect(14, 22, 18, 25, el)
        c.ring(16, 16, 11, darken(el, 0.3), 1)
    elif mech == 'PULL':
        for i in range(5):
            x, y = 24 - i * 4, 8 + i * 4
            c.ring(x, y, 2, el, 1)
        c.poly([(5, 27), (6, 20), (9, 23), (12, 26)], lighten(el, 0.3))
    elif mech == 'HEAL':
        c.rect(13, 7, 19, 25, el)
        c.rect(7, 13, 25, 19, el)
    elif mech == 'PROJECTILE':
        c.circle(20, 12, 5, el)
        c.circle(19, 11, 2, lighten(el, 0.6))
        for i in range(3):
            c.line(16 - i * 3, 15 + i * 3, 10 - i * 3, 21 + i * 3, with_alpha(el, 220 - i * 60), 2)
    elif mech == 'LIGHTNING':
        c.poly([(18, 4), (9, 17), (15, 17), (12, 28), (23, 13), (17, 13)], el)
    elif mech == 'BLINK':
        for r, a in ((10, 255), (7, 200), (4, 150)):
            c.ring(16, 16, r, with_alpha(el, a), 1)
        c.circle(16, 16, 2, lighten(el, 0.6))
    elif mech == 'METEOR':
        c.circle(19, 19, 6, el)
        c.circle(18, 18, 3, lighten(el, 0.5))
        c.line(14, 14, 7, 7, with_alpha(el, 200), 3)
        c.line(19, 12, 14, 5, with_alpha(el, 150), 2)
    elif mech == 'MULTI_SHOT':
        for off in (-6, 0, 6):
            c.line(8, 24 + off // 2, 23, 9 + off, hexc('#c8a070'), 1)
            c.poly([(23, 9 + off), (26, 7 + off), (24, 11 + off)], el)
    elif mech == 'RAIN':
        for x in (9, 14, 19, 24):
            c.line(x, 6 + (x % 3) * 2, x - 2, 14 + (x % 3) * 2, el, 1)
            c.line(x - 1, 17, x - 3, 25, el, 1)
    elif mech == 'STEALTH':
        c.poly([(6, 16), (16, 9), (26, 16), (16, 23)], el)
        c.circle(16, 16, 3, hexc('#130f18'))
        c.line(7, 25, 25, 7, hexc('#130f18'), 2)
    else:  # PASSIVE
        c.poly([(16, 5), (19, 13), (27, 16), (19, 19), (16, 27), (13, 19), (5, 16), (13, 13)], el)
        c.circle(16, 16, 2, lighten(el, 0.6))
    c.ring(16, 16, 15, hexc(ring), 2)
    c.ring(16, 16, 13, darken(hexc(ring), 0.4), 1)
    return c


def skill_variants(skill):
    base = skill_emblem(skill)
    locked = Canvas.of(grayscale(base.img, 0.5))
    lock = icon_lock().img.resize((14, 14), Image.NEAREST)
    locked.img.alpha_composite(lock, (17, 17))
    maxed = Canvas.of(base.img.copy())
    maxed.ring(16, 16, 15, GOLD_LIGHT, 2)
    maxed.ring(16, 16, 13, GOLD, 1)
    for (x, y) in ((16, 1), (30, 16), (16, 30), (1, 16)):
        sparkle(maxed, x, y, (255, 245, 200, 255))
    return base, locked, maxed


# ───────────────────────────── font glyphs ─────────────────────────────

def marker(kind):
    c = Canvas(16, 20)
    if kind == 'active':
        body, edge, sym = hexc('#5a5a66'), hexc('#2a2a30'), hexc('#d8d8e0')
    else:
        body, edge, sym = hexc('#f2c230'), hexc('#7a5a10'), hexc('#ffffff')
    c.poly([(2, 1), (13, 1), (15, 4), (15, 12), (8, 19), (0, 12), (0, 4)], edge)
    c.poly([(3, 2), (12, 2), (14, 5), (14, 11), (8, 17), (1, 11), (1, 5)], body)
    c.poly([(3, 2), (12, 2), (13, 4), (2, 4)], lighten(body, 0.35))
    if kind == 'new':
        c.rect(7, 4, 8, 10, sym)
        c.rect(7, 12, 8, 13, sym)
    elif kind == 'ready':
        for (x, y) in ((5, 5), (6, 4), (7, 4), (8, 4), (9, 4), (10, 5), (10, 6), (9, 7), (8, 8), (7, 8), (7, 9), (7, 10)):
            c.px(x, y, sym)
        c.px(7, 12, sym)
        c.px(8, 12, sym)
        c.px(7, 13, sym)
        c.px(8, 13, sym)
    else:
        for x in (4, 7, 10):
            c.rect(x, 9, x + 1, 10, sym)
    return c


def hud_glyph(kind):
    c = Canvas(9, 9)
    if kind == 'heart':
        col = hexc('#e02828')
        c.rect(1, 1, 3, 3, col)
        c.rect(5, 1, 7, 3, col)
        c.poly([(0, 2), (8, 2), (4, 7)], col)
        c.px(2, 2, lighten(col, 0.6))
        finish(c, outline=(50, 8, 8, 255), shade=False)
    elif kind == 'mana':
        col = hexc('#3a6ef0')
        c.poly([(4, 0), (7, 4), (4, 8), (1, 4)], col)
        c.px(3, 3, lighten(col, 0.6))
    elif kind == 'coin':
        c.circle(4, 4, 3, hexc('#e2b23a'))
        c.rect(4, 2, 4, 6, hexc('#a8801e'))
    elif kind == 'shield':
        c.poly([(4, 0), (8, 1), (7, 5), (4, 8), (1, 5), (0, 1)], hexc('#5ad0e8'))
    elif kind == 'level':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 4 if i % 2 == 0 else 2
            pts.append((4 + math.cos(a) * r, 4.5 + math.sin(a) * r))
        c.poly(pts, hexc('#ffc830'))
    elif kind == 'sword':
        c.line(1, 7, 7, 1, hexc('#d8dee6'))
        c.line(1, 5, 3, 7, hexc('#c9a24a'))
    return c


def xp_segment(full):
    c = Canvas(3, 7)
    if full:
        c.rect(0, 0, 2, 6, hexc('#58d048'))
        c.rect(0, 0, 2, 1, hexc('#a8f090'))
        c.rect(0, 6, 2, 6, hexc('#2a8020'))
    else:
        c.rect(0, 0, 2, 6, hexc('#2a2a30'))
        c.rect(0, 0, 2, 0, hexc('#3a3a44'))
    return c


BAR_COLORS = {'hp': ('#e03030', '#ff8a7a', '#901818'), 'mana': ('#3a7ae8', '#9ac4ff', '#1c3c90'),
              'shield': ('#d8d8e8', '#ffffff', '#8a8aa0')}


def bar_segment(kind, state):
    """5x8 piece of the unit frame bars; state: full, empty, left, right (end caps)."""
    if state in ('left', 'right'):
        c = Canvas(2, 8)
        c.rect(0, 0, 1, 7, hexc('#c9a24a'))
        c.rect(1 if state == 'left' else 0, 1, 1 if state == 'left' else 0, 6, hexc('#120c10'))
        return c
    c = Canvas(5, 8)
    c.rect(0, 0, 4, 0, hexc('#c9a24a'))
    c.rect(0, 7, 4, 7, hexc('#7a5e2a'))
    if state == 'full':
        base, light, dark = (hexc(v) for v in BAR_COLORS[kind])
        c.rect(0, 1, 4, 6, base)
        c.rect(0, 1, 4, 2, light)
        c.rect(0, 6, 4, 6, dark)
    else:
        c.rect(0, 1, 4, 6, hexc('#1c1418'))
        c.rect(0, 1, 4, 1, hexc('#2a2026'))
    return c


def transparent(w, h):
    return Canvas(w, h)


# ───────────────────────────── tooltip frames & book ─────────────────────────────

RARITY_COLORS = {
    'common': '#b8b8c0', 'uncommon': '#4ac04a', 'rare': '#4a7af0', 'epic': '#b04ae0', 'legendary': '#f0a828',
    'mythic': '#e83a3a', 'ascended': '#ff5ad0', 'divine': '#fff2a0', 'gui': '#c9a24a',
}


def tooltip_background():
    c = Canvas(27, 27)
    c.rect(6, 6, 20, 20, (20, 15, 26, 238))
    for i in range(6, 21):
        c.px(i, 5, (20, 15, 26, 160))
        c.px(i, 21, (20, 15, 26, 160))
        c.px(5, i, (20, 15, 26, 160))
        c.px(21, i, (20, 15, 26, 160))
    return c


def tooltip_frame(rarity):
    col = hexc(RARITY_COLORS[rarity])
    c = Canvas(27, 27)
    c.outline_rect(5, 5, 21, 21, darken(col, 0.45))
    c.outline_rect(6, 6, 20, 20, col)
    for (x, y) in ((6, 6), (20, 6), (6, 20), (20, 20)):
        c.px(x, y, lighten(col, 0.5))
        c.px(x + (1 if x < 10 else -1), y, lighten(col, 0.2))
        c.px(x, y + (1 if y < 10 else -1), lighten(col, 0.2))
    c.px(13, 5, lighten(col, 0.5))
    c.px(13, 21, lighten(col, 0.5))
    if rarity in ('ascended', 'divine'):
        # the highest tiers get a second, brighter outline and diamond gems on all four sides
        c.outline_rect(4, 4, 22, 22, with_alpha(col, 120))
        gem = lighten(col, 0.7) if rarity == 'divine' else hexc('#ffffff')
        for (x, y) in ((13, 4), (13, 22), (4, 13), (22, 13)):
            c.px(x, y, gem)
            c.px(x - 1, y, col)
            c.px(x + 1, y, col)
            c.px(x, y - 1, col)
            c.px(x, y + 1, col)
    return c


def book_texture():
    """Replaces the vanilla book screen: a leather bound parchment page (192x192 area of a 256 texture)."""
    c = Canvas(256, 256)
    leather = hexc('#4a2a1e')
    c.rect(18, 1, 168, 182, leather)
    noise_fill(c, 18, 1, 168, 182, leather, 6, 11)
    noise_fill(c, 24, 6, 162, 177, hexc('#e8d8b0'), 7, 12)
    # aged edges
    for i in range(5):
        c.outline_rect(24 + i, 6 + i, 162 - i, 177 - i, with_alpha(hexc('#b89a62'), 140 - i * 26))
    c.outline_rect(19, 2, 167, 181, hexc('#c9a24a'))
    c.outline_rect(22, 4, 164, 179, hexc('#7a5e2a'))
    for (x, y) in ((19, 2), (167, 2), (19, 181), (167, 181)):
        c.rect(x - 1, y - 1, x + 1, y + 1, hexc('#f0d68a'))
    # small ornament at the bottom
    c.line(70, 170, 116, 170, hexc('#b89a62'), 1)
    c.poly([(93, 166), (97, 170), (93, 174), (89, 170)], hexc('#b89a62'))
    return c


def pack_icon():
    c = Canvas(64, 64)
    c.circle(32, 32, 30, hexc('#1d1823'))
    c.ring(32, 32, 30, hexc('#c9a24a'), 3)
    c.line(14, 50, 46, 18, hexc('#d8dee6'), 4)
    c.line(10, 44, 20, 54, hexc('#c9a24a'), 3)
    c.line(50, 50, 22, 18, hexc('#8a5a2e'), 3)
    c.circle(20, 16, 6, hexc('#7fd0ff'))
    finish(c, shade=False)
    glow(c, 20, 16, 12, (120, 210, 255, 150))
    return c

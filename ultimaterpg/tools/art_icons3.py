"""Menu icons for peoples, the admin button, guild banners, the bank and the new codex tabs (32x32)."""
import math
from draw import Canvas, finish, hexc, lighten, darken, glow, sparkle


def admin():
    """Red cogwheel with a golden hammer - only admins ever see it."""
    c = Canvas(32, 32)
    for i in range(8):
        a = i * math.pi / 4
        x, y = 16 + math.cos(a) * 11, 16 + math.sin(a) * 11
        c.rect(int(x) - 2, int(y) - 2, int(x) + 2, int(y) + 2, hexc('#8a1a1a'))
    c.circle(16, 16, 10, hexc('#b02a2a'))
    c.circle(16, 16, 8, hexc('#d04040'))
    c.circle(16, 16, 4, hexc('#3a0a0a'))
    c.line(10, 24, 21, 13, hexc('#6a4a2a'), 2)
    c.rect(18, 8, 25, 13, hexc('#f0c040'))
    c.rect(19, 9, 24, 12, hexc('#ffe080'))
    return finish(c)


def _face(c, skin, hair, eyes='#2a2a2a'):
    c.rect(10, 9, 22, 22, hexc(skin))
    c.rect(10, 7, 22, 11, hexc(hair))
    c.rect(13, 14, 15, 16, hexc(eyes))
    c.rect(17, 14, 19, 16, hexc(eyes))


def race_human():
    c = Canvas(32, 32)
    c.rect(7, 22, 25, 30, hexc('#3a5a9a'))                # tunic
    c.rect(14, 22, 18, 30, hexc('#e8c27a'))
    _face(c, '#e0b090', '#6a4020')
    c.rect(13, 19, 19, 20, hexc('#a06a50'))
    finish(c)
    sparkle(c, 25, 6, (255, 220, 140, 255))
    return c


def race_elf():
    c = Canvas(32, 32)
    c.rect(8, 22, 24, 30, hexc('#3a6a3a'))
    _face(c, '#f0dcc8', '#f0e8b0', '#4ab060')
    c.poly([(10, 12), (4, 6), (10, 16)], hexc('#f0dcc8'))   # pointed ears
    c.poly([(22, 12), (28, 6), (22, 16)], hexc('#f0dcc8'))
    c.rect(10, 7, 22, 9, hexc('#c0e0c0'))                  # circlet
    c.rect(15, 6, 17, 8, hexc('#60e0a0'))
    finish(c)
    glow(c, 16, 7, 6, (96, 224, 160, 70))
    return c


def race_dwarf():
    c = Canvas(32, 32)
    c.rect(6, 24, 26, 30, hexc('#6a6e76'))                 # broad armor
    _face(c, '#d8a080', '#a0502a')
    c.rect(8, 6, 24, 10, hexc('#8a8a96'))                  # helmet
    c.rect(15, 3, 17, 7, hexc('#c0c0c8'))
    c.poly([(10, 17), (22, 17), (21, 27), (16, 30), (11, 27)], hexc('#b0602a'))   # beard
    c.line(16, 19, 16, 28, hexc('#e0b040'), 1)             # braid ring
    c.rect(15, 24, 17, 25, hexc('#e0b040'))
    return finish(c)


def race_locked():
    c = Canvas(32, 32)
    c.rect(10, 9, 22, 22, hexc('#4a4a50'))
    c.rect(8, 22, 24, 30, hexc('#3a3a40'))
    c.rect(11, 15, 21, 26, hexc('#7a6a3a'))
    c.ring(16, 14, 4, hexc('#7a6a3a'), 2)
    c.rect(15, 19, 17, 23, hexc('#1a1a1a'))
    return finish(c)


def members():
    """Three heads in a row."""
    c = Canvas(32, 32)
    for x, col, y in ((8, '#3a6ad0', 12), (24, '#c03a3a', 12), (16, '#e0b030', 9)):
        c.circle(x, y, 4, hexc('#e0b090'))
        c.rect(x - 5, y + 5, x + 5, y + 16, hexc(col))
    return finish(c)


def banner_edit(color='#3a6ad0'):
    """A banner with a brush."""
    c = Canvas(32, 32)
    c.rect(6, 2, 22, 4, hexc('#8a6a3e'))
    c.poly([(7, 4), (21, 4), (21, 22), (14, 27), (7, 22)], hexc(color))
    c.poly([(14, 8), (17, 13), (14, 18), (11, 13)], hexc('#f0d68a'))
    c.line(19, 28, 28, 14, hexc('#7a5a32'), 2)
    c.rect(26, 10, 29, 15, hexc('#e8e0d0'))
    c.rect(27, 8, 29, 11, hexc('#d04040'))
    return finish(c)


def pattern(name='stripe'):
    """Small banner swatch with a generic pattern glyph."""
    c = Canvas(32, 32)
    c.poly([(8, 3), (24, 3), (24, 25), (16, 30), (8, 25)], hexc('#e8e0d0'))
    ink = hexc('#3a3a4a')
    if name == 'stripe':
        c.rect(14, 3, 18, 28, ink)
    elif name == 'cross':
        c.rect(14, 3, 18, 28, ink)
        c.rect(8, 12, 24, 16, ink)
    elif name == 'circle':
        c.circle(16, 14, 5, ink)
    else:
        c.poly([(16, 6), (21, 14), (16, 22), (11, 14)], ink)
    return finish(c)


def shield_banner():
    c = Canvas(32, 32)
    c.poly([(6, 4), (26, 4), (26, 18), (16, 29), (6, 18)], hexc('#7a5a32'))
    c.poly([(8, 6), (24, 6), (24, 17), (16, 26), (8, 17)], hexc('#3a6ad0'))
    c.rect(15, 6, 17, 26, hexc('#f0d68a'))
    c.rect(8, 11, 24, 13, hexc('#f0d68a'))
    return finish(c)


def vault():
    """Bank vault door."""
    c = Canvas(32, 32)
    c.rect(4, 4, 28, 28, hexc('#5a5a66'))
    c.rect(6, 6, 26, 26, hexc('#8a8a96'))
    c.ring(16, 16, 8, hexc('#c9a24a'), 2)
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        c.line(16, 16, int(16 + math.cos(a) * 7), int(16 + math.sin(a) * 7), hexc('#c9a24a'), 1)
    c.circle(16, 16, 2, hexc('#ffe080'))
    return finish(c)


def chest_slot(n=1):
    """Double chest with a number of pips (storage compartment)."""
    c = Canvas(32, 32)
    c.rect(3, 10, 29, 27, hexc('#8a5a2a'))
    c.rect(3, 10, 29, 15, hexc('#a06c3c'))
    c.rect(15, 13, 17, 18, hexc('#c0c0c8'))
    c.line(16, 10, 16, 27, hexc('#5a3a1e'), 1)
    for i in range(min(n, 6)):
        c.rect(5 + i * 4, 22, 7 + i * 4, 24, hexc('#f0c040'))
    return finish(c)


def depth():
    """A dark hole with a blue ghost light."""
    c = Canvas(32, 32)
    c.poly([(3, 26), (8, 14), (16, 10), (24, 14), (29, 26)], hexc('#4a4a50'))
    c.poly([(8, 26), (11, 17), (16, 14), (21, 17), (24, 26)], hexc('#0a0a12'))
    c.circle(16, 21, 3, hexc('#80e8ff'))
    finish(c)
    glow(c, 16, 21, 9, (100, 220, 255, 90))
    sparkle(c, 12, 7, (180, 240, 255, 255))
    return c


def rune_book():
    c = Canvas(32, 32)
    c.rect(6, 5, 26, 28, hexc('#3a2a5a'))
    c.rect(8, 7, 24, 26, hexc('#4a3a7a'))
    c.line(16, 9, 16, 24, hexc('#ff7a2a'), 1)
    c.line(16, 15, 11, 10, hexc('#7ae8ff'), 1)
    c.line(16, 15, 21, 10, hexc('#60e070'), 1)
    finish(c)
    glow(c, 16, 15, 9, (200, 140, 255, 60))
    return c


def peoples():
    """Codex tab: three small faces (human, elf, dwarf)."""
    c = Canvas(32, 32)
    for x, skin, hair in ((7, '#e0b090', '#6a4020'), (16, '#f0dcc8', '#f0e8b0'), (25, '#d8a080', '#a0502a')):
        c.rect(x - 4, 10, x + 4, 18, hexc(skin))
        c.rect(x - 4, 8, x + 4, 10, hexc(hair))
        c.rect(x - 2, 13, x - 1, 14, hexc('#2a2a2a'))
        c.rect(x + 1, 13, x + 2, 14, hexc('#2a2a2a'))
    c.poly([(21, 17), (29, 17), (28, 24), (25, 26), (22, 24)], hexc('#b0602a'))
    c.poly([(12, 12), (9, 8), (12, 15)], hexc('#f0dcc8'))
    c.poly([(20, 12), (23, 8), (20, 15)], hexc('#f0dcc8'))
    return finish(c)


def icons():
    return {
        'admin': admin, 'race_human': race_human, 'race_elf': race_elf, 'race_dwarf': race_dwarf,
        'race_locked': race_locked, 'members': members, 'banner_edit': banner_edit,
        'banner_color': lambda: banner_edit('#c03a3a'), 'shield_banner': shield_banner,
        **{f'pattern_{p}': (lambda p: (lambda: pattern(p)))(p) for p in ('stripe', 'cross', 'circle', 'rhombus')},
        'bank': vault, **{f'bank_slot_{n}': (lambda n: (lambda: chest_slot(n)))(n) for n in range(1, 7)},
        'codex_depths': depth, 'codex_runes': rune_book, 'codex_races': peoples, 'depth': depth,
    }

"""Menu icons for the character screen, guilds, codex and shops (32x32)."""
import math
from draw import Canvas, finish, hexc, lighten, darken, glow, sparkle


def banner(color='#3a6ad0', emblem='#f0d68a'):
    c = Canvas(32, 32)
    c.rect(14, 2, 16, 30, hexc('#6a4a2a'))
    c.rect(6, 3, 26, 4, hexc('#8a6a3e'))
    c.poly([(8, 5), (24, 5), (24, 24), (16, 29), (8, 24)], hexc(color))
    c.poly([(16, 10), (19, 15), (16, 21), (13, 15)], hexc(emblem))
    return finish(c)


def play():
    c = Canvas(32, 32)
    c.circle(16, 16, 13, hexc('#2a8a2a'))
    c.poly([(12, 8), (24, 16), (12, 24)], hexc('#e8ffe0'))
    finish(c)
    glow(c, 16, 16, 15, (120, 255, 120, 80))
    return c


def scroll(lines='#6a5034'):
    c = Canvas(32, 32)
    c.rect(8, 6, 24, 26, hexc('#e6d3a6'))
    c.rect(6, 4, 26, 7, hexc('#b8935a'))
    c.rect(6, 25, 26, 28, hexc('#b8935a'))
    for y in (10, 13, 16, 19, 22):
        c.line(11, y, 21, y, hexc(lines), 1)
    return finish(c)


def bell():
    c = Canvas(32, 32)
    c.poly([(10, 22), (12, 10), (16, 6), (20, 10), (22, 22)], hexc('#e8b840'))
    c.rect(8, 22, 24, 24, hexc('#c89820'))
    c.circle(16, 26, 2, hexc('#a07010'))
    c.px(14, 10, hexc('#fff0b0'))
    finish(c)
    sparkle(c, 25, 7, hexc('#ffffff'))
    return c


def crown(color='#e0b030'):
    c = Canvas(32, 32)
    c.poly([(6, 22), (6, 10), (11, 16), (16, 7), (21, 16), (26, 10), (26, 22)], hexc(color))
    c.rect(6, 22, 26, 25, darken(hexc(color), 0.2))
    for x, col in ((11, '#e03030'), (16, '#3080e0'), (21, '#30c050')):
        c.circle(x, 23, 1, hexc(col))
    finish(c)
    sparkle(c, 26, 6, hexc('#ffffff'))
    return c


def gem_bag():
    c = Canvas(32, 32)
    c.circle(16, 19, 9, hexc('#7a5230'))
    c.rect(13, 7, 19, 11, hexc('#7a5230'))
    c.line(12, 11, 20, 11, hexc('#d0a040'), 1)
    c.poly([(16, 15), (19, 19), (16, 23), (13, 19)], hexc('#40e0a0'))
    return finish(c)


def board():
    c = Canvas(32, 32)
    c.rect(4, 6, 28, 24, hexc('#7a5230'))
    c.rect(6, 8, 26, 22, hexc('#a07040'))
    for x, y, col in ((8, 10, '#e6d3a6'), (17, 9, '#f0e0b0'), (10, 16, '#e0c890'), (19, 15, '#e6d3a6')):
        c.rect(x, y, x + 6, y + 5, hexc(col))
        c.px(x + 3, y, hexc('#c03030'))
    c.rect(8, 24, 10, 29, hexc('#5a3a1e'))
    c.rect(22, 24, 24, 29, hexc('#5a3a1e'))
    return finish(c)


def helmet(color='#e0b030'):
    c = Canvas(32, 32)
    c.poly([(8, 24), (8, 13), (12, 7), (20, 7), (24, 13), (24, 24), (20, 24), (20, 16), (12, 16), (12, 24)], hexc(color))
    c.rect(15, 4, 17, 8, hexc('#c03030'))
    c.rect(12, 16, 20, 18, darken(hexc(color), 0.4))
    return finish(c)


def ladder():
    c = Canvas(32, 32)
    for i, col in enumerate(('#9a9a9a', '#ffffff', '#58d048', '#4ac0e8', '#3a6ad0', '#b04ae0', '#f0a828')):
        y = 27 - i * 3
        c.rect(6 + i, y, 26 - i, y + 1, hexc(col))
    return finish(c)


def trophy():
    c = Canvas(32, 32)
    c.poly([(9, 5), (23, 5), (22, 14), (16, 18), (10, 14)], hexc('#e8b840'))
    c.rect(15, 18, 17, 23, hexc('#c89820'))
    c.rect(10, 23, 22, 27, hexc('#8a5a2a'))
    c.ring(8, 9, 3, hexc('#e8b840'))
    c.ring(24, 9, 3, hexc('#e8b840'))
    return finish(c)


def target():
    c = Canvas(32, 32)
    for r, col in ((12, '#e03030'), (9, '#f0f0f0'), (6, '#e03030'), (3, '#f0f0f0')):
        c.circle(16, 16, r, hexc(col))
    c.line(16, 16, 27, 5, hexc('#6a4a2a'), 2)
    return finish(c)


def dye():
    c = Canvas(32, 32)
    for i, col in enumerate(('#e03030', '#e0b030', '#30c050', '#3080e0', '#b040e0')):
        a = i * 2 * math.pi / 5
        c.circle(16 + math.cos(a) * 7, 16 + math.sin(a) * 7, 4, hexc(col))
    return finish(c)


def quill():
    c = Canvas(32, 32)
    c.rect(6, 8, 22, 26, hexc('#e6d3a6'))
    for y in (12, 15, 18):
        c.line(9, y, 19, y, hexc('#6a5034'), 1)
    c.poly([(28, 2), (20, 18), (22, 19)], hexc('#f0f0f0'))
    c.line(20, 18, 18, 23, hexc('#303030'), 1)
    return finish(c)


def tome(color='#6a3a1e'):
    c = Canvas(32, 32)
    c.rect(7, 5, 25, 27, hexc(color))
    c.rect(9, 7, 25, 25, lighten(hexc(color), 0.15))
    c.rect(23, 6, 26, 26, hexc('#e6d3a6'))
    c.poly([(16, 10), (20, 16), (16, 22), (12, 16)], hexc('#f0d68a'))
    return finish(c)


def keycap(label_color='#f0f0f0'):
    c = Canvas(32, 32)
    c.rect(5, 7, 27, 25, hexc('#505058'))
    c.rect(7, 8, 25, 22, hexc('#7a7a84'))
    # letter F
    c.rect(13, 11, 14, 19, hexc(label_color))
    c.rect(13, 11, 19, 12, hexc(label_color))
    c.rect(13, 15, 17, 16, hexc(label_color))
    return finish(c)


def skull(col='#e8e0d0'):
    c = Canvas(32, 32)
    c.circle(16, 14, 10, hexc(col))
    c.rect(11, 20, 21, 26, hexc(col))
    c.circle(12, 13, 2, hexc('#200a0a'))
    c.circle(20, 13, 2, hexc('#200a0a'))
    for x in (13, 16, 19):
        c.line(x, 22, x, 26, hexc('#200a0a'), 1)
    return finish(c)


def beast():
    c = Canvas(32, 32)
    c.poly([(6, 10), (12, 4), (14, 12), (18, 12), (20, 4), (26, 10), (24, 24), (16, 28), (8, 24)], hexc('#7a8a6a'))
    c.circle(12, 16, 2, hexc('#f0d040'))
    c.circle(20, 16, 2, hexc('#f0d040'))
    c.poly([(14, 22), (18, 22), (16, 25)], hexc('#f0f0f0'))
    return finish(c)


def portal():
    c = Canvas(32, 32)
    c.rect(6, 4, 26, 28, hexc('#3a3a44'))
    c.rect(9, 7, 23, 28, hexc('#6a2ab0'))
    for y in range(9, 27, 4):
        c.line(11, y, 21, y + 2, hexc('#b070f0'), 1)
    return finish(c)


def particles():
    c = Canvas(32, 32)
    for x, y in ((9, 9), (22, 7), (16, 16), (8, 23), (24, 22)):
        sparkle(c, x, y, hexc('#f0d0ff'))
    glow(c, 16, 16, 14, (200, 120, 255, 90))
    return c


def cape():
    c = Canvas(32, 32)
    c.poly([(9, 5), (23, 5), (27, 28), (16, 25), (5, 28)], hexc('#b02a2a'))
    c.rect(9, 5, 23, 7, hexc('#e0b030'))
    return finish(c)


def paw():
    c = Canvas(32, 32)
    c.circle(16, 20, 6, hexc('#c08a5a'))
    for x, y in ((9, 12), (14, 8), (19, 8), (24, 12)):
        c.circle(x, y, 3, hexc('#c08a5a'))
    return finish(c)


def firework():
    c = Canvas(32, 32)
    for i in range(10):
        a = i * math.pi / 5
        c.line(16, 14, 16 + math.cos(a) * 11, 14 + math.sin(a) * 11, hexc(['#ff5050', '#ffd040', '#50a0ff'][i % 3]), 1)
    c.rect(15, 22, 17, 30, hexc('#a03030'))
    return c


def sword_skin():
    c = Canvas(32, 32)
    c.line(8, 24, 25, 7, hexc('#f0d040'), 3)
    c.line(6, 21, 11, 26, hexc('#a07010'), 2)
    finish(c)
    sparkle(c, 24, 8, hexc('#ffffff'))
    return c


def class_swap():
    """Two class emblems with circular arrows."""
    c = Canvas(32, 32)
    c.circle(10, 11, 6, hexc('#c83a3a'))
    c.circle(22, 21, 6, hexc('#e0a030'))
    c.line(8, 9, 12, 13, hexc('#f0e0d8'), 1)
    c.line(12, 9, 8, 13, hexc('#f0e0d8'), 1)
    c.poly([(19, 18), (25, 18), (25, 22), (22, 25), (19, 22)], hexc('#f0e6c0'))
    for i in range(7):
        a = -math.pi * 0.15 + i * math.pi * 0.1
        c.px(16 + math.cos(a) * 12, 16 + math.sin(a) * 12 - 6, hexc('#7ad0ff'))
        c.px(16 - math.cos(a) * 12, 16 - math.sin(a) * 12 + 6, hexc('#7ad0ff'))
    c.poly([(25, 7), (29, 10), (24, 12)], hexc('#7ad0ff'))
    c.poly([(7, 25), (3, 22), (8, 20)], hexc('#7ad0ff'))
    return finish(c)


def character_delete():
    """Tombstone with a red cross."""
    c = Canvas(32, 32)
    c.rect(8, 27, 24, 29, hexc('#5a4a3a'))
    c.rect(10, 12, 22, 27, hexc('#8a8a94'))
    c.circle(16, 12, 6, hexc('#8a8a94'))
    c.rect(15, 9, 17, 20, hexc('#5a5a64'))
    c.rect(12, 12, 20, 14, hexc('#5a5a64'))
    c.line(20, 18, 28, 26, hexc('#d02828'), 3)
    c.line(28, 18, 20, 26, hexc('#d02828'), 3)
    return finish(c)


def confirm_yes():
    c = Canvas(32, 32)
    c.circle(16, 16, 13, hexc('#2a8a2a'))
    c.line(9, 16, 14, 22, hexc('#e8ffe0'), 3)
    c.line(14, 22, 24, 10, hexc('#e8ffe0'), 3)
    return finish(c)


def confirm_no():
    c = Canvas(32, 32)
    c.circle(16, 16, 13, hexc('#8a2020'))
    c.line(10, 10, 22, 22, hexc('#ffe0e0'), 3)
    c.line(22, 10, 10, 22, hexc('#ffe0e0'), 3)
    return finish(c)


def finder():
    """Spyglass over two small figures."""
    c = Canvas(32, 32)
    for x, col in ((8, '#c83a3a'), (16, '#e0a030'), (24, '#3ab8e0')):
        c.circle(x, 21, 3, hexc(col))
        c.rect(x - 3, 24, x + 3, 29, hexc(col))
    c.line(6, 14, 20, 4, hexc('#c9a24a'), 4)
    c.circle(22, 4, 3, hexc('#9ae8ff'))
    c.line(4, 15, 8, 13, hexc('#6a4a2a'), 3)
    return finish(c)


def role(kind):
    c = Canvas(32, 32)
    c.circle(16, 16, 14, hexc({'tank': '#5a4a1a', 'healer': '#1a4a2a', 'damage': '#4a1a1a'}[kind]))
    if kind == 'tank':
        c.poly([(16, 6), (25, 9), (24, 18), (16, 26), (8, 18), (7, 9)], hexc('#e0b040'))
        c.poly([(16, 9), (22, 11), (21, 17), (16, 23)], hexc('#f0d070'))
    elif kind == 'healer':
        c.rect(13, 7, 19, 25, hexc('#60e080'))
        c.rect(7, 13, 25, 19, hexc('#60e080'))
    else:
        c.line(8, 24, 24, 8, hexc('#e0e6ee'), 3)
        c.line(8, 8, 24, 24, hexc('#e0e6ee'), 3)
        c.line(6, 22, 10, 26, hexc('#c9a24a'), 2)
        c.line(22, 26, 26, 22, hexc('#c9a24a'), 2)
    return finish(c)


def backpack():
    """Leather backpack with straps and a buckle."""
    c = Canvas(32, 32)
    c.rect(8, 9, 24, 28, hexc('#7a4e2a'))
    c.rect(9, 10, 23, 27, hexc('#8e5e34'))
    c.rect(6, 14, 8, 26, hexc('#6a4222'))
    c.rect(24, 14, 26, 26, hexc('#6a4222'))
    c.rect(10, 5, 22, 9, hexc('#6a4222'))
    c.rect(12, 3, 20, 5, hexc('#5a3a1e'))
    c.rect(9, 10, 23, 16, hexc('#a06c3c'))
    c.rect(15, 15, 17, 19, hexc('#c9a24a'))
    c.rect(12, 20, 13, 27, hexc('#5a3a1e'))
    c.rect(19, 20, 20, 27, hexc('#5a3a1e'))
    return finish(c)


RUNE_COLORS = {'fire': '#ff7a2a', 'frost': '#7ae8ff', 'storm': '#ffe040', 'life': '#60e070', 'shadow': '#b060ff',
               'arcane': '#ff70e0', 'ward': '#f0c040'}
# glyph strokes on a 32x32 grid (rough futhark shapes)
RUNE_GLYPHS = {
    'fire': [(13, 7, 13, 25), (13, 9, 20, 13), (13, 15, 20, 19)],             # ᚠ
    'frost': [(16, 7, 16, 25), (12, 12, 20, 12)],                             # ᛁ with a frost bar
    'storm': [(18, 7, 13, 15), (13, 15, 19, 17), (19, 17, 14, 25)],           # ᛋ lightning
    'life': [(12, 7, 12, 25), (12, 7, 19, 11), (19, 11, 12, 16), (12, 16, 19, 21), (19, 21, 12, 25)],  # ᛒ
    'shadow': [(10, 7, 10, 25), (22, 7, 22, 25), (10, 7, 22, 25), (22, 7, 10, 25)],                     # ᛞ
    'arcane': [(13, 7, 13, 25), (13, 9, 20, 13), (13, 14, 20, 18)],           # ᚨ
    'ward': [(16, 9, 16, 25), (16, 15, 10, 8), (16, 15, 22, 8)],              # ᛉ
}


def rune_stone(kind):
    """Grey rune stone with a glowing glyph."""
    c = Canvas(32, 32)
    c.poly([(9, 4), (23, 3), (27, 10), (26, 27), (16, 30), (6, 27), (5, 10)], hexc('#5a5a66'))
    c.poly([(9, 4), (23, 3), (25, 8), (8, 9)], hexc('#74747f'))
    c.poly([(6, 25), (16, 28), (26, 25), (26, 27), (16, 30), (6, 27)], hexc('#3e3e48'))
    col = hexc(RUNE_COLORS[kind])
    for x1, y1, x2, y2 in RUNE_GLYPHS[kind]:
        c.line(x1, y1, x2, y2, darken(col, 0.45), 3)
    for x1, y1, x2, y2 in RUNE_GLYPHS[kind]:
        c.line(x1, y1, x2, y2, col, 1)
    finish(c)
    glow(c, 16, 16, 12, col[:3] + (60,))
    return c


def rune_tier(level):
    """Amethyst shard with 1-3 golden pips; level 0 = locked."""
    c = Canvas(32, 32)
    shard = '#9a6ae0' if level else '#5a5a60'
    c.poly([(16, 2), (23, 12), (20, 24), (12, 24), (9, 12)], hexc(shard))
    c.poly([(16, 2), (16, 24), (12, 24), (9, 12)], lighten(hexc(shard), 0.25))
    if level:
        for i in range(level):
            x = 16 + (i - (level - 1) / 2) * 7
            c.circle(int(x), 28, 2, hexc('#f0c040'))
        finish(c)
        sparkle(c, 19, 7, (255, 255, 255, 255))
        return c
    c.rect(11, 16, 21, 27, hexc('#7a6a3a'))
    c.ring(16, 15, 4, hexc('#7a6a3a'), 2)
    c.rect(15, 20, 17, 24, hexc('#2a2a2a'))
    return finish(c)


def rune_bind():
    """Enchanting table with a floating book."""
    c = Canvas(32, 32)
    c.rect(5, 20, 27, 29, hexc('#2a1e3a'))
    c.rect(5, 18, 27, 20, hexc('#b02a2a'))
    c.rect(7, 21, 9, 28, hexc('#46a0c0'))
    c.rect(23, 21, 25, 28, hexc('#46a0c0'))
    c.poly([(8, 9), (16, 12), (16, 16), (8, 13)], hexc('#e8dcc0'))
    c.poly([(24, 9), (16, 12), (16, 16), (24, 13)], hexc('#d8ccb0'))
    c.line(8, 13, 16, 16, hexc('#7a3a1a'), 1)
    c.line(24, 13, 16, 16, hexc('#7a3a1a'), 1)
    finish(c)
    for x, y in ((5, 6), (27, 5), (13, 4), (21, 3)):
        sparkle(c, x, y, (200, 140, 255, 255))
    glow(c, 16, 12, 10, (180, 120, 255, 60))
    return c


def rune_weapon():
    """Sword outline with a question mark - no weapon chosen."""
    c = Canvas(32, 32)
    c.line(7, 25, 24, 8, hexc('#8a8a96'), 3)
    c.line(5, 20, 12, 27, hexc('#6a5a3a'), 2)
    c.line(19, 22, 25, 22, hexc('#f0c040'), 2)
    c.line(25, 22, 25, 26, hexc('#f0c040'), 2)
    c.rect(24, 29, 25, 30, hexc('#f0c040'))
    return finish(c)

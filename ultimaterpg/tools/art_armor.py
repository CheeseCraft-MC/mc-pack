"""Raid kit armor: inventory icons (32x32), armor layers (64x32 humanoid / humanoid_leggings) and 3D helmet models."""
import random
import zlib
from draw import Canvas, finish, hexc, lighten, darken, mix, sparkle, glow

KITS = {
    # base, dark, trim, accent (glow), crest style
    'dragon_emperor': {'base': '#7a1a14', 'dark': '#3a0a0a', 'trim': '#e8b030', 'accent': '#ff8a2a', 'crest': 'horns'},
    'frost_throne': {'base': '#9ad0ec', 'dark': '#3a6a8a', 'trim': '#f4fbff', 'accent': '#40d0ff', 'crest': 'ice'},
    'star_eater': {'base': '#241640', 'dark': '#0c0618', 'trim': '#c9a0ff', 'accent': '#fff2a0', 'crest': 'halo'},
    'infernal_scourge': {'base': '#2a0e0a', 'dark': '#120402', 'trim': '#ff6a20', 'accent': '#ffc24a', 'crest': 'flame'},
}
PIECES = ('helm', 'chest', 'legs', 'boots')


def _rnd(*key):
    return random.Random(zlib.crc32('|'.join(map(str, key)).encode()))


def _metal(c, x1, y1, x2, y2, col, rnd, var=0.12):
    """Fills a rectangle with slightly noisy metal."""
    for x in range(x1, x2):
        for y in range(y1, y2):
            t = rnd.uniform(-var, var)
            c.px(x, y, lighten(col, t) if t > 0 else darken(col, -t))


# ───────────────────────────── icons ─────────────────────────────

def icon(kit, piece):
    k = KITS[kit]
    base, dark, trim, acc = (hexc(k[n]) for n in ('base', 'dark', 'trim', 'accent'))
    c = Canvas(32, 32)
    if piece == 'helm':
        c.poly([(8, 26), (7, 14), (10, 7), (16, 5), (22, 7), (25, 14), (24, 26), (19, 26), (19, 18), (13, 18), (13, 26)], base)
        c.poly([(8, 14), (16, 9), (24, 14), (24, 16), (8, 16)], trim)
        c.rect(15, 18, 16, 25, trim)
        c.poly([(10, 8), (16, 6), (22, 8), (16, 10)], lighten(base, 0.3))
        if k['crest'] == 'horns':
            c.poly([(8, 12), (3, 6), (2, 1), (6, 4), (10, 9)], trim)
            c.poly([(24, 12), (29, 6), (30, 1), (26, 4), (22, 9)], trim)
        elif k['crest'] == 'ice':
            for x, h in ((10, 6), (16, 9), (22, 6), (13, 4), (19, 4)):
                c.poly([(x - 2, 8), (x, 8 - h), (x + 2, 8)], lighten(acc, 0.3))
        elif k['crest'] == 'flame':
            c.poly([(10, 8), (9, 2), (12, 5), (13, -1), (15, 4), (16, -3), (17, 4), (19, -1), (20, 5), (23, 2), (22, 8)], acc)
            c.poly([(12, 8), (11, 4), (16, 1), (21, 4), (20, 8)], lighten(acc, 0.35))
        else:
            c.ring(16, 6, 6, acc, 1)
            sparkle(c, 16, 0, acc + (255,) if len(acc) == 3 else acc)
        c.rect(11, 16, 13, 17, acc)
        c.rect(19, 16, 21, 17, acc)
    elif piece == 'chest':
        c.poly([(5, 8), (11, 5), (16, 8), (21, 5), (27, 8), (28, 16), (24, 16), (24, 29), (8, 29), (8, 16), (4, 16)], base)
        c.poly([(5, 8), (11, 5), (12, 9), (8, 12), (4, 12)], trim)
        c.poly([(27, 8), (21, 5), (20, 9), (24, 12), (28, 12)], trim)
        c.rect(8, 22, 24, 23, trim)
        c.poly([(16, 11), (20, 15), (16, 20), (12, 15)], acc)
        c.poly([(16, 13), (18, 15), (16, 17), (14, 15)], lighten(acc, 0.5))
        c.rect(9, 25, 23, 28, darken(base, 0.25))
    elif piece == 'legs':
        c.rect(8, 5, 24, 9, trim)
        c.poly([(8, 9), (15, 9), (15, 28), (9, 28)], base)
        c.poly([(17, 9), (24, 9), (23, 28), (17, 28)], base)
        c.rect(9, 16, 14, 18, trim)
        c.rect(18, 16, 23, 18, trim)
        c.rect(15, 6, 17, 8, acc)
    else:
        c.poly([(6, 10), (13, 10), (13, 22), (15, 26), (15, 29), (4, 29), (4, 25), (6, 22)], base)
        c.poly([(19, 10), (26, 10), (26, 22), (28, 25), (28, 29), (17, 29), (17, 26), (19, 22)], base)
        c.rect(6, 10, 13, 12, trim)
        c.rect(19, 10, 26, 12, trim)
        c.rect(4, 27, 15, 29, darken(base, 0.35))
        c.rect(17, 27, 28, 29, darken(base, 0.35))
        c.px(9, 18, acc)
        c.px(22, 18, acc)
    finish(c)
    glow(c, 16, 16, 15, acc[:3] + (40,))
    return c


# ───────────────────────────── armor layers ─────────────────────────────

def _box(c, ox, oy, w, h, d, col, rnd, rows=None):
    """Paints all faces of a skin box (UV origin ox/oy, size w x h x d). rows limits the painted side rows."""
    y1, y2 = (rows if rows else (0, h))
    # top and bottom
    if rows is None or rows[0] == 0:
        _metal(c, ox + d, oy, ox + d + w, oy + d, lighten(col, 0.15), rnd)
    if rows is None or rows[1] == h:
        _metal(c, ox + d + w, oy, ox + d + w + w, oy + d, darken(col, 0.2), rnd)
    # right, front, left, back
    _metal(c, ox, oy + d + y1, ox + d, oy + d + y2, darken(col, 0.1), rnd)
    _metal(c, ox + d, oy + d + y1, ox + d + w, oy + d + y2, col, rnd)
    _metal(c, ox + d + w, oy + d + y1, ox + d + w + d, oy + d + y2, darken(col, 0.1), rnd)
    _metal(c, ox + d + w + d, oy + d + y1, ox + d + w + d + w, oy + d + y2, darken(col, 0.05), rnd)


def _band(c, ox, oy, w, d, y, col):
    """A horizontal band around a box at side row y."""
    for x in range(ox, ox + 2 * (w + d)):
        c.px(x, oy + d + y, col)


def layer(kit):
    """humanoid layer: helmet (unused for 3D helmets, still painted), chest with arms, boots."""
    k = KITS[kit]
    base, dark, trim, acc = (hexc(k[n]) for n in ('base', 'dark', 'trim', 'accent'))
    rnd = _rnd(kit, 'layer')
    c = Canvas(64, 32)
    # helmet
    _box(c, 0, 0, 8, 8, 8, base, rnd)
    _band(c, 0, 0, 8, 8, 2, trim)
    # body (chest plate)
    _box(c, 16, 16, 8, 12, 4, base, rnd)
    _band(c, 16, 16, 8, 4, 0, trim)
    _band(c, 16, 16, 8, 4, 8, trim)
    _band(c, 16, 16, 8, 4, 9, darken(trim, 0.3))
    # emblem on the front (front face x 20..27, y 20..31)
    for (x, y) in ((23, 23), (24, 23), (22, 24), (23, 24), (24, 24), (25, 24), (23, 25), (24, 25), (23, 26), (24, 26)):
        c.px(x, y, acc)
    c.px(23, 24, lighten(acc, 0.6))
    c.px(24, 24, lighten(acc, 0.6))
    # arms: plated, shoulder caps in the trim color
    _box(c, 40, 16, 4, 12, 4, base, rnd)
    _band(c, 40, 16, 4, 4, 0, trim)
    _band(c, 40, 16, 4, 4, 1, lighten(base, 0.2))
    _band(c, 40, 16, 4, 4, 9, trim)
    _metal(c, 44, 16, 48, 20, trim, rnd)   # shoulder top
    # boots (lower rows of the leg box)
    _box(c, 0, 16, 4, 12, 4, dark, rnd, rows=(7, 12))
    _band(c, 0, 16, 4, 4, 7, trim)
    _metal(c, 8, 16, 12, 20, darken(dark, 0.3), rnd)   # soles
    if k['crest'] == 'halo':
        for _ in range(10):
            x, y = rnd.randrange(16, 40), rnd.randrange(20, 32)
            c.px(x, y, acc)
    elif k['crest'] == 'ice':
        for _ in range(14):
            x, y = rnd.randrange(16, 40), rnd.randrange(20, 32)
            c.px(x, y, lighten(base, 0.45))
    elif k['crest'] == 'flame':
        for _ in range(16):
            x, y = rnd.randrange(16, 40), rnd.randrange(20, 32)
            c.px(x, y, lighten(acc, rnd.uniform(-0.1, 0.4)))
    else:
        for y in range(21, 31, 2):   # dragon scales
            for x in range(20 + (y // 2) % 2, 28, 2):
                c.px(x, y, darken(base, 0.25))
    return c


def leggings_layer(kit):
    k = KITS[kit]
    base, dark, trim, acc = (hexc(k[n]) for n in ('base', 'dark', 'trim', 'accent'))
    rnd = _rnd(kit, 'legs')
    c = Canvas(64, 32)
    # belt area on the body box (lower rows)
    _box(c, 16, 16, 8, 12, 4, base, rnd, rows=(8, 12))
    _band(c, 16, 16, 8, 4, 8, trim)
    c.px(23, 29, acc)
    c.px(24, 29, acc)
    # legs: upper part plated, knee guards
    _box(c, 0, 16, 4, 12, 4, base, rnd, rows=(0, 10))
    _band(c, 0, 16, 4, 4, 4, trim)
    _band(c, 0, 16, 4, 4, 5, darken(trim, 0.3))
    c.px(5, 25, acc)
    c.px(6, 25, acc)
    return c


# ───────────────────────────── 3D helmets ─────────────────────────────

def helmet_texture(kit):
    """16x16 texture for the 3D helmet: rows 0-3 base metal, 4-7 trim, 8-11 accent, 12-15 dark."""
    k = KITS[kit]
    rnd = _rnd(kit, 'helmet3d')
    c = Canvas(16, 16)
    _metal(c, 0, 0, 16, 4, hexc(k['base']), rnd, 0.15)
    _metal(c, 0, 4, 16, 8, hexc(k['trim']), rnd, 0.1)
    _metal(c, 0, 8, 16, 12, hexc(k['accent']), rnd, 0.08)
    _metal(c, 0, 12, 16, 16, hexc(k['dark']), rnd, 0.1)
    return c


def _el(fr, to, row, rot=None):
    """Element with all faces mapped to a 4-pixel tall material row of the helmet texture."""
    v = row * 4
    faces = {f: {'uv': [0, v, 16, v + 4], 'texture': '#t'} for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    e = {'from': fr, 'to': to, 'faces': faces}
    if rot:
        e['rotation'] = rot
    return e


BASE, TRIM, ACCENT, DARK = 0, 1, 2, 3


def helmet_model(kit, texture):
    """Item model worn on the head: shell with a face opening (north = front) and a crest per kit."""
    k = KITS[kit]
    lo, hi = 1.0, 15.0
    els = [
        _el([lo, 13.4, lo], [hi, 15.4, hi], BASE),                 # top
        _el([lo, 3.5, 13.0], [hi, 13.4, hi], BASE),                # back
        _el([lo, 3.5, lo], [2.8, 13.4, 13.0], BASE),               # left
        _el([13.2, 3.5, lo], [hi, 13.4, 13.0], BASE),              # right
        _el([2.8, 10.2, lo], [13.2, 13.4, 2.6], TRIM),             # brow band
        _el([2.8, 3.5, lo], [5.2, 10.2, 2.6], BASE),               # cheek guards
        _el([10.8, 3.5, lo], [13.2, 10.2, 2.6], BASE),
        _el([7.4, 6.4, 0.6], [8.6, 10.2, 2.0], TRIM),              # nose guard
        _el([lo - 0.3, 12.6, lo - 0.3], [hi + 0.3, 13.6, hi + 0.3], TRIM),   # rim
        _el([6.0, 11.0, 0.5], [7.0, 12.0, 1.2], ACCENT),           # eye gems on the brow
        _el([9.0, 11.0, 0.5], [10.0, 12.0, 1.2], ACCENT),
    ]
    if k['crest'] == 'horns':
        # dragon horns: out of the temples, then up and leaning outwards, golden tips
        els += [
            _el([-2.5, 10.5, 6.0], [1.0, 12.8, 8.4], TRIM),
            _el([-2.6, 12.4, 6.2], [-0.4, 17.4, 8.2], TRIM, {'angle': 22.5, 'axis': 'z', 'origin': [-1.5, 12.4, 7.2]}),
            _el([-2.4, 17.0, 6.5], [-0.8, 20.0, 7.9], ACCENT, {'angle': 45, 'axis': 'z', 'origin': [-1.5, 17.0, 7.2]}),
            _el([15.0, 10.5, 6.0], [18.5, 12.8, 8.4], TRIM),
            _el([16.4, 12.4, 6.2], [18.6, 17.4, 8.2], TRIM, {'angle': -22.5, 'axis': 'z', 'origin': [17.5, 12.4, 7.2]}),
            _el([16.8, 17.0, 6.5], [18.4, 20.0, 7.9], ACCENT, {'angle': -45, 'axis': 'z', 'origin': [17.5, 17.0, 7.2]}),
            _el([7.0, 15.4, 2.0], [9.0, 17.0, 12.0], DARK),     # spine ridge
            _el([7.4, 17.0, 3.0], [8.6, 18.2, 6.0], DARK),
        ]
    elif k['crest'] == 'ice':
        for x, z, h in ((2.0, 4.0, 4.0), (7.0, 2.5, 6.5), (12.0, 4.0, 4.0), (4.5, 8.0, 3.0), (9.5, 8.0, 3.0)):
            els.append(_el([x, 15.4, z], [x + 2.0, 15.4 + h, z + 2.0], ACCENT,
                           {'angle': 22.5, 'axis': 'y', 'origin': [x + 1, 15.4, z + 1]}))
    elif k['crest'] == 'flame':
        # a crown of jagged flame tongues leaning outward from the crown, tallest at the centre
        for x, z, h, lean in ((3.0, 7.0, 5.0, -22.5), (6.0, 5.5, 7.5, -11.25), (9.0, 5.0, 9.0, 0),
                              (12.0, 5.5, 7.5, 11.25), (15.0, 7.0, 5.0, 22.5)):
            els.append(_el([x, 13.4, z], [x + 2.0, 13.4 + h, z + 2.0], ACCENT,
                           {'angle': lean, 'axis': 'z', 'origin': [x + 1, 13.4, z + 1]}))
            els.append(_el([x + 0.4, 13.4 + h * 0.4, z + 0.4], [x + 1.6, 13.4 + h, z + 1.6], TRIM,
                           {'angle': lean, 'axis': 'z', 'origin': [x + 1, 13.4, z + 1]}))
        els.append(_el([lo + 0.3, 2.2, lo + 0.3], [hi - 0.3, 3.6, hi - 0.3], DARK))   # soot band at the jaw
    else:
        # halo of the star eater: a thin ring floating above the head, plus a crest
        els.append(_el([3.0, 18.0, 3.0], [13.0, 18.6, 4.0], ACCENT))
        els.append(_el([3.0, 18.0, 12.0], [13.0, 18.6, 13.0], ACCENT))
        els.append(_el([3.0, 18.0, 4.0], [4.0, 18.6, 12.0], ACCENT))
        els.append(_el([12.0, 18.0, 4.0], [13.0, 18.6, 12.0], ACCENT))
        els.append(_el([7.3, 15.4, 1.5], [8.7, 17.5, 13.0], TRIM))
    return {
        'textures': {'t': texture, 'particle': texture},
        'elements': els,
        'display': {'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [1, 1, 1]}},
    }

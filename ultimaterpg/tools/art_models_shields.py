"""Schild-Designs cosmetic: real 3D shield shapes (spikes, jagged rims, wings - not just recolours).

Each design gets its own 16x16 texture (4 material rows, same scheme as art_armor's helmet3d
textures) and its own `elements` list of cuboids, so the silhouette itself differs between
designs, not just the colour. Wired into the vanilla `minecraft:shield` item model via a
`minecraft:select` on `minecraft:custom_model_data` (see generate.py) - unmodified shields fall
back to the vanilla banner-capable shield untouched, a shield with a cosmetic active renders one
of these models in every display context (hand, GUI, ground) instead.
"""
import random
import zlib

from draw import Canvas, hexc, lighten, darken

# base, trim, accent, dark - same 4-row palette idea as art_armor.KITS
DESIGNS = {
    'buckler_spike':  {'base': '#8a8f96', 'trim': '#4a4e54', 'accent': '#d8dde2', 'dark': '#23262a'},
    'kite_jagged':    {'base': '#6a4a2a', 'trim': '#caa24a', 'accent': '#e8d090', 'dark': '#2a1c0e'},
    'rune_ward':      {'base': '#2a3a6a', 'trim': '#7ab0ff', 'accent': '#c8e8ff', 'dark': '#101830'},
    'dragonwing':     {'base': '#5a1a1a', 'trim': '#ff6a2a', 'accent': '#ffcf6a', 'dark': '#200505'},
    'tower_ribbed':   {'base': '#4a4a4a', 'trim': '#8a8a8a', 'accent': '#c0a040', 'dark': '#1a1a1a'},
    'thornguard':     {'base': '#2a2a2a', 'trim': '#5a1414', 'accent': '#e03030', 'dark': '#0a0a0a'},
    'voidmaw':        {'base': '#140a24', 'trim': '#5a2a8a', 'accent': '#c070ff', 'dark': '#05020a'},
    'celestial_aegis': {'base': '#e8d890', 'trim': '#fff2a0', 'accent': '#ff5ad0', 'dark': '#a0307f'},
}

BASE, TRIM, ACCENT, DARK = 0, 1, 2, 3


def _rnd(*key):
    return random.Random(zlib.crc32('|'.join(map(str, key)).encode()))


def _metal(c, x1, y1, x2, y2, col, rnd, var=0.12):
    for x in range(x1, x2):
        for y in range(y1, y2):
            t = rnd.uniform(-var, var)
            c.px(x, y, lighten(col, t) if t > 0 else darken(col, -t))


def texture(design_id):
    """16x16 texture: rows 0-3 base, 4-7 trim, 8-11 accent, 12-15 dark."""
    k = DESIGNS[design_id]
    rnd = _rnd(design_id, 'shield3d')
    c = Canvas(16, 16)
    _metal(c, 0, 0, 16, 4, hexc(k['base']), rnd, 0.14)
    _metal(c, 0, 4, 16, 8, hexc(k['trim']), rnd, 0.1)
    _metal(c, 0, 8, 16, 12, hexc(k['accent']), rnd, 0.08)
    _metal(c, 0, 12, 16, 16, hexc(k['dark']), rnd, 0.1)
    return c


def _el(fr, to, row, rot=None):
    v = row * 4
    faces = {f: {'uv': [0, v, 16, v + 4], 'texture': '#t'} for f in ('north', 'south', 'east', 'west', 'up', 'down')}
    e = {'from': fr, 'to': to, 'faces': faces}
    if rot:
        e['rotation'] = rot
    return e


# Display block shared by every design: same anchoring as vanilla shield.json (models/item/shield.json)
# so held/GUI/ground scale and position still read as "a shield", just with different elements.
DISPLAY = {
    'thirdperson_righthand': {'rotation': [0, 90, 0], 'translation': [10, 6, -4], 'scale': [1, 1, 1]},
    'thirdperson_lefthand': {'rotation': [0, 90, 0], 'translation': [10, 6, 12], 'scale': [1, 1, 1]},
    'firstperson_righthand': {'rotation': [0, 180, 5], 'translation': [-10, 1.75, -10], 'scale': [1.25, 1.25, 1.25]},
    'firstperson_lefthand': {'rotation': [0, 180, 5], 'translation': [10, 0, -10], 'scale': [1.25, 1.25, 1.25]},
    'gui': {'rotation': [15, -25, -5], 'translation': [2, 3, 0], 'scale': [0.65, 0.65, 0.65]},
    'fixed': {'rotation': [0, 180, 0], 'translation': [-4.5, 4.5, -5], 'scale': [0.55, 0.55, 0.55]},
    'ground': {'rotation': [0, 0, 0], 'translation': [2, 4, 2], 'scale': [0.25, 0.25, 0.25]},
}


def _plate(lo=3.0, hi=13.0, depth_lo=6.0, depth_hi=8.0, row=BASE):
    """A flat rectangular shield body, 2 units thick, centred like the vanilla shield plank."""
    return _el([lo, lo, depth_lo], [hi, hi, depth_hi], row)


def _spike(cx, cy, cz, length, row=ACCENT, axis='z', lean=0):
    """A thin pyramid-ish spike (stepped cuboids) poking out of the shield face along `axis`."""
    w = 1.6
    out = {'x': [cx, cx + length], 'y': [cy, cy + length] if axis == 'y' else [cy, cy + w],
           'z': [cz, cz + length] if axis == 'z' else [cz, cz + w]}
    if axis == 'z':
        fr, to = [cx - w / 2, cy - w / 2, cz], [cx + w / 2, cy + w / 2, cz + length]
        rot = {'angle': lean, 'axis': 'x', 'origin': [cx, cy, cz]} if lean else None
    elif axis == 'y':
        fr, to = [cx - w / 2, cy, cz - w / 2], [cx + w / 2, cy + length, cz + w / 2]
        rot = {'angle': lean, 'axis': 'z', 'origin': [cx, cy, cz]} if lean else None
    else:  # x
        fr, to = [cx, cy - w / 2, cz - w / 2], [cx + length, cy + w / 2, cz + w / 2]
        rot = {'angle': lean, 'axis': 'y', 'origin': [cx, cy, cz]} if lean else None
    return _el(fr, to, row, rot)


def model(design_id):
    """Full item `elements`/`display` for one shield design."""
    els = []
    if design_id == 'buckler_spike':
        # small round-ish buckler (octagon approximated by cut corners) with one long centre spike
        els += [_el([5.0, 5.0, 6.0], [11.0, 11.0, 8.0], BASE),
                _el([4.0, 6.0, 6.0], [12.0, 10.0, 8.0], BASE),
                _el([6.0, 4.0, 6.0], [10.0, 12.0, 8.0], BASE),
                _el([4.5, 4.5, 5.6], [11.5, 11.5, 6.0], TRIM)]
        els.append(_spike(8.0, 8.0, 5.4, 6.0, ACCENT, axis='z'))
    elif design_id == 'kite_jagged':
        # wide top narrowing to a point at the bottom, with a zigzag top edge
        els += [_el([2.5, 7.0, 6.2], [13.5, 13.0, 7.8], BASE),
                _el([4.5, 2.0, 6.2], [11.5, 7.0, 7.8], BASE),
                _el([6.5, -1.5, 6.4], [9.5, 2.0, 7.6], BASE)]
        for i, x in enumerate((2.5, 5.2, 7.9, 10.6)):
            h = 1.6 if i % 2 == 0 else 0.4
            els.append(_el([x, 13.0, 6.3], [x + 2.2, 13.0 + h, 7.7], TRIM))
        els.append(_el([7.3, -1.5, 6.0], [8.7, 0.0, 8.0], ACCENT))  # bottom tip gem
    elif design_id == 'rune_ward':
        els.append(_plate(3.0, 13.0, 6.4, 7.6, BASE))
        els.append(_el([3.0, 3.0, 6.2], [13.0, 13.0, 6.4], TRIM))  # thin trim rim
        for (cx, cy) in ((4.0, 4.0), (12.0, 4.0), (4.0, 12.0), (12.0, 12.0)):
            els.append(_el([cx - 1.0, cy - 1.0, 5.8], [cx + 1.0, cy + 1.0, 6.2], ACCENT))  # corner studs
        els.append(_el([6.5, 6.5, 7.6], [9.5, 9.5, 7.9], ACCENT))  # glowing rune inlay, floats off the face
    elif design_id == 'dragonwing':
        els.append(_plate(5.0, 11.0, 6.5, 7.5, BASE))
        for i, (y1, y2) in enumerate(((3, 13), (5, 11), (7, 9))):
            lean = (i - 1) * -14
            els.append(_el([-3.0 + i * 2.5, y1, 6.6], [5.0, y2, 7.4], TRIM,
                            {'angle': lean, 'axis': 'y', 'origin': [5.0, 8.0, 7.0]}))
            els.append(_el([11.0, y1, 6.6], [19.0 - i * 2.5, y2, 7.4], TRIM,
                            {'angle': -lean, 'axis': 'y', 'origin': [11.0, 8.0, 7.0]}))
        els.append(_spike(-3.0, 8.0, 7.0, 3.0, ACCENT, axis='x'))
        els.append(_spike(16.0, 8.0, 7.0, 3.0, ACCENT, axis='x'))
    elif design_id == 'tower_ribbed':
        els.append(_el([3.5, -2.0, 6.2], [12.5, 15.0, 7.8], BASE))
        els.append(_el([6.0, 15.0, 6.6], [10.0, 17.5, 7.4], BASE, {'angle': 0, 'axis': 'y', 'origin': [8, 15, 7]}))
        for y in (2.0, 6.5, 11.0):
            els.append(_el([3.0, y, 6.0], [13.0, y + 1.0, 8.0], TRIM))  # horizontal ribs
        els.append(_el([7.2, 15.0, 6.9], [8.8, 18.5, 7.1], ACCENT))  # tip finial
    elif design_id == 'thornguard':
        els.append(_el([4.0, 4.0, 6.3], [12.0, 12.0, 7.7], BASE))
        els.append(_el([3.0, 3.0, 6.5], [13.0, 13.0, 7.5], DARK))
        rim = ((8.0, 2.0), (8.0, 14.0), (2.0, 8.0), (14.0, 8.0), (4.2, 4.2))
        axes = ('y', 'y', 'x', 'x', 'y')
        leans = (0, 180, 0, 0, -45)
        for (cx, cy), axis, lean in zip(rim, axes, leans):
            els.append(_spike(cx, cy, 7.0, 3.2, ACCENT, axis=axis if axis != 'y' else 'y', lean=lean))
    elif design_id == 'voidmaw':
        els.append(_el([3.5, 3.0, 6.4], [12.5, 13.5, 7.6], DARK))
        els.append(_el([3.0, 6.0, 6.2], [13.0, 11.0, 7.8], BASE))
        for x, h, lean in ((3.5, 3.5, 20), (6.2, 2.0, 5), (9.6, 2.5, -8), (11.6, 4.0, -22)):
            els.append(_spike(x, 3.0, 7.0, h, ACCENT, axis='y', lean=lean + 180))
        for x, h in ((5.0, 2.5), (10.0, 2.0)):
            els.append(_spike(x, 13.5, 7.0, h, TRIM, axis='y'))
    else:  # celestial_aegis
        els += [_el([5.0, 5.0, 6.0], [11.0, 11.0, 8.0], BASE),
                _el([4.0, 6.0, 6.0], [12.0, 10.0, 8.0], BASE),
                _el([6.0, 4.0, 6.0], [10.0, 12.0, 8.0], BASE),
                _el([6.5, 6.5, 5.5], [9.5, 9.5, 6.0], ACCENT)]  # raised centre boss
        for angle in (0, 60, 120, 180, 240, 300):
            els.append(_spike(8.0, 8.0, 7.8, 5.5, TRIM, axis='z', lean=0) if False else
                        _el([7.3, 7.3, 7.8], [8.7, 8.7, 12.8], TRIM,
                            {'angle': angle, 'axis': 'z', 'origin': [8.0, 8.0, 8.0]}))
    return {
        'textures': {'t': f'ultimaterpg:item/shield3d/{design_id}', 'particle': f'ultimaterpg:item/shield3d/{design_id}'},
        'elements': els,
        'display': DISPLAY,
    }


def build(assets, ns, write_json, save_canvas):
    """Writes one texture + model json per design, returns the ordered list of design ids
    (used both as the resourcepack index and as the `minecraft:custom_model_data` string
    each case in items/shield.json matches against)."""
    for design_id in DESIGNS:
        save_canvas(texture(design_id), f'item/shield3d/{design_id}')
        write_json(f'{assets}/models/item/shield3d/{design_id}.json', model(design_id))
    return list(DESIGNS)

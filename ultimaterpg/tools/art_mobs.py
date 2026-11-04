"""Head skins for RPG mobs (64x64 player skin layout, only the head is used).

The plugin puts a player head with this skin on the mob (resource pack skin patch), so goblins get real
goblin faces instead of a dyed leather cap. Faces: front, right, left, back, top, bottom (8x8 each).
"""
import random
from draw import Canvas, hexc, lighten, darken, mix

# base layer origins in the skin (hat overlay = x + 32)
FACES = {'top': (8, 0), 'bottom': (16, 0), 'right': (0, 8), 'front': (8, 8), 'left': (16, 8), 'back': (24, 8)}


class Head:
    def __init__(self, skin, seed=1):
        self.c = Canvas(64, 64)
        self.rnd = random.Random(seed)
        self.skin = hexc(skin)
        for face in FACES:
            self.fill(face, self.skin, noise=10)

    def fill(self, face, color, noise=0, hat=False, rows=range(8)):
        ox, oy = FACES[face]
        ox += 32 if hat else 0
        for y in rows:
            for x in range(8):
                self.c.px(ox + x, oy + y, self.vary(color, noise))

    def vary(self, color, noise):
        if not noise or color[3] == 0:
            return color
        d = self.rnd.randint(-noise, noise)
        return tuple(max(0, min(255, v + d)) for v in color[:3]) + (color[3],)

    def px(self, face, x, y, color, hat=False):
        ox, oy = FACES[face]
        self.c.px(ox + (32 if hat else 0) + x, oy + y, hexc(color) if isinstance(color, str) else color)

    def row(self, face, y, x1, x2, color, hat=False):
        for x in range(x1, x2 + 1):
            self.px(face, x, y, color, hat)

    def sides(self, fn):
        """Calls fn(face, toward_front) for both side faces; toward_front maps 0..7 from back to front."""
        fn('right', lambda i: i)
        fn('left', lambda i: 7 - i)

    def ears(self, color, inner):
        def ear(face, f):
            for x, y in ((0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (6, 4), (6, 5), (5, 6), (4, 6)):
                self.px(face, f(x + 1), y, darken(color, 0.4))
            for x, y in ((0, 2), (1, 2), (1, 3), (2, 3), (3, 3), (2, 4), (3, 4), (4, 4), (5, 4), (4, 5), (5, 5)):
                self.px(face, f(x + 1), y, color)
            for x, y in ((2, 4), (3, 4), (4, 5)):
                self.px(face, f(x + 1), y, inner)
        self.sides(ear)

    def save(self):
        return self.c


def goblin_face(h, eye='#f0d040', pupil='#1a1408', mouth='#2a1408', tooth='#f0ead0', nose=None):
    skin = h.skin
    h.row('front', 1, 1, 2, darken(skin, 0.35))           # heavy brows
    h.row('front', 1, 5, 6, darken(skin, 0.35))
    h.px('front', 1, 2, eye)
    h.px('front', 2, 2, pupil)
    h.px('front', 5, 2, pupil)
    h.px('front', 6, 2, eye)
    n = nose or darken(skin, 0.18)
    h.row('front', 3, 3, 4, n)                            # long hooked nose
    h.row('front', 4, 3, 4, darken(n, 0.15))
    h.row('front', 5, 2, 5, mouth)                        # wide grin with fangs
    h.px('front', 2, 6, tooth)
    h.px('front', 5, 6, tooth)
    h.row('front', 6, 3, 4, mouth)


def goblin(variant='scout'):
    skins = {'scout': '#6a9a3a', 'warrior': '#5f8f34', 'archer': '#6f9f40', 'cave': '#6f8264',
             'brute': '#4a6e28', 'king': '#5a8a30', 'shaman': '#628a52'}
    h = Head(skins[variant], seed=len(variant))
    skin = h.skin
    h.ears(lighten(skin, 0.22), mix(skin, hexc('#d08080'), 0.45))
    if variant == 'cave':
        goblin_face(h, eye='#f4f4e8', pupil='#c03030')      # pale, light-blind eyes
    elif variant == 'brute':
        goblin_face(h, eye='#e05020', pupil='#200808', tooth='#e8e0c0')
        for y in range(0, 5):                                # scar over the left eye
            h.px('front', 1 + (y % 2), y, '#8a4a3a')
    else:
        goblin_face(h)
    for x in range(8):                                       # dirty dark hair tufts on top
        if (x * 7 + len(variant)) % 3 == 0:
            h.px('top', x, (x * 5) % 8, darken(skin, 0.4))
    # headgear on the hat layer
    leather, dark = hexc('#7a5230'), hexc('#5a3a1e')
    if variant == 'scout':
        for face in ('front', 'right', 'left', 'back'):
            h.row(face, 0, 0, 7, leather, hat=True)          # leather headband
        h.px('back', 3, 1, dark, hat=True)
        h.px('back', 4, 1, dark, hat=True)
    elif variant == 'warrior':
        h.fill('top', leather, noise=8, hat=True)
        for face in ('front', 'right', 'left', 'back'):
            h.row(face, 0, 0, 7, leather, hat=True)
            h.row(face, 1, 0, 7, dark, hat=True)
        for face in ('right', 'left', 'back'):
            h.row(face, 2, 0, 7, leather, hat=True)
        h.px('front', 3, 1, '#c8c8c8', hat=True)              # rivets
        h.px('front', 4, 1, '#c8c8c8', hat=True)
    elif variant == 'archer':
        hood = hexc('#3d6324')
        h.fill('top', hood, noise=8, hat=True)
        h.fill('back', hood, noise=8, hat=True)
        for face in ('right', 'left'):
            h.fill(face, hood, noise=8, hat=True, rows=range(0, 8))
        h.row('front', 0, 0, 7, hood, hat=True)
        for y in range(1, 8):
            h.px('front', 0, y, hood, hat=True)
            h.px('front', 7, y, hood, hat=True)
    elif variant == 'brute':
        iron, shade = hexc('#a8a8b0'), hexc('#6a6a74')
        h.fill('top', iron, noise=6, hat=True)
        for face in ('front', 'right', 'left', 'back'):
            h.row(face, 0, 0, 7, iron, hat=True)
            h.row(face, 1, 0, 7, shade, hat=True)
        for y in (2, 3, 4):
            h.px('front', 3, y, iron, hat=True)               # nose guard
            h.px('front', 4, y, shade, hat=True)
    elif variant == 'king':
        gold, deep = hexc('#e8b830'), hexc('#a87810')
        for face in ('front', 'right', 'left', 'back'):
            h.row(face, 1, 0, 7, gold, hat=True)
            for x in (0, 2, 5, 7):
                h.px(face, x, 0, gold, hat=True)              # crown spikes
            h.px(face, 1, 1, deep, hat=True)
            h.px(face, 6, 1, deep, hat=True)
        h.px('front', 3, 1, '#e02828', hat=True)
        h.px('front', 4, 1, '#e02828', hat=True)
        h.px('right', 4, 1, '#30a0e0', hat=True)
        h.px('left', 3, 1, '#30a0e0', hat=True)
        h.px('back', 3, 1, '#30c050', hat=True)
    elif variant == 'shaman':
        bone = hexc('#e8e0c8')
        for face in ('front', 'right', 'left', 'back'):
            h.row(face, 0, 0, 7, hexc('#5a2a6a'), hat=True)
        for x in (1, 3, 5):
            h.px('front', x + 1, 0, bone, hat=True)           # bone charms
        h.px('front', 1, 3, '#b040e0')                        # war paint
        h.px('front', 6, 3, '#b040e0')
    return h.save()


def undead():
    h = Head('#6a7a5a', seed=7)
    h.row('front', 2, 1, 2, '#141a10')
    h.row('front', 2, 5, 6, '#141a10')
    h.px('front', 2, 2, '#c0f040')
    h.px('front', 5, 2, '#c0f040')
    h.row('front', 4, 3, 4, '#2a2018')
    for x in range(1, 7):
        h.px('front', x, 6, '#e0d8c0' if x % 2 else '#2a2018')     # bare teeth
    for face, x, y in (('front', 6, 5), ('right', 3, 3), ('left', 5, 2), ('top', 2, 4), ('back', 4, 5)):
        h.px(face, x, y, '#d8d0b8')                                  # exposed bone
        h.px(face, x + 1, y, '#b8b098')
    for face in ('top', 'back', 'right', 'left'):
        for x in range(0, 8, 3):
            h.px(face, x, 0, '#3a3a2a')
    return h.save()


def bandit():
    h = Head('#c89a70', seed=3)
    h.row('front', 2, 1, 2, '#f0f0f0')
    h.row('front', 2, 5, 6, '#f0f0f0')
    h.px('front', 2, 2, '#3a2a1a')
    h.px('front', 5, 2, '#3a2a1a')
    h.row('front', 1, 1, 2, '#4a3020')
    h.row('front', 1, 5, 6, '#4a3020')
    mask = hexc('#2a2a30')
    for y in range(4, 8):
        h.row('front', y, 0, 7, mask, hat=True)          # cloth mask over mouth and nose
        h.row('right', y, 4, 7, mask, hat=True)
        h.row('left', y, 0, 3, mask, hat=True)
    red = hexc('#a02020')
    h.fill('top', red, noise=8, hat=True)                # bandana
    for face in ('front', 'right', 'left', 'back'):
        h.row(face, 0, 0, 7, red, hat=True)
    h.row('back', 1, 3, 4, red, hat=True)
    h.px('back', 3, 2, red, hat=True)
    return h.save()


def cultist():
    h = Head('#3a2a2a', seed=5)
    h.fill('front', hexc('#1a1012'), noise=4)
    h.px('front', 2, 3, '#ff6020')
    h.px('front', 5, 3, '#ff6020')
    h.px('front', 2, 4, '#a02010')
    h.px('front', 5, 4, '#a02010')
    hood = hexc('#7a1010')
    for face in ('top', 'back', 'right', 'left'):
        h.fill(face, hood, noise=10, hat=True)
    h.row('front', 0, 0, 7, hood, hat=True)
    h.row('front', 1, 0, 7, hood, hat=True)
    for y in range(2, 8):
        h.px('front', 0, y, hood, hat=True)
        h.px('front', 7, y, hood, hat=True)
    h.px('front', 3, 1, '#e8b830', hat=True)             # dragon sigil
    h.px('front', 4, 1, '#e8b830', hat=True)
    return h.save()


def ghoul():
    h = Head('#a8a898', seed=9)
    for x, y in ((1, 2), (2, 2), (5, 2), (6, 2), (1, 3), (6, 3)):
        h.px('front', x, y, '#2a2a30')                   # sunken eye holes
    h.px('front', 2, 3, '#e04040')
    h.px('front', 5, 3, '#e04040')
    h.row('front', 5, 1, 6, '#3a1a1a')
    for x in (1, 3, 4, 6):
        h.px('front', x, 6, '#d8d0b0')
    h.row('front', 6, 2, 2, '#3a1a1a')
    h.row('front', 6, 5, 5, '#3a1a1a')
    for face in ('top', 'back', 'right', 'left'):
        for x in range(1, 8, 2):
            h.px(face, x, 0, '#5a5a50')
    return h.save()


def knight(metal='#3a3a42', eye='#e0e0e0', plume='#a02020'):
    h = Head(metal, seed=11)
    m = hexc(metal)
    for face in ('front', 'right', 'left', 'back', 'top'):
        h.fill(face, m, noise=6)
    h.row('front', 3, 1, 6, '#0a0a0e')                   # visor slit
    h.px('front', 2, 3, eye)
    h.px('front', 5, 3, eye)
    for y in range(5, 8):
        for x in (2, 4, 6):
            h.px('front', x, y, darken(m, 0.5))          # breathing holes
    for face in ('front', 'right', 'left', 'back'):
        h.row(face, 0, 0, 7, lighten(m, 0.18))
    h.row('top', 3, 0, 7, plume)                          # crest
    h.row('top', 4, 0, 7, darken(hexc(plume), 0.2))
    return h.save()


def dummy():
    h = Head('#c8a46e', seed=13)
    for face in ('front', 'right', 'left', 'back', 'top'):
        for i in range(0, 8, 2):
            h.px(face, i, (i * 3) % 8, '#a8844e')
    for x, y in ((1, 1), (3, 3), (3, 1), (1, 3)):
        h.px('front', x, y, '#3a2a1a')                   # stitched X eyes
    h.px('front', 2, 2, '#3a2a1a')
    for x, y in ((4, 1), (6, 3), (6, 1), (4, 3)):
        h.px('front', x, y, '#3a2a1a')
    h.px('front', 5, 2, '#3a2a1a')
    h.row('front', 5, 2, 5, '#6a4a2a')
    h.row('top', 3, 0, 7, '#8a6a3a')                      # tied rope
    return h.save()


MOB_HEADS = {
    'goblin': lambda: goblin('scout'),
    'goblin_warrior': lambda: goblin('warrior'),
    'goblin_archer': lambda: goblin('archer'),
    'goblin_shaman': lambda: goblin('shaman'),
    'cave_goblin': lambda: goblin('cave'),
    'goblin_brute': lambda: goblin('brute'),
    'goblin_king': lambda: goblin('king'),
    'undead': undead,
    'bandit': bandit,
    'cultist': cultist,
    'ghoul': ghoul,
    'knight': knight,
    'cursed_guardian': lambda: knight('#2a2236', eye='#c060ff', plume='#5a1a8a'),
    'dummy': dummy,
}

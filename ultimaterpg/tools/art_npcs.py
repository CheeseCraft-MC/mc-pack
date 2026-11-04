"""Full player skins (64x64) for the human NPCs, worn by the mannequins via a resource pack skin patch.

Each NPC is described by a few parameters (skin tone, hair, beard, outfit colours, headgear ...) and painted
onto the standard skin layout, so new NPCs only need one more entry in NPCS.
"""
import random
from PIL import Image

from draw import hexc, lighten, darken, mix

# face origins (x, y, w, h) of every part in the 64x64 layout: base layer, overlay layer
HEAD = {'top': (8, 0, 8, 8), 'bottom': (16, 0, 8, 8), 'right': (0, 8, 8, 8), 'front': (8, 8, 8, 8),
        'left': (16, 8, 8, 8), 'back': (24, 8, 8, 8)}
BODY = {'top': (20, 16, 8, 4), 'bottom': (28, 16, 8, 4), 'right': (16, 20, 4, 12), 'front': (20, 20, 8, 12),
        'left': (28, 20, 4, 12), 'back': (32, 20, 8, 12)}
R_LEG = {'top': (4, 16, 4, 4), 'bottom': (8, 16, 4, 4), 'right': (0, 20, 4, 12), 'front': (4, 20, 4, 12),
         'left': (8, 20, 4, 12), 'back': (12, 20, 4, 12)}
L_LEG = {'top': (20, 48, 4, 4), 'bottom': (24, 48, 4, 4), 'right': (16, 52, 4, 12), 'front': (20, 52, 4, 12),
         'left': (24, 52, 4, 12), 'back': (28, 52, 4, 12)}


def arm(x, y, slim):
    w = 3 if slim else 4
    return {'top': (x + 4, y, w, 4), 'bottom': (x + 4 + w, y, w, 4), 'right': (x, y + 4, 4, 12),
            'front': (x + 4, y + 4, w, 12), 'left': (x + 4 + w, y + 4, 4, 12), 'back': (x + 8 + w, y + 4, w, 12)}


OVERLAY = {'head': (32, 0), 'body': (0, 16), 'r_arm': (0, 16), 'l_arm': (16, 0), 'r_leg': (0, 16), 'l_leg': (-16, 0)}


class Skin:
    def __init__(self, seed, slim):
        self.img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        self.rnd = random.Random(seed)
        self.slim = slim
        self.parts = {'head': HEAD, 'body': BODY, 'r_arm': arm(40, 16, slim), 'l_arm': arm(32, 48, slim),
                      'r_leg': R_LEG, 'l_leg': L_LEG}

    def px(self, x, y, c, noise=6):
        if c is None:
            return
        c = hexc(c) if isinstance(c, str) else c
        if noise and c[3] > 0:
            d = self.rnd.randint(-noise, noise)
            c = tuple(max(0, min(255, v + d)) for v in c[:3]) + (c[3],)
        self.img.putpixel((x, y), c)

    def face(self, part, face, fn, overlay=False):
        """fn(u, v, w, h) -> colour or None for every pixel of the face."""
        x0, y0, w, h = self.parts[part][face]
        if overlay:
            dx, dy = OVERLAY[part]
            x0, y0 = x0 + dx, y0 + dy
        for v in range(h):
            for u in range(w):
                self.px(x0 + u, y0 + v, fn(u, v, w, h))

    def all_faces(self, part, fn, overlay=False):
        for f in self.parts[part]:
            self.face(part, f, lambda u, v, w, h, f=f: fn(f, u, v, w, h), overlay)


def paint(spec, seed=1):
    s = Skin(seed, spec.get('slim', False))
    skin = hexc(spec.get('skin', '#c89a70'))
    hair = hexc(spec.get('hair', '#4a3020'))
    eyes = spec.get('eyes', '#3a6ad0')
    shirt = hexc(spec['shirt'])
    pants = hexc(spec.get('pants', '#4a3a2a'))
    boots = hexc(spec.get('boots', '#3a2a1a'))
    belt = spec.get('belt', '#2a1a10')
    trim = spec.get('trim')
    robe = spec.get('robe', False)
    sleeve = hexc(spec.get('sleeve', spec['shirt']))
    style = spec.get('hair_style', 'short')
    beard = spec.get('beard')

    # ---------------- head
    def head(f, u, v, w, h):
        if f == 'top':
            return hair if style != 'bald' else darken(skin, 0.05)
        if f == 'bottom':
            return darken(skin, 0.15)
        if f == 'front':
            if style in ('short', 'long', 'bun', 'ponytail', 'braid') and v == 0:
                return hair
            if style in ('long', 'bun', 'braid') and v == 1 and u in (0, 7):
                return hair
            return skin
        # sides and back
        if style == 'bald':
            return skin if v > 1 or f != 'back' else darken(skin, 0.05)
        if f == 'back':
            return hair if (style != 'short' or v < 6) else skin
        if style == 'short':
            return hair if v < 3 or (v < 5 and ((f == 'right' and u < 3) or (f == 'left' and u > 4))) else skin
        return hair if v < 7 or ((f == 'right' and u < 4) or (f == 'left' and u > 3)) else skin
    s.all_faces('head', head)
    # eyes, brows, nose, mouth
    hx, hy = HEAD['front'][:2]
    s.px(hx + 1, hy + 4, '#f0f0f0', 0)
    s.px(hx + 2, hy + 4, eyes, 0)
    s.px(hx + 5, hy + 4, eyes, 0)
    s.px(hx + 6, hy + 4, '#f0f0f0', 0)
    brow = darken(hair, 0.2) if style != 'bald' else darken(skin, 0.35)
    for x in (1, 2, 5, 6):
        s.px(hx + x, hy + 3, brow)
    s.px(hx + 3, hy + 5, darken(skin, 0.12))
    s.px(hx + 4, hy + 5, darken(skin, 0.12))
    for x in (3, 4):
        s.px(hx + x, hy + 6, spec.get('mouth', '#8a4a40'))
    if spec.get('scar'):
        for y in (2, 3, 4, 5):
            s.px(hx + 6 + (y % 2) * 0, hy + y, '#a05a50')
    if spec.get('eyepatch'):
        s.px(hx + 5, hy + 4, '#1a1a1a', 0)
        s.px(hx + 6, hy + 4, '#1a1a1a', 0)
        for x in range(0, 8):
            s.px(hx + x, hy + 3 if x > 3 else hy + 2, '#2a2a2a')
    if spec.get('glasses'):
        for x in (1, 2, 5, 6):
            s.px(HEAD['front'][0] + 32 + x, hy + 4, (200, 220, 240, 120), 0)
        for x in (0, 3, 4, 7):
            s.px(HEAD['front'][0] + 32 + x, hy + 4, (60, 50, 40, 255), 0)
    if beard:
        b = hexc(beard)
        length = spec.get('beard_length', 2)
        for y in range(5, 8):
            for x in range(1, 7):
                if y == 5 and x in (3, 4):
                    continue
                s.px(hx + x, hy + y, b)
        s.px(hx + 3, hy + 6, darken(b, 0.3))
        s.px(hx + 4, hy + 6, darken(b, 0.3))
        for f in ('right', 'left'):
            x0, y0 = HEAD[f][:2]
            for y in (6, 7):
                for x in ((5, 6, 7) if f == 'right' else (0, 1, 2)):
                    s.px(x0 + x, y0 + y, b)
        if length > 2:   # long beard flows over the chest
            bx, by = BODY['front'][:2]
            for y in range(0, length * 2):
                for x in range(2, 6):
                    if y < length * 2 - 1 or x in (3, 4):
                        s.px(bx + 32 - 32 + x, by + 16 + y, b)   # jacket overlay of the body
    # long hair falls down the back (overlay of the body back)
    if style in ('long', 'braid', 'ponytail'):
        bx, by = BODY['back'][:2]
        rows = {'long': 6, 'braid': 9, 'ponytail': 7}[style]
        for y in range(rows):
            for x in range(1, 7) if style == 'long' else range(3, 5):
                s.px(bx + x, by + 16 + y, hair)
    if style == 'bun':
        tx, ty = HEAD['back'][:2]
        for x in (3, 4):
            for y in (1, 2):
                s.px(tx + 32 + x, ty + y, darken(hair, 0.1))

    # ---------------- headgear on the hat layer
    gear = spec.get('headgear')
    gear_col = hexc(spec.get('headgear_color', '#9a9aa0'))

    def hat(f, u, v, w, h):
        if gear == 'hood':
            if f == 'front':
                return gear_col if (v < 2 or u in (0, 7)) else None
            if f == 'bottom':
                return None
            return gear_col if (f != 'top' or True) else None
        if gear == 'helmet':
            if f == 'front':
                if v < 3 or (u in (0, 7) and v < 6):
                    return gear_col
                if u in (3, 4) and v < 6:
                    return darken(gear_col, 0.15)    # nose guard
                return None
            if f == 'bottom':
                return None
            return gear_col if v < 6 or f == 'top' else None
        if gear in ('circlet', 'crown'):
            if f in ('front', 'right', 'left', 'back') and v == 1:
                return gear_col
            if gear == 'crown' and f in ('front', 'right', 'left', 'back') and v == 0 and u % 3 == 0:
                return gear_col
            return None
        if gear == 'cap':
            if f == 'top':
                return gear_col
            if f in ('front', 'right', 'left', 'back') and v < 2:
                return gear_col
            return None
        if gear == 'bandana':
            return gear_col if f in ('front', 'right', 'left', 'back') and v in (1, 2) or f == 'top' else None
        if gear == 'veil':
            if f == 'front':
                return gear_col if v < 1 or u in (0, 7) else None
            return gear_col if f != 'bottom' else None
        return None
    if gear:
        s.all_faces('head', hat, overlay=True)
    if gear == 'circlet' and spec.get('gem'):
        s.px(HEAD['front'][0] + 32 + 3, HEAD['front'][1] + 1, spec['gem'], 0)
        s.px(HEAD['front'][0] + 32 + 4, HEAD['front'][1] + 1, spec['gem'], 0)
    if spec.get('hidden_face'):
        for y in range(1, 8):
            for x in range(8):
                s.px(hx + x, hy + y, '#0a0a0e', 2)
        s.px(hx + 2, hy + 4, spec.get('glow', '#c060ff'), 0)
        s.px(hx + 5, hy + 4, spec.get('glow', '#c060ff'), 0)

    # ---------------- body
    armor = spec.get('armor')

    def body(f, u, v, w, h):
        if f in ('top', 'bottom'):
            return shirt
        if belt and v in (8,) and not robe:
            return hexc(belt)
        c = shirt
        if armor and f in ('front', 'back') and v < 8:
            c = hexc(armor)
            if v in (0, 7):
                c = darken(c, 0.15)
        if trim and f == 'front' and (u in (3, 4)) and not armor:
            c = hexc(trim)
        if trim and v == 0:
            c = hexc(trim)
        if spec.get('apron') and f == 'front' and 1 <= u <= 6 and v >= 3:
            c = hexc(spec['apron'])
        if spec.get('vest') and f == 'front' and u in (0, 1, 6, 7):
            c = hexc(spec['vest'])
        if spec.get('cross') and f == 'front' and ((u in (3, 4) and 2 <= v <= 7) or (v == 4 and 1 <= u <= 6)):
            c = hexc(spec['cross'])
        return c
    s.all_faces('body', body)
    if spec.get('tabard'):
        tab = hexc(spec['tabard'])

        def tabard(f, u, v, w, h):
            if f in ('front', 'back') and 2 <= u <= 5:
                if spec.get('emblem') and f == 'front' and u in (3, 4) and v in (3, 4):
                    return hexc(spec['emblem'])
                return tab
            return None
        s.all_faces('body', tabard, overlay=True)
    if spec.get('shoulders'):
        sh = hexc(spec['shoulders'])
        for part in ('r_arm', 'l_arm'):
            s.all_faces(part, lambda f, u, v, w, h: sh if (v < 4 and f != 'bottom') else None, overlay=True)

    # ---------------- arms
    def arms(f, u, v, w, h):
        if f == 'bottom':
            return skin if not spec.get('gloves') else hexc(spec['gloves'])
        if f == 'top':
            return sleeve
        end = spec.get('sleeve_length', 9)
        if v >= end:
            return hexc(spec['gloves']) if spec.get('gloves') else skin
        if trim and v == end - 1:
            return hexc(trim)
        return sleeve
    s.all_faces('r_arm', arms)
    s.all_faces('l_arm', arms)

    # ---------------- legs (a robe covers them)
    def legs(f, u, v, w, h):
        if f == 'top':
            return pants
        if f == 'bottom':
            return boots
        if robe:
            c = shirt
            if trim and v >= 10:
                c = hexc(trim)
            return c if v < 11 or not spec.get('robe_boots') else boots
        return boots if v >= spec.get('boot_height', 9) else pants
    s.all_faces('r_leg', legs)
    s.all_faces('l_leg', legs)
    if spec.get('elf_ears'):   # pointed ears on the hat layer of both head sides
        for f in ('right', 'left'):
            x0, y0 = HEAD[f][:2]
            pts = ((4, 1), (4, 2), (5, 2), (3, 3), (4, 3), (5, 3), (3, 4), (4, 4), (3, 5))
            for u, v in pts:
                uu = u if f == 'right' else 7 - u
                s.px(x0 + 32 + uu, y0 + v, skin)
            s.px(x0 + 32 + (4 if f == 'right' else 3), y0 + 3, darken(skin, 0.15))
    return s.img


def cape(color, trim=None, emblem=None):
    """64x32 cape texture (front 10x16 at 1,1; back at 12,1)."""
    img = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
    rnd = random.Random(3)
    c = hexc(color)
    for x in range(0, 22):
        for y in range(0, 17):
            d = rnd.randint(-6, 6)
            img.putpixel((x, y), tuple(max(0, min(255, v + d)) for v in c[:3]) + (255,))
    if trim:
        for x in list(range(1, 11)) + list(range(12, 22)):
            img.putpixel((x, 16), hexc(trim))
            img.putpixel((x, 1), hexc(trim))
    if emblem:
        for x, y in ((5, 6), (6, 6), (4, 7), (7, 7), (5, 8), (6, 8), (5, 7), (6, 7)):
            img.putpixel((x, y), hexc(emblem))
            img.putpixel((x + 11, y), hexc(emblem))
    return img


STEEL, GOLD, CITY_BLUE = '#a8acb4', '#e0b030', '#2a4a9a'

NPCS = {
    # --- start village
    'village_guard': dict(shirt='#7a7e86', armor='#9a9ea6', tabard='#3a5a2a', emblem='#e0c060', pants='#4a4038',
                          hair='#5a3a20', beard='#5a3a20', headgear='helmet', headgear_color=STEEL, gloves='#4a3a2a'),
    'village_elder': dict(shirt='#3a5a3a', robe=True, trim='#c8a040', hair='#e8e8e8', hair_style='long',
                          beard='#f0f0f0', beard_length=4, skin='#d8b090', sleeve_length=10),
    'healer': dict(slim=True, shirt='#f0f0e8', robe=True, trim='#5aa060', cross='#c03030', hair='#e8c870',
                   hair_style='long', eyes='#4a8a4a', skin='#e8c0a0'),
    'class_master': dict(shirt='#7a1a1a', armor='#8a6a2a', shoulders=GOLD, hair='#2a2a2a', hair_style='bald',
                         beard='#1a1a1a', pants='#3a2a2a', gloves='#5a3a2a', skin='#b07a50', sleeve_length=6),
    'teleporter': dict(slim=True, shirt='#5a2a8a', robe=True, trim='#c0a0ff', hair='#d8d8e8', hair_style='long',
                       headgear='hood', headgear_color='#4a1a7a', eyes='#a060e0'),
    'dungeon_master': dict(shirt='#3a3a3a', armor='#4a4a50', hair='#8a8a8a', beard='#7a7a7a', eyepatch=True,
                           scar=False, pants='#2a2a2a', gloves='#2a2a2a', skin='#b8906a'),
    'hunter': dict(shirt='#6a5034', vest='#4a3a24', hair='#6a4020', beard='#6a4020', headgear='hood',
                   headgear_color='#3a5a2a', pants='#4a3a24', gloves='#5a3a1e'),
    'scout': dict(shirt='#4a6a3a', vest='#6a5034', hair='#b0502a', headgear='bandana', headgear_color='#3a5a2a',
                  pants='#5a4a34', eyes='#4a8a4a'),
    'scholar': dict(slim=True, shirt='#2a3a6a', robe=True, trim='#c8a040', hair='#1a1a1a', hair_style='bun',
                    glasses=True, eyes='#5a4a3a'),
    'hermit': dict(shirt='#7a7a6a', robe=True, hair='#9a9a9a', hair_style='bald', beard='#b0b0a8', beard_length=4,
                   skin='#c8a080', sleeve_length=11),
    'dragon_hunter': dict(slim=True, shirt='#8a2a1a', armor='#6a1a10', shoulders='#3a3a3a', hair='#1a1a1a',
                          hair_style='ponytail', scar=True, pants='#3a2a2a', gloves='#3a2a2a', eyes='#a06020'),
    'wanderer': dict(shirt='#1a1420', robe=True, headgear='hood', headgear_color='#140e18', hidden_face=True,
                     glow='#c060ff', hair='#140e18'),
    'lobby_guide': dict(shirt='#2a4a7a', vest='#7a5a34', hair='#6a4a2a', headgear='cap', headgear_color='#5a3a1e',
                        pants='#4a3a2a', beard='#6a4a2a'),
    'lobby_dungeon_master': dict(slim=True, shirt='#3a1a4a', armor='#4a3a5a', shoulders='#7a5a9a', hair='#e8e8f0',
                                 hair_style='long', eyes='#c060ff', pants='#2a1a2a', gloves='#2a1a2a'),
    # --- guild capital
    'city_gate_captain': dict(shirt='#6a6e76', armor=STEEL, shoulders=GOLD, tabard=CITY_BLUE, emblem=GOLD,
                              headgear='helmet', headgear_color='#c0c4cc', beard='#4a3020', hair='#4a3020',
                              gloves='#5a5a60', pants='#3a3a40', cape=('#2a4a9a', GOLD, GOLD)),
    'city_gate_guard': dict(shirt='#6a6e76', armor=STEEL, tabard=CITY_BLUE, emblem='#e8e8e8', headgear='helmet',
                            headgear_color=STEEL, hair='#2a1a10', gloves='#5a5a60', pants='#3a3a40'),
    'city_watch': dict(slim=True, shirt='#6a6e76', armor=STEEL, tabard=CITY_BLUE, emblem='#e8e8e8', hair='#e8c870',
                       hair_style='ponytail', gloves='#5a5a60', pants='#3a3a40'),
    'guild_master': dict(slim=True, shirt='#f0e8d8', robe=True, trim=GOLD, sleeve='#e8dcc4', hair='#a0402a',
                         hair_style='long', headgear='circlet', headgear_color=GOLD, gem='#3a8ad0', eyes='#3a8a5a',
                         cape=('#8a1a1a', GOLD, GOLD)),
    'guild_receptionist': dict(slim=True, shirt='#f0f0f0', vest='#2a4a8a', pants='#2a3a5a', belt='#2a4a8a',
                               hair='#6a4020', hair_style='braid', eyes='#5a8ad0'),
    'guild_board_keeper': dict(shirt='#d8d0b8', vest='#6a4a2a', pants='#4a3a2a', hair='#9a9a9a', beard='#a0a0a0',
                               glasses=True, skin='#d0a880'),
    'guild_trial_master': dict(shirt='#3a2a4a', armor='#4a3a6a', shoulders='#7a5aa0', hair='#2a2a2a',
                               hair_style='bald', beard='#2a1a10', beard_length=3, gloves='#2a2a2a', skin='#a87a58',
                               sleeve_length=6, cape=('#3a1a5a', '#a080d0', None)),
    'guild_archivist': dict(slim=True, shirt='#2a5a3a', robe=True, trim='#c8a040', hair='#b0402a', hair_style='bun',
                            glasses=True, eyes='#4a8a4a'),
    'guild_trainer': dict(shirt='#3a6a8a', armor='#6a5034', hair='#1a1a1a', pants='#3a3a3a', gloves='#5a3a1e',
                          skin='#c08a60', sleeve_length=5),
    'guild_dungeon_master': dict(shirt='#5a1a1a', armor='#3a2a2a', shoulders='#6a1a1a', hair='#2a2a2a', scar=True,
                                 headgear='hood', headgear_color='#3a1010', gloves='#2a2a2a', pants='#2a2020'),
    'city_priestess': dict(slim=True, shirt='#f4f0e8', robe=True, trim=GOLD, headgear='veil', headgear_color='#f8f4ec',
                           hair='#c8a060', eyes='#5a8ad0'),
    'city_teleporter': dict(slim=True, shirt='#1a6a6a', robe=True, trim='#80e0e0', hair='#e0e0e8', hair_style='long',
                            eyes='#40c0c0'),
    # --- raids
    'frost_hunter': dict(slim=True, shirt='#c8d8e8', vest='#e8eef4', pants='#5a6a7a', hair='#f0f0f8', hair_style='braid',
                         eyes='#40a0e0', gloves='#e8eef4', skin='#f0d8c8', headgear='hood', headgear_color='#e8eef4',
                         cape=('#c8d8e8', '#ffffff', None)),
    'void_hunter': dict(slim=True, shirt='#2a1a3a', armor='#3a2a5a', shoulders='#8a5ac0', hair='#1a1020',
                        hair_style='long', eyes='#c060ff', scar=True, pants='#1a1020', gloves='#2a1a3a',
                        cape=('#1a0a2a', '#8a5ac0', '#c060ff')),
    # --- side quests
    'bounty_hunter': dict(shirt='#3a2a1a', vest='#5a3a1e', hair='#2a1a10', beard='#2a1a10', scar=True,
                          headgear='hood', headgear_color='#2a2018', gloves='#2a1a10', pants='#2a2018', belt='#7a5a2a'),
    'bard': dict(shirt='#8a2a6a', vest='#e0c060', hair='#c87a3a', hair_style='long', pants='#3a2a4a', headgear='cap',
                 headgear_color='#5a1a4a', eyes='#3a8ad0'),
    'herbalist': dict(slim=True, shirt='#3a5a2a', robe=True, trim='#8ac060', hair='#8a8a7a', hair_style='long',
                      headgear='hood', headgear_color='#2a3a1a', eyes='#8ae04a', skin='#d0b090'),
    'fisherman': dict(shirt='#3a6a9a', vest='#c8b070', hair='#8a6a4a', beard='#8a6a4a', beard_length=3, pants='#4a4a3a',
                      headgear='cap', headgear_color='#c8b070', skin='#c09070'),
    'watch_sergeant': dict(shirt='#6a6e76', armor=STEEL, tabard='#3a5a2a', emblem='#e0c060', hair='#5a5a5a',
                           beard='#5a5a5a', gloves='#4a3a2a', pants='#3a3a40', headgear='helmet', headgear_color=STEEL),
    'dwarf_smith': dict(shirt='#7a3a1a', apron='#4a3a2a', hair='#c86a2a', beard='#c86a2a', beard_length=5,
                        hair_style='bald', gloves='#3a2a1a', pants='#3a3a3a', skin='#d0a080', sleeve_length=5),
    # --- Khaz Durrak (dwarf capital) ---
    'dwarf_captain': dict(shirt='#5a5a52', armor=STEEL, tabard='#6a1a1a', emblem='#e0c060', hair='#8a7050',
                          beard='#8a7050', beard_length=6, gloves='#3a3a3a', pants='#4a4a44', skin='#d8ac84',
                          headgear='helmet', headgear_color=STEEL),
    'dwarf_armorsmith': dict(shirt='#6a5a4a', apron='#3a3028', armor='#8a8a90', hair='#c0c0c0', hair_style='braid',
                             beard='#c0c0c0', beard_length=5, gloves='#4a4038', pants='#3a3632', skin='#d8ac88'),
    'dwarf_weaponsmith': dict(shirt='#7a3018', apron='#3a2a20', hair='#b03818', beard='#b03818', beard_length=6,
                              hair_style='bald', gloves='#2a1e16', pants='#362a22', skin='#d4a078', sleeve_length=5),
    'dwarf_weapon_trader': dict(shirt='#8a6a2a', vest='#5a4420', hair='#9a7848', beard='#9a7848', beard_length=4,
                                gloves='#4a3a20', pants='#4a3a24', skin='#d4a884'),
    'dwarf_armor_trader': dict(shirt='#6a6a70', vest='#4a4a52', hair='#d8d0c0', hair_style='long', beard='#d8d0c0',
                               beard_length=4, gloves='#3a3a40', pants='#3a3a40', skin='#dcae88'),
    'dwarf_rune_mage': dict(shirt='#3a2a4a', robe=True, trim='#b060e0', headgear='circlet', headgear_color='#b060e0',
                            gem='#e080ff', hair='#2a2030', hair_style='long', beard='#2a2030', beard_length=4,
                            eyes='#c080ff', skin='#cca888'),
    'dwarf_guild_outpost': dict(shirt='#2a6a7a', vest='#1a4a54', hair='#7a5a3a', beard='#7a5a3a', beard_length=5,
                                gloves='#3a2a1a', pants='#3a3a3a', skin='#d0a884'),
    'dwarf_provisioner': dict(shirt='#a08020', apron='#6a4a18', hair='#c89050', hair_style='braid', beard='#c89050',
                              beard_length=4, gloves='#5a3e1a', pants='#4a3a1e', skin='#dcae88'),
    'dwarf_cart_master': dict(shirt='#5a4a3a', vest='#3a2e22', hair='#8a7858', hair_style='bald', beard='#8a7858',
                              beard_length=5, gloves='#4a3828', pants='#3a2e22', skin='#d0a480'),
    'dwarf_trainer': dict(shirt='#7a2020', vest='#4a1414', armor='#8a8a90', hair='#a05020', hair_style='ponytail',
                          beard='#a05020', beard_length=3, gloves='#3a2a1a', pants='#3a3230', skin='#d4a480'),
    'dwarf_master_smith': dict(shirt='#6a2a10', apron='#2a1c14', hair='#e08030', beard='#e08030', beard_length=7,
                               hair_style='bald', gloves='#2a1a0e', pants='#2e241c', skin='#d8a87c', sleeve_length=5),
    'dwarf_rune_master': dict(shirt='#2a1a3a', robe=True, trim='#8040c0', headgear='circlet', headgear_color='#8040c0',
                              gem='#c060ff', hair='#d8d8e0', hair_style='long', beard='#d8d8e0', beard_length=7,
                              eyes='#a060ff', skin='#c8a488'),
    'dwarf_king': dict(shirt='#3a2a10', robe=True, trim='#e0c040', headgear='crown', headgear_color='#e0c040',
                       gem='#ff4040', hair='#c0c0c8', hair_style='long', beard='#c0c0c8', beard_length=8,
                       eyes='#80c0ff', skin='#d4a880'),
    'dwarf_archivist': dict(shirt='#2a4a5a', robe=True, trim='#60c0d0', hair='#9a9a9a', hair_style='bun',
                            beard='#9a9a9a', beard_length=4, eyes='#60c0d0', skin='#cca888'),
    'dwarf_mine_foreman': dict(shirt='#6a5020', vest='#4a3818', headgear='cap', headgear_color='#5a3a18',
                              hair='#8a6838', beard='#8a6838', beard_length=5, gloves='#3a2a14', pants='#3a3028',
                              skin='#c89c78'),
    'dwarf_merchant_yrsa': dict(shirt='#a0702a', apron='#6a4420', hair='#d09850', hair_style='braid', beard=None,
                               gloves='#5a3e1c', pants='#4a3a1e', skin='#d8ac88'),
    'pilgrim': dict(slim=True, shirt='#f0e8d0', robe=True, trim='#e0a020', hair='#e8c870', hair_style='long',
                    headgear='circlet', headgear_color='#e0a020', gem='#ff6020', eyes='#c08020'),
    # --- elves (Grove of Silver Leaves)
    'elf_elder': dict(slim=True, shirt='#e8f0e0', robe=True, trim='#a0d8a0', hair='#f0f0e8', hair_style='long',
                      headgear='circlet', headgear_color='#c0e0c0', gem='#60e0a0', eyes='#60c080', skin='#f0dcc8',
                      elf_ears=True, cape=('#3a6a3a', '#c0e0c0', None)),
    'elf_ranger': dict(slim=True, shirt='#3a5a2a', vest='#5a7a3a', pants='#3a4a2a', hair='#e8d080', hair_style='braid',
                       eyes='#4ab060', gloves='#4a3a24', skin='#f0d8c0', elf_ears=True, headgear='hood',
                       headgear_color='#2a4a1a'),
    'elf_merchant': dict(slim=True, shirt='#c8a070', vest='#4a7a5a', pants='#3a4a3a', hair='#a05a2a', hair_style='long',
                         eyes='#6ab070', skin='#f0d8c0', elf_ears=True),
    'elf_priestess': dict(slim=True, shirt='#e8e8ff', robe=True, trim='#a0a0ff', hair='#c8d8ff', hair_style='long',
                          headgear='circlet', headgear_color='#c0c8ff', gem='#a0b0ff', eyes='#8090ff', skin='#f4e4d4',
                          elf_ears=True),
    'valmora_seer': dict(shirt='#2a2a3a', robe=True, trim='#60ffd0', headgear='hood', headgear_color='#1a1a2a',
                         hair='#d8d8d8', beard='#d8d8d8', beard_length=5, eyes='#f0f0f0', skin='#b8a090',
                         sleeve_length=11),
    'gravedigger': dict(shirt='#4a4a44', vest='#3a3a34', hair='#9a9a9a', hair_style='bald', beard='#8a8a8a',
                        pants='#2a2a2a', gloves='#3a3a34', skin='#c8b0a0', eyes='#6a6a6a'),
}


def skins():
    """name -> (skin image, slim, cape image or None)."""
    result = {}
    for i, (name, spec) in enumerate(NPCS.items()):
        c = spec.get('cape')
        result[name] = (paint(spec, seed=i + 3), spec.get('slim', False), cape(*c) if c else None)
    return result

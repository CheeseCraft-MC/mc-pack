"""Renders how a few menus look in game (background + icons in their slots), for the README."""
import os
import sys
from PIL import Image, ImageDraw

A = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'resourcepack', 'assets', 'ultimaterpg')
SCALE = 3


def tex(path):
    return Image.open(os.path.join(A, 'textures', path + '.png')).convert('RGBA')


def menu(bg, slots, title):
    img = tex('gui/bg_' + bg)
    for slot, path in slots.items():
        icon = tex(path).resize((16, 16), Image.NEAREST)
        img.alpha_composite(icon, (8 + (slot % 9) * 18, 18 + (slot // 9) * 18))
    img = img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)
    ImageDraw.Draw(img).text((8 * SCALE, 6 * SCALE - 4), title, fill=(220, 210, 190, 255))
    return img


main = menu('main', {4: 'item/gui/character', 20: 'item/gui/character', 21: 'item/gui/skills', 22: 'item/gui/quests',
                     23: 'item/gui/map', 24: 'item/gui/dungeons', 29: 'item/gui/equipment', 30: 'item/gui/party',
                     31: 'item/gui/achievements', 32: 'item/gui/settings', 33: 'item/gui/help', 40: 'item/gui/close'},
            'RPG-Menue')
tree = {4: 'arcane_storm_locked', 13: 'meteor_locked', 20: 'lightning', 22: 'frost_nova_locked', 24: 'teleport_locked',
        29: 'ice_lance_max', 31: 'mana_flow', 33: 'mana_shield_locked', 38: 'fireball_max', 42: 'arcane_knowledge'}
slots = {k: 'item/skill/' + v for k, v in tree.items()}
slots.update({30: 'item/gui/connector_on', 45: 'item/gui/back', 46: 'item/gui/skillbar', 47: 'item/skill/fireball',
              48: 'item/skill/ice_lance', 52: 'item/gui/skill_points', 53: 'item/gui/skill_reset'})
skills = menu('skills_mage', slots, 'Skilltree - Magier')
weapons = Image.new('RGBA', (skills.width, 16 * SCALE * 2 + 24), (30, 26, 36, 255))
for i, name in enumerate(['novice_staff', 'staff_of_whispers', 'ignaroths_scepter', 'dragonfang_blade', 'cursed_greatsword',
                          'flameheart_bow', 'wraith_kris', 'skill_book', 'health_potion_large', 'dragon_heart']):
    icon = tex("item/" + name).resize((48, 48), Image.NEAREST)
    weapons.alpha_composite(icon, (8 + i * (icon.width + 4), 8))
markers = Image.new('RGBA', (skills.width, 0), (0, 0, 0, 0))
w = main.width + skills.width + 24
h = max(main.height, skills.height) + weapons.height + 24
sheet = Image.new('RGBA', (w, h), (44, 44, 52, 255))
sheet.alpha_composite(main, (8, 8))
sheet.alpha_composite(skills, (main.width + 16, 8))
sheet.alpha_composite(weapons, (8, max(main.height, skills.height) + 16))
x = 8 + weapons.width + 0
for i, kind in enumerate(['marker_new', 'marker_active', 'marker_ready']):
    m = tex('font/' + kind)
    m = m.resize((m.width * SCALE * 2, m.height * SCALE * 2), Image.NEAREST)
    pos = (main.width + 16 + 20 + i * (m.width + 20), max(main.height, skills.height) + 16)
    if pos[0] + m.width < w and pos[1] + m.height < h:
        sheet.alpha_composite(m, pos)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'pack-preview.png')
sheet.convert('RGB').save(out)
print(out, sheet.size)


# ── second sheet: class themes and the unit frame
def unit_frame(scale=4):
    font = os.path.join(A, 'textures', 'font')
    seg = {k: Image.open(os.path.join(font, f'bar_{k}.png')).convert('RGBA') for k in
           ('hp_full', 'mana_full', 'empty', 'left', 'right')}
    w, h = 150, 40
    c = Image.new('RGBA', (w, h), (0, 0, 0, 110))
    d = ImageDraw.Draw(c)
    head = Image.new('RGBA', (8, 8), (150, 105, 75, 255))           # stand-in for the skin head
    ImageDraw.Draw(head).rectangle([0, 0, 7, 2], fill=(70, 45, 30, 255))
    head.putpixel((2, 4), (255, 255, 255, 255)); head.putpixel((5, 4), (255, 255, 255, 255))
    head.putpixel((3, 4), (60, 60, 160, 255)); head.putpixel((4, 4), (60, 60, 160, 255))
    c.alpha_composite(head, (2, 3))
    d.text((13, 1), 'Spieler  Lv.12 Magier', fill=(255, 255, 255, 255))

    def bar(y, kind, filled, text, color):
        x = 2
        c.alpha_composite(seg['left'], (x, y)); x += 2
        for i in range(16):
            c.alpha_composite(seg[kind if i < filled else 'empty'], (x, y)); x += 5
        c.alpha_composite(seg['right'], (x, y))
        d.text((x + 5, y - 2), text, fill=color)
    bar(15, 'hp_full', 12, '178/220', (255, 85, 85, 255))
    bar(27, 'mana_full', 9, '90/160', (85, 255, 255, 255))
    return c.resize((w * scale, h * scale), Image.NEAREST)


menus = []
for theme, title in (('warrior', 'Krieger'), ('mage', 'Magier'), ('assassin', 'Assassine'), ('archer', 'Bogenschuetze')):
    m = tex(f'gui/bg_main_{theme}')
    for slot, path in {20: 'item/gui/character', 21: 'item/gui/skills', 22: 'item/gui/quests', 23: 'item/gui/map',
                       24: 'item/gui/dungeons', 4: f'item/gui/class_{theme}'}.items():
        m.alpha_composite(tex(path).resize((16, 16), Image.NEAREST), (8 + (slot % 9) * 18, 18 + (slot // 9) * 18))
    m = m.resize((m.width * 2, m.height * 2), Image.NEAREST)
    ImageDraw.Draw(m).text((16, 8), title, fill=(230, 230, 230, 255))
    menus.append(m)
frame = unit_frame()
W = sum(m.width for m in menus) + 50
sheet2 = Image.new('RGBA', (W, menus[0].height + frame.height + 30), (44, 44, 52, 255))
x = 10
for m in menus:
    sheet2.alpha_composite(m, (x, 10)); x += m.width + 10
sheet2.alpha_composite(frame, (10, menus[0].height + 20))
out2 = out.replace('pack-preview.png', 'pack-preview-classes.png')
sheet2.convert('RGB').save(out2)
print(out2, sheet2.size)

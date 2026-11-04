"""32x32 item textures: weapons, bows, potions, jewellery, materials, quest items, books."""
import math
from draw import Canvas, finish, hexc, lighten, darken, with_alpha, glow, sparkle

S = 32


def _diag(c, x1, y1, x2, y2, col, width):
    c.line(x1, y1, x2, y2, col, width)


def sword(blade='#c8d0dc', edge='#eef3f8', guard='#8a6a3a', grip='#5a3a22', pommel='#c9a24a', gem=None,
          length=1.0, wide=False):
    c = Canvas(S, S)
    tip = (min(28, 6 + int(22 * length)), max(3, 26 - int(22 * length)))
    w = 4 if wide else 3
    _diag(c, 9, 22, tip[0], tip[1], hexc(blade), w)
    _diag(c, 10, 21, tip[0], tip[1], hexc(edge), 1)
    c.px(tip[0] + 1, tip[1] - 1, hexc(edge))
    # guard
    _diag(c, 5, 19, 12, 26, hexc(guard), 2)
    # grip and pommel
    _diag(c, 7, 24, 4, 27, hexc(grip), 2)
    c.rect(2, 27, 4, 29, hexc(pommel))
    if gem:
        c.px(8, 22, hexc(gem))
        c.px(9, 23, hexc(gem))
    return finish(c)


def axe(head='#9aa3ad', edge='#e6ebf0', handle='#6b4426', accent=None):
    c = Canvas(S, S)
    _diag(c, 5, 28, 22, 9, hexc(handle), 2)
    c.poly([(17, 5), (27, 6), (29, 15), (24, 20), (19, 14)], hexc(head))
    c.line(27, 6, 29, 15, hexc(edge), 1)
    c.line(28, 7, 29, 14, hexc(edge), 1)
    c.poly([(16, 9), (19, 6), (21, 12), (18, 14)], darken(hexc(head), 0.2))
    if accent:
        c.px(21, 11, hexc(accent))
        c.px(22, 12, hexc(accent))
    c.rect(4, 27, 6, 29, darken(hexc(handle), 0.3))
    return finish(c)


def mace(head='#9aa3ad', edge='#e6ebf0', handle='#6b4426', accent=None, spikes=True):
    c = Canvas(S, S)
    _diag(c, 4, 28, 19, 13, hexc(handle), 2)
    c.rect(3, 27, 5, 29, darken(hexc(handle), 0.3))
    _diag(c, 14, 18, 16, 16, hexc('#8a6a3a'), 2)
    # flanged head
    c.poly([(18, 8), (24, 6), (27, 9), (26, 15), (20, 17), (16, 13)], hexc(head))
    c.poly([(19, 9), (23, 8), (25, 10), (21, 13)], lighten(hexc(head), 0.25))
    c.line(24, 6, 27, 9, hexc(edge), 1)
    if spikes:
        for x, y in ((25, 4), (29, 10), (27, 17), (19, 19), (15, 11), (19, 5)):
            c.px(x, y, hexc(edge))
    if accent:
        c.rect(21, 11, 22, 12, hexc(accent))
    return finish(c)


def dagger(blade='#c0c8d2', edge='#f0f4f8', guard='#6b5530', grip='#3d2a1c', gem=None, curved=False):
    c = Canvas(S, S)
    if curved:
        pts = [(12, 19), (16, 13), (19, 8), (22, 5), (25, 4)]
        for i in range(len(pts) - 1):
            c.line(*pts[i], *pts[i + 1], hexc(blade), 3)
        for i in range(len(pts) - 1):
            c.line(pts[i][0] + 1, pts[i][1], pts[i + 1][0] + 1, pts[i + 1][1], hexc(edge), 1)
    else:
        _diag(c, 12, 19, 24, 7, hexc(blade), 3)
        _diag(c, 13, 18, 25, 6, hexc(edge), 1)
    _diag(c, 8, 17, 14, 23, hexc(guard), 2)
    _diag(c, 10, 21, 5, 26, hexc(grip), 2)
    c.rect(3, 26, 5, 28, hexc(guard))
    if gem:
        c.px(11, 20, hexc(gem))
    return finish(c)


def staff(wood='#7a5230', orb='#7fd0ff', prongs='#c9a24a', glow_color=None, crystal=False, flame=False, bone=False):
    c = Canvas(S, S)
    shaft = hexc('#e8dcc0') if bone else hexc(wood)
    _diag(c, 4, 29, 22, 11, shaft, 2)
    for i, (x, y) in enumerate([(9, 24), (14, 19), (18, 15)]):
        c.px(x, y, darken(shaft, 0.35))
    # head
    if crystal:
        c.poly([(25, 2), (29, 7), (25, 13), (21, 7)], hexc(orb))
        c.line(25, 3, 25, 12, lighten(hexc(orb), 0.4), 1)
    else:
        c.circle(25, 7, 4, hexc(orb))
        c.px(23, 5, lighten(hexc(orb), 0.6))
        c.px(24, 5, lighten(hexc(orb), 0.4))
    c.line(20, 12, 21, 7, hexc(prongs), 1)
    c.line(22, 13, 28, 12, hexc(prongs), 1)
    c.px(21, 12, hexc(prongs))
    if bone:
        c.line(19, 9, 17, 4, hexc('#f2ead6'), 1)
        c.px(16, 3, hexc('#c23b2b'))
        c.px(17, 3, hexc('#c23b2b'))
    finish(c)
    if flame:
        for (x, y) in [(25, 1), (24, 2), (26, 2), (27, 3)]:
            c.px(x, y, hexc('#ffb02e'))
        c.px(25, 0, hexc('#ffe27a'))
    glow(c, 25, 7, 8, with_alpha(hexc(glow_color or orb), 150))
    return c


def bow(wood='#8a5a2e', string='#e8e2d0', accent=None, pull=0):
    """pull: 0 (idle) .. 3 (fully drawn, with arrow)."""
    c = Canvas(S, S)
    w = hexc(wood)
    # the bow limb is an arc from top-right to bottom-left, bulging to the upper left
    pts = []
    for i in range(0, 21):
        t = i / 20
        x = 27 - 23 * t
        y = 4 + 23 * t
        bulge = math.sin(t * math.pi) * (7 - pull)
        pts.append((x - bulge * 0.7, y - bulge * 0.7))
    for i in range(len(pts) - 1):
        c.line(*pts[i], *pts[i + 1], w, 2)
    mid = pts[10]
    sx = 16 + pull * 1.6
    sy = 16 + pull * 1.6
    c.line(27, 4, sx, sy, hexc(string), 1)
    c.line(sx, sy, 4, 27, hexc(string), 1)
    if accent:
        c.px(int(mid[0]), int(mid[1]), hexc(accent))
        c.px(int(mid[0]) + 1, int(mid[1]), hexc(accent))
    if pull > 0:
        # arrow on the string
        c.line(sx, sy, sx - 9 - pull, sy - 9 - pull, hexc('#9a7a50'), 1)
        c.px(int(sx - 10 - pull), int(sy - 10 - pull), hexc('#d0d4da'))
        c.px(int(sx - 9 - pull), int(sy - 10 - pull), hexc('#d0d4da'))
        c.px(int(sx + 1), int(sy), hexc('#e0e0e0'))
    return finish(c)


def potion(liquid='#e03030', size='small', glass='#cfe6f0'):
    c = Canvas(S, S)
    big = size == 'large'
    r = 9 if big else 7
    cy = 20 if big else 21
    c.circle(16, cy, r, with_alpha(hexc(glass), 200))
    c.rect(13, cy - r - 6, 19, cy - r + 1, with_alpha(hexc(glass), 200))
    # liquid
    liq = hexc(liquid)
    for y in range(cy - r + 3, cy + r + 1):
        for x in range(16 - r, 16 + r + 1):
            if (x - 16) ** 2 + (y - cy) ** 2 <= (r - 1) ** 2:
                c.px(x, y, liq if y > cy - 1 else lighten(liq, 0.15))
    c.rect(12, cy - r - 9, 20, cy - r - 6, hexc('#8a5a32'))
    c.px(12, cy - 3, (255, 255, 255, 230))
    c.px(12, cy - 2, (255, 255, 255, 200))
    c.px(13, cy - 4, (255, 255, 255, 200))
    finish(c, shade=False)
    sparkle(c, 21, cy + 2, lighten(liq, 0.6))
    return c


def bread():
    c = Canvas(S, S)
    c.poly([(6, 18), (10, 12), (20, 10), (27, 14), (26, 21), (16, 24), (8, 23)], hexc('#c88a3e'))
    for x in (11, 15, 19, 23):
        c.line(x, 13, x + 2, 19, hexc('#8a5524'), 1)
    c.poly([(8, 14), (12, 11), (18, 10), (14, 13)], hexc('#e3b26a'))
    return finish(c)


def honey_cake():
    c = Canvas(S, S)
    c.poly([(5, 17), (16, 12), (27, 17), (27, 23), (16, 28), (5, 23)], hexc('#b8742e'))
    c.poly([(5, 17), (16, 12), (27, 17), (16, 22)], hexc('#f0c860'))
    c.poly([(9, 17), (16, 14), (23, 17), (16, 20)], hexc('#ffe08a'))
    for x, y in ((10, 21), (14, 23), (20, 22), (24, 20)):
        c.px(x, y, hexc('#e8a030'))
        c.px(x, y + 1, hexc('#e8a030'))
    c.line(16, 22, 16, 28, hexc('#8a5224'), 1)
    finish(c)
    sparkle(c, 18, 15, (255, 255, 230, 255))
    return c


def smoked_fish():
    c = Canvas(S, S)
    c.poly([(5, 16), (10, 11), (20, 10), (25, 14), (20, 19), (10, 20)], hexc('#b06a3a'))
    c.poly([(25, 14), (29, 9), (29, 19)], hexc('#7a4424'))
    c.poly([(8, 15), (12, 12), (19, 11), (15, 14)], hexc('#d8955a'))
    for x in (13, 16, 19):
        c.line(x, 12, x - 1, 18, hexc('#7a4424'), 1)
    c.px(8, 14, hexc('#1a1010'))
    c.line(4, 22, 28, 22, hexc('#6a4a2a'), 1)
    return finish(c)


def ring(metal='#c9a24a', gem='#3fbf5f'):
    c = Canvas(S, S)
    c.ring(16, 18, 9, hexc(metal), 3)
    c.ring(16, 18, 7, darken(hexc(metal), 0.3), 1)
    c.poly([(13, 6), (19, 6), (21, 9), (16, 14), (11, 9)], hexc(gem))
    c.px(14, 8, lighten(hexc(gem), 0.6))
    c.rect(12, 10, 20, 11, hexc(metal))
    finish(c)
    sparkle(c, 21, 6, (255, 255, 255, 255))
    return c


def amulet(chain='#c9a24a', gem='#a050ff', tooth=False):
    c = Canvas(S, S)
    c.line(6, 3, 16, 17, hexc(chain), 1)
    c.line(26, 3, 16, 17, hexc(chain), 1)
    for (x, y) in [(8, 6), (11, 10), (21, 10), (24, 6)]:
        c.px(x, y, lighten(hexc(chain), 0.4))
    if tooth:
        c.poly([(12, 16), (20, 16), (16, 29)], hexc('#efe6cf'))
        c.line(16, 17, 16, 26, hexc('#cfc2a0'), 1)
    else:
        c.poly([(16, 15), (23, 21), (16, 29), (9, 21)], hexc(chain))
        c.poly([(16, 17), (21, 21), (16, 26), (11, 21)], hexc(gem))
        c.px(14, 20, lighten(hexc(gem), 0.6))
    finish(c)
    if not tooth:
        glow(c, 16, 22, 9, with_alpha(hexc(gem), 90))
    return c


def idol():
    c = Canvas(S, S)
    c.rect(11, 8, 21, 28, hexc('#5a4a3a'))
    c.rect(9, 12, 23, 15, hexc('#6a5848'))
    c.rect(13, 4, 19, 8, hexc('#5a4a3a'))
    c.rect(13, 17, 15, 19, hexc('#a020ff'))
    c.rect(17, 17, 19, 19, hexc('#a020ff'))
    c.line(13, 23, 19, 23, hexc('#2a2018'), 1)
    finish(c)
    glow(c, 14, 18, 4, (190, 80, 255, 200))
    glow(c, 18, 18, 4, (190, 80, 255, 200))
    return c


def heart():
    c = Canvas(S, S)
    col = hexc('#c01830')
    c.circle(11, 12, 6, col)
    c.circle(21, 12, 6, col)
    c.poly([(5, 14), (27, 14), (16, 28)], col)
    c.line(16, 9, 16, 23, darken(col, 0.3), 1)
    c.px(9, 9, lighten(col, 0.6))
    c.px(10, 9, lighten(col, 0.5))
    finish(c)
    glow(c, 16, 16, 15, (255, 80, 40, 110))
    return c


def book(cover='#5a2e2e', trim='#c9a24a', rune='#ffd66a', pages='#efe4c8', glow_rune=False, clasp=True):
    c = Canvas(S, S)
    c.poly([(6, 8), (24, 5), (27, 24), (9, 28)], hexc(cover))
    c.line(6, 8, 9, 28, darken(hexc(cover), 0.35), 2)
    c.line(9, 28, 27, 24, hexc(pages), 2)
    c.line(24, 5, 27, 24, hexc(pages), 1)
    c.line(8, 9, 24, 6, hexc(trim), 1)
    c.line(10, 26, 26, 23, hexc(trim), 1)
    # rune in the middle
    cx, cy = 16, 16
    c.ring(cx, cy, 4, hexc(rune), 1)
    c.line(cx, cy - 4, cx, cy + 4, hexc(rune), 1)
    c.line(cx - 3, cy + 1, cx + 3, cy - 1, hexc(rune), 1)
    if clasp:
        c.rect(25, 13, 28, 16, hexc(trim))
    finish(c)
    if glow_rune:
        glow(c, cx, cy, 7, with_alpha(hexc(rune), 150))
    return c


def scroll_letter():
    c = Canvas(S, S)
    c.rect(5, 9, 27, 24, hexc('#e9dcb8'))
    c.line(5, 9, 16, 18, hexc('#b8a67e'), 1)
    c.line(27, 9, 16, 18, hexc('#b8a67e'), 1)
    c.circle(16, 18, 3, hexc('#b01e1e'))
    c.px(15, 17, hexc('#ff6060'))
    return finish(c)


def package():
    c = Canvas(S, S)
    c.rect(6, 10, 26, 26, hexc('#a8783e'))
    c.rect(6, 10, 26, 13, hexc('#c08e4e'))
    c.line(16, 10, 16, 26, hexc('#e8e0c8'), 1)
    c.line(6, 18, 26, 18, hexc('#e8e0c8'), 1)
    c.circle(16, 9, 2, hexc('#e8e0c8'))
    return finish(c)


def crown():
    c = Canvas(S, S)
    g = hexc('#e2b23a')
    c.poly([(5, 24), (5, 11), (10, 17), (16, 8), (22, 17), (27, 11), (27, 24)], g)
    c.rect(5, 22, 27, 25, darken(g, 0.2))
    for x, col in ((9, '#3fbf5f'), (16, '#d02030'), (23, '#3060e0')):
        c.circle(x, 23, 1, hexc(col))
    c.rect(14, 20, 18, 21, (90, 70, 40, 255))
    finish(c)
    sparkle(c, 16, 7, (255, 250, 210, 255))
    return c


def tablet():
    c = Canvas(S, S)
    c.poly([(7, 6), (25, 5), (26, 27), (6, 27)], hexc('#8a8478'))
    c.poly([(16, 5), (25, 5), (26, 16), (20, 13)], hexc('#9a9488'))
    for (x1, y1, x2, y2) in [(10, 10, 14, 10), (10, 14, 18, 14), (10, 18, 15, 18), (10, 22, 20, 22), (17, 9, 21, 11)]:
        c.line(x1, y1, x2, y2, hexc('#57d0ff'), 1)
    c.line(19, 13, 23, 25, hexc('#5a554c'), 1)
    finish(c)
    glow(c, 14, 16, 9, (90, 200, 255, 80))
    return c


def eye():
    c = Canvas(S, S)
    c.poly([(3, 16), (10, 9), (22, 9), (29, 16), (22, 23), (10, 23)], hexc('#f0c040'))
    c.circle(16, 16, 6, hexc('#d02010'))
    c.rect(15, 11, 17, 21, hexc('#1a0a08'))
    c.px(13, 13, (255, 255, 220, 255))
    finish(c)
    glow(c, 16, 16, 14, (255, 120, 20, 90))
    return c


def footprint():
    c = Canvas(S, S)
    col = hexc('#6a4a2a')
    c.circle(15, 20, 5, col)
    c.circle(16, 13, 4, col)
    for (x, y) in ((10, 7), (14, 5), (19, 6), (22, 9)):
        c.circle(x, y, 1, col)
    c.poly([(20, 22), (27, 25), (24, 29)], hexc('#3f7a2a'))
    return finish(c)


def pelt():
    c = Canvas(S, S)
    c.poly([(5, 10), (11, 5), (22, 6), (28, 12), (26, 24), (18, 28), (8, 25), (4, 18)], hexc('#8a6a4a'))
    for (x, y) in ((10, 12), (16, 9), (20, 16), (12, 20), (22, 22)):
        c.line(x, y, x + 3, y + 2, hexc('#a8886a'), 1)
    return finish(c)


def silk():
    c = Canvas(S, S)
    for r, col in ((10, '#f2f2f2'), (7, '#dcdcdc'), (4, '#f8f8f8')):
        c.ring(16, 16, r, hexc(col), 2)
    c.line(24, 20, 29, 28, hexc('#e8e8e8'), 1)
    return finish(c)


def herb():
    c = Canvas(S, S)
    c.line(16, 29, 16, 12, hexc('#3d7a2a'), 1)
    for (x, y, d) in ((16, 14, -1), (16, 18, 1), (16, 22, -1), (16, 10, 1)):
        c.poly([(x, y), (x + 8 * d, y - 4), (x + 4 * d, y + 1)], hexc('#5cb84a'))
    c.circle(16, 7, 2, hexc('#e8f070'))
    return finish(c)


def goblin_ear():
    c = Canvas(S, S)
    c.poly([(8, 26), (12, 12), (26, 4), (22, 16), (16, 26)], hexc('#6aa040'))
    c.poly([(12, 22), (15, 14), (22, 9), (18, 18)], hexc('#8ac060'))
    c.px(23, 6, hexc('#c0a080'))
    return finish(c)


def tusk():
    c = Canvas(S, S)
    pts = [(6, 27), (10, 20), (16, 14), (22, 10), (27, 5)]
    for i in range(len(pts) - 1):
        c.line(*pts[i], *pts[i + 1], hexc('#efe6cf'), 3 if i < 2 else 2)
    c.rect(4, 26, 8, 29, hexc('#a07a50'))
    return finish(c)


def dust(col='#e8e0d0'):
    c = Canvas(S, S)
    c.poly([(5, 26), (10, 19), (16, 16), (22, 19), (27, 26)], hexc(col))
    for (x, y) in ((12, 14), (18, 12), (22, 15), (9, 17)):
        c.px(x, y, hexc(col))
    c.ring(14, 22, 2, darken(hexc(col), 0.2), 1)
    return finish(c)


def essence():
    c = Canvas(S, S)
    c.circle(16, 18, 9, hexc('#3a1458'))
    for i in range(14):
        a = i / 14 * math.pi * 4
        c.px(16 + math.cos(a) * i * 0.6, 18 + math.sin(a) * i * 0.6, hexc('#c060ff'))
    finish(c)
    glow(c, 16, 18, 13, (170, 60, 255, 120))
    return c


def shard(col='#7ae0f0'):
    c = Canvas(S, S)
    c.poly([(16, 3), (23, 13), (19, 29), (11, 25), (9, 12)], hexc(col))
    c.poly([(16, 3), (19, 15), (16, 27), (12, 14)], lighten(hexc(col), 0.3))
    finish(c)
    sparkle(c, 21, 8, (255, 255, 255, 255))
    return c


def ember():
    c = Canvas(S, S)
    c.circle(16, 17, 8, hexc('#d0501a'))
    c.circle(15, 16, 5, hexc('#ff9a30'))
    c.circle(14, 15, 2, hexc('#ffe27a'))
    finish(c)
    glow(c, 16, 17, 14, (255, 140, 40, 130))
    return c


def scale():
    c = Canvas(S, S)
    col = hexc('#a01818')
    c.poly([(16, 3), (27, 12), (24, 25), (16, 29), (8, 25), (5, 12)], col)
    c.poly([(16, 6), (23, 13), (16, 26), (9, 13)], darken(col, 0.25))
    c.line(16, 6, 16, 26, hexc('#ff6a3a'), 1)
    return finish(c)


def scrap():
    c = Canvas(S, S)
    c.poly([(6, 20), (12, 14), (18, 17), (14, 25)], hexc('#9aa3ad'))
    c.poly([(16, 10), (24, 8), (26, 16), (19, 15)], hexc('#b0b8c2'))
    c.poly([(18, 22), (26, 21), (24, 28)], hexc('#848c96'))
    return finish(c)


def arrows():
    c = Canvas(S, S)
    for off in (0, 4, 8):
        c.line(6 + off, 27, 22 + off, 11 - off // 2, hexc('#9a7a50'), 1)
        c.poly([(22 + off, 11 - off // 2), (26 + off, 7 - off // 2), (24 + off, 13 - off // 2)], hexc('#d0d4da'))
        c.line(5 + off, 25, 8 + off, 28, hexc('#e8e8e8'), 1)
    return finish(c)


def lucky_ring():
    return ring('#b06030', '#ffd060')


def bone_bow(pull=0):
    return bow('#efe6cf', '#c8c0b0', '#8a2020', pull)

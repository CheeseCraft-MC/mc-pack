"""Effect textures for skill animations (64x64, white with soft alpha - the plugin tints them per skill).

Shown on flat, glowing item displays: slash arcs, shockwave rings, rune circles, shield hexagons, crosses, bursts.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

S = 64


def _canvas():
    return Image.new('RGBA', (S * 4, S * 4), (255, 255, 255, 0))


def _finish(img):
    img = img.filter(ImageFilter.GaussianBlur(2.2))
    img = img.resize((S, S), Image.LANCZOS)
    # keep it white: only the alpha carries the shape
    alpha = img.getchannel('A')
    out = Image.new('RGBA', (S, S), (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def slash():
    """Crescent of a weapon swing, thick in the middle, thin at the tips."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    for i in range(140):
        t = i / 139
        a = math.radians(200 + t * 140)
        w = math.sin(t * math.pi)
        r_out = S * 1.8
        r_in = r_out - 6 - 30 * w
        for r in range(int(r_in), int(r_out)):
            x, y = c + math.cos(a) * r, c + 30 + math.sin(a) * r
            v = int(255 * (0.35 + 0.65 * w) * (1 - (r_out - r) / (r_out - r_in + 1) * 0.6))
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255, v))
    return _finish(img)


def ring():
    """Shockwave: bright thin ring with a soft inner glow."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    for r in range(int(S * 1.2), int(S * 1.9)):
        v = int(255 * ((r - S * 1.2) / (S * 0.7)) ** 2)
        d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, v), width=2)
    return _finish(img)


def runes():
    """Magic circle: two rings, a hexagram and rune marks."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    for r, w in ((S * 1.9, 7), (S * 1.6, 4), (S * 0.75, 4)):
        d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, 255), width=w)
    for k in (0, 1):
        pts = [(c + math.cos(math.radians(90 + k * 60 + i * 120)) * S * 1.6,
                c + math.sin(math.radians(90 + k * 60 + i * 120)) * S * 1.6) for i in range(3)]
        d.polygon(pts, outline=(255, 255, 255, 230), width=4)
    rnd = random.Random(7)
    for i in range(16):
        a = math.radians(i * 22.5 + 11)
        x, y = c + math.cos(a) * S * 1.75, c + math.sin(a) * S * 1.75
        for _ in range(2):
            dx, dy = rnd.randint(-7, 7), rnd.randint(-7, 7)
            d.line([x - dx, y - dy, x + dx, y + dy], fill=(255, 255, 255, 255), width=3)
    return _finish(img)


def hexshield():
    """Honeycomb disc for shields."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    size = S * 0.32
    for q in range(-6, 7):
        for r in range(-6, 7):
            x = c + size * 1.75 * (q + r / 2)
            y = c + size * 1.5 * r
            dist = math.hypot(x - c, y - c)
            if dist > S * 1.85:
                continue
            pts = [(x + math.cos(math.radians(30 + 60 * i)) * size, y + math.sin(math.radians(30 + 60 * i)) * size)
                   for i in range(6)]
            v = int(110 + 145 * (dist / (S * 1.85)) ** 2)
            d.polygon(pts, outline=(255, 255, 255, v), width=3)
    d.ellipse([c - S * 1.9, c - S * 1.9, c + S * 1.9, c + S * 1.9], outline=(255, 255, 255, 255), width=6)
    return _finish(img)


def cross():
    """Healing cross with a glow."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    for g in range(10, 0, -1):
        w = S * 0.28 + g * 6
        v = int(255 * (1 - g / 11) ** 1.5)
        d.rectangle([c - w / 2, c - S * 1.3 - g * 4, c + w / 2, c + S * 1.3 + g * 4], fill=(255, 255, 255, v))
        d.rectangle([c - S * 1.3 - g * 4, c - w / 2, c + S * 1.3 + g * 4, c + w / 2], fill=(255, 255, 255, v))
    return _finish(img)


def burst():
    """Star burst for impacts and taunts."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    rnd = random.Random(3)
    for i in range(18):
        a = math.radians(i * 20 + rnd.uniform(-6, 6))
        length = S * rnd.uniform(1.2, 1.9)
        w = math.radians(5)
        d.polygon([(c + math.cos(a - w) * S * 0.3, c + math.sin(a - w) * S * 0.3),
                   (c + math.cos(a) * length, c + math.sin(a) * length),
                   (c + math.cos(a + w) * S * 0.3, c + math.sin(a + w) * S * 0.3)], fill=(255, 255, 255, 230))
    d.ellipse([c - S * 0.45, c - S * 0.45, c + S * 0.45, c + S * 0.45], fill=(255, 255, 255, 255))
    return _finish(img)


def chevron():
    """Arrow head for dashes and pulls (points up)."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    c = S * 2
    for k, v in ((0, 255), (1, 170), (2, 90)):
        y = c - S * 0.9 + k * S * 0.75
        d.line([c - S * 1.3, y + S * 0.9, c, y, c + S * 1.3, y + S * 0.9], fill=(255, 255, 255, v), width=22, joint='curve')
    return _finish(img)


SHAPES = {'slash': slash, 'ring': ring, 'runes': runes, 'hexshield': hexshield, 'cross': cross, 'burst': burst,
          'chevron': chevron}


def plane_model(texture_ref):
    """Flat square (1 block at scale 1), both sides visible, full bright."""
    face = {'uv': [0, 0, 16, 16], 'texture': '#0', 'tintindex': 0}
    return {'textures': {'0': texture_ref, 'particle': texture_ref},
            'elements': [{'from': [0, 0, 8], 'to': [16, 16, 8], 'light_emission': 15, 'shade': False,
                          'faces': {'north': face, 'south': dict(face, uv=[16, 0, 0, 16])}}]}

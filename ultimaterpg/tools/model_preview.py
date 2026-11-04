"""Draws the mob models (all frames) into one picture, to check them without a Minecraft client.

  python3 tools/pack/model_preview.py <out.png> [model ...]
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import art_models  # noqa: E402

FACES = {  # corner indices (x,y,z bits) and normal
    'north': ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, -1)),
    'south': ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1)),
    'west': ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0), (-1, 0, 0)),
    'east': ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0), (1, 0, 0)),
    'up': ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 1, 0)),
    'down': ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1), (0, -1, 0)),
}
SHADE = {'up': 1.0, 'down': 0.5, 'north': 0.8, 'south': 0.8, 'east': 0.6, 'west': 0.6}


def rotate(p, rot):
    if not rot:
        return p
    axis, angle, (ox, oy, oz) = rot['axis'], math.radians(rot['angle']), rot['origin']
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    c, s = math.cos(angle), math.sin(angle)
    if axis == 'x':
        y, z = y * c - z * s, y * s + z * c
    elif axis == 'y':
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return x + ox, y + oy, z + oz


def render(model, frame, size=220, yaw=35, pitch=20):
    data = model.json(frame, 'x')
    tex = model.texture()
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def project(p):
        x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
        x, z = x * cy_ - z * sy_, x * sy_ + z * cy_          # turn around y
        y, z = y * cp + z * sp, -y * sp + z * cp             # tilt
        return x, y, z

    polys = []
    for e in data['elements']:
        f, t = e['from'], e['to']
        rot = e.get('rotation')
        for name, (a, b, c, d, n) in FACES.items():
            corners = [rotate([(t if bit else f)[i] for i, bit in enumerate(k)], rot) for k in (a, b, c, d)]
            pts = [project(p) for p in corners]
            nrm = rotate([n[0] + 8, n[1] + 8, n[2] + 8], {'axis': rot['axis'], 'angle': rot['angle'], 'origin': (8, 8, 8)}
                         if rot else None)
            nv = project(nrm)
            if nv[2] > 0:                                  # facing away (camera looks towards +z after projection)
                continue
            uv = e['faces'][name]['uv']
            col = tex.getpixel((int(uv[0] * 2) + 1, int(uv[1] * 2) + 1))
            glow = e.get('light_emission', 0)
            k = 1 if glow else SHADE[name]
            polys.append((sum(p[2] for p in pts) / 4, [(p[0], p[1]) for p in pts], tuple(int(v * k) for v in col[:3])))
    polys.sort(key=lambda p: -p[0])
    img = Image.new('RGB', (size, size), (40, 44, 54))
    d = ImageDraw.Draw(img)
    scale = size / 52
    for _, pts, col in polys:
        d.polygon([(size / 2 + x * scale, size * 0.5 - (y + 6) * scale) for x, y in pts], fill=col, outline=tuple(v // 2 for v in col))
    d.text((4, 4), f'{model.name} {frame}', fill=(255, 255, 160))
    return img


def main():
    out = sys.argv[1]
    models = art_models.models()
    names = sys.argv[2:] or list(models)
    sheet = Image.new('RGB', (len(art_models.FRAMES) * 220 + 220, len(names) * 220), (20, 20, 26))
    for r, name in enumerate(names):
        m = models[name]
        for c, frame in enumerate(art_models.FRAMES):
            sheet.paste(render(m, frame), (c * 220, r * 220))
        sheet.paste(render(m, 'idle', yaw=180 + 35), (len(art_models.FRAMES) * 220, r * 220))   # back view
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main()

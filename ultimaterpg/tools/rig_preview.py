"""Draws animated mob models exactly as the client would place them, from a server dump.

  /rpg debug rig                      (on the server: writes plugins/UltimateRPG/dumps/rigs_<time>.json)
  python3 tools/pack/rig_preview.py <rigs.json> <out.png> [view yaw]

Every part is an item display riding on the mob. The client draws the part model like this (checked against the
26.3 client): element rotation (right-handed around its axis), centre on (8, 8, 8), turn 180 degrees around Y,
then the display transformation (scale, left rotation, translation), at the display's position.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, '..', '..', 'src', 'main', 'resources', 'resourcepack', 'assets', 'ultimaterpg', 'models', 'mob')
FACES = (((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
         ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)),
         ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)))


def qrot(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    # v' = v + 2w(q x v) + 2 q x (q x v)
    cx, cy, cz = y * vz - z * vy, z * vx - x * vz, x * vy - y * vx
    ccx, ccy, ccz = y * cz - z * cy, z * cx - x * cz, x * cy - y * cx
    return vx + 2 * (w * cx + ccx), vy + 2 * (w * cy + ccy), vz + 2 * (w * cz + ccz)


def element_rot(p, rot):
    if not rot:
        return p
    a = math.radians(rot['angle'])
    ox, oy, oz = rot['origin']
    x, y, z = p[0] - ox, p[1] - oy, p[2] - oz
    c, s = math.cos(a), math.sin(a)
    if rot['axis'] == 'x':
        y, z = y * c - z * s, y * s + z * c
    elif rot['axis'] == 'y':
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return x + ox, y + oy, z + oz


def world_quads(rig):
    quads = []
    mob = rig['pos']
    for i, part in enumerate(rig['parts']):
        path = os.path.join(MODELS, rig['model'], 'part', part['group'].lower() + '.json')
        model = json.load(open(path))
        hue = (i * 47) % 360
        for e in model['elements']:
            f, t = e['from'], e['to']
            for face in FACES:
                pts = []
                for corner in face:
                    v = [f[k] if corner[k] == 0 else t[k] for k in range(3)]
                    v = element_rot(v, e.get('rotation'))
                    c = (-(v[0] / 16 - 0.5), v[1] / 16 - 0.5, -(v[2] / 16 - 0.5))
                    c = tuple(x * part['s'] for x in c)
                    c = qrot(part['q'], c)
                    c = tuple(c[k] + part['t'][k] + part['pos'][k] - mob[k] for k in range(3))
                    pts.append(c)
                quads.append((pts, hue, e.get('light_emission', 0)))
    return quads


def draw(rig, size=300, view=30):
    img = Image.new('RGB', (size, size), (34, 32, 40))
    d = ImageDraw.Draw(img)
    yaw = math.radians(view + rig['yaw'])
    pitch = math.radians(18)
    scale = size / 3.4

    def project(p):
        x, y, z = p
        x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
        y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
        return size / 2 + x * scale, size * 0.88 - y * scale, z

    # ground grid around the mob position
    for k in range(-3, 4):
        a, b = project((k * 0.5, 0, -1.5)), project((k * 0.5, 0, 1.5))
        d.line([a[:2], b[:2]], fill=(60, 58, 70))
        a, b = project((-1.5, 0, k * 0.5)), project((1.5, 0, k * 0.5))
        d.line([a[:2], b[:2]], fill=(60, 58, 70))
    faces = []
    for pts, hue, glow in world_quads(rig):
        pr = [project(p) for p in pts]
        depth = sum(p[2] for p in pr) / 4
        faces.append((depth, pr, hue, glow))
    faces.sort(key=lambda f: -f[0])
    import colorsys
    for depth, pr, hue, glow in faces:
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 0.45, 0.85 if not glow else 1)
        shade = 0.55 + 0.45 * ((len(faces) and (pr[0][1] < pr[2][1])) and 1 or 0.7)
        d.polygon([p[:2] for p in pr], fill=(int(r * 255 * shade), int(g * 255 * shade), int(b * 255 * shade)),
                  outline=(20, 20, 24))
    d.text((6, 6), f"{rig['model']}  walk {rig['walk']:.2f}", fill=(230, 230, 230))
    return img


def main():
    rigs = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    view = float(sys.argv[3]) if len(sys.argv) > 3 else 30
    images = [draw(r, view=view) for r in rigs[:12]]
    if not images:
        print('keine Rigs im Dump')
        return
    cols = min(4, len(images))
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 300, rows * 300))
    for i, im in enumerate(images):
        sheet.paste(im, ((i % cols) * 300, (i // cols) * 300))
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main()

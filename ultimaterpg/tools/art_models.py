"""3D models for RPG mobs, built from boxes like a Blockbench model.

Every model is an item model shown by an item display that follows the (invisible) mob.
Coordinates: 16 units = 1 block, the model looks north (low z), feet at y = FEET, x/z centred on 8.
Each model gets four frames (idle, walk_a, walk_b, attack); frames rotate or move groups of boxes
(legs, arms, wings ...) around their pivot. Allowed rotations: -45, -22.5, 0, 22.5, 45 (one axis per box).
"""
import random
from PIL import Image

FEET = -16
FRAMES = ('idle', 'walk_a', 'walk_b', 'attack')
CELLS = 8                      # palette texture: 8x8 colour cells of 4x4 pixels (32x32)


def hexc(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


class Model:
    def __init__(self, name, height, seed=1):
        self.name = name
        self.height = height               # units from the feet to the top of the "hitbox" part
        self.boxes = []
        self.colors = []
        self.pivots = {}
        self.frames = {f: {} for f in FRAMES}
        self.seed = seed

    def color(self, value):
        value = hexc(value) if isinstance(value, str) else value
        if value not in self.colors:
            self.colors.append(value)
        return self.colors.index(value)

    def box(self, x1, y1, z1, x2, y2, z2, color, group=None, rot=None, glow=0):
        """rot = (axis, angle, (ox, oy, oz)) - a static rotation, frames of the group may replace it."""
        self.boxes.append({'from': [min(x1, x2), min(y1, y2), min(z1, z2)], 'to': [max(x1, x2), max(y1, y2), max(z1, z2)],
                           'color': self.color(color), 'group': group, 'rot': rot, 'glow': glow})

    def cube(self, cx, cy, cz, sx, sy, sz, color, **kw):
        self.box(cx - sx / 2, cy - sy / 2, cz - sz / 2, cx + sx / 2, cy + sy / 2, cz + sz / 2, color, **kw)

    def pivot(self, group, x, y, z):
        self.pivots[group] = (x, y, z)

    def pose(self, frame, group, axis=None, angle=0, move=(0, 0, 0)):
        self.frames[frame][group] = (axis, angle, move)

    def walk(self, pairs, angle=22.5, axis='x'):
        """pairs: groups that swing forward in walk_a and back in walk_b (and the opposite list)."""
        a, b = pairs
        for g in a:
            self.pose('walk_a', g, axis, angle)
            self.pose('walk_b', g, axis, -angle)
        for g in b:
            self.pose('walk_a', g, axis, -angle)
            self.pose('walk_b', g, axis, angle)

    # ------------------------------------------------------------------ output
    def texture(self):
        rnd = random.Random(self.seed)
        img = Image.new('RGBA', (CELLS * 4, CELLS * 4), (0, 0, 0, 0))
        for i, c in enumerate(self.colors):
            cx, cy = (i % CELLS) * 4, (i // CELLS) * 4
            for y in range(4):
                for x in range(4):
                    d = rnd.randint(-10, 10) + (6 if y == 0 else -6 if y == 3 else 0)
                    img.putpixel((cx + x, cy + y), tuple(max(0, min(255, v + d)) for v in c) + (255,))
        return img

    def groups(self):
        """Part names for the animated rig: every group plus '_body' for the boxes without a group."""
        names = []
        for b in self.boxes:
            g = b['group'] or '_body'
            if g not in names:
                names.append(g)
        return names

    def rig(self):
        """Animation data for the plugin: pivots and the per-frame poses of every group."""
        return {'pivots': {g: [round(v, 3) for v in self.pivots.get(g, (8, 8, 8))] for g in self.groups() if g != '_body'},
                'poses': {f: {g: [p[0] or '', p[1], list(p[2])] for g, p in poses.items()} for f, poses in self.frames.items()},
                'parts': self.groups()}

    def part_json(self, part, texture_ref):
        """Only the boxes of one group, unposed (the plugin rotates the part around its pivot)."""
        elements = []
        for b in self.boxes:
            if (b['group'] or '_body') != part:
                continue
            f, t = list(b['from']), list(b['to'])
            i = b['color']
            u, v = (i % CELLS) * 2, (i // CELLS) * 2
            uv = [u + 0.25, v + 0.25, u + 1.75, v + 1.75]
            e = {'from': [round(x, 3) for x in f], 'to': [round(x, 3) for x in t],
                 'faces': {d: {'uv': uv, 'texture': '#0', 'tintindex': 0}
                           for d in ('north', 'south', 'east', 'west', 'up', 'down')}}
            rot = b['rot']
            if rot and rot[1]:
                e['rotation'] = {'angle': rot[1], 'axis': rot[0], 'origin': [round(x, 3) for x in rot[2]]}
            if b['glow']:
                e['light_emission'] = b['glow']
            elements.append(e)
        return {'textures': {'0': texture_ref, 'particle': texture_ref}, 'elements': elements}

    def json(self, frame, texture_ref):
        if len(self.colors) > CELLS * CELLS:
            raise ValueError(f'{self.name}: too many colours')
        elements = []
        poses = self.frames.get(frame, {})
        for b in self.boxes:
            f, t = list(b['from']), list(b['to'])
            rot = b['rot']
            g = b['group']
            pose = poses.get(g) or self.frames['idle'].get(g) if g else None
            if pose:
                axis, angle, move = pose
                f = [f[i] + move[i] for i in range(3)]
                t = [t[i] + move[i] for i in range(3)]
                if axis:
                    px, py, pz = self.pivots.get(g, (8, 8, 8))
                    rot = (axis, angle, (px + move[0], py + move[1], pz + move[2]))
            for i in range(3):
                if f[i] < -16 or t[i] > 32:
                    raise ValueError(f'{self.name}/{frame}: box outside -16..32: {f} {t}')
            i = b['color']
            u, v = (i % CELLS) * 2, (i // CELLS) * 2
            uv = [u + 0.25, v + 0.25, u + 1.75, v + 1.75]
            e = {'from': [round(x, 3) for x in f], 'to': [round(x, 3) for x in t],
                 'faces': {d: {'uv': uv, 'texture': '#0', 'tintindex': 0}
                           for d in ('north', 'south', 'east', 'west', 'up', 'down')}}
            if rot and rot[1]:
                e['rotation'] = {'angle': rot[1], 'axis': rot[0], 'origin': [round(x, 3) for x in rot[2]]}
            if b['glow']:
                e['light_emission'] = b['glow']
            elements.append(e)
        return {'textures': {'0': texture_ref, 'particle': texture_ref}, 'elements': elements}


# ====================================================================== building blocks

def eyes(m, x_center, y, z_front, gap, color, glow=0, size=(1.5, 1.2)):
    for side in (-1, 1):
        m.cube(x_center + side * gap, y, z_front - 0.15, size[0], size[1], 0.6, color, group='head', glow=glow)


def weapon(m, kind, hand_x, hand_y, hand_z, colors=None, group='arm_r'):
    c = colors or {}
    metal, wood = c.get('metal', '#b8bcc4'), c.get('wood', '#6a4a2a')
    if kind == 'sword':
        m.box(hand_x - 0.5, hand_y - 2, hand_z - 2.5, hand_x + 0.5, hand_y + 1, hand_z - 1.5, wood, group=group)
        m.box(hand_x - 1.5, hand_y + 1, hand_z - 2.75, hand_x + 1.5, hand_y + 1.75, hand_z - 1.25, c.get('guard', '#8a7030'), group=group)
        m.box(hand_x - 0.6, hand_y + 1.75, hand_z - 2.5, hand_x + 0.6, hand_y + 12, hand_z - 1.5, metal, group=group)
    elif kind == 'dagger':
        m.box(hand_x - 0.5, hand_y - 1, hand_z - 2.5, hand_x + 0.5, hand_y + 1, hand_z - 1.5, wood, group=group)
        m.box(hand_x - 0.5, hand_y + 1, hand_z - 2.5, hand_x + 0.5, hand_y + 6, hand_z - 1.5, metal, group=group)
    elif kind == 'axe':
        m.box(hand_x - 0.5, hand_y - 3, hand_z - 2.5, hand_x + 0.5, hand_y + 11, hand_z - 1.5, wood, group=group)
        m.box(hand_x - 0.6, hand_y + 6, hand_z - 6.5, hand_x + 0.6, hand_y + 11, hand_z - 2.5, metal, group=group)
    elif kind == 'big_axe':
        m.box(hand_x - 0.75, hand_y - 4, hand_z - 2.75, hand_x + 0.75, hand_y + 14, hand_z - 1.25, wood, group=group)
        m.box(hand_x - 0.75, hand_y + 7, hand_z - 8.5, hand_x + 0.75, hand_y + 14, hand_z - 2.75, metal, group=group)
        m.box(hand_x - 0.75, hand_y + 8, hand_z - 1.25, hand_x + 0.75, hand_y + 13, hand_z + 2.5, metal, group=group)
    elif kind == 'club':
        m.box(hand_x - 0.75, hand_y - 3, hand_z - 2.75, hand_x + 0.75, hand_y + 6, hand_z - 1.25, wood, group=group)
        m.box(hand_x - 2, hand_y + 6, hand_z - 4, hand_x + 2, hand_y + 15, hand_z, c.get('club', '#7a5a3a'), group=group)
        for dy in (8, 11, 14):
            m.box(hand_x - 2.5, hand_y + dy, hand_z - 2.5, hand_x + 2.5, hand_y + dy + 1, hand_z - 1.5, '#9a9aa0', group=group)
    elif kind == 'bow':
        for y1, y2, dz in ((-6, -3, 0), (-3, 3, -1.25), (3, 6, 0)):
            m.box(hand_x - 0.5, hand_y + y1, hand_z - 3 + dz, hand_x + 0.5, hand_y + y2, hand_z - 2 + dz, wood, group=group)
        m.box(hand_x - 0.25, hand_y - 6, hand_z - 1.25, hand_x + 0.25, hand_y + 6, hand_z - 1, '#e8e0d0', group=group)
    elif kind == 'staff':
        m.box(hand_x - 0.5, hand_y - 6, hand_z - 2.5, hand_x + 0.5, hand_y + 14, hand_z - 1.5, wood, group=group)
        m.cube(hand_x, hand_y + 15.5, hand_z - 2, 2.5, 2.5, 2.5, c.get('orb', '#b060ff'), group=group, glow=15)


def humanoid(name, *, skin, shirt, pants, boots, height=32, seed=1, legs=12, body=(8, 12, 4), head=(8, 8, 8),
             arm=(4, 12), eye='#f0f0f0', pupil='#202020', eye_glow=0, weapon_kind=None, weapon_colors=None,
             arm_pose=0, sleeves=None, thin=False):
    m = Model(name, height, seed)
    bw, bh, bd = body
    hw, hh, hd = head
    aw, al = arm
    y_hip = FEET + legs
    y_neck = y_hip + bh
    lw = 2 if thin else min(bw / 2, 4)
    ld = 2 if thin else min(bd, 4)
    # legs: thigh + shin as two boxes with a slight knee bend (one rigid piece per pivot,
    # like the spider legs - not a free joint, but reads as an articulated limb, not a rod)
    y_knee = y_hip - (y_hip - FEET) * 0.42
    knee_z = 8 + ld / 2 + (0.5 if not thin else 0.3)
    for g, x1, x2 in (('leg_l', 8 - lw - (0.5 if thin else 0), 8 - (0.5 if thin else 0)),
                      ('leg_r', 8 + (0.5 if thin else 0), 8 + lw + (0.5 if thin else 0))):
        m.box(x1, y_knee, 8 - ld / 2, x2, y_hip, 8 + ld / 2, pants, group=g)
        m.box(x1, FEET, 8 - ld / 2, x2, y_knee, knee_z, pants, group=g)
        if not thin:
            m.box(x1 - 0.25, FEET, 8 - ld / 2 - 0.25, x2 + 0.25, FEET + 3, knee_z + 0.25, boots, group=g)
        m.pivot(g, (x1 + x2) / 2, y_hip, 8)
    # body
    if thin:
        m.box(7, y_hip, 7, 9, y_neck, 9, shirt)                                  # spine
        m.box(8 - bw / 2 + 1, y_hip - 1, 7, 8 + bw / 2 - 1, y_hip + 1, 9, shirt)  # pelvis
        for y in range(int(y_hip + 4), int(y_neck), 2):                          # ribs
            m.box(8 - bw / 2, y, 8 - bd / 2, 8 + bw / 2, y + 1, 8 + bd / 2, shirt)
    else:
        m.box(8 - bw / 2, y_hip, 8 - bd / 2, 8 + bw / 2, y_neck, 8 + bd / 2, shirt)
    # arms: upper arm + forearm with a slight elbow bend, same single-pivot approach as the legs
    aw_ = 2 if thin else aw
    y_elbow = y_neck - al * 0.52
    elbow_z = 8 + aw_ / 2 + 0.4
    for g, x1, x2 in (('arm_l', 8 - bw / 2 - aw_, 8 - bw / 2), ('arm_r', 8 + bw / 2, 8 + bw / 2 + aw_)):
        m.box(x1, y_elbow, 8 - aw_ / 2, x2, y_neck, 8 + aw_ / 2, sleeves or skin, group=g)
        m.box(x1, y_neck - al, 8 - aw_ / 2, x2, y_elbow, elbow_z, sleeves or skin, group=g)
        if sleeves:
            m.box(x1, y_neck - al, 8 - aw_ / 2, x2, y_neck - al + 3, 8 + aw_ / 2, skin, group=g)
        m.pivot(g, (x1 + x2) / 2, y_neck - 1, 8)
    # head
    m.box(8 - hw / 2, y_neck, 8 - hd / 2, 8 + hw / 2, y_neck + hh, 8 + hd / 2, skin, group='head')
    m.pivot('head', 8, y_neck, 8)
    ey = y_neck + hh * 0.55
    eyes(m, 8, ey, 8 - hd / 2, hw / 4, eye, glow=eye_glow)
    if pupil:
        for side in (-1, 1):
            m.cube(8 + side * hw / 4 + side * 0.3, ey - 0.1, 8 - hd / 2 - 0.35, 0.7, 0.8, 0.4, pupil, group='head')
    # animation
    m.walk((['leg_l', 'arm_r'], ['leg_r', 'arm_l']))
    if arm_pose:
        for f in FRAMES:
            for g in ('arm_l', 'arm_r'):
                m.pose(f, g, 'x', arm_pose)
        m.pose('attack', 'arm_l', 'x', 45)
        m.pose('attack', 'arm_r', 'x', 45, (0, 1, -2))
    else:
        m.pose('attack', 'arm_r', 'x', 45, (0, 0, -1))
        m.pose('attack', 'arm_l', 'x', -22.5)
    m.pose('attack', 'head', 'x', 22.5)
    if weapon_kind:
        hx = 8 + bw / 2 + aw_ / 2
        weapon(m, weapon_kind, hx, y_neck - al + 1, 8, weapon_colors)
    m.hand = (8 + bw / 2 + aw_ / 2, y_neck - al + 1)
    m.neck = y_neck
    m.hip = y_hip
    m.dims = (bw, bh, bd, hw, hh, hd, aw_, al)
    return m


# ====================================================================== goblins

def goblin(name, skin='#6a9a3a', vest='#7a5230', pants='#5a4028', seed=3, weapon_kind='sword', extra=None,
           body=(9, 9, 6), eye='#f0d040', eye_glow=0):
    m = humanoid(name, skin=skin, shirt=vest, pants=pants, boots='#3a2a1a', height=27, seed=seed, legs=8, body=body,
                 head=(10, 9, 9), arm=(3, 11), eye=eye, pupil='#1a1408', eye_glow=eye_glow, weapon_kind=weapon_kind,
                 weapon_colors={'metal': '#a8a8a8'})
    bw, bh, bd, hw, hh, hd, aw, al = m.dims
    n = m.neck
    # big pointed ears sticking out sideways
    for side in (-1, 1):
        x0 = 8 + side * hw / 2
        m.box(x0, n + 4, 7, x0 + side * 3, n + 6.5, 9.5, skin, group='head')
        m.box(x0 + side * 3, n + 5, 7.5, x0 + side * 5, n + 6.5, 9, skin, group='head')
    # long nose, wide mouth with fangs
    m.box(7, n + 2.5, 8 - hd / 2 - 2.5, 9, n + 4.5, 8 - hd / 2, skin, group='head')
    m.box(5, n + 1, 8 - hd / 2 - 0.3, 11, n + 2, 8 - hd / 2 + 0.2, '#2a1408', group='head')
    for x in (5.5, 9.5):
        m.box(x, n + 0.5, 8 - hd / 2 - 0.45, x + 1, n + 1.5, 8 - hd / 2, '#f0ead0', group='head')
    # belt
    m.box(8 - bw / 2 - 0.25, m.hip, 8 - bd / 2 - 0.25, 8 + bw / 2 + 0.25, m.hip + 1.5, 8 + bd / 2 + 0.25, '#3a2a1a')
    m.box(7, m.hip, 8 - bd / 2 - 0.5, 9, m.hip + 1.5, 8 - bd / 2, '#c8a040')
    if extra:
        extra(m)
    return m


def g_scout(m):
    n, hw, hd = m.neck, m.dims[3], m.dims[5]
    m.box(8 - hw / 2 - 0.3, n + 7, 8 - hd / 2 - 0.3, 8 + hw / 2 + 0.3, n + 8, 8 + hd / 2 + 0.3, '#7a5230', group='head')


def g_warrior(m):
    n, hw, hd = m.neck, m.dims[3], m.dims[5]
    m.box(8 - hw / 2 - 0.5, n + 6, 8 - hd / 2 - 0.5, 8 + hw / 2 + 0.5, n + 9.5, 8 + hd / 2 + 0.5, '#6a4a2a', group='head')
    m.box(7.5, n + 9.5, 7, 8.5, n + 11.5, 10, '#8a2a2a', group='head')
    # round shield on the left arm
    x = 8 - m.dims[0] / 2 - m.dims[6] - 1
    m.box(x - 1, m.neck - 10, 4, x, m.neck - 2, 12, '#7a5230', group='arm_l')
    m.box(x - 1.3, m.neck - 7, 7, x - 1, m.neck - 5, 9, '#a8a8a8', group='arm_l')


def g_archer(m):
    n, hw, hd = m.neck, m.dims[3], m.dims[5]
    hood = '#3d6324'
    m.box(8 - hw / 2 - 0.5, n + 5, 8 - hd / 2 + 1, 8 + hw / 2 + 0.5, n + 9.5, 8 + hd / 2 + 0.5, hood, group='head')
    m.box(8 - hw / 2 - 0.5, n - 0.5, 8 + hd / 2 - 1, 8 + hw / 2 + 0.5, n + 5, 8 + hd / 2 + 0.5, hood, group='head')
    # quiver on the back - its own group so it sways loosely while walking
    qrot = ('z', 22.5, (10, m.hip + 6, 12))
    m.box(9, m.hip + 2, 8 + m.dims[2] / 2, 12, m.neck + 3, 8 + m.dims[2] / 2 + 2.5, '#5a3a1e', group='quiver', rot=qrot)
    for x in (9.5, 10.5, 11.5):
        m.box(x, m.neck + 3, 8 + m.dims[2] / 2 + 0.5, x + 0.5, m.neck + 5, 8 + m.dims[2] / 2 + 1.5, '#e8e0d0',
              group='quiver', rot=qrot)
    m.pivot('quiver', 10, m.hip + 6, 12)
    # smooth animation applies these as an additional rotation on top of the baked (already
    # tilted) rest geometry, so these are small deltas, like the existing tail/robe sways
    for f in ('walk_a', 'attack'):
        m.pose(f, 'quiver', 'z', 8)
    m.pose('walk_b', 'quiver', 'z', -6)


def g_shaman(m):
    n, hw, hd = m.neck, m.dims[3], m.dims[5]
    # bone mask + feathers
    m.box(8 - hw / 2 + 1, n + 3, 8 - hd / 2 - 0.6, 8 + hw / 2 - 1, n + 7, 8 - hd / 2 - 0.1, '#e8e0c8', group='head')
    eyes(m, 8, n + 5, 8 - hd / 2 - 0.5, 2, '#b040e0', glow=12)
    for x, c in ((5, '#d04040'), (7.5, '#40a0d0'), (10, '#e0c040')):
        m.box(x, n + 9, 9, x + 1.2, n + 14, 10, c, group='head', rot=('z', 22.5 if x < 7 else -22.5 if x > 9 else 0, (x, n + 9, 9.5)))
    # robe skirt
    bw, bd = m.dims[0], m.dims[2]
    m.box(8 - bw / 2 - 0.5, m.hip - 5, 8 - bd / 2 - 0.5, 8 + bw / 2 + 0.5, m.hip + 1, 8 + bd / 2 + 0.5, '#5a2a6a')


def g_cave(m):
    pass


def g_brute(m):
    n, hw, hd, bw, bd = m.neck, m.dims[3], m.dims[5], m.dims[0], m.dims[2]
    iron = '#a8a8b0'
    m.box(8 - hw / 2 - 0.5, n + 6, 8 - hd / 2 - 0.5, 8 + hw / 2 + 0.5, n + 9.5, 8 + hd / 2 + 0.5, iron, group='head')
    m.box(7.5, n + 2, 8 - hd / 2 - 1, 8.5, n + 6.5, 8 - hd / 2 - 0.4, iron, group='head')
    for side, g in ((-1, 'arm_l'), (1, 'arm_r')):                      # shoulder plates
        x = 8 + side * (bw / 2 + m.dims[6] / 2)
        m.box(x - 2.5, n - 1, 8 - 3, x + 2.5, n + 1.5, 8 + 3, iron, group=g)
    m.box(8 - bw / 2, m.hip + 3, 8 - bd / 2 - 0.5, 8 + bw / 2, m.hip + 4, 8 + bd / 2 + 0.5, '#5a3a1e')   # chest strap


def g_king(m):
    n, hw, hd, bw, bd = m.neck, m.dims[3], m.dims[5], m.dims[0], m.dims[2]
    gold = '#e8b830'
    m.box(8 - hw / 2 - 0.3, n + 9, 8 - hd / 2 - 0.3, 8 + hw / 2 + 0.3, n + 10.5, 8 + hd / 2 + 0.3, gold, group='head')
    for x in (8 - hw / 2, 7.25, 8 + hw / 2 - 1.5):
        for z in (8 - hd / 2 - 0.3, 8 + hd / 2 - 1.2):
            m.box(x, n + 10.5, z, x + 1.5, n + 12.5, z + 1.5, gold, group='head')
    m.cube(8, n + 9.75, 8 - hd / 2 - 0.5, 1.5, 1.2, 0.5, '#e02828', group='head', glow=8)
    m.box(8 - bw / 2 - 1, m.hip - 6, 8 + bd / 2, 8 + bw / 2 + 1, n, 8 + bd / 2 + 1, '#9a1a1a', group='cape')  # cape
    m.pivot('cape', 8, n, 8 + bd / 2)
    for f in ('walk_a', 'attack'):
        m.pose(f, 'cape', 'x', 12)
    m.pose('walk_b', 'cape', 'x', -8)
    m.box(8 - bw / 2 - 1.5, n - 1.5, 8 - bd / 2 - 1, 8 + bw / 2 + 1.5, n + 0.5, 8 + bd / 2 + 1.5, '#e8e0d0')  # fur collar


def goblins():
    return {
        'goblin_scout': goblin('goblin_scout', extra=g_scout, weapon_kind='dagger'),
        # skin tones lined up with the hand-authored goblin_scout/brute/archer/gunner/warlord
        # models (muted olive-to-moss green, #40-90 range) so the whole goblin family reads as one group.
        'goblin_warrior': goblin('goblin_warrior', skin='#5c8a35', vest='#4a6a2a', extra=g_warrior, weapon_kind='axe', seed=4),
        'goblin_archer': goblin('goblin_archer', skin='#6f9f40', vest='#4a7a2c', extra=g_archer, weapon_kind='bow', seed=5),
        'goblin_shaman': goblin('goblin_shaman', skin='#5e8a3e', vest='#5a2a6a', extra=g_shaman, weapon_kind='staff', seed=6),
        'cave_goblin': goblin('cave_goblin', skin='#6f8a5c', vest='#3a3a34', pants='#2a2a24', extra=g_cave, eye='#f4f4e8',
                              eye_glow=10, seed=7),
        'goblin_brute': goblin('goblin_brute', skin='#4a6e28', vest='#5a3a1e', body=(12, 10, 7), extra=g_brute,
                               weapon_kind='big_axe', seed=8),
        'goblin_king': goblin('goblin_king', skin='#5a8a30', vest='#2f4d1c', body=(12, 10, 8), extra=g_king,
                              weapon_kind='big_axe', seed=9),
    }


# ====================================================================== undead & humans

def skeleton(name, bone='#d8d0b8', extra=None, weapon_kind='sword', eye='#202020', eye_glow=0, seed=11):
    m = humanoid(name, skin=bone, shirt=bone, pants=bone, boots=bone, height=32, seed=seed, thin=True,
                 eye=eye, pupil=None, eye_glow=eye_glow, weapon_kind=weapon_kind)
    n = m.neck
    m.box(5, n, 4, 11, n + 1.5, 9, '#c0b8a0', group='head')                    # jaw
    m.box(6, n + 1.5, 3.7, 10, n + 2.2, 4.2, '#302820', group='head')          # teeth gap
    m.box(7.5, n + 3, 3.6, 8.5, n + 4, 4.1, '#302820', group='head')           # nose hole
    if extra:
        extra(m)
    return m


def sk_helmet(color, crest=None):
    def f(m):
        n = m.neck
        m.box(3.6, n + 5, 3.6, 12.4, n + 8.6, 12.4, color, group='head')
        m.box(3.6, n + 1, 10, 12.4, n + 5, 12.4, color, group='head')
        if crest:
            m.box(7.5, n + 8.6, 5, 8.5, n + 10.5, 12, crest, group='head')
    return f


def sk_cursed(m):
    n = m.neck
    m.box(3.6, n + 6, 3.6, 12.4, n + 8.6, 12.4, '#4a6a8a', group='head')           # frozen hood
    m.box(3.6, n - 1, 10.5, 12.4, n + 6, 12.6, '#4a6a8a', group='head')
    m.box(4.5, m.hip - 4, 9, 11.5, m.neck, 10.5, '#5a7a9a')                       # tattered cloak


def zombie_like(name, skin, shirt, pants, extra=None, seed=13, hunch=False, eye='#c0f040', eye_glow=6):
    m = humanoid(name, skin=skin, shirt=shirt, pants=pants, boots='#3a3a2a', height=32, seed=seed, arm_pose=45,
                 eye=eye, pupil=None, eye_glow=eye_glow, sleeves=shirt)
    n = m.neck
    for x in (5, 7, 9):                                                          # torn shirt
        m.box(x, m.hip - 1.5, 5.8, x + 1.2, m.hip, 6.2, shirt)
    m.box(6, n + 1, 3.7, 10, n + 2, 4.1, '#2a1a10', group='head')                # mouth
    m.box(6.5, n + 1, 3.6, 7.2, n + 1.8, 3.9, '#d8d0b8', group='head')
    m.box(8.8, n + 1, 3.6, 9.5, n + 1.8, 3.9, '#d8d0b8', group='head')
    if hunch:
        for f in FRAMES:
            m.pose(f, 'head', 'x', 22.5, (0, -1, -1.5))
    if extra:
        extra(m)
    return m


def ghoul_claws(m):
    for g, x in (('arm_l', 8 - 4 - 2), ('arm_r', 8 + 4 + 2)):
        y = m.neck - 12
        for dx in (-1.2, 0, 1.2):
            m.box(x + dx - 0.3, y - 3, 7.6, x + dx + 0.3, y, 8.4, '#e8e0c0', group=g)


def armored(name, armor, trim, skin='#c89a70', cloth='#5a3a2a', helmet='visor', weapon_kind='sword', shield=None,
            eye='#f0f0f0', eye_glow=0, seed=21, cape=None, horns=None, weapon_colors=None):
    m = humanoid(name, skin=armor, shirt=armor, pants=armor, boots=trim, height=32, seed=seed, eye=eye, pupil=None,
                 eye_glow=eye_glow, weapon_kind=weapon_kind, weapon_colors=weapon_colors, sleeves=armor)
    n, hip = m.neck, m.hip
    # face behind the helmet
    if helmet == 'visor':
        m.box(4.5, n + 4, 3.7, 11.5, n + 5, 4.1, '#0a0a0e', group='head')
        for x in (5.5, 7.5, 9.5):
            m.box(x, n + 1, 3.7, x + 1, n + 3, 4.1, '#1a1a20', group='head')
        m.box(7.5, n + 8, 5, 8.5, n + 10.5, 12, trim, group='head')
    elif helmet == 'hood':
        m.box(4, n, 3.7, 12, n + 8, 4, '#1a1012', group='head')
        m.box(3.5, n + 5, 3.5, 12.5, n + 8.5, 12.5, cloth, group='head')
        m.box(3.5, n - 0.5, 3.5, 4.5, n + 8.5, 12.5, cloth, group='head')
        m.box(11.5, n - 0.5, 3.5, 12.5, n + 8.5, 12.5, cloth, group='head')
        m.box(3.5, n - 0.5, 11.5, 12.5, n + 8.5, 12.5, cloth, group='head')
    elif helmet == 'bandana':
        m.box(4, n + 4.2, 3.9, 12, n + 8, 12, skin, group='head')
        m.box(3.7, n + 6, 3.7, 12.3, n + 8.3, 12.3, cloth, group='head')
        m.box(3.7, n, 3.7, 12.3, n + 3.2, 4.2, '#2a2a30', group='head')          # mask over mouth
        m.box(9, n + 3, 12, 11, n + 6, 13.5, cloth, group='head')
    # chest plate, belt, shoulder pads
    m.box(3.7, hip + 4, 5.7, 12.3, n - 0.5, 6.2, trim)
    m.box(3.7, hip, 5.7, 12.3, hip + 1.5, 10.3, '#3a2a1a')
    for side, g in ((-1, 'arm_l'), (1, 'arm_r')):
        x = 8 + side * 6
        m.box(x - 2.6, n - 2, 5.4, x + 2.6, n + 1, 10.6, trim, group=g)
    if shield:
        m.box(-1, n - 13, 3, 0, n - 2, 13, shield, group='arm_l')
        m.box(-1.3, n - 9, 7, -1, n - 6, 9, trim, group='arm_l')
    if cape:
        m.box(4, hip - 8, 10.2, 12, n, 11.2, cape, group='cape')
        m.pivot('cape', 8, n, 10.2)
        for f in ('walk_a', 'attack'):
            m.pose(f, 'cape', 'x', 10)
        m.pose('walk_b', 'cape', 'x', -7)
    if horns:
        for side in (-1, 1):
            m.box(8 + side * 4, n + 6, 7, 8 + side * 6, n + 8, 9, horns, group='head')
            m.box(8 + side * 5, n + 8, 7.25, 8 + side * 6.5, n + 11, 8.75, horns, group='head')
    return m


def troll(name='mountain_troll', skin='#7a8a7a', shirt='#5a4a3a', pants='#4a3a2a', boots='#3a3a3a', belly='#8a9a8a',
          dark='#6a7a6a', eye='#f0b020', eye_glow=0, seed=31, crystals=None):
    m = humanoid(name, skin=skin, shirt=shirt, pants=pants, boots=boots, height=32, seed=seed,
                 legs=10, body=(14, 13, 8), head=(7, 7, 7), arm=(5, 17), eye=eye, pupil='#301010',
                 weapon_kind='club', eye_glow=eye_glow)
    n = m.neck
    m.box(1, m.hip + 2, 3.5, 15, n - 3, 4.5, belly)                               # belly
    m.box(6.5, n + 1.5, 3.8 - 1.5, 9.5, n + 3.5, 4.5, dark, group='head')         # nose
    for x in (5.2, 10):
        m.box(x, n + 0.5, 4, x + 0.8, n + 2.5, 4.3, '#f0ead0', group='head')       # tusks
    for g, x in (('arm_l', -0.5), ('arm_r', 13.5)):
        m.box(x, n - 2, 5, x + 3, n + 0.5, 11, dark, group=g)                      # shoulders
    if crystals:
        for x, y, z, h in ((3, n - 1, 11, 4), (7, n - 2, 11.5, 6), (11, n - 1, 11, 4), (5, m.hip + 4, 11.5, 3)):
            m.box(x, y, z, x + 2, y + h, z + 2, crystals, glow=10)
        for g, x in (('arm_l', 0), ('arm_r', 14)):
            m.box(x, n + 0.5, 7, x + 2, n + 4, 9, crystals, group=g, glow=10)
    return m


# ====================================================================== beasts

def quadruped(name, *, fur, belly, height, body=(6, 6, 14), legs=8, head=(6, 6, 6), snout=(3, 3, 3), seed=41,
              eye='#f0d040', eye_glow=0, ears=True, tusks=False, tail=True, mane=None):
    m = Model(name, height, seed)
    bw, bh, bl = body
    y_body = FEET + legs
    z0, z1 = 8 - bl / 2, 8 + bl / 2
    m.box(8 - bw / 2, y_body, z0, 8 + bw / 2, y_body + bh, z1, fur)
    m.box(8 - bw / 2 + 0.5, y_body - 0.3, z0 + 1, 8 + bw / 2 - 0.5, y_body + 0.5, z1 - 1, belly)
    if mane:
        m.box(8 - bw / 2 - 0.5, y_body + 1, z0 - 0.5, 8 + bw / 2 + 0.5, y_body + bh + 1.5, z0 + 5, mane, group='mane')
        m.pivot('mane', 8, y_body + bh + 1, z0)
        m.pose('walk_a', 'mane', 'x', 9)
        m.pose('walk_b', 'mane', 'x', -7)
    lw = 2
    for g, x, z in (('leg_fl', 8 - bw / 2 + 0.25, z0 + 1), ('leg_fr', 8 + bw / 2 - lw - 0.25, z0 + 1),
                    ('leg_bl', 8 - bw / 2 + 0.25, z1 - 3), ('leg_br', 8 + bw / 2 - lw - 0.25, z1 - 3)):
        m.box(x, FEET, z, x + lw, y_body + 1, z + 2, fur, group=g)
        m.box(x - 0.2, FEET, z - 0.2, x + lw + 0.2, FEET + 1, z + 2.2, belly, group=g)
        m.pivot(g, x + 1, y_body + 1, z + 1)
    hw, hh, hd = head
    hy = y_body + bh - hh / 2 - 1
    hz = z0 - hd + 1
    m.box(8 - hw / 2, hy, hz, 8 + hw / 2, hy + hh, hz + hd, fur, group='head')
    sw, sh, sd = snout
    m.box(8 - sw / 2, hy, hz - sd, 8 + sw / 2, hy + sh, hz, belly, group='head')
    m.box(8 - 0.6, hy + sh - 0.8, hz - sd - 0.3, 8 + 0.6, hy + sh, hz - sd + 0.2, '#1a1a1a', group='head')
    eyes(m, 8, hy + hh * 0.7, hz, hw / 4 + 0.3, eye, glow=eye_glow, size=(1.2, 1))
    if ears:
        for side in (-1, 1):
            m.box(8 + side * (hw / 2 - 2), hy + hh, hz + hd - 3, 8 + side * (hw / 2 - 0.5), hy + hh + 2.5, hz + hd - 1.8,
                  fur, group='head')
    if tusks:
        for side in (-1, 1):
            m.box(8 + side * 1.5 - 0.4, hy - 0.5, hz - sd - 0.2, 8 + side * 1.5 + 0.4, hy + 2.5, hz - sd + 0.6,
                  '#f0ead0', group='head')
    m.pivot('head', 8, hy + hh / 2, hz + hd)
    if tail:
        m.box(7.25, y_body + bh - 2, z1, 8.75, y_body + bh - 0.5, z1 + 6, fur, group='tail')
        m.pivot('tail', 8, y_body + bh - 1, z1)
        for f in FRAMES:
            m.pose(f, 'tail', 'x', -22.5)
    m.walk((['leg_fl', 'leg_br'], ['leg_fr', 'leg_bl']), angle=22.5)
    m.pose('attack', 'head', 'x', 22.5, (0, -1, -1.5))
    return m


def spider(name, body='#3a3028', abdomen='#2a2420', marks='#a02020', eye='#e02020', height=14, seed=51):
    """A proper arachnid: a narrow cephalothorax, a round tapering abdomen, fangs and palps, and eight
    bent (hip-knee-foot), individually angled legs instead of straight sticks fanned out flat."""
    m = Model(name, height, seed)
    y = -8
    m.box(5.5, y, 3, 10.5, y + 5, 9, body)                    # cephalothorax (narrower than before)
    m.box(6.2, y + 4.6, 2.6, 9.8, y + 5.6, 9.4, body)         # carapace ridge
    m.box(4, y - 1.5, 8.5, 12, y + 3.5, 14.5, abdomen)        # abdomen, tapering...
    m.box(3, y - 0.5, 13.5, 13, y + 6.5, 21, abdomen)         # ...to a bigger rear lobe
    m.box(5.5, y + 6, 15, 10.5, y + 6.8, 19.5, marks)         # dorsal stripe
    m.box(7, y + 3.8, 9, 9, y + 7, 13, marks)
    eyes = ((-1.6, 2.4, 1.1), (1.6, 2.4, 1.1), (-0.9, 3.3, 0.6), (0.9, 3.3, 0.6), (-0.3, 3.9, 0.2), (0.3, 3.9, 0.2))
    for dx, dy, dz in eyes:
        m.box(8 + dx - 0.35, y + dy, 2 + dz, 8 + dx + 0.35, y + dy + 0.6, 2.6 + dz, eye, glow=12)
    m.box(6, y, 0.2, 7.3, y + 1.6, 2.2, '#1a1a1a')            # fangs
    m.box(8.7, y, 0.2, 10, y + 1.6, 2.2, '#1a1a1a')
    m.box(5.6, y + 1.2, 1.4, 6.4, y + 2.4, 2.6, body, group='_body')   # palps
    m.box(9.6, y + 1.2, 1.4, 10.4, y + 2.4, 2.6, body, group='_body')
    # legs: pairs run from near the head (steep, reaching forward) to near the tail (swept back, wide)
    leg_z = (3.4, 5.0, 6.6, 8.2)
    reach = (8, 10, 10, 8.5)       # how far the leg spreads sideways
    forward = (3.5, 0.5, -1.5, -4)  # front legs angle forward, back legs angle backward
    droop = (2.5, 3.5, 3.8, 3)      # how far the foot drops below the hip (close to the floor)
    for side in (-1, 1):
        for i, z in enumerate(leg_z):
            g = f'leg{"L" if side < 0 else "R"}{i}'
            hx, hy, hz = 8 + side * 3.2, y + 3, z
            kx, ky, kz = hx + side * reach[i] * 0.55, hy - droop[i] * 0.35, z + forward[i] * 0.5
            fx, fy, fz = hx + side * reach[i], hy - droop[i], z + forward[i]
            m.box(min(hx, kx), min(hy, ky) - 0.35, min(hz, kz) - 0.35, max(hx, kx), max(hy, ky) + 0.35,
                  max(hz, kz) + 0.35, body, group=g)
            m.box(min(kx, fx), min(ky, fy) - 0.3, min(kz, fz) - 0.3, max(kx, fx), max(ky, fy) + 0.3,
                  max(kz, fz) + 0.3, body, group=g)
            m.pivot(g, hx, hy, hz)
            base_angle = -40 if side > 0 else 40
            for f in FRAMES:
                m.pose(f, g, 'z', base_angle)
            swing = 10
            m.pose('walk_a', g, 'z', base_angle + (swing if (i + (side > 0)) % 2 else -swing))
            m.pose('walk_b', g, 'z', base_angle - (swing if (i + (side > 0)) % 2 else -swing))
            m.pose('attack', g, 'z', (base_angle * 0.4) if i == 0 else (base_angle - (10 if side > 0 else -10)))
    return m


def winged(m, y, z, span, color, membrane, flap=True):
    for side, g in ((-1, 'wing_l'), (1, 'wing_r')):
        x_root = 8 + side * 3
        x_tip = x_root + side * span
        m.box(min(x_root, x_tip), y, z, max(x_root, x_tip), y + 1, z + 1.5, color, group=g)
        m.box(min(x_root, x_tip), y - 0.2, z + 1.5, max(x_root, x_tip) - (0 if side > 0 else 0), y + 0.3, z + span * 0.6,
              membrane, group=g)
        m.pivot(g, x_root, y + 0.5, z + 1)
        up = 22.5 if side > 0 else -22.5
        m.pose('idle', g, 'z', up)
        m.pose('walk_a', g, 'z', up * 2 if flap else up)
        m.pose('walk_b', g, 'z', -up if flap else up)
        m.pose('attack', g, 'z', up * 2)


def demon(name, skin='#c03018', dark='#401010', fire='#ffb020', height=30, seed=61, wings=False, flame='#ff7020'):
    m = Model(name, height, seed)
    y_hip = -8
    for i, (w, y1, y2) in enumerate(((3, -16, -12), (5, -13, -10), (7, -11, -8))):   # flame tail instead of legs
        m.box(8 - w / 2, y1, 8 - w / 2, 8 + w / 2, y2, 8 + w / 2, fire if i == 0 else flame, glow=15, group='flame')
    m.pivot('flame', 8, -10, 8)
    m.pose('walk_a', 'flame', 'y', 22.5)
    m.pose('walk_b', 'flame', 'y', -22.5)
    m.box(4, y_hip, 6, 12, y_hip + 12, 10, skin)
    m.box(5, y_hip + 3, 5.7, 11, y_hip + 9, 6.1, dark)
    n = y_hip + 12
    for g, x1, x2 in (('arm_l', 1, 4), ('arm_r', 12, 15)):
        m.box(x1, n - 11, 6.5, x2, n, 9.5, skin, group=g)
        for dx in (0.5, 1.5, 2.5):
            m.box(x1 + dx - 0.25, n - 13, 7.6, x1 + dx + 0.25, n - 11, 8.4, '#f0e0c0', group=g)
        m.box(x1 + 0.5, n - 12.5, 6.5 - 2, x2 - 0.5, n - 10, 6.5, fire, glow=15, group=g)   # fire in the hands
        m.pivot(g, (x1 + x2) / 2, n - 1, 8)
    m.box(4.5, n, 4.5, 11.5, n + 7, 11.5, skin, group='head')
    m.pivot('head', 8, n, 8)
    eyes(m, 8, n + 4, 4.5, 1.8, '#fff060', glow=15)
    m.box(6, n + 1, 4.2, 10, n + 2, 4.6, '#200808', group='head')
    for side in (-1, 1):
        m.box(8 + side * 3, n + 6, 7, 8 + side * 5, n + 8, 9, dark, group='head')
        m.box(8 + side * 4.5, n + 8, 7.3, 8 + side * 5.8, n + 11, 8.7, dark, group='head')
    if wings:
        winged(m, n - 2, 10, 9, dark, '#802020')
    m.walk((['arm_r'], ['arm_l']))
    m.pose('attack', 'arm_r', 'x', 45, (0, 0, -1))
    m.pose('attack', 'arm_l', 'x', 45, (0, 0, -1))
    return m


def wraith(name='temple_wraith', robe='#3a4a5a', dark='#1a222a', eye='#60e0ff', claws='#c0e8f0', seed=71, crown=None):
    m = Model(name, 30, seed)
    for i, (w, y1, y2) in enumerate(((5, -14, -9), (7, -9, -3), (8, -3, 4))):
        m.box(8 - w / 2, y1, 8 - w / 2 + 1, 8 + w / 2, y2, 8 + w / 2, robe if i else dark, group='robe' if i == 0 else None)
    m.pivot('robe', 8, -9, 8)
    m.pose('walk_a', 'robe', 'x', -22.5)
    m.pose('walk_b', 'robe', 'x', 22.5)
    n = 4
    m.box(3.5, n, 4, 12.5, n + 8, 12.5, robe, group='head')
    m.box(4.5, n + 0.5, 3.6, 11.5, n + 7, 4.2, '#05070a', group='head')
    eyes(m, 8, n + 4.5, 4, 1.7, eye, glow=15)
    if crown:
        for x in (4, 7, 10):
            m.box(x, n + 8, 7, x + 2, n + 11, 9, crown, group='head', glow=8)
    m.pivot('head', 8, n, 8)
    for g, x1, x2 in (('arm_l', 1, 4), ('arm_r', 12, 15)):
        m.box(x1, n - 10, 6, x2, n, 10, robe, group=g)
        for dx in (0.5, 1.5, 2.5):
            m.box(x1 + dx - 0.25, n - 13, 7.6, x1 + dx + 0.25, n - 10, 8.4, claws, group=g, glow=6)
        m.pivot(g, (x1 + x2) / 2, n - 1, 8)
    for f in FRAMES:
        for g in ('arm_l', 'arm_r'):
            m.pose(f, g, 'x', 22.5 if f != 'attack' else 45)
    return m


def dragon(name, scale_body=1.0, scales='#8a1a10', belly='#e0a040', horn='#e8e0c8', wing='#5a1010', eye='#ffe040',
           height=22, seed=81):
    m = Model(name, height, seed)
    y_body = -8
    m.box(3, y_body, 2, 13, y_body + 8, 18, scales)                     # body
    m.box(4, y_body - 0.3, 3, 12, y_body + 1, 17, belly)
    for z in (4, 8, 12, 16):                                            # back spikes
        m.box(7.5, y_body + 8, z, 8.5, y_body + 10, z + 2, horn)
    for g, x, z in (('leg_fl', 3.5, 3), ('leg_fr', 10, 3), ('leg_bl', 3.5, 14), ('leg_br', 10, 14)):
        m.box(x, FEET, z, x + 2.5, y_body + 2, z + 3, scales, group=g)
        m.box(x - 0.3, FEET, z - 1, x + 2.8, FEET + 1, z + 1, horn, group=g)
        m.pivot(g, x + 1.25, y_body + 2, z + 1.5)
    # neck and head
    m.box(6, y_body + 4, -3, 10, y_body + 10, 3, scales, group='head', rot=('x', -22.5, (8, y_body + 6, 2)))
    hy = y_body + 9
    m.box(4.5, hy, -11, 11.5, hy + 6, -3, scales, group='head')
    m.box(5.5, hy - 2, -15, 10.5, hy + 2, -7, scales, group='head')     # snout / jaw
    m.box(5.8, hy - 2.6, -14.6, 10.2, hy - 2, -8, belly, group='head')
    for x in (6, 9.4):
        m.box(x, hy + 1.6, -15.3, x + 0.6, hy + 2.2, -14.8, '#1a0a0a', group='head')
    eyes(m, 8, hy + 4, -11, 2.5, eye, glow=15, size=(1.5, 1))
    for side in (-1, 1):
        m.box(8 + side * 2.5 - 0.75, hy + 5, -5, 8 + side * 2.5 + 0.75, hy + 7, -2, horn, group='head',
              rot=('x', -22.5, (8, hy + 6, -4)))
        m.box(8 + side * 2.5 - 0.6, hy + 6, -2, 8 + side * 2.5 + 0.6, hy + 7.2, 2.5, horn, group='head',
              rot=('x', -22.5, (8, hy + 6, -4)))
    m.pivot('head', 8, y_body + 6, 2)
    # tail
    m.box(6, y_body + 2, 18, 10, y_body + 6, 25, scales, group='tail')
    m.box(7, y_body + 2.5, 25, 9, y_body + 5, 31, scales, group='tail')
    m.box(7.5, y_body + 2, 30, 8.5, y_body + 6, 32, horn, group='tail')
    m.pivot('tail', 8, y_body + 4, 18)
    m.pose('walk_a', 'tail', 'y', 22.5)
    m.pose('walk_b', 'tail', 'y', -22.5)
    winged(m, y_body + 7, 5, 13, scales, wing)
    m.walk((['leg_fl', 'leg_br'], ['leg_fr', 'leg_bl']))
    m.pose('attack', 'head', 'x', 22.5)
    return m


# ====================================================================== all models

def models():
    result = dict(goblins())
    result.update({
        'skeleton_warrior': skeleton('skeleton_warrior', extra=sk_helmet('#9a9aa0'), weapon_kind='sword'),
        'undead_minion': skeleton('undead_minion', bone='#c8c0a8', weapon_kind='sword', seed=12),
        'crypt_skeleton': skeleton('crypt_skeleton', extra=sk_helmet('#c8c8d0', '#6a1a1a'), weapon_kind='sword',
                                   eye='#ff4040', eye_glow=12, seed=14),
        'cursed_archer': skeleton('cursed_archer', bone='#c8d8e0', extra=sk_cursed, weapon_kind='bow', eye='#60e0ff',
                                  eye_glow=15, seed=15),
        'undead_zombie': zombie_like('undead_zombie', '#6a7a5a', '#4a5a6a', '#3a3a4a'),
        'crypt_ghoul': zombie_like('crypt_ghoul', '#a8a898', '#4a3a3a', '#3a2a2a', extra=ghoul_claws, hunch=True,
                                   eye='#e04040', eye_glow=12, seed=16),
        'mountain_bandit': armored('mountain_bandit', '#6a5040', '#4a3a2a', helmet='bandana', cloth='#a02020',
                                   weapon_kind='axe', seed=22),
        'dragon_cultist': armored('dragon_cultist', '#6a1010', '#c8a040', helmet='hood', cloth='#7a1010',
                                  weapon_kind='axe', eye='#ff6020', eye_glow=15, weapon_colors={'metal': '#e8b830'}, seed=23,
                                  cape='#4a0a0a'),
        'fortress_knight': armored('fortress_knight', '#8a8a94', '#5a5a64', weapon_kind='sword', shield='#6a2020', seed=24,
                                   cape='#5a1a1a'),
        'drake_guard': armored('drake_guard', '#3a1a1a', '#8a2a1a', weapon_kind='sword', eye='#ffa020', eye_glow=15,
                               horns='#d8c8a0', seed=25),
        'cursed_guardian': armored('cursed_guardian', '#2a2236', '#5a3a7a', weapon_kind='sword', shield='#3a2a4a',
                                   eye='#c060ff', eye_glow=15, cape='#3a1a5a', horns='#8a7aa0',
                                   weapon_colors={'metal': '#7a50b0'}, seed=26),
        'mountain_troll': troll(),
        'forest_wolf': quadruped('forest_wolf', fur='#8a7a6a', belly='#c8b8a0', height=14, seed=42),
        'shadow_wolf': quadruped('shadow_wolf', fur='#2a2236', belly='#4a3a5a', height=14, eye='#c060ff', eye_glow=15,
                                 seed=43, mane='#1a1424'),
        'frost_wolf': quadruped('frost_wolf', fur='#e0e8f0', belly='#ffffff', height=14, eye='#60c0ff', eye_glow=12,
                                seed=44, mane='#c8d8e8'),
        'wild_boar': quadruped('wild_boar', fur='#6a4a32', belly='#8a6a4a', height=18, body=(9, 9, 15), legs=7,
                               head=(7, 7, 6), snout=(4, 3, 3), tusks=True, ears=True, mane='#4a3020', seed=45),
        'forest_spider': spider('forest_spider'),
        'cave_spider': spider('cave_spider', body='#1a3a3a', abdomen='#14302e', marks='#40c0a0', eye='#60ff60', seed=52),
        'fire_demon': demon('fire_demon'),
        'fire_imp': demon('fire_imp', skin='#e05020', dark='#5a1a0a', wings=True, seed=62),
        'temple_wraith': wraith(),
        'dragon_whelp': dragon('dragon_whelp', scales='#b04020', wing='#6a2010', seed=82),
        'dragon_lord': dragon('dragon_lord', scales='#6a0a0a', wing='#3a0606', seed=83),
        # ----- raid: Frostgrab
        'frost_revenant': skeleton('frost_revenant', bone='#c8e0f0', extra=sk_helmet('#a8d0e8', '#4080c0'),
                                   weapon_kind='sword', eye='#60e0ff', eye_glow=15, seed=17),
        'ice_wraith': wraith('ice_wraith', robe='#a8c8e0', dark='#5a7a9a', eye='#e0ffff', claws='#ffffff', seed=72),
        'glacier_golem': troll('glacier_golem', skin='#9ac0d8', shirt='#6a8aa0', pants='#5a7a90', boots='#4a6a80',
                               belly='#c0e0f0', dark='#7aa0b8', eye='#60e0ff', eye_glow=15, seed=32, crystals='#c8f0ff'),
        'frost_king': armored('frost_king', '#a8c8e0', '#e0f0ff', weapon_kind='sword', shield='#6a9ac0',
                              eye='#60e0ff', eye_glow=15, cape='#2a4a8a', horns='#e0f8ff',
                              weapon_colors={'metal': '#c0f0ff'}, seed=27),
        # ----- raid: Leerenzitadelle
        'void_cultist': armored('void_cultist', '#2a1a3a', '#8a5ac0', helmet='hood', cloth='#3a1a5a',
                                weapon_kind='axe', eye='#c060ff', eye_glow=15, weapon_colors={'metal': '#a070e0'}, seed=28,
                                cape='#1a0a2a'),
        'shadow_knight': armored('shadow_knight', '#1a1424', '#5a3a8a', weapon_kind='sword', shield='#2a1a3a',
                                 eye='#c060ff', eye_glow=15, cape='#2a0a3a', horns='#4a3a6a',
                                 weapon_colors={'metal': '#3a2a5a'}, seed=29),
        'void_horror': demon('void_horror', skin='#3a1a5a', dark='#140820', fire='#c060ff', seed=63, flame='#7a30c0'),
        'void_queen': wraith('void_queen', robe='#2a1440', dark='#0a0414', eye='#ff60ff', claws='#e0a0ff', seed=73,
                             crown='#c060ff'),
    })
    import art_models2
    result.update(art_models2.models())
    return result

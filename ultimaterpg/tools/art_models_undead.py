"""
Imports the hand-authored "undead" Blockbench export (uploaded by the user) as nine new, fully
rigged mob models (skeleton_warrior/archer/necromancer, zombie_walker/brute/knight, ghost_spirit/
banshee/wraith).

Same approach as art_models_goblins.py: the source files use real per-face textures/UVs instead of
the palette-cell atlas the rest of art_models.py uses, so this writes model/item/rig JSON directly
in generate.py's output structure. The source rigs are much more granular (anatomical bone names)
than the goblin source, so the name->group classification vocabulary is wider.
"""
import json
import os

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, 'undead_src', 'undead')

#   source file -> existing mobs.yml/bosses.yml "model:" key the new model replaces.
# All nine reuse an existing procedural model key, so no mob/boss YAML needed to change at all -
# the plugin just gets a better-looking model under the same name it already spawns by.
VARIANTS = {
    'skeleton_warrior': 'skeleton_warrior',      # mobs.yml: skeleton_warrior (unchanged key)
    'skeleton_archer': 'crypt_skeleton',         # mobs.yml: crypt_skeleton
    'skeleton_necromancer': 'undead_minion',     # mobs.yml: undead_minion
    'zombie_walker': 'undead_zombie',            # mobs.yml: undead_zombie
    'zombie_brute': 'crypt_ghoul',               # mobs.yml: crypt_ghoul
    'zombie_knight': 'cursed_guardian',          # bosses.yml: cursed_guardian ("Der Verfluchte Wächter")
    'ghost_spirit': 'grave_ghost',               # mobs.yml: depth_grave_ghost
    'ghost_banshee': 'city_ghost',               # mobs.yml: depth_city_ghost ("Klagende Seele")
    'ghost_wraith': 'ghost_knight',              # mobs.yml: depth_ghost_knight + bosses.yml: depth_grave_warden
}

LEG_WORDS = ('leg', 'thigh', 'calf', 'shin', 'boot', 'ankle', 'knee', 'femur', 'tibia', 'fibula',
             'toe', 'greave', 'hip', 'fauld')
ARM_WORDS = ('arm', 'hand', 'finger', 'humerus', 'radius', 'elbow', 'cuff', 'gauntlet', 'pauldron',
             'shoulder', 'sleeve', 'bandage', 'chain', 'claw', 'sword', 'knife', 'dagger', 'bow',
             'xbow', 'quiver', 'arrow', 'staff', 'book', 'scythe', 'lantern', 'shield', 'club',
             'bolt', 'ribbon', 'clavicle', 'bone')
HEAD_WORDS = ('head', 'skull', 'jaw', 'brow', 'cheek', 'chin', 'nose', 'teeth', 'ear', 'hair',
              'helm', 'nasal', 'plume', 'crown', 'horn', 'hood', 'tiara', 'mantle', 'neck', 'tusk')


def _dedupe(elements):
    """Same convention as the goblin source: a repeated name is the right side first, then left."""
    counts = {}
    for e in elements:
        counts[e['name']] = counts.get(e['name'], 0) + 1
    seen = {}
    suffixes = ['_r', '_l', '_a', '_b', '_c', '_d']
    for e in elements:
        name = e['name']
        if counts[name] > 1:
            i = seen.get(name, 0)
            seen[name] = i + 1
            e['name'] = name + suffixes[min(i, len(suffixes) - 1)]
    return elements


def _center(e, axis):
    return (e['from'][axis] + e['to'][axis]) / 2.0


def _classify(name, x_center):
    tokens = name.lower().split('_')
    is_right = tokens[-1] == 'r'
    is_left = tokens[-1] == 'l'
    if any(w in tokens for w in LEG_WORDS):
        return 'leg_r' if is_right else ('leg_l' if is_left else ('leg_r' if x_center < 8 else 'leg_l'))
    if any(w in tokens for w in ARM_WORDS):
        if is_right:
            return 'arm_r'
        if is_left:
            return 'arm_l'
        return 'arm_r' if x_center >= 8 else 'arm_l'
    if any(w in tokens for w in HEAD_WORDS):
        return 'head'
    return 'body'


def _group(elements):
    groups = {g: [] for g in ('leg_r', 'leg_l', 'arm_r', 'arm_l', 'head', 'body')}
    for e in elements:
        groups[_classify(e['name'], _center(e, 0))].append(e)
    return {g: es for g, es in groups.items() if es}


def _pivot(group, elements):
    xs = [v for e in elements for v in (e['from'][0], e['to'][0])]
    zs = [v for e in elements for v in (e['from'][2], e['to'][2])]
    x = (min(xs) + max(xs)) / 2
    z = (min(zs) + max(zs)) / 2
    if group in ('leg_r', 'leg_l', 'arm_r', 'arm_l'):
        y = max(v for e in elements for v in (e['from'][1], e['to'][1]))
    elif group == 'head':
        y = min(v for e in elements for v in (e['from'][1], e['to'][1]))
    else:
        y = 8
    return [round(x, 3), round(y, 3), round(z, 3)]


def _elements_json(elements, shift_y):
    out = []
    for e in elements:
        out.append({
            'from': [round(e['from'][0], 3), round(e['from'][1] + shift_y, 3), round(e['from'][2], 3)],
            'to': [round(e['to'][0], 3), round(e['to'][1] + shift_y, 3), round(e['to'][2], 3)],
            'faces': e['faces'],
        })
    return out


def build(assets_dir, ns, feet, write_json, copy_texture):
    results = {}
    for src_name, key in VARIANTS.items():
        with open(os.path.join(SRC, 'models', 'mob', src_name + '.json'), encoding='utf-8') as f:
            data = json.load(f)
        elements = _dedupe(data['elements'])
        texture_size = data.get('texture_size', [128, 128])
        groups = _group(elements)
        top = max(v for e in elements for v in (e['from'][1], e['to'][1]))
        shift_y = feet

        tex = f'{ns}:item/mob_model/{key}'
        src_png = os.path.join(SRC, 'textures', 'mob', src_name + '.png')
        copy_texture(src_png, 'item/mob_model/' + key)

        pivots = {g: _pivot(g, es) for g, es in groups.items()}
        for g in pivots:
            pivots[g][1] += shift_y

        is_ghost = src_name.startswith('ghost')
        poses = {'idle': {}, 'walk_a': {}, 'walk_b': {}, 'attack': {}}
        if 'leg_r' in groups and 'leg_l' in groups and not is_ghost:
            poses['walk_a']['leg_r'] = ['x', 22.5, [0, 0, 0]]
            poses['walk_b']['leg_r'] = ['x', -22.5, [0, 0, 0]]
            poses['walk_a']['leg_l'] = ['x', -22.5, [0, 0, 0]]
            poses['walk_b']['leg_l'] = ['x', 22.5, [0, 0, 0]]
        if 'arm_r' in groups:
            poses['walk_a']['arm_r'] = ['x', -16, [0, 0, 0]]
            poses['walk_b']['arm_r'] = ['x', 16, [0, 0, 0]]
            poses['attack']['arm_r'] = ['x', -45, [0, 0, 0]]
        if 'arm_l' in groups:
            poses['walk_a']['arm_l'] = ['x', 16, [0, 0, 0]]
            poses['walk_b']['arm_l'] = ['x', -16, [0, 0, 0]]
        if is_ghost:
            # ghosts float: a slow bob instead of a walk cycle, no leg swing (most have no legs anyway).
            poses['walk_a']['body'] = ['x', 0, [0, 1, 0]]
            poses['walk_b']['body'] = ['x', 0, [0, -1, 0]]

        parts = list(groups.keys())
        for group, es in groups.items():
            model_json = {'textures': {'0': tex, 'particle': tex}, 'texture_size': texture_size,
                          'elements': _elements_json(es, shift_y)}
            write_json(os.path.join(assets_dir, 'models', 'mob', key, 'part', group + '.json'), model_json)
            write_json(os.path.join(assets_dir, 'items', 'mob', key, 'part', group + '.json'), {'model': {
                'type': 'minecraft:model', 'model': f'{ns}:mob/{key}/part/{group}',
                'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})

        combined = {'textures': {'0': tex, 'particle': tex}, 'texture_size': texture_size,
                    'elements': _elements_json(elements, shift_y)}
        for frame in ('idle', 'walk_a', 'walk_b', 'attack'):
            write_json(os.path.join(assets_dir, 'models', 'mob', key, frame + '.json'), combined)
            write_json(os.path.join(assets_dir, 'items', 'mob', key, frame + '.json'), {'model': {
                'type': 'minecraft:model', 'model': f'{ns}:mob/{key}/{frame}',
                'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})

        results[key] = {'height': top / 16, 'feet': feet / 16,
                        'rig': {'parts': parts, 'pivots': pivots, 'poses': poses}}
    return results

"""
Imports the hand-authored "goblin_models" Blockbench export (uploaded by the user) as five new,
fully rigged mob models (goblin_scout, goblin_brute, goblin_marksman, goblin_gunner, goblin_warlord).

The source files keep their own real textures and per-face UVs (not the palette-cell atlas the rest of
art_models.py uses), so this writes its own model/item/rig JSON directly in generate.py's output
structure instead of going through the Model class. Elements are regrouped into a small animated rig
(leg_r/leg_l/arm_r/arm_l/head/body) by name, since the source model treats each visual part (toes, straps,
a held weapon, ...) as its own element.
"""
import json
import os

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, 'goblin_src', 'goblins')

# source file -> (new model key, display height factor vs the plugin's goblin() mobs)
VARIANTS = {
    # small/large/archer reuse the existing mobs.yml model keys (goblin_scout, goblin_brute,
    # goblin_archer already exist as mobs) - these new hand-authored models simply replace the
    # plugin's own procedural ones. crossbow and king are new variants with no earlier equivalent.
    'small': 'goblin_scout',
    'large': 'goblin_brute',
    'archer': 'goblin_archer',
    'crossbow': 'goblin_gunner',
    'king': 'goblin_warlord',
}

LEG_WORDS = ('leg', 'foot', 'toe')
# names that make an element follow an arm/hand (a held weapon or shield); assigned to whichever
# arm is on the same side (x < 8 -> left, x >= 8 -> right) since these aren't duplicated per side.
ARM_WORDS = ('arm', 'hand', 'claw', 'dagger', 'bow', 'xbow', 'quiver', 'bolt', 'arrow', 'club', 'shield')
HEAD_WORDS = ('head', 'brow', 'nose', 'jaw', 'tusk', 'ear', 'horn', 'helm', 'hood', 'crown', 'cap', 'feather', 'beard')


def _dedupe(elements):
    """Blockbench allows two elements with the same name (e.g. both arms are just 'arm_upper'); the
    exporter always emits the right side first, so the first occurrence of a repeated name becomes
    '<name>_r', the second '<name>_l' (further repeats get _a, _b, ...)."""
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
    base = name.lower()
    tokens = base.split('_')
    is_right = tokens[-1] == 'r'
    is_left = tokens[-1] == 'l'
    if any(w in tokens for w in LEG_WORDS):
        return 'leg_r' if is_right else 'leg_l'
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
    """Shoulder/hip/neck joint: the top (or, for legs, the attaching end) of the group's own bounding box."""
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
    """Writes model/item files under assets_dir using the same layout generate.py uses for its own
    mob models, and returns the 'mob_models' index entries to merge in. ns: resource pack namespace
    ('ultimaterpg'). feet: the plugin's FEET constant (floor y, e.g. -16) that every model shares."""
    results = {}
    for src_name, key in VARIANTS.items():
        with open(os.path.join(SRC, 'models', 'goblin', src_name + '.json'), encoding='utf-8') as f:
            data = json.load(f)
        elements = _dedupe(data['elements'])
        texture_size = data.get('texture_size', [128, 128])
        groups = _group(elements)
        top = max(v for e in elements for v in (e['from'][1], e['to'][1]))
        shift_y = feet  # the source model's floor (y=0) lines up with the plugin's FEET (-16)

        tex = f'{ns}:item/mob_model/{key}'
        src_png = os.path.join(SRC, 'textures', 'goblin', src_name + '.png')
        copy_texture(src_png, 'item/mob_model/' + key)

        pivots = {g: _pivot(g, es) for g, es in groups.items()}
        for g in pivots:
            pivots[g][1] += shift_y

        # idle: raw pose. walk: legs and the opposite arm swing against each other. attack: the
        # weapon arm (same side as the dagger/bow/club elements, i.e. "arm_r" by convention) stabs
        # forward. Body and head stay put - a small cast of visual parts, but no rig entry means no
        # motion, which is the safe default for decorative elements of a hand-authored model.
        poses = {'idle': {}, 'walk_a': {}, 'walk_b': {}, 'attack': {}}
        if 'leg_r' in groups and 'leg_l' in groups:
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

        parts = list(groups.keys())
        for group, es in groups.items():
            model_json = {'textures': {'0': tex, 'particle': tex}, 'texture_size': texture_size,
                          'elements': _elements_json(es, shift_y)}
            write_json(os.path.join(assets_dir, 'models', 'mob', key, 'part', group + '.json'), model_json)
            write_json(os.path.join(assets_dir, 'items', 'mob', key, 'part', group + '.json'), {'model': {
                'type': 'minecraft:model', 'model': f'{ns}:mob/{key}/part/{group}',
                'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})

        # non-smooth fallback (mobs.model_animation: frames): one static combined pose for every frame.
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

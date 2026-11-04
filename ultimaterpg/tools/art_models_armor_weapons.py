"""
Imports the hand-authored "armor" Blockbench weapon export (uploaded by the user) as real 3D item
models for the nether/frost legendary sword+dagger pairs (infernal_edge/cinderfang, glacier_edge/
icicle_fang), replacing their flat procedural icon with the actual Blockbench geometry. The source
files already include full vanilla display transforms (gui/ground/fixed/handheld), so this is a
straight copy with the texture/model references rewritten into the plugin's own namespace.
"""
import json
import os

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, 'armor_src', 'armor')

# plugin item id -> source model name (assets/armor/models/set/<name>.json)
WEAPONS = {
    'infernal_edge': 'nether_sword',
    'cinderfang': 'nether_dagger',
    'glacier_edge': 'frost_sword',
    'icicle_fang': 'frost_dagger',
}


# plugin helmet item id (<kit>_helm, kit from art_armor.KITS) -> source model name
HELMETS = {
    'infernal_scourge_helm': 'nether_helmet',
    'frost_throne_helm': 'frost_helmet',
}


def build_helmets(assets_dir, ns, write_json, copy_texture):
    """Overwrites the kit's procedural 3D helmet model (written by generate.py's raid-kit loop,
    at models/item/<kit>_helm_3d.json) with the real Blockbench helmet - the icon, the flat
    inventory model and the minecraft:select item json that picks between them stay untouched."""
    for item_id, src_name in HELMETS.items():
        with open(os.path.join(SRC, 'models', 'set', src_name + '.json'), encoding='utf-8') as f:
            data = json.load(f)
        tex = f'{ns}:item/weapon3d/{src_name}'
        copy_texture(os.path.join(SRC, 'textures', 'set', src_name + '.png'), 'item/weapon3d/' + src_name)
        model_json = {'textures': {'0': tex, 'particle': tex}, 'texture_size': data.get('texture_size', [256, 256]),
                      'elements': data['elements'], 'display': data['display']}
        write_json(os.path.join(assets_dir, 'models', 'item', item_id + '_3d.json'), model_json)


def build(assets_dir, ns, write_json, copy_texture):
    """Writes model/item files for each weapon and returns the set of item ids handled (so
    generate.py's HANDHELD icon loop skips them)."""
    for item_id, src_name in WEAPONS.items():
        with open(os.path.join(SRC, 'models', 'set', src_name + '.json'), encoding='utf-8') as f:
            data = json.load(f)
        tex = f'{ns}:item/weapon3d/{src_name}'
        copy_texture(os.path.join(SRC, 'textures', 'set', src_name + '.png'), 'item/weapon3d/' + src_name)
        model_json = {'textures': {'0': tex, 'particle': tex}, 'texture_size': data.get('texture_size', [256, 256]),
                      'elements': data['elements'], 'display': data['display']}
        write_json(os.path.join(assets_dir, 'models', 'item', 'weapon3d', src_name + '.json'), model_json)
        write_json(os.path.join(assets_dir, 'items', item_id + '.json'), {'model': {
            'type': 'minecraft:model', 'model': f'{ns}:item/weapon3d/{src_name}'}})
    return set(WEAPONS.keys())

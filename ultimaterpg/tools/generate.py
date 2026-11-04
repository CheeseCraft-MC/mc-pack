"""Generates the UltimateRPG resource pack into mc-pack/ultimaterpg/ (this repo).

Run: python3 tools/generate.py
All art is drawn procedurally (see draw.py / art_items.py / art_gui.py). The plugin reads
assets/ultimaterpg/ultimaterpg_index.json to know which models and glyphs exist.

This script lives in the public `mc-pack` repo but still needs read access to the private
`CheeseCraft-plugin` repo's items.yml/skills.yml/regions.yml/config.yml (what items/skills
exist comes from the plugin, not from here) - check out both repos as siblings:

    CheeseCraft-plugin/modules/ultimaterpg/   <- plugin source (read-only for this script)
    mc-pack/ultimaterpg/                       <- this directory (written to)

Override either path with an env var if your checkout isn't laid out that way:
    ULTIMATERPG_PLUGIN_RES=/path/to/CheeseCraft-plugin/modules/ultimaterpg/src/main/resources
    ULTIMATERPG_PACK_OUT=/path/to/mc-pack/ultimaterpg
"""
import json
import os
import shutil
import sys

import yaml
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import art_gui as gui
import art_hud as hud  # noqa: E402
import art_icons2 as ic  # noqa: E402
import art_icons3 as ic3  # noqa: E402
import art_models_goblins  # noqa: E402
import art_models_undead  # noqa: E402
import art_models_armor_weapons  # noqa: E402
import art_items as it  # noqa: E402
import art_mobs as mobs  # noqa: E402
import art_models  # noqa: E402
import art_fx  # noqa: E402
import art_sounds  # noqa: E402
import art_npcs  # noqa: E402
import art_armor  # noqa: E402
import art_models_shields  # noqa: E402

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# Default assumes the sibling-checkout layout documented in the module docstring above.
_DEFAULT_PLUGIN_RES = os.path.abspath(os.path.join(
    THIS_DIR, '..', '..', '..', 'CheeseCraft-plugin', 'modules', 'ultimaterpg', 'src', 'main', 'resources'))
RES = os.environ.get('ULTIMATERPG_PLUGIN_RES', _DEFAULT_PLUGIN_RES)
OUT = os.environ.get('ULTIMATERPG_PACK_OUT', os.path.abspath(os.path.join(THIS_DIR, '..')))
if not os.path.isdir(RES):
    raise SystemExit(
        f"Plugin-Resources nicht gefunden unter {RES!r}. CheeseCraft-plugin als Sibling-Checkout "
        "anlegen oder ULTIMATERPG_PLUGIN_RES setzen (siehe Docstring am Dateianfang).")
NS = 'ultimaterpg'
PACK_VERSION = 6

ASSETS = os.path.join(OUT, 'assets', NS)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def save(canvas, rel):
    path = os.path.join(ASSETS, 'textures', rel + '.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    canvas.img.save(path)


def model_def(path, model_ref):
    write_json(os.path.join(ASSETS, 'items', path + '.json'), {'model': {'type': 'minecraft:model', 'model': model_ref}})


def simple_item(path, canvas, parent='minecraft:item/generated'):
    """Texture + model + item definition for ultimaterpg:<path>."""
    save(canvas, 'item/' + path)
    write_json(os.path.join(ASSETS, 'models', 'item', path + '.json'),
               {'parent': parent, 'textures': {'layer0': f'{NS}:item/{path}'}})
    model_def(path, f'{NS}:item/{path}')


def bow_item(item_id, factory):
    for pull in range(4):
        suffix = '' if pull == 0 else f'_pulling_{pull - 1}'
        save(factory(pull), f'item/{item_id}{suffix}')
        write_json(os.path.join(ASSETS, 'models', 'item', item_id + suffix + '.json'),
                   {'parent': 'minecraft:item/bow', 'textures': {'layer0': f'{NS}:item/{item_id}{suffix}'}})

    def m(suffix):
        return {'type': 'minecraft:model', 'model': f'{NS}:item/{item_id}{suffix}'}

    write_json(os.path.join(ASSETS, 'items', item_id + '.json'), {'model': {
        'type': 'minecraft:condition', 'property': 'minecraft:using_item',
        'on_false': m(''),
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05,
                    'entries': [{'threshold': 0.65, 'model': m('_pulling_1')},
                                {'threshold': 0.9, 'model': m('_pulling_2')}],
                    'fallback': m('_pulling_0')}}})


# ───────────────────────────── item art per RPG item id ─────────────────────────────

HANDHELD = {
    'novice_sword': lambda: it.sword('#a0784a', '#c8a070', '#6a4a2a', '#4a3020', '#8a6a3a'),
    'iron_blade': lambda: it.sword(),
    'goblin_cleaver': lambda: it.axe('#7a8a6a', '#d8e0c8', '#5a3a1e', '#5aa040'),
    'cursed_greatsword': lambda: it.sword('#5a3a7a', '#b080e0', '#2a2030', '#1a1020', '#a050ff', '#e080ff', wide=True),
    'dragonfang_blade': lambda: it.sword('#e8d8c0', '#ffffff', '#b01818', '#3a1010', '#e2b23a', '#ff4020', wide=True),
    # infernal_edge/cinderfang/glacier_edge/icicle_fang: real 3D Blockbench models (see
    # art_models_armor_weapons.WEAPONS), written separately below - not flat icons.
    'novice_mace': lambda: it.mace('#8a7a6a', '#b8a890', '#6a4a2a', spikes=False),
    'iron_morningstar': lambda: it.mace(),
    'goblin_crusher': lambda: it.mace('#6a7a5a', '#c8d0b0', '#5a3a1e', '#5aa040'),
    'bastion_hammer': lambda: it.mace('#5a6a8a', '#c0d0f0', '#3a2a1a', '#4080ff'),
    'aegis_of_dawn': lambda: it.mace('#e2c26a', '#fff4c0', '#6a3a1a', '#ff6020'),
    'permafrost_maul': lambda: it.mace('#a8d8f0', '#ffffff', '#4a6a8a', '#60e0ff'),
    'oblivion_hammer': lambda: it.mace('#2a1a3a', '#c080ff', '#140a1e', '#ff60ff'),
    'voidreaver': lambda: it.sword('#2a1a3a', '#c080ff', '#5a3a8a', '#140a1e', '#ff60ff', '#c060ff', wide=True),
    'nightfall_kris': lambda: it.dagger('#3a2a5a', '#c080ff', '#1a1028', '#0a0614', '#ff60ff', curved=True),
    'frostbinder_staff': lambda: it.staff('#c8e0f0', '#9ae8ff', '#e0f8ff', crystal=True),
    'starless_scepter': lambda: it.staff('#1a1028', '#c060ff', '#5a3a8a', crystal=True),
    'novice_dagger': lambda: it.dagger('#9a7a60', '#c0a080'),
    'twin_fang': lambda: it.dagger(gem='#3fbf5f'),
    'shadow_fang': lambda: it.dagger('#3a2a4a', '#8a6ab0', '#1a1020', '#100810', '#40ff80', curved=True),
    'wraith_kris': lambda: it.dagger('#9ae8ff', '#e0faff', '#5a6a7a', '#2a3a4a', '#ffffff', curved=True),
    'novice_staff': lambda: it.staff('#8a6038', '#c8b890', '#6a4a2a'),
    'oak_staff': lambda: it.staff(orb='#7ae070', prongs='#4a6a2a'),
    'shaman_totem_staff': lambda: it.staff(orb='#e04a2a', prongs='#a08060', bone=True),
    'staff_of_whispers': lambda: it.staff('#c0c8d0', '#b060ff', '#e0e0f0', crystal=True),
    'ignaroths_scepter': lambda: it.staff('#c9a24a', '#ff6a1a', '#ffd060', flame=True),
}

# Kosmetische Waffen-Skins (cosmetics.yml, category "skins"): eigene Modelle unter ultimaterpg:<id>,
# unabhaengig von RpgItem-Definitionen - werden spielerbezogen ueber ItemManager.applyWeaponSkin() aufgelegt.
WEAPON_SKINS = {
    'skin_sword_crimson': lambda: it.sword('#8a1818', '#ff6050', '#3a1010', '#1a0808', '#c9a24a'),
    'skin_sword_azure': lambda: it.sword('#4a90d8', '#d0f0ff', '#2a4a6a', '#1a2a3a', '#b8d8f0'),
    'skin_sword_obsidian': lambda: it.sword('#1a1a22', '#6a50a0', '#0a0a10', '#050508', '#c060ff', wide=True),
    'skin_sword_void': lambda: it.sword('#140a1e', '#c060ff', '#2a1a3a', '#0a0612', '#ff60ff', '#e080ff', wide=True),
    'skin_axe_ember': lambda: it.axe('#a03018', '#ffb060', '#3a1a10', '#ff8020'),
    'skin_axe_runic': lambda: it.axe('#5a6a8a', '#c0d0f0', '#2a2a30', '#60e0ff'),
    'skin_mace_thorn': lambda: it.mace('#2a4a1a', '#8ad060', '#3a2a1a', '#60a030'),
    'skin_mace_sunforged': lambda: it.mace('#e2b23a', '#fff0a0', '#6a4a1a', '#ff8020'),
    'skin_dagger_shadow': lambda: it.dagger('#2a2030', '#8a6ab0', '#140a1e', '#0a0612', curved=True),
    'skin_dagger_venom': lambda: it.dagger('#2a4a1a', '#8ad060', '#1a2a10', '#0a1408', '#40ff80', curved=True),
    'skin_staff_arcane': lambda: it.staff('#4a3a6a', '#c060ff', '#e0c0ff', crystal=True),
    'skin_staff_bone': lambda: it.staff(orb='#e04a2a', prongs='#a08060', bone=True),
}

WEAPON_SKIN_BOWS = {
    'skin_bow_phoenix': lambda p: it.bow('#a01818', '#ffd8a0', '#ffb020', p),
}

BOWS = {
    'novice_bow': lambda p: it.bow('#8a5a2e', pull=p),
    'hunters_longbow': lambda p: it.bow('#5a3a1e', '#e8e2d0', '#c9a24a', p),
    'goblin_shortbow': lambda p: it.bow('#6a7a3a', '#d8d0b0', '#5aa040', p),
    'bone_bow': lambda p: it.bone_bow(p),
    'flameheart_bow': lambda p: it.bow('#a01818', '#ffd8a0', '#ffb020', p),
    'winters_breath': lambda p: it.bow('#a8d0e8', '#ffffff', '#60e0ff', p),
    'eventide_bow': lambda p: it.bow('#2a1a3a', '#e0c0ff', '#c060ff', p),
}

FLAT = {
    'copper_ring': lambda: it.ring('#c07040', '#e0e0e0'),
    'ring_of_wisdom': lambda: it.ring('#c0c8d0', '#3060e0'),
    'ring_of_vigor': lambda: it.ring('#c9a24a', '#e02828'),
    'goblin_tooth_amulet': lambda: it.amulet('#8a6a3a', tooth=True),
    'whisper_amulet': lambda: it.amulet('#c0c8d0', '#a050ff'),
    'cursed_idol': it.idol,
    'dragon_heart': it.heart,
    'crown_of_winter': lambda: it.ring('#c0e8ff', '#60e0ff'),
    'heart_of_the_void': lambda: it.amulet('#3a2a5a', '#ff60ff'),
    'glacial_core': lambda: it.shard('#9ae8ff'),
    'void_essence': lambda: it.shard('#c060ff'),
    'health_potion_small': lambda: it.potion('#e03030'),
    'health_potion_large': lambda: it.potion('#b00000', 'large'),
    'mana_potion_small': lambda: it.potion('#3060e0'),
    'mana_potion_large': lambda: it.potion('#1030a0', 'large'),
    'strength_elixir': lambda: it.potion('#ff8000', 'large'),
    'travel_bread': it.bread,
    'honey_cake': it.honey_cake,
    'smoked_fish': it.smoked_fish,
    'vigor_tonic': lambda: it.potion('#40d060'),
    'focus_draught': lambda: it.potion('#a060ff', 'large'),
    'wolf_pelt': it.pelt,
    'spider_silk': it.silk,
    'healing_herb': it.herb,
    'goblin_ear': it.goblin_ear,
    'boar_tusk': it.tusk,
    'bone_dust': it.dust,
    'cursed_essence': it.essence,
    'frost_shard': it.shard,
    'ember_core': it.ember,
    'dragon_scale': it.scale,
    'iron_scrap': it.scrap,
    'novice_arrows': it.arrows,
    'goblin_tracks': it.footprint,
    'lost_ring': lambda: it.ring('#e2b23a', '#ff6080'),
    'merchant_package': it.package,
    'king_crown': it.crown,
    'elder_letter': it.scroll_letter,
    'tablet_fragment': it.tablet,
    'dragon_eye': it.eye,
    'book_village_history': lambda: it.book('#3a5a2a'),
    'book_dragon_legend': lambda: it.book('#6a1a1a', rune='#ff8a3a'),
    'book_cursed_temple': lambda: it.book('#3a2a4a', rune='#c080ff'),
    'spell_tome': lambda: it.book('#2a3a6a', '#c0c8d0', '#7ae0ff', glow_rune=True),
    'skill_book': lambda: it.book('#3a1e4a', '#e2b23a', '#ffd66a', glow_rune=True),
}

# ───────────────────────────── menu layouts (must match the plugin) ─────────────────────────────

CONTENT = [r * 9 + c for r in range(1, 5) for c in range(1, 8)]

MENUS = {
    # slot 44 (admin button) deliberately has no socket: for normal players it is plain border
    'main': (5, [4, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 40], [4, 40]),
    'race_select': (6, [4, 10, 19, 28, 37, 46, 13, 22, 31, 15, 16, 24, 25, 33, 34, 42, 43, 45, 49], [4, 49]),
    'guild_banner': (6, [4] + list(range(9, 25)) + [25, 26] + list(range(27, 45)) + [45, 47, 48, 50], [4, 50]),
    'guild_members': (6, [4, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34,
                          37, 38, 39, 40, 41, 42, 43, 45, 48, 50], [4]),
    **{f'backpack_{r}': (r, list(range(r * 9)), []) for r in range(1, 7)},
    'rune_enchant': (5, [4, 19, 20, 21, 22, 23, 24, 25, 29, 31, 33, 36, 40], [4, 40]),
    'dungeon_finder': (6, [4, 10, 11, 12, 13, 14, 15, 16, 20, 22, 24, 29, 30, 31, 33, 34, 45, 49], [4, 49]),
    'character': (6, [4, 13, 21, 22, 23, 29, 30, 31, 32, 33, 10, 19, 28, 37, 16, 25, 34, 43, 42, 45, 48, 49, 50],
                  [13, 48, 49, 50]),
    'stats': (5, [4, 20, 21, 22, 23, 24, 31, 36], [4, 31]),
    'class_select': (3, [11, 12, 13, 14, 15, 22], [11, 12, 13, 14, 15]),
    'quests': (6, [0, 1, 2, 3, 4, 5, 6, 7, 8] + CONTENT + [45, 48, 49, 50], [0, 1, 2, 3, 4, 5, 6, 7, 8, 49]),
    'quest_detail': (4, [11, 13, 15, 27, 31], [13]),
    'dungeons': (5, [11, 13, 15, 21, 23, 31, 36], [21, 23, 31]),
    'dungeon_detail': (4, [4, 20, 22, 24, 27], [20, 22, 24]),
    'party': (4, [11, 12, 13, 14, 15, 27, 31], []),
    'achievements': (6, [4] + CONTENT + [45, 48, 50], [4]),
    'settings': (6, [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34,
                     37, 38, 39, 40, 41, 42, 43, 45], []),
    'character_screen': (6, [4, 20, 22, 24, 30, 31, 32, 38, 42, 45, 46, 48, 49, 50, 52, 53], [22, 48, 49, 50]),
    'confirm': (3, [11, 13, 15], [13]),
    'changelog': (6, [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 45, 48, 50, 53], []),
    'coming_soon_shop': (6, [4, 20, 21, 22, 23, 24, 30, 31, 32, 45], [4]),
    'cosmetics': (6, [4, 20, 21, 22, 23, 24, 31, 45], [4]),
    'cosmetic_list': (6, [4] + CONTENT + [45, 48, 49, 50], [4]),
    'guild': (5, [4, 20, 22, 24, 30, 32, 36], [4]),
    'guild_board': (6, [4, 20, 21, 22, 23, 24, 29, 30, 31, 32, 33, 45], [20, 21, 22, 23, 24]),
    'guild_trials': (5, [4, 19, 20, 21, 22, 23, 24, 25, 36], [4]),
    'guild_ranking': (6, [4, 10, 11, 12, 19, 20, 21, 28, 29, 30, 37, 14, 15, 16, 23, 24, 25, 32, 33, 34, 43, 45], [4]),
    'player_guild': (6, [2, 4, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43,
                         45, 6, 47, 48, 49, 50], [4]),
    'profile': (6, [13, 19, 28, 37, 46, 29, 31, 38, 39, 40, 24, 25, 45, 49, 50], [13]),
    # codex: one background per tab, the highlighted socket marks the open tab
    'codex_regions': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [1]),
    'codex_bestiary': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [2]),
    'codex_bosses': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [3]),
    'codex_dungeons': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [5]),
    'codex_depths': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [6]),
    'codex_runes': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [7]),
    'codex_races': (6, [1, 2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 45], [8]),
    'help': (3, [10, 11, 12, 13, 14, 15, 16, 18], []),
    'keybinds': (3, [4, 10, 11, 12, 13, 14, 15, 16, 22], [10, 11, 12, 13, 14, 15, 16]),
    'shop': (6, [4] + CONTENT + [49], [4]),
    'equipment': (5, [4, 11, 20, 29, 38, 22, 31, 15, 24, 33, 36], [15, 24, 33]),
}

GUI_ICONS = {
    'back': gui.icon_back, 'close': gui.icon_close, 'character': gui.icon_character, 'skills': gui.icon_skills,
    'quests': gui.icon_quests, 'map': gui.icon_map, 'dungeons': gui.icon_dungeons, 'equipment': gui.icon_equipment,
    'party': gui.icon_party, 'achievements': gui.icon_achievements, 'settings': gui.icon_settings,
    'help': gui.icon_help, 'hp': gui.icon_heart, 'mana': gui.icon_mana, 'gold': gui.icon_gold,
    'progress': gui.icon_progress, 'stats': gui.icon_stats, 'attribute_points': gui.icon_plus_orb,
    'derived_stats': gui.icon_derived, 'skill_points': lambda: gui.icon_plus_orb('#4ac0e8'),
    'skill_reset': gui.icon_reset, 'skill_locked': gui.icon_lock, 'skillbar': gui.icon_skillbar,
    'connector_on': gui.icon_connector, 'filler': gui.icon_empty, 'toggle_on': lambda: gui.icon_toggle(True),
    'toggle_off': lambda: gui.icon_toggle(False), 'page_prev': gui.icon_back, 'page_next': gui.icon_next,
    'map_cell': gui.icon_empty, 'map_fog': gui.icon_fog, 'map_player': lambda: gui.icon_map_marker('player'),
    'map_quest': lambda: gui.icon_map_marker('quest'), 'map_dungeon': lambda: gui.icon_map_marker('dungeon'),
    'map_town': lambda: gui.icon_map_marker('town'), 'map_waypoint': lambda: gui.icon_map_marker('waypoint'), 'pinned': lambda: gui.icon_map_marker('quest'),
}
GUI_ICONS.update({
    'logo': ic.crown, 'play': ic.play, 'changelog': ic.quill, 'news': ic.bell, 'cosmetics': ic.particles,
    'shop': ic.gem_bag, 'guild': lambda: ic.banner('#e8e0d0', '#c9a24a'), 'player_guild': ic.banner,
    'board': ic.board, 'trial': ic.helmet, 'ranking': ic.trophy, 'ranks': ic.ladder, 'goal': ic.target,
    'color': ic.dye, 'invite': ic.quill, 'codex': ic.tome, 'codex_regions': gui.icon_map,
    'codex_bestiary': ic.beast, 'codex_bosses': ic.skull, 'codex_dungeons': ic.portal, 'keybinds': ic.keycap,
    'cosmetic_titles': lambda: ic.crown('#c0c0d0'), 'cosmetic_particles': ic.particles, 'cosmetic_capes': ic.cape,
    'cosmetic_pets': ic.paw, 'cosmetic_emotes': ic.firework, 'cosmetic_skins': ic.sword_skin,
    'cosmetic_name_colors': ic.dye, 'class_change': ic.class_swap, 'character_reset': ic.character_delete,
    'confirm_yes': ic.confirm_yes, 'confirm_no': ic.confirm_no, 'dungeon_finder': ic.finder,
    'backpack': ic.backpack, 'role_tank': lambda: ic.role('tank'), 'role_healer': lambda: ic.role('healer'), 'role_damage': lambda: ic.role('damage'),
    'rune_bind': ic.rune_bind, 'rune_weapon': ic.rune_weapon, 'rune_tier_locked': lambda: ic.rune_tier(0),
    **{f'rune_tier_{t}': (lambda t: (lambda: ic.rune_tier(t)))(t) for t in (1, 2, 3)},
    **{f'rune_{k}': (lambda k: (lambda: ic.rune_stone(k)))(k) for k in ic.RUNE_COLORS},
})
GUI_ICONS.update(ic3.icons())
for tab in ('active', 'main', 'side', 'class', 'dungeon', 'guild', 'daily', 'available', 'completed'):
    GUI_ICONS['tab_' + tab] = (lambda t: (lambda: gui.icon_tab(t)))(tab)
for cls in ('warrior', 'mage', 'assassin', 'archer', 'guardian'):
    GUI_ICONS['class_' + cls] = (lambda c: (lambda: gui.icon_class(c)))(cls)
for diff in ('normal', 'hard', 'nightmare', 'mythic'):
    GUI_ICONS['difficulty_' + diff] = (lambda d: (lambda: gui.icon_difficulty(d)))(diff)


def load(name):
    with open(os.path.join(RES, name), encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(ASSETS)
    items_yml = load('items.yml')['items']
    skills_yml = load('skills.yml')['skills']
    regions_yml = load('regions.yml')['regions']
    config_yml = load('config.yml')

    index = {'version': PACK_VERSION, 'items': [], 'gui_icons': [], 'skills': [], 'tooltip_styles': [],
             'gui_backgrounds': {}, 'glyphs': {}}

    # ── RPG items
    def _copy_texture(src_png, rel):
        img = Image.open(src_png).convert('RGBA')
        save(type('C', (), {'img': img}), rel)

    weapon3d_ids = art_models_armor_weapons.build(ASSETS, NS, write_json, _copy_texture)
    for item_id in items_yml:
        if item_id in weapon3d_ids:
            index['items'].append(item_id)
            continue
        if item_id in HANDHELD:
            simple_item(item_id, HANDHELD[item_id](), 'minecraft:item/handheld')
        elif item_id in BOWS:
            bow_item(item_id, BOWS[item_id])
        elif item_id in FLAT:
            simple_item(item_id, FLAT[item_id]())
        else:
            continue
        index['items'].append(item_id)
    # ── raid kits: icons, own armor layers (equipment assets) and 3D helmets worn on the head
    index['equipment'] = []
    index['head_models'] = []
    for kit in art_armor.KITS:
        save(art_armor.layer(kit), 'entity/equipment/humanoid/' + kit)
        save(art_armor.leggings_layer(kit), 'entity/equipment/humanoid_leggings/' + kit)
        write_json(os.path.join(ASSETS, 'equipment', kit + '.json'), {'layers': {
            'humanoid': [{'texture': f'{NS}:{kit}'}], 'humanoid_leggings': [{'texture': f'{NS}:{kit}'}]}})
        index['equipment'].append(kit)
        save(art_armor.helmet_texture(kit), 'item/armor3d/' + kit)
        for piece in art_armor.PIECES:
            item_id = f'{kit}_{piece}'
            if item_id not in items_yml:
                continue
            if piece != 'helm':
                simple_item(item_id, art_armor.icon(kit, piece))
            else:
                save(art_armor.icon(kit, piece), 'item/' + item_id)
                write_json(os.path.join(ASSETS, 'models', 'item', item_id + '.json'),
                           {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{item_id}'}})
                write_json(os.path.join(ASSETS, 'models', 'item', item_id + '_3d.json'),
                           art_armor.helmet_model(kit, f'{NS}:item/armor3d/{kit}'))
                write_json(os.path.join(ASSETS, 'items', item_id + '.json'), {'model': {
                    'type': 'minecraft:select', 'property': 'minecraft:display_context',
                    'cases': [{'when': 'head', 'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{item_id}_3d'}}],
                    'fallback': {'type': 'minecraft:model', 'model': f'{NS}:item/{item_id}'}}})
                index['head_models'].append(item_id)
            index['items'].append(item_id)
    art_models_armor_weapons.build_helmets(ASSETS, NS, write_json, _copy_texture)

    missing = [i for i in list(HANDHELD) + list(BOWS) + list(FLAT) if i not in items_yml]
    if missing:
        print('note: art without item definition:', missing)

    # ── cosmetic weapon skins (not RpgItems - standalone models applied player-side on top of a weapon)
    for skin_id, factory in WEAPON_SKINS.items():
        simple_item(skin_id, factory(), 'minecraft:item/handheld')
        index['items'].append(skin_id)
    for skin_id, factory in WEAPON_SKIN_BOWS.items():
        bow_item(skin_id, factory)
        index['items'].append(skin_id)

    # ── cosmetic shield designs: real 3D silhouettes (spikes, jagged rims, wings), not re-textures.
    # Registered as their own item ids (same as WEAPON_SKINS above) so the plugin can point an
    # equipped shield's `minecraft:item_model` component at one of them (ItemMeta.setItemModel) -
    # the shield stays a real minecraft:shield (blocking, banners, durability all untouched) and
    # just the client-rendered model is swapped, exactly like applyWeaponSkin() does for weapons.
    shield_design_ids = art_models_shields.build(ASSETS, NS, write_json, save)
    for design_id in shield_design_ids:
        item_id = 'shield3d/' + design_id
        model_def(item_id, f'{NS}:item/shield3d/{design_id}')
        index['items'].append(item_id)

    # ── menu icons
    for key, factory in GUI_ICONS.items():
        simple_item('gui/' + key, factory())
        index['gui_icons'].append(key)

    # ── mob head skins (worn as player heads with a skin patch)
    index['mob_heads'] = []
    for key, factory in mobs.MOB_HEADS.items():
        save(factory(), 'entity/mob/' + key)
        index['mob_heads'].append(key)

    # ── NPC skins (mannequins with a skin patch; entity textures, no atlas needed)
    index['npc_skins'] = {}
    for key, (skin_img, slim, cape_img) in art_npcs.skins().items():
        save(type('C', (), {'img': skin_img}), 'entity/npc/' + key)
        if cape_img is not None:
            save(type('C', (), {'img': cape_img}), 'entity/npc/' + key + '_cape')
        index['npc_skins'][key] = {'slim': slim, 'cape': cape_img is not None}

    # ── 3D mob models (item models shown by an item display that follows the invisible mob)
    index['mob_models'] = {}
    for key, model in art_models.models().items():
        tex = f'{NS}:item/mob_model/{key}'   # item model textures must be in the block/item atlas
        save(type('C', (), {'img': model.texture()}), 'item/mob_model/' + key)
        for frame in art_models.FRAMES:
            write_json(os.path.join(ASSETS, 'models', 'mob', key, frame + '.json'), model.json(frame, tex))
            write_json(os.path.join(ASSETS, 'items', 'mob', key, frame + '.json'), {'model': {
                'type': 'minecraft:model', 'model': f'{NS}:mob/{key}/{frame}',
                'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})
        # parts for the smooth rig: every group as its own model, rotated by the plugin with interpolation
        for part in model.groups():
            write_json(os.path.join(ASSETS, 'models', 'mob', key, 'part', part.lower() + '.json'), model.part_json(part, tex))
            write_json(os.path.join(ASSETS, 'items', 'mob', key, 'part', part.lower() + '.json'), {'model': {
                'type': 'minecraft:model', 'model': f'{NS}:mob/{key}/part/{part.lower()}',
                'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})
        index['mob_models'][key] = {'height': model.height / 16, 'feet': art_models.FEET / 16, 'rig': model.rig()}

    # ── hand-authored goblin variants (uploaded Blockbench export): real textures, regrouped rig
    index['mob_models'].update(art_models_goblins.build(ASSETS, NS, art_models.FEET, write_json, _copy_texture))
    index['mob_models'].update(art_models_undead.build(ASSETS, NS, art_models.FEET, write_json, _copy_texture))

    # ── sounds: synthesised mob voices and the guild city theme (sounds.json + Ogg Vorbis)
    sounds_json = {}
    index['mob_voices'] = []
    for voice, kinds in art_sounds.mob_sounds().items():
        for kind, samples in kinds.items():
            art_sounds.encode(samples, os.path.join(ASSETS, 'sounds', 'mob', voice, kind + '.ogg'))
            sounds_json[f'mob.{voice}.{kind}'] = {'sounds': [{'name': f'{NS}:mob/{voice}/{kind}'}],
                                                    'subtitle': f'subtitles.{NS}.mob.{voice}.{kind}'}
        index['mob_voices'].append(voice)
    art_sounds.encode(art_sounds.guild_theme(), os.path.join(ASSETS, 'sounds', 'music', 'guild_city.ogg'), 5)
    sounds_json['music.guild_city'] = {'sounds': [{'name': f'{NS}:music/guild_city', 'stream': True}]}
    art_sounds.encode(art_sounds.dwarf_theme(), os.path.join(ASSETS, 'sounds', 'music', 'dwarf_city.ogg'), 5)
    sounds_json['music.dwarf_city'] = {'sounds': [{'name': f'{NS}:music/dwarf_city', 'stream': True}]}
    index['music'] = ['guild_city', 'dwarf_city']
    write_json(os.path.join(ASSETS, 'sounds.json'), sounds_json)
    names = {'goblin': 'Goblin', 'troll': 'Troll', 'wolf': 'Wolf', 'shadow_wolf': 'Schattenwolf', 'frost_wolf': 'Frostwolf',
             'undead': 'Untoter', 'frost_undead': 'Frostuntoter', 'wraith': 'Geist', 'ice_wraith': 'Eisgeist',
             'void_wraith': 'Leerenwesen', 'demon': 'Dämon', 'void_demon': 'Leerenschrecken', 'dragon': 'Drache',
             'golem': 'Koloss'}
    verbs = {'idle': {'de': 'murmelt', 'en': 'mutters'}, 'hurt': {'de': 'wird verletzt', 'en': 'hurts'},
             'death': {'de': 'stirbt', 'en': 'dies'}, 'attack': {'de': 'greift an', 'en': 'attacks'}}
    for lang in ('de', 'en'):
        texts = {f'subtitles.{NS}.mob.{v}.{k}': f'{names.get(v, v)} {verbs[k][lang]}'
                 for v in index['mob_voices'] for k in verbs}
        for file in (('de_de',) if lang == 'de' else ('en_us', 'en_gb')):
            write_json(os.path.join(ASSETS, 'lang', file + '.json'), texts)

    # ── skill animation effects: flat glowing planes, tinted by the plugin (fx/<shape>)
    index['fx'] = []
    for shape, painter in art_fx.SHAPES.items():
        save(type('C', (), {'img': painter()}), 'item/fx/' + shape)
        write_json(os.path.join(ASSETS, 'models', 'fx', shape + '.json'), art_fx.plane_model(f'{NS}:item/fx/{shape}'))
        write_json(os.path.join(ASSETS, 'items', 'fx', shape + '.json'), {'model': {
            'type': 'minecraft:model', 'model': f'{NS}:fx/{shape}',
            'tints': [{'type': 'minecraft:custom_model_data', 'index': 0, 'default': 16777215}]}})
        index['fx'].append(shape)

    # ── skill emblems (normal, locked, maxed)
    for skill_id, skill in skills_yml.items():
        base, locked, maxed = gui.skill_variants(skill)
        simple_item('skill/' + skill_id, base)
        simple_item('skill/' + skill_id + '_locked', locked)
        simple_item('skill/' + skill_id + '_max', maxed)
        index['skills'].append(skill_id)

    # ── tooltip styles per rarity
    for rarity in gui.RARITY_COLORS:
        base = os.path.join(ASSETS, 'textures', 'gui', 'sprites', 'tooltip')
        os.makedirs(base, exist_ok=True)
        gui.tooltip_background().img.save(os.path.join(base, rarity + '_background.png'))
        gui.tooltip_frame(rarity).img.save(os.path.join(base, rarity + '_frame.png'))
        meta = {'gui': {'scaling': {'type': 'nine_slice', 'width': 27, 'height': 27, 'border': 9}}}
        write_json(os.path.join(base, rarity + '_background.png.mcmeta'), meta)
        write_json(os.path.join(base, rarity + '_frame.png.mcmeta'), meta)
        index['tooltip_styles'].append(rarity)

    # ── menu backgrounds (font glyphs placed in the inventory title)
    providers = [{'type': 'space', 'advances': {'': -8, '': -169}}]
    code = 0xE100
    backgrounds = {}
    regions = []
    for r in regions_yml.values():
        regions.append({'min': r['min'], 'max': r['max'], 'terrain': r.get('terrain', 'WILDS'),
                        'priority': r.get('priority', 0)})
    design = config_yml['world_design']
    roads = [road['points'] for road in design['roads']]
    sites = [(s['x'], s['z'], s['radius'] >= 30) for s in design['sites'].values()]
    class_ids = sorted({s.get('class') for s in skills_yml.values()})
    # one set of menus per class theme ("main@mage"), the neutral set ("main") for players without a class
    for theme in [None] + class_ids:
        gui.set_theme(theme)
        suffix = '' if theme is None else '@' + theme
        for key, (rows, sockets, special) in MENUS.items():
            backgrounds[key + suffix] = (rows, gui.panel(rows, sockets, special, seed=code))
        backgrounds['map' + suffix] = (6, gui.map_background(regions, roads, sites, design['border']))
        if theme is not None:
            tree = {sid: s for sid, s in skills_yml.items() if s.get('class') == theme}
            nodes = [(s['slot'], s.get('ultimate', False)) for s in tree.values()]
            links = []
            for s in tree.values():
                for req in (s.get('requires') or {}):
                    if req in tree:
                        links.append((tree[req]['slot'], s['slot']))
            backgrounds['skills_' + theme] = (6, gui.skilltree(nodes, links))
    gui.set_theme(None)
    # plain 128x128 picture for the in-game map item (lives in the plugin jar, not in the pack)
    world_map = gui.world_map_image(regions, roads, sites, design['border'])
    os.makedirs(os.path.join(RES, 'map'), exist_ok=True)
    world_map.img.save(os.path.join(RES, 'map', 'world_map.png'))
    for key, (rows, canvas) in backgrounds.items():
        save(canvas, f'gui/bg_{key.replace("@", "_")}')
        char = chr(code)
        code += 1
        providers.append({'type': 'bitmap', 'file': f'{NS}:gui/bg_{key.replace("@", "_")}.png', 'ascent': 13,
                          'height': gui.gui_height(rows), 'chars': [char]})
        index['gui_backgrounds'][key] = char
        if key.split('@')[0] in MENUS:
            index.setdefault('gui_sockets', {})[key.split('@')[0]] = MENUS[key.split('@')[0]][1]
    write_json(os.path.join(ASSETS, 'font', 'gui.json'), {'providers': providers})
    index['space_before'] = ''
    index['space_after'] = ''

    # ── icon font: quest markers, HUD symbols, XP bar
    icon_providers = []
    glyphs = {}

    def glyph(name, canvas, ascent, height):
        char = chr(0xE000 + len(glyphs) + 1)
        save(canvas, f'font/{name}')
        icon_providers.append({'type': 'bitmap', 'file': f'{NS}:font/{name}.png', 'ascent': ascent,
                               'height': height, 'chars': [char]})
        glyphs[name] = char

    for kind in ('new', 'active', 'ready'):
        glyph('marker_' + kind, gui.marker(kind), 16, 20)
    for kind in ('heart', 'mana', 'coin', 'shield', 'level', 'sword'):
        glyph(kind, gui.hud_glyph(kind), 8, 9)
    glyph('xp_full', gui.xp_segment(True), 7, 7)
    glyph('xp_empty', gui.xp_segment(False), 7, 7)
    # unit frame bars (scoreboard): segments are joined with a -1 space
    for kind in ('hp', 'mana', 'shield'):
        glyph(f'bar_{kind}_full', gui.bar_segment(kind, 'full'), 7, 8)
    glyph('bar_empty', gui.bar_segment('hp', 'empty'), 7, 8)
    glyph('bar_left', gui.bar_segment('hp', 'left'), 7, 8)
    glyph('bar_right', gui.bar_segment('hp', 'right'), 7, 8)
    icon_providers.append({'type': 'space', 'advances': {'\uf803': -1}})
    index['space_join'] = '\uf803'
    write_json(os.path.join(ASSETS, 'font', 'icons.json'), {'providers': icon_providers})
    index['glyphs'] = glyphs

    # ── HUD font: skill bar next to the hotbar and the main actionbar line, positioned with space glyphs
    hud_providers = []
    hud_glyphs = {}
    advances = {}
    for k in range(10):
        advances[chr(0xF810 + k)] = -(2 ** k)
        advances[chr(0xF830 + k)] = 2 ** k
    hud_providers.append({'type': 'space', 'advances': advances})

    def hud_glyph(name, canvas, ascent):
        img = canvas.img
        # make the advance deterministic: the client measures the rightmost non-transparent column
        if img.getpixel((img.width - 1, img.height - 1))[3] == 0:
            img.putpixel((img.width - 1, img.height - 1), (0, 0, 0, 1))
        char = chr(0xE200 + len(hud_glyphs))
        save(canvas, f'hud/{name.lower()}')
        hud_providers.append({'type': 'bitmap', 'file': f'{NS}:hud/{name.lower()}.png', 'ascent': ascent,
                              'height': img.height, 'chars': [char]})
        hud_glyphs[name] = {'char': char, 'width': img.width}

    # vertical placement: the actionbar line starts 72 px above the bottom, the hotbar 22 px
    hud_glyph('slot', hud.slot_frame(), -43)
    hud_glyph('slot_empty', hud.empty_slot(), -46)
    for step in range(1, 9):
        hud_glyph(f'cd_{step}', hud.cooldown(step), -46)
    hud_glyph('no_mana', hud.no_mana(), -46)
    hud_glyph('slot_bag', hud.bag_frame(), -43)
    hud_glyph('bag', hud.bag_icon(), -46)
    for skill_id, skill in skills_yml.items():
        base, _, _ = gui.skill_variants(skill)
        hud_glyph('sk_' + skill_id, hud.icon16(base.img), -46)
    for key, label in (('SWAP', 'F'), ('SNEAK_SWAP', '^F'), ('DROP', 'Q'), ('SNEAK_DROP', '^Q'),
                       ('SNEAK_RIGHT', '^R'), ('SNEAK_LEFT', '^L'), ('HOTBAR_6', '6'), ('HOTBAR_7', '7'),
                       ('HOTBAR_8', '8'), ('HOTBAR_9', '9')):
        hud_glyph('key_' + key, hud.key_label(label), -57)
    for ch in '0123456789ms':
        hud_glyph('d_' + ch, hud.digit(ch), 7)
    for i in range(8):
        hud_glyph(f'nav_{i}', hud.arrow(i), 8)
    hud_glyph('nav_here', hud.arrived(), 8)
    hud_glyph('level', gui.hud_glyph('level'), 8)
    hud_glyph('xp_full', gui.xp_segment(True), 7)
    hud_glyph('xp_empty', gui.xp_segment(False), 7)
    write_json(os.path.join(ASSETS, 'font', 'hud.json'), {'providers': hud_providers})
    index['hud'] = hud_glyphs

    # ── vanilla hearts hidden: the unit frame in the scoreboard shows HP instead
    heart_dir = os.path.join(OUT, 'assets', 'minecraft', 'textures', 'gui', 'sprites', 'hud', 'heart')
    os.makedirs(heart_dir, exist_ok=True)
    heart_names = ['container', 'container_blinking', 'container_hardcore', 'container_hardcore_blinking',
                   'vehicle_container', 'vehicle_full', 'vehicle_half']
    for prefix in ('', 'absorbing_', 'frozen_', 'poisoned_', 'withered_'):
        for hardcore in ('', 'hardcore_'):
            for part in ('full', 'half'):
                for blink in ('', '_blinking'):
                    heart_names.append(f'{prefix}{hardcore}{part}{blink}')
    empty = gui.transparent(9, 9)
    for name in heart_names:
        empty.img.save(os.path.join(heart_dir, name + '.png'))
    index['hidden_hearts'] = True

    # ── book screen (vanilla texture override)
    book_path = os.path.join(OUT, 'assets', 'minecraft', 'textures', 'gui', 'book.png')
    os.makedirs(os.path.dirname(book_path), exist_ok=True)
    gui.book_texture().img.save(book_path)

    # ── pack metadata
    write_json(os.path.join(OUT, 'pack.mcmeta'), {'pack': {
        'description': '§6UltimateRPG §7- Menüs, Icons, Waffen & HUD',
        'min_format': [97, 0], 'max_format': [97, 1]}})
    gui.pack_icon().img.save(os.path.join(OUT, 'pack.png'))
    write_json(os.path.join(ASSETS, 'ultimaterpg_index.json'), index)
    count = sum(len(files) for _, _, files in os.walk(OUT))
    print(f'generated {count} files: {len(index["items"])} items, {len(index["gui_icons"])} menu icons, '
          f'{len(index["skills"])} skills, {len(index["gui_backgrounds"])} menu backgrounds, {len(glyphs)} glyphs')


if __name__ == '__main__':
    main()

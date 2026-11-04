"""Checks the generated resource pack for the mistakes the client would only report as purple/black
textures or a broken font: missing files, broken references, invalid names and glyph sizes.

Usage: python3 tools/validate.py [pack folder]
"""
import json
import os
import re
import sys

from PIL import Image

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    'ULTIMATERPG_PACK_OUT', os.path.join(os.path.dirname(__file__), '..'))
ASSETS = os.path.join(ROOT, 'assets')
VALID = re.compile(r'^[a-z0-9_.\-/]+$')
VANILLA = {'minecraft:item/generated', 'minecraft:item/handheld', 'item/generated', 'item/handheld',
           'minecraft:builtin/generated', 'minecraft:item/bow', 'item/bow'}
errors = []


def ref(resource, kind, ext):
    ns, _, path = resource.partition(':') if ':' in resource else ('minecraft', '', resource)
    return os.path.join(ASSETS, ns, kind, path + ext)


def load(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError) as ex:
        errors.append(f'{path}: {ex}')
        return None


def models_in(node):
    """All 'model' references of an item model definition (1.21.4+ format)."""
    if isinstance(node, dict):
        if node.get('type') in ('minecraft:model', 'model') and 'model' in node:
            yield node['model']
        for value in node.values():
            yield from models_in(value)
    elif isinstance(node, list):
        for value in node:
            yield from models_in(value)


def main():
    meta = load(os.path.join(ROOT, 'pack.mcmeta'))
    if meta is not None and ('min_format' not in meta.get('pack', {}) or 'description' not in meta['pack']):
        errors.append('pack.mcmeta: pack.min_format/description fehlt')
    counts = {'item definitions': 0, 'models': 0, 'textures': 0, 'fonts': 0}
    for dirpath, _, files in os.walk(ASSETS):
        for name in files:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ASSETS).replace(os.sep, '/')
            if not VALID.match(rel):
                errors.append(f'{rel}: ungültiger Ressourcen-Name (nur a-z 0-9 _ . - /)')
            if name.endswith('.png'):
                counts['textures'] += 1
                with Image.open(path) as img:
                    if img.mode not in ('RGBA', 'RGB', 'P', 'LA', 'L'):
                        errors.append(f'{rel}: Bildmodus {img.mode}')
            if not name.endswith('.json'):
                if name.endswith('.mcmeta'):
                    load(path)
                continue
            data = load(path)
            if data is None:
                continue
            parts = rel.split('/')
            if len(parts) > 2 and parts[1] == 'items':
                counts['item definitions'] += 1
                for model in models_in(data.get('model')):
                    if model not in VANILLA and not os.path.exists(ref(model, 'models', '.json')):
                        errors.append(f'{rel}: Modell {model} fehlt')
            elif len(parts) > 2 and parts[1] == 'models':
                counts['models'] += 1
                parent = data.get('parent')
                if parent and parent not in VANILLA and not os.path.exists(ref(parent, 'models', '.json')):
                    errors.append(f'{rel}: Parent {parent} fehlt')
                for key, texture in (data.get('textures') or {}).items():
                    if texture.startswith('#'):
                        continue
                    if not os.path.exists(ref(texture, 'textures', '.png')):
                        errors.append(f'{rel}: Textur {texture} ({key}) fehlt')
                    path = texture.split(':', 1)[-1]
                    if not (path.startswith('item/') or path.startswith('block/')):
                        # models only find textures of the block atlas (textures/item, textures/block)
                        errors.append(f'{rel}: Textur {texture} liegt nicht unter item/ oder block/ - wird lila-schwarz')
            elif len(parts) > 2 and parts[1] == 'font':
                counts['fonts'] += 1
                seen = set()
                for provider in data.get('providers', []):
                    chars = provider.get('chars', [])
                    for char in ''.join(chars) + ''.join(provider.get('advances', {}).keys()):
                        if char in seen:
                            errors.append(f'{rel}: Zeichen U+{ord(char):04X} doppelt')
                        seen.add(char)
                    if provider.get('type') != 'bitmap':
                        continue
                    file = ref(provider['file'], 'textures', '')
                    if not os.path.exists(file):
                        errors.append(f'{rel}: Font-Bild {provider["file"]} fehlt')
                        continue
                    if provider.get('ascent', 0) > provider.get('height', 8):
                        errors.append(f'{rel}: ascent > height bei {provider["file"]}')
                    with Image.open(file) as img:
                        columns = max(len(row) for row in chars)
                        if img.width % columns or img.height % len(chars):
                            errors.append(f'{rel}: {provider["file"]} lässt sich nicht in {columns}x{len(chars)} Zeichen teilen')
    index = load(os.path.join(ASSETS, 'ultimaterpg', 'ultimaterpg_index.json'))
    if index:
        for item in index['items']:
            if not os.path.exists(os.path.join(ASSETS, 'ultimaterpg', 'items', item + '.json')):
                errors.append(f'Index: Item {item} ohne Definition')
        for icon in index['gui_icons']:
            if not os.path.exists(os.path.join(ASSETS, 'ultimaterpg', 'items', 'gui', icon + '.json')):
                errors.append(f'Index: GUI-Icon {icon} ohne Definition')
        for skill in index['skills']:
            for variant in ('', '_locked', '_max'):
                if not os.path.exists(os.path.join(ASSETS, 'ultimaterpg', 'items', 'skill', skill + variant + '.json')):
                    errors.append(f'Index: Skill-Icon {skill}{variant} fehlt')
        for style in index['tooltip_styles']:
            for part in ('background', 'frame'):
                base = os.path.join(ASSETS, 'ultimaterpg', 'textures', 'gui', 'sprites', 'tooltip', f'{style}_{part}')
                if not os.path.exists(base + '.png') or not os.path.exists(base + '.png.mcmeta'):
                    errors.append(f'Index: Tooltip {style}_{part} unvollständig')
    print('Geprüft:', ', '.join(f'{v} {k}' for k, v in counts.items()))
    if errors:
        print(f'{len(errors)} Fehler:')
        for error in errors[:60]:
            print('  -', error)
        sys.exit(1)
    print('Keine Fehler gefunden.')


if __name__ == '__main__':
    main()

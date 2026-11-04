"""Builds preview sheets of the generated pack (for checking the art)."""
import os
import sys
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEX = os.path.join(ROOT, 'src', 'main', 'resources', 'resourcepack', 'assets', 'ultimaterpg', 'textures')
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/preview'
os.makedirs(OUT, exist_ok=True)


def sheet(folder, name, scale=3, cols=12, filt=lambda f: True):
    files = sorted(f for f in os.listdir(os.path.join(TEX, folder)) if f.endswith('.png') and filt(f))
    cell = 32 * scale + 8
    rows = (len(files) + cols - 1) // cols
    img = Image.new('RGBA', (cols * cell, rows * cell), (40, 40, 48, 255))
    for i, f in enumerate(files):
        icon = Image.open(os.path.join(TEX, folder, f)).convert('RGBA')
        icon = icon.resize((icon.width * scale, icon.height * scale), Image.NEAREST)
        img.alpha_composite(icon, ((i % cols) * cell + 4, (i // cols) * cell + 4))
    img.save(os.path.join(OUT, name))


sheet('item', 'items.png', filt=lambda f: 'pulling' not in f)
sheet('item/gui', 'gui_icons.png')
sheet('item/skill', 'skills.png', cols=15, filt=lambda f: True)
bgs = sorted(f for f in os.listdir(os.path.join(TEX, 'gui')) if f.startswith('bg_'))
w = 4 * (176 * 2 + 10)
h = ((len(bgs) + 3) // 4) * (222 * 2 + 10)
img = Image.new('RGBA', (w, h), (60, 60, 70, 255))
for i, f in enumerate(bgs):
    bg = Image.open(os.path.join(TEX, 'gui', f)).convert('RGBA')
    bg = bg.resize((bg.width * 2, bg.height * 2), Image.NEAREST)
    img.alpha_composite(bg, ((i % 4) * (176 * 2 + 10), (i // 4) * (222 * 2 + 10)))
img.save(os.path.join(OUT, 'backgrounds.png'))
print('ok', OUT)

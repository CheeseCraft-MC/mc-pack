"""Small pixel-art toolkit used by the resource pack generator.

Everything in the UltimateRPG pack is drawn here from primitives, no vanilla textures are copied.
"""
import math
import random
from PIL import Image, ImageDraw

TRANSPARENT = (0, 0, 0, 0)


def hexc(value, alpha=255):
    value = value.lstrip('#')
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (a[3] if len(a) > 3 else 255,)


def lighten(c, t=0.25):
    return mix(c, (255, 255, 255, 255), t)


def darken(c, t=0.25):
    return mix(c, (0, 0, 0, 255), t)


def with_alpha(c, a):
    return c[:3] + (a,)


class Canvas:
    def __init__(self, w, h, fill=TRANSPARENT):
        self.img = Image.new('RGBA', (w, h), fill)
        self.d = ImageDraw.Draw(self.img)
        self.w, self.h = w, h

    @classmethod
    def of(cls, image):
        canvas = cls(image.width, image.height)
        canvas.img = image
        canvas.d = ImageDraw.Draw(image)
        return canvas

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((int(x), int(y)), c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.img.getpixel((int(x), int(y)))
        return TRANSPARENT

    def rect(self, x1, y1, x2, y2, c):
        self.d.rectangle([x1, y1, x2, y2], fill=c)

    def outline_rect(self, x1, y1, x2, y2, c, width=1):
        self.d.rectangle([x1, y1, x2, y2], outline=c, width=width)

    def circle(self, cx, cy, r, c):
        self.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    def ring(self, cx, cy, r, c, width=1):
        self.d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=width)

    def poly(self, points, c):
        self.d.polygon(points, fill=c)

    def line(self, x1, y1, x2, y2, c, width=1):
        """Pixel line with a square brush of the given width."""
        steps = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
        for i in range(steps + 1):
            t = i / max(1, steps)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            for ox in range(width):
                for oy in range(width):
                    self.px(round(x) + ox - width // 2, round(y) + oy - width // 2, c)

    def paste(self, other, x, y):
        self.img.alpha_composite(other.img if isinstance(other, Canvas) else other, (x, y))

    def save(self, path):
        self.img.save(path)


def finish(canvas, outline=(24, 16, 14, 255), shade=True):
    """Adds a dark outline around opaque pixels and a light/dark bevel - the classic item look."""
    img = canvas.img
    w, h = img.size
    src = img.copy()
    if shade:
        for y in range(h):
            for x in range(w):
                c = src.getpixel((x, y))
                if c[3] < 128:
                    continue
                up_left = src.getpixel((x - 1, y - 1))[3] < 128 if x > 0 and y > 0 else True
                down_right = src.getpixel((x + 1, y + 1))[3] < 128 if x < w - 1 and y < h - 1 else True
                if up_left and not down_right:
                    img.putpixel((x, y), lighten(c, 0.22))
                elif down_right and not up_left:
                    img.putpixel((x, y), darken(c, 0.22))
    if outline:
        src = img.copy()
        for y in range(h):
            for x in range(w):
                if src.getpixel((x, y))[3] >= 128:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src.getpixel((nx, ny))[3] >= 128:
                        img.putpixel((x, y), outline)
                        break
    return canvas


def noise_fill(canvas, x1, y1, x2, y2, base, amount=8, seed=1):
    rnd = random.Random(seed)
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            n = rnd.randint(-amount, amount)
            canvas.px(x, y, tuple(max(0, min(255, base[i] + n)) for i in range(3)) + (base[3],))


def sparkle(canvas, x, y, c):
    canvas.px(x, y, c)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        canvas.px(x + dx, y + dy, with_alpha(c, 170))


def grayscale(img, factor=0.55):
    out = img.copy()
    px = out.load()
    for y in range(out.size[1]):
        for x in range(out.size[0]):
            r, g, b, a = px[x, y]
            v = int((0.3 * r + 0.59 * g + 0.11 * b) * factor)
            px[x, y] = (v, v, int(v * 1.05), a)
    return out


def glow(canvas, cx, cy, r, c):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                a = int(c[3] * (1 - d / r) ** 1.5)
                if a > 0:
                    base = canvas.get(x, y)
                    if base[3] == 0:
                        canvas.px(x, y, c[:3] + (a,))
                    else:
                        canvas.px(x, y, mix(base, c, a / 255 * 0.6))

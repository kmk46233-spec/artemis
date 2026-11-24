"""Runs after `npx cap add android`: replaces the default icon, splash and bar colors."""
import glob, os, re
from PIL import Image, ImageDraw

RES = 'android/app/src/main/res'
TOP, BOT = (28, 122, 95), (10, 90, 78)

def art(size=1024):
    """Glass dome with island and a pine tree, transparent background."""
    S = 1024
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([172, 172, 852, 852], fill=(255, 255, 255, 40), outline=(255, 255, 255, 110), width=6)
    d.pieslice([262, 610, 762, 830], 0, 180, fill=(141, 103, 91, 255))
    d.ellipse([262, 600, 762, 720], fill=(122, 208, 111, 255))
    d.rectangle([488, 560, 536, 660], fill=(123, 90, 69, 255))
    for b, t, h, c in [(560, 420, 150, (60, 148, 68)), (500, 350, 125, (72, 166, 78)),
                       (440, 290, 100, (85, 181, 89)), (385, 230, 76, (99, 196, 102))]:
        d.polygon([(512, t - 60), (512 + h, b + 40), (512 - h, b + 40)], fill=c + (255,))
    return img.resize((size, size), Image.LANCZOS) if size != S else img

def gradient(size):
    bg = Image.new('RGBA', (size, size))
    bd = ImageDraw.Draw(bg)
    for y in range(size):
        t = y / max(1, size - 1)
        bd.line([(0, y), (size, y)], fill=tuple(int(TOP[i] + (BOT[i] - TOP[i]) * t) for i in range(3)) + (255,))
    return bg

def legacy(size, round_):
    S = 512
    base = gradient(S)
    mask = Image.new('L', (S, S), 0)
    md = ImageDraw.Draw(mask)
    if round_:
        md.ellipse([0, 0, S - 1, S - 1], fill=255)
    else:
        md.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)
    out.alpha_composite(art(S))
    return out.resize((size, size), Image.LANCZOS)

def foreground(size):
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    inner = int(size * 0.66)
    a = art(inner)
    off = (size - inner) // 2
    out.alpha_composite(a, (off, off))
    return out

for folder in glob.glob(os.path.join(RES, 'mipmap-*dpi')):
    if not os.path.isdir(folder):
        continue
    sz = Image.open(os.path.join(folder, 'ic_launcher.png')).size[0]
    legacy(sz, False).save(os.path.join(folder, 'ic_launcher.png'))
    legacy(sz, True).save(os.path.join(folder, 'ic_launcher_round.png'))
    fsz = Image.open(os.path.join(folder, 'ic_launcher_foreground.png')).size[0]
    foreground(fsz).save(os.path.join(folder, 'ic_launcher_foreground.png'))

with open(os.path.join(RES, 'values/ic_launcher_background.xml'), 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#14705A</color>\n</resources>\n')

for sp in glob.glob(os.path.join(RES, 'drawable*/splash.png')):
    w, h = Image.open(sp).size
    img = Image.new('RGBA', (w, h), (10, 90, 78, 255))
    s = int(min(w, h) * 0.38)
    img.alpha_composite(art(s), ((w - s) // 2, (h - s) // 2))
    img.convert('RGB').save(sp)

sx = os.path.join(RES, 'values/styles.xml')
t = open(sx, encoding='utf-8').read()
bars = '\n        <item name="android:statusBarColor">#0A5A4E</item>\n        <item name="android:navigationBarColor">#0A5A4E</item>'
t = t.replace('<item name="android:background">@null</item>', '<item name="android:background">@null</item>' + bars)
t = t.replace('<item name="android:background">@drawable/splash</item>', '<item name="android:background">@drawable/splash</item>' + bars)
open(sx, 'w', encoding='utf-8').write(t)
print('assets ok')

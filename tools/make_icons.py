"""Génère les icônes PNG de l'appli (carré rouge arrondi + flèche de téléchargement).

Usage :  pip install pillow && python tools/make_icons.py
Produit static/icon-192.png, static/icon-512.png et static/apple-touch-icon.png.
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "static"
OUT.mkdir(exist_ok=True)


def make(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=size * 0.22, fill=(230, 57, 70, 255))
    u = size / 52  # unités du logo de référence (52 px)
    w = int(4 * u)
    d.line([(26 * u, 12 * u), (26 * u, 30 * u)], fill="white", width=w)   # tige
    d.line([(18 * u, 22 * u), (26 * u, 30 * u)], fill="white", width=w)   # pointe gauche
    d.line([(34 * u, 22 * u), (26 * u, 30 * u)], fill="white", width=w)   # pointe droite
    d.rounded_rectangle([14 * u, 36 * u, 38 * u, 40 * u], radius=2 * u, fill="white")  # barre
    return img


for size, name in ((192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")):
    make(size).save(OUT / name)
    print("ok", name)

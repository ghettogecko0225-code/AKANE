"""Generate the Google Play feature graphic (1024 x 500).

    python tools/make_feature_graphic.py

Play requires a 1024 x 500 PNG or JPG with NO alpha channel, so the file is
written as plain RGB. Everything is drawn from the same brand assets as the
app icon: the navy tile, the rising sun, the 「あ」 in Noto Sans CJK JP.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "brand"
FONT = ROOT / "assets" / "fonts" / "NotoSansCJKjp-Regular.otf"

BG = (18, 20, 28, 255)
SUN = (224, 83, 61, 255)
CREAM = (242, 244, 251, 255)
DIM = (154, 163, 189, 255)

TITLE = "Benkyo Studio"
TAGLINE = "Study Japanese. Fully offline."
CHIPS = [
    "10,832 cards",
    "JLPT N5-N1",
    "Speak & get scored",
    "No ads. No account.",
]


def _font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except Exception:
        return ImageFont.load_default()


def _text(draw, xy, text, font, fill, anchor_center_x=None):
    box = draw.textbbox((0, 0), text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = xy
    if anchor_center_x is not None:
        x = anchor_center_x - tw / 2 - box[0]
    draw.text((x, y - box[1]), text, font=font, fill=fill)
    return tw, th


def make(width=1024, height=500):
    img = Image.new("RGBA", (width, height), BG)
    d = ImageDraw.Draw(img)

    # app icon mark on the left, same as the launcher icon
    tile = 210
    tx, ty = 40, (height - tile) // 2
    d.rounded_rectangle(
        [tx, ty, tx + tile, ty + tile],
        radius=34,
        fill=(28, 32, 48, 255),
        outline=(46, 53, 80, 255),
        width=2,
    )
    sun_r = 62
    cx, cy = tx + tile // 2, ty + tile // 2 - 12
    d.ellipse([cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r], fill=SUN)
    _text(d, (cx, cy + 18), "あ", _font(74), CREAM, anchor_center_x=cx)
    d.rounded_rectangle(
        [cx - 38, ty + tile - 26, cx + 38, ty + tile - 21],
        radius=2,
        fill=SUN,
    )

    # wordmark
    x = tx + tile + 44
    _text(d, (x, 148), TITLE, _font(66), CREAM)
    _text(d, (x, 228), TAGLINE, _font(31), DIM)

    # feature chips, wrapped so nothing runs off the right edge
    chip_font = _font(23)
    rows = [CHIPS[:2], CHIPS[2:]]
    chip_y = 306
    for row in rows:
        chip_x = x
        for chip in row:
            box = d.textbbox((0, 0), chip, font=chip_font)
            w = (box[2] - box[0]) + 32
            th = box[3] - box[1]
            d.rounded_rectangle(
                [chip_x, chip_y, chip_x + w, chip_y + 44],
                radius=22,
                fill=(36, 41, 61, 255),
                outline=(56, 64, 92, 255),
                width=2,
            )
            _text(d, (chip_x + 16, chip_y + (44 - th) // 2), chip, chip_font, CREAM)
            chip_x += w + 12
        chip_y += 56

    return img.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "play_feature_graphic_1024x500.png"
    make().save(path, "PNG", optimize=True)
    print("wrote", path)


if __name__ == "__main__":
    main()

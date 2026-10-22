"""Generate the app icon and splash image.

    python tools/make_brand.py

The mark: a deep navy tile with a warm rising-sun disc and the hiragana
「あ」 in a cream face - simple enough to read at 48px on a launcher.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "brand"
FONT = ROOT / "assets" / "fonts" / "NotoSansCJKjp-Regular.otf"
APP_TITLE = "AKANE"
APP_KANJI = "茜"

BG = (18, 20, 28, 255)
SUN = (224, 83, 61, 255)
CREAM = (242, 244, 251, 255)
DIM = (154, 163, 189, 255)


def _font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except Exception:
        return ImageFont.load_default()


def make_icon(size=512):
    img = Image.new("RGBA", (size, size), BG)
    d = ImageDraw.Draw(img)

    pad = int(size * 0.06)
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=int(size * 0.16),
        fill=(28, 32, 48, 255),
        outline=(46, 53, 80, 255),
        width=max(2, int(size * 0.012)),
    )

    sun_r = int(size * 0.30)
    cx, cy = int(size * 0.50), int(size * 0.42)
    d.ellipse([cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r], fill=SUN)

    f = _font(int(size * 0.42))
    text = "あ"
    box = d.textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text(
        (cx - tw / 2 - box[0], cy - th / 2 - box[1] + int(size * 0.16)),
        text,
        font=f,
        fill=CREAM,
    )

    bar_h = max(3, int(size * 0.022))
    bar_w = int(size * 0.30)
    d.rounded_rectangle(
        [cx - bar_w // 2, int(size * 0.76), cx + bar_w // 2, int(size * 0.76) + bar_h],
        radius=bar_h // 2,
        fill=SUN,
    )
    return img


def make_splash(w=1280, h=1280):
    img = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(img)
    sun_r = int(min(w, h) * 0.16)
    cx, cy = w // 2, int(h * 0.40)
    d.ellipse([cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r], fill=SUN)
    f = _font(int(min(w, h) * 0.24))
    text = "あ"
    box = d.textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((cx - tw / 2 - box[0], cy - th / 2 - box[1]), text, font=f, fill=CREAM)

    # wordmark: AKANE with its kanji
    f2 = _font(int(min(w, h) * 0.085))
    sub = APP_TITLE
    box2 = d.textbbox((0, 0), sub, font=f2)
    sub_w = box2[2] - box2[0]
    d.text(
        (cx - sub_w / 2 - box2[0], int(h * 0.58)),
        sub,
        font=f2,
        fill=CREAM,
    )

    # the kanji the name means: 茜 (crimson)
    f3 = _font(int(min(w, h) * 0.055))
    kanji = APP_KANJI
    box3 = d.textbbox((0, 0), kanji, font=f3)
    d.text(
        (cx - (box3[2] - box3[0]) / 2 - box3[0], int(h * 0.675)),
        kanji,
        font=f3,
        fill=SUN,
    )

    # the letters spelled out
    f4 = _font(int(min(w, h) * 0.032))
    line = "AI  ·  Kanji  ·  Audio  ·  Nihongo  ·  Everywhere"
    box4 = d.textbbox((0, 0), line, font=f4)
    d.text(
        (cx - (box4[2] - box4[0]) / 2 - box4[0], int(h * 0.755)),
        line,
        font=f4,
        fill=DIM,
    )
    return img



def main():
    OUT.mkdir(parents=True, exist_ok=True)
    icon = make_icon(512)
    icon.save(OUT / "icon.png")
    for size in (192, 144, 96, 72, 48):
        icon.resize((size, size), Image.LANCZOS).save(OUT / f"icon_{size}.png")
    make_splash().save(OUT / "splash.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Gera santinhos Feto 67 (frente + verso/cola) — foto antiga e foto nova."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "santinhos"
W, H = 1080, 1543  # ~7x10 cm digital

NAVY = (11, 31, 58)
NAVY_MID = (18, 48, 86)
BLUE = (27, 79, 156)
BLUE_BRIGHT = (46, 107, 199)
PAPER = (244, 247, 251)
WHITE = (255, 255, 255)
INK = (11, 31, 58)
GREEN_URN = (6, 34, 20)
GREEN_SOFT = (157, 255, 176)
GREEN_OK = (61, 154, 88)

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
FONT_BOLD = FONT_DIR / "Arial Bold.ttf"
FONT_BLACK = FONT_DIR / "Arial Black.ttf"
FONT_REG = FONT_DIR / "Arial.ttf"
FONT_NUM = FONT_DIR / "DIN Condensed Bold.ttf"
FONT_DISPLAY = FONT_DIR / "Arial Rounded Bold.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.truetype(str(FONT_BOLD), size)


def gradient_bg(top=NAVY, bottom=NAVY_MID) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return img


def cover_crop(src: Image.Image, box: tuple[int, int, int, int], focus=(0.5, 0.35)) -> Image.Image:
    """Crop-cover into box with focus (fx, fy) in 0..1 of source."""
    x0, y0, x1, y1 = box
    tw, th = x1 - x0, y1 - y0
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    left = max(0, min(cx - tw // 2, nw - tw))
    top = max(0, min(cy - th // 2, nh - th))
    cropped = resized.crop((left, top, left + tw, top + th))
    return cropped


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


def paste_photo(base: Image.Image, photo: Image.Image, box, focus, radius=28, border=8):
    x0, y0, x1, y1 = box
    inner = (x0 + border, y0 + border, x1 - border, y1 - border)
    frame = Image.new("RGB", (x1 - x0, y1 - y0), WHITE)
    base.paste(frame, (x0, y0))
    # blue outer stroke
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius + 4, outline=BLUE_BRIGHT, width=6)

    crop = cover_crop(photo, (0, 0, inner[2] - inner[0], inner[3] - inner[1]), focus)
    mask = rounded_mask(crop.size, radius)
    base.paste(crop, (inner[0], inner[1]), mask)


def text_center(draw, text, y, fnt, fill=WHITE, max_w=None):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if max_w and tw > max_w:
        # shrink somehow — caller should pick size
        pass
    draw.text((x, y), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def wrap_center(draw, text, y, fnt, fill, max_w, line_gap=8):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    cy = y
    for line in lines:
        text_center(draw, line, cy, fnt, fill)
        cy += draw.textbbox((0, 0), line, font=fnt)[3] + line_gap
    return cy


def make_frente(photo_path: Path, out_path: Path, *, nova: bool, focus):
    photo = Image.open(photo_path).convert("RGB")
    img = gradient_bg(NAVY, (10, 39, 72))
    draw = ImageDraw.Draw(img)

    # top bar
    draw.rectangle((0, 0, W, 110), fill=BLUE)
    f_small = font(FONT_BOLD, 34)
    text_center(draw, "PAUPITEIROS  ·  ADMINISTRADOR", 38, f_small, WHITE)

    # photo area
    margin = 70
    photo_top = 150
    photo_h = 820 if not nova else 760
    paste_photo(
        img,
        photo,
        (margin, photo_top, W - margin, photo_top + photo_h),
        focus=focus,
        radius=32,
        border=10,
    )

    # name block
    y = photo_top + photo_h + 40
    f_name = font(FONT_BLACK, 92)
    text_center(draw, "FETO", y, f_name, WHITE)
    y += 100
    f_sub = font(FONT_REG, 36)
    text_center(draw, "Ruan Ranison", y, f_sub, (200, 220, 245))
    y += 55

    # number badge
    badge_w, badge_h = 280, 140
    bx = (W - badge_w) // 2
    by = y + 10
    draw.rounded_rectangle((bx, by, bx + badge_w, by + badge_h), radius=24, fill=BLUE_BRIGHT)
    f_num = font(FONT_NUM, 120)
    nb = draw.textbbox((0, 0), "67", font=f_num)
    draw.text(
        (bx + (badge_w - (nb[2] - nb[0])) // 2, by + (badge_h - (nb[3] - nb[1])) // 2 - 8),
        "67",
        font=f_num,
        fill=WHITE,
    )

    y = by + badge_h + 28
    if nova:
        f_vice = font(FONT_BOLD, 28)
        y = wrap_center(
            draw,
            "Chapa: Doson's de Oliveira Vitor  ·  José Marcos Correia dos Santos",
            y,
            f_vice,
            (180, 210, 245),
            W - 100,
            line_gap=6,
        )
        y += 8
        f_slog = font(FONT_BOLD, 30)
        wrap_center(draw, "Fim da 424  ·  Nova era da 924", y, f_slog, GREEN_SOFT, W - 120)
    else:
        f_slog = font(FONT_BOLD, 32)
        text_center(draw, "Presença, regra e grupo", y, f_slog, (180, 210, 245))

    # bottom strip
    draw.rectangle((0, H - 70, W, H), fill=BLUE_BRIGHT)
    text_center(draw, "VOTE  67", H - 52, font(FONT_BLACK, 36), WHITE)

    img.save(out_path, "PNG", optimize=True)
    print("wrote", out_path)


def make_verso(out_path: Path, *, nova: bool):
    img = gradient_bg(GREEN_URN, (8, 50, 30))
    draw = ImageDraw.Draw(img)

    # header COLA
    draw.rounded_rectangle((60, 80, W - 60, 220), radius=20, fill=(10, 60, 35))
    f_cola = font(FONT_BLACK, 96)
    text_center(draw, "COLA", 105, f_cola, GREEN_SOFT)

    f_hint = font(FONT_BOLD, 32)
    text_center(draw, "Na urna, digite o número", 250, f_hint, (180, 240, 190))

    # huge number
    f_huge = font(FONT_NUM, 420)
    nb = draw.textbbox((0, 0), "67", font=f_huge)
    tw, th = nb[2] - nb[0], nb[3] - nb[1]
    # soft glow plate
    plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle(
        ((W - tw) // 2 - 40, 340, (W + tw) // 2 + 40, 340 + th + 60),
        radius=36,
        fill=(255, 255, 255, 28),
    )
    img = Image.alpha_composite(img.convert("RGBA"), plate).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text(((W - tw) // 2, 360), "67", font=f_huge, fill=WHITE)

    y = 360 + th + 50
    f_name = font(FONT_BLACK, 64)
    text_center(draw, "FETO", y, f_name, GREEN_SOFT)
    y += 80
    f_sub = font(FONT_REG, 34)
    text_center(draw, "Ruan Ranison", y, f_sub, (200, 235, 210))
    y += 60

    if nova:
        f_v = font(FONT_BOLD, 30)
        y = wrap_center(
            draw,
            "Vices: Doson's de Oliveira Vitor  ·  José Marcos Correia dos Santos",
            y,
            f_v,
            (190, 230, 200),
            W - 100,
        )
        y += 20
        f_s = font(FONT_BLACK, 36)
        wrap_center(draw, "Fim da 424 no poder. Nova era da 924.", y, f_s, WHITE, W - 100)
    else:
        f_s = font(FONT_BOLD, 34)
        wrap_center(
            draw,
            "Administrador do Paupiteiros. Presença, regra e grupo.",
            y,
            f_s,
            (200, 235, 210),
            W - 100,
        )

    # footer
    draw.rectangle((0, H - 90, W, H), fill=GREEN_OK)
    text_center(draw, "CONFIRMA  ·  VOTE 67", H - 62, font(FONT_BLACK, 38), WHITE)

    img.save(out_path, "PNG", optimize=True)
    print("wrote", out_path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    antiga = ROOT / "assets" / "feto-antiga.jpg"
    nova = ROOT / "assets" / "feto.jpg"

    make_frente(
        antiga,
        OUT / "santinho-foto-antiga-frente.png",
        nova=False,
        focus=(0.50, 0.38),
    )
    make_verso(OUT / "santinho-foto-antiga-verso.png", nova=False)

    make_frente(
        nova,
        OUT / "santinho-foto-nova-frente.png",
        nova=True,
        focus=(0.70, 0.28),
    )
    make_verso(OUT / "santinho-foto-nova-verso.png", nova=True)


if __name__ == "__main__":
    main()

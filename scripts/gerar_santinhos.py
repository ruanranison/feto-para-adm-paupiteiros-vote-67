#!/usr/bin/env python3
"""
Santinhos eleitorais Feto 67 — padrão clássico brasileiro 7×10.
Frente e verso com a mesma identidade visual (azul campanha).
Referências: TSE (cola), Expo/Printi/Alvo (santinho 7×10, foto + número).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "santinhos"
W, H = 1080, 1543  # ~7×10 cm @ ~390 dpi

# Identidade da campanha (frente = verso)
NAVY = (11, 31, 58)
BLUE = (27, 79, 156)
BLUE_BRIGHT = (46, 107, 199)
BLUE_BAND = (37, 94, 180)
PAPER = (247, 249, 252)
WHITE = (255, 255, 255)
MUTED = (90, 110, 140)
YELLOW = (255, 214, 10)  # destaque clássico de número em santinho BR

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
F_BLACK = FONT_DIR / "Arial Black.ttf"
F_BOLD = FONT_DIR / "Arial Bold.ttf"
F_REG = FONT_DIR / "Arial.ttf"
F_NUM = FONT_DIR / "DIN Condensed Bold.ttf"


def fnt(path: Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.truetype(str(F_BOLD), size)


def text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0]


def text_h(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    b = draw.textbbox((0, 0), text, font=font)
    return b[3] - b[1]


def center_text(draw, text, y, font, fill=WHITE):
    tw = text_w(draw, text, font)
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)


def wrap_center(draw, text, y, font, fill, max_w, gap=6):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    cy = y
    for line in lines:
        center_text(draw, line, cy, font, fill)
        cy += text_h(draw, line, font) + gap
    return cy


def face_crop(src: Image.Image, tw: int, th: int, focus=(0.5, 0.42), zoom=1.35) -> Image.Image:
    """Close crop estilo santinho: rosto grande, quase sem parede acima."""
    sw, sh = src.size
    base = max(tw / sw, th / sh) * zoom
    nw, nh = int(sw * base), int(sh * base)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    # rosto bem alto no quadro (~18% do topo)
    left = max(0, min(cx - tw // 2, nw - tw))
    top = max(0, min(cy - int(th * 0.18), nh - th))
    return resized.crop((left, top, left + tw, top + th))


def band_header(draw: ImageDraw.ImageDraw, label: str):
    """Faixa superior idêntica na frente e no verso."""
    draw.rectangle((0, 0, W, 96), fill=BLUE_BAND)
    center_text(draw, label, 28, fnt(F_BOLD, 36), WHITE)


def band_footer(draw: ImageDraw.ImageDraw, label: str):
    """Faixa inferior idêntica na frente e no verso."""
    draw.rectangle((0, H - 100, W, H), fill=BLUE_BAND)
    center_text(draw, label, H - 68, fnt(F_BLACK, 42), WHITE)


def number_badge(draw, cx, cy, size=220, digits="67"):
    """Bloco de número — elemento mais forte da peça (padrão BR)."""
    half = size // 2
    box = (cx - half - 20, cy - half + 10, cx + half + 20, cy + half - 10)
    draw.rounded_rectangle(box, radius=28, fill=YELLOW)
    draw.rounded_rectangle(box, radius=28, outline=NAVY, width=6)
    font = fnt(F_NUM, int(size * 0.95))
    tw = text_w(draw, digits, font)
    th = text_h(draw, digits, font)
    draw.text((cx - tw // 2, cy - th // 2 - 12), digits, font=font, fill=NAVY)


def make_frente(photo_path: Path, out_path: Path, *, nova: bool):
    photo = Image.open(photo_path).convert("RGB")
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    band_header(draw, "PAUPITEIROS  ·  ADMINISTRADOR")

    # Foto grande (padrão “foto grande”): quase meia peça, close no rosto
    margin = 48
    photo_top = 118
    photo_h = 720
    pw, ph = W - 2 * margin, photo_h
    if nova:
        crop = face_crop(photo, pw, ph, focus=(0.70, 0.55), zoom=1.55)
    else:
        crop = face_crop(photo, pw, ph, focus=(0.50, 0.58), zoom=1.90)

    # moldura branca + filete azul (clássico)
    frame = (margin - 8, photo_top - 8, margin + pw + 8, photo_top + ph + 8)
    draw.rounded_rectangle(frame, radius=18, fill=WHITE, outline=BLUE_BRIGHT, width=8)
    img.paste(crop, (margin, photo_top))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (margin, photo_top, margin + pw, photo_top + ph),
        radius=12,
        outline=BLUE_BRIGHT,
        width=5,
    )

    # Bloco inferior (mesmo papel do verso)
    y = photo_top + ph + 36
    center_text(draw, "FETO", y, fnt(F_BLACK, 96), NAVY)
    y += 100
    center_text(draw, "Ruan Ranison", y, fnt(F_REG, 38), MUTED)
    y += 70

    number_badge(draw, W // 2, y + 90, size=200)
    y += 210

    if nova:
        y = wrap_center(
            draw,
            "Vices: Doson's de Oliveira Vitor  ·  José Marcos Correia dos Santos",
            y,
            fnt(F_BOLD, 26),
            BLUE,
            W - 90,
        )
        y += 10
        wrap_center(
            draw,
            "Fim da 424  ·  Nova era da 924",
            y,
            fnt(F_BOLD, 30),
            NAVY,
            W - 90,
        )
    else:
        center_text(draw, "Presença, regra e grupo", y, fnt(F_BOLD, 32), BLUE)

    band_footer(draw, "VOTE  67")
    img.save(out_path, "PNG", optimize=True)
    print("wrote", out_path.name)


def make_verso(out_path: Path, *, nova: bool):
    """Verso/cola — mesma identidade da frente (faixas azul + papel + número amarelo)."""
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    band_header(draw, "COLA  ·  PAUPITEIROS")

    # Card central — cola clássica (mesmo visual da frente)
    card = (56, 130, W - 56, H - 130)
    draw.rounded_rectangle(card, radius=28, fill=WHITE, outline=BLUE_BRIGHT, width=6)

    y = 175
    center_text(draw, "Na urna, digite o número", y, fnt(F_BOLD, 36), MUTED)
    y += 80

    # Número gigante — hierarquia máxima (Printi/Expo)
    number_badge(draw, W // 2, y + 180, size=380)
    y += 400

    center_text(draw, "FETO", y, fnt(F_BLACK, 96), NAVY)
    y += 105
    center_text(draw, "Ruan Ranison", y, fnt(F_REG, 38), MUTED)
    y += 58
    center_text(draw, "Administrador", y, fnt(F_BOLD, 34), BLUE)
    y += 80

    if nova:
        y = wrap_center(
            draw,
            "Vices: Doson's de Oliveira Vitor  ·  José Marcos Correia dos Santos",
            y,
            fnt(F_BOLD, 28),
            NAVY,
            W - 140,
        )
        y += 22
        wrap_center(
            draw,
            "Fim da 424 no poder. Nova era da 924.",
            y,
            fnt(F_BOLD, 32),
            BLUE,
            W - 140,
        )
    else:
        wrap_center(
            draw,
            "Presença, regra e grupo em primeiro lugar.",
            y,
            fnt(F_BOLD, 34),
            BLUE,
            W - 140,
        )

    # Faixa interna amarela (eco do badge — fecha o verso sem “vazio”)
    draw.rounded_rectangle((100, H - 250, W - 100, H - 170), radius=18, fill=YELLOW, outline=NAVY, width=4)
    center_text(draw, "MEMORIZE:  67", H - 228, fnt(F_BLACK, 44), NAVY)

    band_footer(draw, "CONFIRMA  ·  67")
    img.save(out_path, "PNG", optimize=True)
    print("wrote", out_path.name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    antiga = ROOT / "assets" / "feto-antiga.jpg"
    nova = ROOT / "assets" / "feto.jpg"

    make_frente(antiga, OUT / "santinho-foto-antiga-frente.png", nova=False)
    make_verso(OUT / "santinho-foto-antiga-verso.png", nova=False)
    make_frente(nova, OUT / "santinho-foto-nova-frente.png", nova=True)
    make_verso(OUT / "santinho-foto-nova-verso.png", nova=True)


if __name__ == "__main__":
    main()

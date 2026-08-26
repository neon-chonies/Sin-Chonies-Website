from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Image Assets" / "winchesters-june-20-2026-flyer.png"
OUT = ROOT / "Image Assets" / "winchesters-november-21-2026-flyer.png"

SIZE = 2048
SCALE = 2

RED = (188, 24, 18)
RED_HOT = (223, 40, 25)
CREAM = (232, 218, 190)
BLACK = (5, 5, 5)
TEAL = (81, 143, 137)

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
GEORGIA_BOLD = str(FONT_DIR / "Georgia Bold.ttf")
ARIAL_BLACK = str(FONT_DIR / "Arial Black.ttf")
ARIAL_BOLD = str(FONT_DIR / "Arial Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size * SCALE)


def centered(draw, xy, text, font_obj, fill, stroke=0, stroke_fill=BLACK):
    draw.text(
        xy,
        text,
        font=font_obj,
        fill=fill,
        anchor="mm",
        stroke_width=stroke * SCALE,
        stroke_fill=stroke_fill,
    )


def add_texture(draw, box):
    x0, y0, x1, y1 = box
    for offset in range(0, int(y1 - y0), 16 * SCALE):
        alpha = 12 if offset % (32 * SCALE) == 0 else 7
        draw.line((x0, y0 + offset, x1, y0 + offset), fill=(255, 255, 255, alpha), width=1 * SCALE)


def main():
    img = Image.open(BASE).convert("RGBA").resize((SIZE * SCALE, SIZE * SCALE), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img = ImageEnhance.Color(img).enhance(1.02)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Repaint the prior date/time band while preserving the Winchesters poster art.
    band = (145 * SCALE, 1495 * SCALE, (SIZE - 145) * SCALE, 1908 * SCALE)
    draw.rounded_rectangle(band, radius=26 * SCALE, fill=(7, 7, 7, 255), outline=(214, 192, 158, 150), width=3 * SCALE)
    draw.rectangle((band[0] + 18 * SCALE, band[1] + 18 * SCALE, band[2] - 18 * SCALE, band[3] - 18 * SCALE), outline=(*RED, 145), width=4 * SCALE)
    add_texture(draw, band)

    divider_y = 1680 * SCALE
    draw.line((215 * SCALE, divider_y, (SIZE - 215) * SCALE, divider_y), fill=(RED_HOT[0], RED_HOT[1], RED_HOT[2], 210), width=5 * SCALE)
    draw.line((215 * SCALE, 1818 * SCALE, (SIZE - 215) * SCALE, 1818 * SCALE), fill=(CREAM[0], CREAM[1], CREAM[2], 130), width=3 * SCALE)

    for x in (650, 1110, 1510):
        draw.line((x * SCALE, 1548 * SCALE, x * SCALE, 1848 * SCALE), fill=(CREAM[0], CREAM[1], CREAM[2], 155), width=3 * SCALE)

    f_day = font(GEORGIA_BOLD, 84)
    f_month = font(IMPACT, 98)
    f_small = font(ARIAL_BLACK, 42)
    f_time = font(GEORGIA_BOLD, 84)
    f_label = font(IMPACT, 48)
    f_city = font(ARIAL_BLACK, 62)
    f_footer = font(ARIAL_BOLD, 34)

    centered(draw, (390 * SCALE, 1586 * SCALE), "SAT", f_day, CREAM, stroke=2)
    centered(draw, (390 * SCALE, 1698 * SCALE), "NOVEMBER", f_month, RED_HOT, stroke=2)
    centered(draw, (390 * SCALE, 1805 * SCALE), "21ST", f_month, RED_HOT, stroke=2)

    centered(draw, (875 * SCALE, 1642 * SCALE), "7 PM", f_time, CREAM, stroke=2)
    centered(draw, (875 * SCALE, 1745 * SCALE), "START", f_label, RED_HOT, stroke=2)

    centered(draw, (1310 * SCALE, 1642 * SCALE), "10 PM", f_time, CREAM, stroke=2)
    centered(draw, (1310 * SCALE, 1745 * SCALE), "END", f_label, RED_HOT, stroke=2)

    centered(draw, (1728 * SCALE, 1643 * SCALE), "VENTURA", f_city, RED_HOT, stroke=2)
    centered(draw, (1728 * SCALE, 1740 * SCALE), "CA", f_city, CREAM, stroke=2)

    centered(draw, (SIZE * SCALE / 2, 1876 * SCALE), "GREAT MUSIC  •  NO PANTIES", f_footer, CREAM, stroke=1)

    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4 * SCALE, percent=120, threshold=3))
    img.resize((SIZE, SIZE), Image.Resampling.LANCZOS).convert("RGB").save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()

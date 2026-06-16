import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BAND_SHEET = ROOT.parent / "sin-chonies-bandsheet" / "bandsheet-data.json"
OUT = ROOT / "Image Assets" / "sin-chonies-upcoming-dates-square.png"
LOGO = ROOT / "Image Assets" / "sin chonies logo.png"
BG_PHOTO = ROOT / "Image Assets" / "strikeout-white-black-bg.png"

SIZE = 2048
SCALE = 3
W = SIZE * SCALE
H = SIZE * SCALE

RED = (209, 25, 5)
RED_HOT = (235, 76, 26)
GOLD = (214, 174, 51)
TEAL = (0, 184, 156)
OFF_WHITE = (242, 238, 229)
MUTED = (167, 160, 149)
BLACK = (7, 7, 7)
PANEL = (18, 18, 18)

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
IMPACT = str(FONT_DIR / "Impact.ttf")
ARIAL = str(FONT_DIR / "Arial.ttf")
ARIAL_BOLD = str(FONT_DIR / "Arial Bold.ttf")
ARIAL_BLACK = str(FONT_DIR / "Arial Black.ttf")


def font(path, size):
    return ImageFont.truetype(path, size * SCALE)


def draw_letterspaced(draw, xy, text, font_obj, fill, tracking=0, anchor=None):
    x, y = xy
    widths = [draw.textlength(ch, font=font_obj) for ch in text]
    total = sum(widths) + tracking * SCALE * max(0, len(text) - 1)
    if anchor and "m" in anchor:
        x -= total / 2
    if anchor and "r" in anchor:
        x -= total
    for ch, width in zip(text, widths):
        draw.text((x, y), ch, font=font_obj, fill=fill, anchor="la")
        x += width + tracking * SCALE


def parse_gig(line):
    pattern = r"^([A-Z]{3}) (\d{1,2})-(\d{1,2})-(\d{2}) @([0-9:]+)(AM|PM) \u2014 (.*?), (.*?)$"
    match = re.match(pattern, line)
    if not match:
        tba_pattern = r"^([A-Z]{3}) (\d{1,2})-(\d{1,2})-(\d{2}) \u2014 TBA$"
        tba_match = re.match(tba_pattern, line)
        if tba_match:
            day_abbr, month, day, year = tba_match.groups()
            start = datetime.strptime(f"20{year}-{int(month):02d}-{int(day):02d}", "%Y-%m-%d")
            return {
                "day_abbr": day_abbr,
                "month": start.strftime("%b").upper(),
                "day": start.strftime("%d"),
                "date": start.strftime("%b %-d").upper(),
                "venue": "TBA",
                "city": "",
                "time": "TBA",
            }
    if not match:
        raise ValueError(f"Could not parse gig: {line}")
    day_abbr, month, day, year, time_value, meridiem, venue, city = match.groups()
    time_format = "%I:%M%p" if ":" in time_value else "%I%p"
    start = datetime.strptime(
        f"20{year}-{int(month):02d}-{int(day):02d} {time_value}{meridiem}",
        f"%Y-%m-%d {time_format}",
    )
    end = start + timedelta(hours=3)
    return {
        "day_abbr": day_abbr,
        "month": start.strftime("%b").upper(),
        "day": start.strftime("%d"),
        "date": start.strftime("%b %-d").upper(),
        "venue": venue,
        "city": city,
        "time": f"{fmt_time(start)}-{fmt_time(end)}",
    }


def fmt_time(dt):
    if dt.minute:
        return dt.strftime("%-I:%M%p")
    return dt.strftime("%-I%p")


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        tuple(int(v) for v in box),
        radius=int(radius),
        fill=fill,
        outline=outline,
        width=int(width),
    )


def cover_image(path):
    img = Image.open(path).convert("RGB")
    target_ratio = W / H
    ratio = img.width / img.height
    if ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
    return img.resize((W, H), Image.Resampling.LANCZOS)


def fit_logo(max_width, max_height):
    logo = Image.open(LOGO).convert("RGBA")
    # The logo file has a lot of empty top space. Crop to meaningful pixels.
    alpha = logo.getchannel("A")
    bbox = alpha.getbbox() or logo.getbbox()
    logo = logo.crop(bbox)
    ratio = min(max_width / logo.width, max_height / logo.height)
    size = (int(logo.width * ratio), int(logo.height * ratio))
    return logo.resize(size, Image.Resampling.LANCZOS)


def add_noise(img, opacity=22):
    # Deterministic gritty texture, no external assets.
    noise = Image.effect_noise((W, H), 90).convert("L")
    tint = Image.new("RGBA", (W, H), (255, 255, 255, opacity))
    alpha = ImageEnhance.Contrast(noise).enhance(1.6)
    tint.putalpha(alpha.point(lambda p: int(p * opacity / 255)))
    return Image.alpha_composite(img, tint)


def main():
    data = json.loads(BAND_SHEET.read_text())
    gigs = [parse_gig(item) for item in data["booked_gigs"]]

    base = cover_image(BG_PHOTO).convert("RGBA")
    base = ImageEnhance.Color(base).enhance(0.78)
    base = ImageEnhance.Brightness(base).enhance(0.34)
    base = base.filter(ImageFilter.GaussianBlur(radius=2 * SCALE))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 0, W, H), fill=(0, 0, 0, 128))
    for i in range(0, H, 42 * SCALE):
        od.rectangle((0, i, W, i + 2 * SCALE), fill=(255, 255, 255, 10))
    od.rectangle((0, 0, W, H), outline=(*RED, 210), width=18 * SCALE)
    od.rectangle((54 * SCALE, 54 * SCALE, W - 54 * SCALE, H - 54 * SCALE), outline=(*GOLD, 120), width=3 * SCALE)
    img = Image.alpha_composite(base, overlay)
    img = add_noise(img)
    draw = ImageDraw.Draw(img)

    f_title = font(IMPACT, 122)
    f_sub = font(ARIAL_BOLD, 30)
    f_month = font(ARIAL_BLACK, 38)
    f_day = font(IMPACT, 54)
    f_dow = font(ARIAL_BOLD, 24)
    f_venue = font(ARIAL_BLACK, 36)
    f_meta = font(ARIAL_BOLD, 26)
    f_tba = font(ARIAL_BLACK, 42)
    f_footer = font(ARIAL_BOLD, 22)

    logo = fit_logo(900 * SCALE, 210 * SCALE)
    img.alpha_composite(logo, (int((W - logo.width) / 2), 96 * SCALE))
    draw.text((W / 2, 330 * SCALE), "UPCOMING DATES", font=f_title, fill=OFF_WHITE, anchor="mt", stroke_width=3 * SCALE, stroke_fill=BLACK)
    draw_letterspaced(draw, (W / 2, 476 * SCALE), "2026 LIVE SHOW CALENDAR", f_sub, GOLD, tracking=6, anchor="ma")

    left = 120 * SCALE
    top = 560 * SCALE
    col_gap = 34 * SCALE
    row_gap = 17 * SCALE
    col_w = (W - left * 2 - col_gap) / 2
    row_h = 132 * SCALE

    for i, gig in enumerate(gigs):
        col = i % 2
        row = i // 2
        x = left + col * (col_w + col_gap)
        y = top + row * (row_h + row_gap)
        accent = RED_HOT if i == 0 else RED
        rounded_rect(draw, (x, y, x + col_w, y + row_h), 9 * SCALE, (*PANEL, 224), outline=(*accent, 172), width=3 * SCALE)
        draw.rectangle((x, y, x + 12 * SCALE, y + row_h), fill=accent)
        date_x = x + 46 * SCALE
        draw.text((date_x, y + 24 * SCALE), gig["month"], font=f_month, fill=GOLD, anchor="la")
        draw.text((date_x, y + 60 * SCALE), gig["day"], font=f_day, fill=OFF_WHITE, anchor="la")
        draw.text((date_x + 100 * SCALE, y + 71 * SCALE), gig["day_abbr"], font=f_dow, fill=MUTED, anchor="la")

        info_x = x + 212 * SCALE
        max_venue = col_w - 250 * SCALE
        venue = gig["venue"].upper()
        while draw.textlength(venue, font=f_venue) > max_venue and len(venue) > 5:
            venue = venue[:-2] + "."
        draw.text((info_x, y + 28 * SCALE), venue, font=f_venue, fill=OFF_WHITE, anchor="la")
        time_text = gig["time"]
        city_text = f"/ {gig['city'].upper()}" if gig["city"] else ""
        draw.text((info_x, y + 75 * SCALE), time_text, font=f_meta, fill=TEAL, anchor="la")
        if city_text:
            city_x = info_x + draw.textlength(time_text, font=f_meta) + 28 * SCALE
            max_city_width = x + col_w - city_x - 24 * SCALE
            city_font = f_meta
            if draw.textlength(city_text, font=city_font) > max_city_width:
                city_font = font(ARIAL_BOLD, 22)
            draw.text((city_x, y + 75 * SCALE), city_text, font=city_font, fill=MUTED, anchor="la")

    footer_y = H - 134 * SCALE
    draw_letterspaced(draw, (W / 2, footer_y - 96 * SCALE), "MORE DATES TBA, STAY TUNED", f_tba, TEAL, tracking=4, anchor="ma")
    draw.line((150 * SCALE, footer_y, W - 150 * SCALE, footer_y), fill=(*RED, 170), width=3 * SCALE)
    draw_letterspaced(draw, (W / 2, footer_y + 35 * SCALE), "VENTURA COUNTY AND BEYOND", f_footer, OFF_WHITE, tracking=5, anchor="ma")

    final = img.convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    final.save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    main()

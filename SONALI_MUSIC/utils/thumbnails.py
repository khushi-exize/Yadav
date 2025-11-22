import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL
from SONALI_MUSIC import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88
TRANSPARENCY = 170
INNER_OFFSET = 36

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = 377
META_X = 377
TITLE_Y = THUMB_Y + THUMB_H + 10
META_Y = TITLE_Y + 45

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580

SHUKLA_COLOR = [
    (188, 250, 152),   
    (110, 180, 245),   
    (242, 179, 240),   
    (249, 255, 158),   
    (164, 163, 240),
    (135, 250, 244),
    (255, 255, 255),
]

def trim_to_width(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    ellipsis = "…"
    try:
        if font.getlength(text) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + ellipsis) <= max_w:
                return text[:i] + ellipsis
    except AttributeError:
        return text[:max_w // 10] + "…" if len(text) > max_w // 10 else text
    return ellipsis

async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v4.png")
    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        search_result = await results.next()
        data = search_result.get("result", [])[0]
        title = re.sub(r"\W+", " ", data.get("title", "Unsupported Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
    except Exception:
        title, thumbnail, duration, views = "Unsupported Title", YOUTUBE_IMG_URL, None, "Unknown Views"

    is_live = not duration or str(duration).strip().lower() in {"", "live", "live now"}
    duration_text = "Live" if is_live else duration or "Unknown Mins"

    thumb_path = os.path.join(CACHE_DIR, f"thumb{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    base = Image.open(thumb_path).resize((1280, 720)).convert("RGBA")
    bg = ImageEnhance.Brightness(base.filter(ImageFilter.BoxBlur(10))).enhance(0.6)

    panel_area = bg.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
    random_color = random.choice(SHUKLA_COLOR)
    rgba_color = (*random_color, TRANSPARENCY)
    overlay = Image.new("RGBA", (PANEL_W, PANEL_H), rgba_color)
    frosted = Image.alpha_composite(panel_area, overlay)
    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 50, fill=255)
    bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

    draw = ImageDraw.Draw(bg)

    try:
        title_font = ImageFont.truetype("SONALI_MUSIC/assets/f.ttf", 32)
        regular_font = ImageFont.truetype("SONALI_MUSIC/assets/font.ttf", 18)
        shukla_font = ImageFont.truetype("SONALI_MUSIC/assets/font.ttf", 26)
    except OSError:
        title_font = regular_font = shukla_font = ImageFont.load_default()

    BORDER_SIZE = 6
    thumb_with_border = Image.new("RGBA", (THUMB_W + 2 * BORDER_SIZE, THUMB_H + 2 * BORDER_SIZE), (255, 255, 255, 0))

    border_mask = Image.new("L", (THUMB_W + 2 * BORDER_SIZE, THUMB_H + 2 * BORDER_SIZE), 0)
    ImageDraw.Draw(border_mask).rounded_rectangle(
        (0, 0, THUMB_W + 2 * BORDER_SIZE, THUMB_H + 2 * BORDER_SIZE), 25, fill=255
    )
    ImageDraw.Draw(thumb_with_border).rounded_rectangle(
        (0, 0, THUMB_W + 2 * BORDER_SIZE, THUMB_H + 2 * BORDER_SIZE), 25, fill=(255, 255, 255, 255)
    )

    thumb = base.resize((THUMB_W, THUMB_H)).convert("RGBA")
    thumb_mask = Image.new("L", (THUMB_W, THUMB_H), 0)
    ImageDraw.Draw(thumb_mask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 20, fill=255)
    thumb_with_border.paste(thumb, (BORDER_SIZE, BORDER_SIZE), thumb_mask)

    bg.paste(thumb_with_border, (THUMB_X - BORDER_SIZE, THUMB_Y - BORDER_SIZE), border_mask)

    draw.text((TITLE_X, TITLE_Y), trim_to_width(title, title_font, MAX_TITLE_WIDTH), fill="black", font=title_font)

    left_text = f"YouTube | {views}"
    right_text = f"Player | @{player_username}"
    left_w = regular_font.getlength(left_text)
    right_w = regular_font.getlength(right_text)
    gap = 30
    total_width = left_w + gap + right_w
    start_x = PANEL_X + (PANEL_W - total_width) // 2

    draw.text((start_x, META_Y), left_text, fill="red", font=regular_font)
    draw.text((start_x + left_w + gap, META_Y), right_text, fill="red", font=regular_font)

    draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill="red", width=6)
    draw.line([(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill="gray", width=5)
    draw.ellipse([(BAR_X + BAR_RED_LEN - 7, BAR_Y - 7), (BAR_X + BAR_RED_LEN + 7, BAR_Y + 7)], fill="red")
    draw.text((BAR_X, BAR_Y + 15), "00:00", fill="black", font=regular_font)
    draw.text((BAR_X + BAR_TOTAL_LEN - (90 if is_live else 60), BAR_Y + 15),
              duration_text, fill="red" if is_live else "black", font=regular_font)

    icons_path = "SONALI_MUSIC/assets/play_icons.png"
    if os.path.isfile(icons_path):
        ic = Image.open(icons_path).resize((ICONS_W, ICONS_H)).convert("RGBA")
        r, g, b, a = ic.split()
        black_ic = Image.merge("RGBA", (r.point(lambda *_: 0), g.point(lambda *_: 0), b.point(lambda *_: 0), a))
        bg.paste(black_ic, (ICONS_X, ICONS_Y), black_ic)

    padding = 25

    
    shashank_text = "IG :- @lllll_BADNAM_BABY_lllll"
    shashank_x = padding
    shashank_y = padding
    draw.text((shashank_x, shashank_y), shashank_text, fill=(255, 255, 0), font=shukla_font)

    shukla_text = "DEV :- @kriti_bot_update"
    shukla_w = shukla_font.getlength(shukla_text)
    shukla_x = 1280 - shukla_w - padding
    shukla_y = padding
    draw.text((shukla_x, shukla_y), shukla_text, fill=(255, 255, 0), font=shukla_font)


    try:
        os.remove(thumb_path)
    except OSError:
        pass

    bg.save(cache_path)
    return cache_path

# 

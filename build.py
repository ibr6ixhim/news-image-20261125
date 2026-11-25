"""Build-time renderer (needs Pillow; NOT run by the judge). Usage: python3 build.py

Reads stories.json and fonts/, writes assets/entry.png (1024x1024, <= 1 MiB).
main.py then just copies that file, so the entry stays dependency-free and deterministic.
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 36  # outer margin

PAPER = (247, 243, 233)
INK = (20, 20, 24)
MUTED = (95, 95, 105)
RULE = (30, 30, 36)
ACCENT = (176, 28, 38)
REGION_COLORS = {
    "AFRICA": (196, 112, 16), "ASIA": (178, 34, 74), "EUROPE": (34, 82, 160),
    "MIDDLE EAST": (140, 96, 20), "N. AMERICA": (28, 118, 84), "S. AMERICA": (110, 60, 150),
    "OCEANIA": (0, 126, 140), "SCIENCE": (60, 90, 200), "ECONOMY": (70, 110, 40),
    "SPORT": (200, 70, 30),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(draw, x, y, w, text, name, size, color, max_lines, line_gap=3):
    """Draw wrapped text; shrinks the font until it fits max_lines. Returns next y."""
    while size >= 11:
        fnt = font(name, size)
        lines = wrap(draw, text, fnt, w)
        if len(lines) <= max_lines:
            break
        size -= 1
    else:
        fnt = font(name, 11)
        lines = wrap(draw, text, fnt, w)[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += size + line_gap
    return y


def chip(draw, x, y, label, color):
    f = font("BodyBold.ttf", 12)
    tw = draw.textlength(label, font=f)
    draw.rectangle([x, y, x + tw + 12, y + 18], fill=color)
    draw.text((x + 6, y + 2), label, font=f, fill=(255, 255, 255))
    return x + tw + 12


def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    mf = font("Headline.ttf", 58)
    mw = d.textlength(data["masthead"], font=mf)
    d.text(((W - mw) / 2, 22), data["masthead"], font=mf, fill=INK)
    d.rectangle([M, 96, W - M, 99], fill=RULE)
    df = font("BodyBold.ttf", 15)
    dw = d.textlength(data["date_line"], font=df)
    d.text(((W - dw) / 2, 106), data["date_line"], font=df, fill=ACCENT)
    d.rectangle([M, 130, W - M, 131], fill=RULE)

    # Lead story (left, large) + two secondaries (right)
    top = 146
    lead_w = 560
    lead = data["lead"]
    chip(d, M, top, lead["region"], REGION_COLORS.get(lead["region"], ACCENT))
    y = draw_block(d, M, top + 30, lead_w, lead["headline"], "Headline.ttf", 40, INK, 5, 4)
    y = draw_block(d, M, y + 8, lead_w, lead["summary"], "Body.ttf", 20, MUTED, 4)
    d.text((M, y + 6), lead["source"], font=font("BodyBold.ttf", 13), fill=ACCENT)
    lead_bottom = y + 28

    sx = M + lead_w + 28
    sy = top
    for s in data["secondary"][:2]:
        chip(d, sx, sy, s["region"], REGION_COLORS.get(s["region"], ACCENT))
        yy = draw_block(d, sx, sy + 26, W - M - sx, s["headline"], "Headline.ttf", 24, INK, 4, 3)
        yy = draw_block(d, sx, yy + 4, W - M - sx, s["summary"], "Body.ttf", 15, MUTED, 3)
        d.text((sx, yy + 2), s["source"], font=font("BodyBold.ttf", 12), fill=ACCENT)
        sy = yy + 30
    section_y = max(lead_bottom, sy, 500) + 6

    d.rectangle([sx - 14, top, sx - 13, section_y], fill=RULE)

    # Regional grid: 2 columns x N rows
    d.rectangle([M, section_y, W - M, section_y + 2], fill=RULE)
    grid = data["grid"]
    cols = 2
    rows = (len(grid) + cols - 1) // cols
    gy0 = section_y + 14
    avail = H - 70 - gy0
    row_h = avail // max(rows, 1)
    col_w = (W - 2 * M - 24) // cols
    for i, g in enumerate(grid):
        r, c = divmod(i, cols)
        gx = M + c * (col_w + 24)
        gy = gy0 + r * row_h
        chip(d, gx, gy, g["region"], REGION_COLORS.get(g["region"], ACCENT))
        draw_block(d, gx, gy + 24, col_w, g["headline"], "BodyBold.ttf", 17, INK, 2, 2)
        d.text((gx, gy + row_h - 24), g["source"], font=font("Body.ttf", 11), fill=MUTED)
        if c == 0:
            d.rectangle([gx + col_w + 11, gy, gx + col_w + 12, gy + row_h - 12], fill=(200, 196, 186))

    # Footer
    d.rectangle([M, H - 52, W - M, H - 51], fill=RULE)
    ff = font("Body.ttf", 13)
    fw = d.textlength(data["footer"], font=ff)
    d.text(((W - fw) / 2, H - 40), data["footer"], font=ff, fill=MUTED)
    return img


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = render(data)
    out = os.path.join(HERE, "assets", "entry.png")
    img.save(out, format="PNG", optimize=True)  # no metadata, no timestamps -> deterministic
    size = os.path.getsize(out)
    if size > 1024 * 1024:  # fall back to a palette PNG if over 1 MiB
        img.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            out, format="PNG", optimize=True)
        size = os.path.getsize(out)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"{out}: {size} bytes, {img.size[0]}x{img.size[1]}, sha256={sha}")
    if size > 1024 * 1024:
        sys.exit("entry.png is over 1 MiB")


if __name__ == "__main__":
    main()

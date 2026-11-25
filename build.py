"""Render the front page for Wednesday 25 November 2026.

Reads stories.json next to this file and draws entry.png (1024x1024,
<= 1 MiB) with Pillow. Build-time only: the judge runs main.py, which
just copies the finished image. Output is deterministic: no timestamps,
no metadata, fixed fonts, fixed layout.
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 32

PAPER = (247, 243, 233)
INK = (18, 18, 22)
MUTED = (96, 96, 106)
RULE = (28, 28, 34)
NAVY = (16, 42, 84)
ACCENT = (176, 28, 38)
LIGHT_LINE = (205, 200, 188)
REGION_COLORS = {
    "AFRICA": (196, 112, 16), "ASIA": (178, 34, 74),
    "EUROPE": (34, 82, 160), "MIDDLE EAST": (140, 96, 20),
    "N. AMERICA": (28, 118, 84), "S. AMERICA": (110, 60, 150),
    "OCEANIA": (0, 126, 140), "SCIENCE": (60, 90, 200),
    "ECONOMY": (70, 110, 40), "SPORT": (200, 70, 30),
    "TECH": (90, 60, 160),
}
TAG_COLORS = {
    "CONFIRMED": (28, 118, 84), "REPORTED": (34, 82, 160),
    "CLAIM": (176, 96, 16), "OFFICIAL": (90, 60, 160),
}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, name), size)


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


def block(draw, x, y, w, text, name, size, color, max_lines, gap=2):
    """Wrapped text, shrinking the font until it fits max_lines."""
    while size >= 10:
        fnt = font(name, size)
        lines = wrap(draw, text, fnt, w)
        if len(lines) <= max_lines:
            break
        size -= 1
    else:
        fnt = font(name, 10)
        lines = wrap(draw, text, fnt, w)[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += size + gap
    return y


def one_line(draw, x, y, w, text, name, size, color):
    """Single line, truncated with an ellipsis when it does not fit."""
    fnt = font(name, size)
    if draw.textlength(text, font=fnt) <= w:
        draw.text((x, y), text, font=fnt, fill=color)
        return
    while text and draw.textlength(text + "…", font=fnt) > w:
        text = text[:-1]
    draw.text((x, y), text + "…", font=fnt, fill=color)


def chip(draw, x, y, label, color, size=11):
    fnt = font("BodyBold.ttf", size)
    tw = draw.textlength(label, font=fnt)
    draw.rectangle([x, y, x + tw + 12, y + 17], fill=color)
    draw.text((x + 6, y + 2), label, font=fnt, fill=(255, 255, 255))
    return tw + 12


def tag(draw, x, y, label):
    fnt = font("BodyBold.ttf", 10)
    tw = draw.textlength(label, font=fnt)
    draw.rectangle([x, y, x + tw + 10, y + 15], outline=TAG_COLORS.get(label, MUTED), width=1)
    draw.text((x + 5, y + 2), label, font=fnt, fill=TAG_COLORS.get(label, MUTED))
    return tw + 10


def art_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 48))
    d.ellipse([x + w * 0.66, y + h * 0.02, x + w * 0.86, y + h * 0.34], fill=(255, 120, 20))
    d.polygon([(x + w * 0.62, y + h), (x + w * 0.72, y + h * 0.25),
               (x + w * 0.82, y + h)], fill=(70, 72, 92))
    d.rectangle([x + w * 0.68, y + h * 0.45, x + w * 0.76, y + h * 0.50], fill=(30, 32, 48))
    d.rectangle([x + w * 0.67, y + h * 0.62, x + w * 0.77, y + h * 0.67], fill=(30, 32, 48))
    d.polygon([(x + w * 0.30, y + h), (x + w * 0.38, y + h * 0.45),
               (x + w * 0.46, y + h)], fill=(70, 72, 92))
    d.rectangle([x + w * 0.10, y + h * 0.55, x + w * 0.24, y + h], fill=(90, 60, 40))
    d.polygon([(x + w * 0.68, y + h * 0.30), (x + w * 0.76, y + h * 0.02),
               (x + w * 0.84, y + h * 0.30)], fill=(255, 150, 30))
    d.polygon([(x + w * 0.72, y + h * 0.30), (x + w * 0.76, y + h * 0.14),
               (x + w * 0.80, y + h * 0.30)], fill=(255, 210, 60))
    d.ellipse([x + w * 0.86, y + h * 0.12, x + w * 0.94, y + h * 0.28], fill=(240, 220, 180))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(18, 18, 22))


def art_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 24, 64))
    for sx, sy in [(0.12, 0.2), (0.3, 0.12), (0.55, 0.25), (0.8, 0.12), (0.9, 0.35), (0.2, 0.45)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * sx + 4, y + h * sy + 4], fill=(255, 255, 255))
    cx = x + w * 0.5
    d.polygon([(cx - 16, y + h * 0.30), (cx, y + h * 0.08), (cx + 16, y + h * 0.30)], fill=(176, 28, 38))
    d.rectangle([cx - 16, y + h * 0.30, cx + 16, y + h * 0.72], fill=(240, 240, 235))
    d.ellipse([cx - 9, y + h * 0.38, cx + 9, y + h * 0.56], fill=(120, 180, 230))
    d.polygon([(cx - 16, y + h * 0.62), (cx - 34, y + h * 0.82), (cx - 16, y + h * 0.78)], fill=(176, 28, 38))
    d.polygon([(cx + 16, y + h * 0.62), (cx + 34, y + h * 0.82), (cx + 16, y + h * 0.78)], fill=(176, 28, 38))
    d.polygon([(cx - 10, y + h * 0.72), (cx, y + h * 0.98), (cx + 10, y + h * 0.72)], fill=(255, 150, 30))
    d.ellipse([x + w * 0.78, y + h * 0.62, x + w * 0.98, y + h * 0.82], fill=(220, 200, 150))


def art_port(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.62], fill=(245, 220, 170))
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.92, y + h * 0.30], fill=(255, 180, 60))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(20, 90, 120))
    d.polygon([(x + w * 0.08, y + h * 0.70), (x + w * 0.92, y + h * 0.70),
               (x + w * 0.84, y + h * 0.92), (x + w * 0.16, y + h * 0.92)], fill=(30, 30, 36))
    for i, col in enumerate([(176, 28, 38), (28, 118, 84), (200, 120, 20), (34, 82, 160)]):
        bx = x + w * (0.14 + i * 0.19)
        d.rectangle([bx, y + h * 0.42, bx + w * 0.15, y + h * 0.70], fill=col)
    d.rectangle([x + w * 0.55, y + h * 0.18, x + w * 0.60, y + h * 0.62], fill=(60, 60, 70))
    d.rectangle([x + w * 0.55, y + h * 0.18, x + w * 0.82, y + h * 0.26], fill=(60, 60, 70))
    d.line([x + w * 0.80, y + h * 0.26, x + w * 0.80, y + h * 0.44], fill=(60, 60, 70), width=2)
    d.rectangle([x + w * 0.76, y + h * 0.44, x + w * 0.84, y + h * 0.52], fill=(176, 28, 38))


ART = {"refinery": art_refinery, "rocket": art_rocket, "port": art_port}


def hero_card(d, x, y, w, story, num):
    art = ART.get(story.get("art", "refinery"))
    art(d, x, y, w, 84)
    d.rectangle([x, y + 84, x + w, y + 85], fill=RULE)
    yy = y + 92
    cw = chip(d, x, yy, story["region"], REGION_COLORS.get(story["region"], ACCENT))
    tag(d, x + cw + 8, yy + 1, story["tag"])
    numf = font("Headline.ttf", 26)
    d.text((x + w - 26, yy - 6), str(num), font=numf, fill=ACCENT)
    yy = block(d, x, yy + 24, w, story["headline"], "Headline.ttf", 19, INK, 3, 2)
    yy = block(d, x, yy + 4, w, story["summary"], "Body.ttf", 12, MUTED, 4, 2)
    d.text((x, yy + 2), story["source"], font=font("BodyBold.ttf", 11), fill=ACCENT)
    return yy + 18


def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Banner: story count + regions
    d.rectangle([0, 0, W, 28], fill=NAVY)
    bf = font("BodyBold.ttf", 13)
    bw = d.textlength(data["banner"], font=bf)
    d.text(((W - bw) / 2, 7), data["banner"], font=bf, fill=(255, 255, 255))

    # Masthead + date
    mf = font("Headline.ttf", 54)
    mw = d.textlength(data["masthead"], font=mf)
    d.text(((W - mw) / 2, 34), data["masthead"], font=mf, fill=INK)
    d.rectangle([M, 96, W - M, 99], fill=RULE)
    df = font("BodyBold.ttf", 16)
    dw = d.textlength(data["date_line"], font=df)
    d.text(((W - dw) / 2, 104), data["date_line"], font=df, fill=ACCENT)
    d.rectangle([M, 126, W - M, 127], fill=RULE)

    # Deck: the three top stories
    y = 132
    for line in data["deck"]:
        one_line(d, M, y, W - 2 * M, "▸  " + line, "BodyBold.ttf", 13, NAVY)
        y += 15
    y += 3

    # Numbers strip
    nums = data["numbers"]
    box_w = (W - 2 * M - 5 * 8) // len(nums)
    ny = y
    for i, n in enumerate(nums):
        bx = M + i * (box_w + 8)
        d.rectangle([bx, ny, bx + box_w, ny + 40], outline=LIGHT_LINE, width=1)
        vf = font("Headline.ttf", 22)
        vw = d.textlength(n["value"], font=vf)
        d.text((bx + (box_w - vw) / 2, ny + 2), n["value"], font=vf, fill=ACCENT)
        one_line(d, bx + 4, ny + 26, box_w - 8, n["label"], "Body.ttf", 9, MUTED)
    y = ny + 48

    # Timeline strip
    d.rectangle([M, y, W - M, y + 20], fill=(232, 228, 216))
    tl = "  ·  ".join(t["time"] + " " + t["label"] for t in data["timeline"])
    one_line(d, M + 6, y + 4, W - 2 * M - 12, "UTC:  " + tl, "BodyBold.ttf", 10, INK)
    y += 28

    # Three hero cards in equal columns
    heroes = [data["lead"]] + data["secondary"][:2]
    col_w = (W - 2 * M - 2 * 16) // 3
    hero_bottom = y
    for i, story in enumerate(heroes):
        hx = M + i * (col_w + 16)
        if i:
            d.rectangle([hx - 9, y, hx - 8, y + 280], fill=LIGHT_LINE)
        bottom = hero_card(d, hx, y, col_w, story, i + 1)
        hero_bottom = max(hero_bottom, bottom)
    y = hero_bottom + 2
    d.rectangle([M, y, W - M, y + 2], fill=RULE)
    y += 10

    # Grid: 2 columns x 5 rows
    grid = data["grid"]
    col_w = (W - 2 * M - 24) // 2
    row_h = 50
    for i, g in enumerate(grid):
        r, c = divmod(i, 2)
        gx = M + c * (col_w + 24)
        gy = y + r * row_h
        cw = chip(d, gx, gy, g["region"], REGION_COLORS.get(g["region"], ACCENT), size=10)
        tag(d, gx + cw + 6, gy, g["tag"])
        block(d, gx, gy + 21, col_w, g["headline"], "BodyBold.ttf", 13, INK, 2, 1)
        d.text((gx, gy + row_h - 11), g["source"], font=font("Body.ttf", 10), fill=MUTED)
        if c == 0:
            d.rectangle([gx + col_w + 11, gy, gx + col_w + 12, gy + row_h - 8], fill=LIGHT_LINE)
    y += 5 * row_h + 2
    d.rectangle([M, y, W - M, y + 1], fill=RULE)
    y += 8

    # ALSO list: two columns
    af = font("Headline.ttf", 15)
    d.text((M, y), "ALSO ON WEDNESDAY", font=af, fill=INK)
    y += 20
    also = data["also"]
    half = (len(also) + 1) // 2
    row_h = 12
    for i, a in enumerate(also):
        col = 0 if i < half else 1
        row = i if i < half else i - half
        ax = M + col * (col_w + 24)
        ay = y + row * row_h
        num = f"{i + 1:02d} "
        nf = font("BodyBold.ttf", 10)
        d.text((ax, ay), num, font=nf, fill=ACCENT)
        nw = d.textlength(num, font=nf)
        one_line(d, ax + nw, ay, col_w - nw, a["headline"] + "  — " + a["source"],
                 "Body.ttf", 10, INK)
    y += half * row_h + 6

    # DATE CHECK box
    d.rectangle([M, y, W - M, y + 32], outline=ACCENT, width=1)
    df2 = font("BodyBold.ttf", 10)
    d.text((M + 8, y + 4), "DATE CHECK — LEFT OUT ON PURPOSE:", font=df2, fill=ACCENT)
    dc = "  ·  ".join(data["date_check"])
    one_line(d, M + 8, y + 18, W - 2 * M - 16, dc, "Body.ttf", 9, MUTED)
    y += 40

    # Footer
    ff = font("Body.ttf", 10)
    fw = d.textlength(data["footer"], font=ff)
    if fw > W - 2 * M:
        lines = wrap(d, data["footer"], ff, W - 2 * M)
        for ln in lines:
            lw = d.textlength(ln, font=ff)
            d.text(((W - lw) / 2, y), ln, font=ff, fill=MUTED)
            y += 13
    else:
        d.text(((W - fw) / 2, y), data["footer"], font=ff, fill=MUTED)
    return img


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = render(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    if size > 1024 * 1024:
        img.quantize(colors=128, method=Image.Quantize.MEDIANCUT,
                     dither=Image.Dither.NONE).save(out, format="PNG", optimize=True)
        size = os.path.getsize(out)
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"{out}: {size} bytes, {img.size[0]}x{img.size[1]}, sha256={sha}")
    if size > 1024 * 1024:
        sys.exit("entry.png is over 1 MiB")


if __name__ == "__main__":
    main()

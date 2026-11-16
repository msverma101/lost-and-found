#!/usr/bin/env python3
"""Title/info/photo/credit cards (1920x1080) for the LinkedIn cut of LOST & FOUND."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "video/cards"); os.makedirs(OUT, exist_ok=True)
DL = os.path.expanduser("~/Downloads")
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
f = lambda p, s: ImageFont.truetype(p, s)
W, H = 1920, 1080; CREAM = "#E8D9B0"; GREY = "#BDBDBD"
REPO = "msverma101.github.io/lost-and-found"


def photo(name):
    return ImageOps.exif_transpose(Image.open(os.path.join(DL, name))).convert("RGB")


def backdrop(im):
    bg = ImageOps.fit(im, (W, H)).filter(ImageFilter.GaussianBlur(40))
    return Image.blend(bg, Image.new("RGB", (W, H), "black"), 0.6)


def centre(d, y, text, font, fill, x0=0, x1=W):
    d.text(((x0 + x1 - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


# 1. opening: poster-wall photo
p = photo("IMG_20261115_211859.jpg"); c = backdrop(p)
ph = ImageOps.contain(p, (720, 960)); c.paste(ph, (110, (H - ph.height) // 2))
d = ImageDraw.Draw(c); x = 920
d.text((x, 300), "LOST & FOUND", font=f(SERIFB, 96), fill=CREAM)
d.text((x, 430), "my solo concept film, written by AI", font=f(SERIF, 44), fill="white")
d.text((x, 490), "and made with Claude + LetzAI", font=f(SERIF, 44), fill="white")
d.text((x, 620), "FILMHACK.AI · Berlin · 13–15 Nov 2026", font=f(SANS, 34), fill=GREY)
c.save(f"{OUT}/01_open.png")

# 2. to be continued
c = Image.new("RGB", (W, H), "black"); d = ImageDraw.Draw(c)
centre(d, 470, "To be continued…", f(SERIF, 88), CREAM)
c.save(f"{OUT}/02_credits_ran_out.png")

# 3. process on GitHub, with three slide thumbnails
c = Image.new("RGB", (W, H), "black"); d = ImageDraw.Draw(c)
centre(d, 150, "Want to see how it was made?", f(SERIFB, 64), CREAM)
centre(d, 250, "Script, character bible, shot boards, sound: the whole process is on this page", f(SANS, 34), GREY)
for i, n in enumerate(("03.png", "08.png", "13.png")):
    t = Image.open(os.path.join(ROOT, "images/process", n)).convert("RGB").resize((560, 315))
    c.paste(t, (100 + i * 600, 380))
centre(d, 790, REPO, f(SANSB, 56), "white")
c.save(f"{OUT}/03_process.png")

# 4. screening photo with friends
g = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, "images/group_filmhack.jpeg"))).convert("RGB")
c = backdrop(g); a = ImageOps.contain(g, (1240, 860)); top = 60
c.paste(a, ((W - a.width) // 2, top)); d = ImageDraw.Draw(c)
centre(d, top + a.height + 40, "With friends at the final screening · Colosseum Berlin, 15 Nov 2026 · a fun night!", f(SANS, 38), "white")
c.save(f"{OUT}/04_screening.png")

# 5. credits
c = Image.new("RGB", (W, H), "black"); d = ImageDraw.Draw(c)
centre(d, 70, "LOST & FOUND", f(SERIFB, 64), CREAM)
rows = [("Directed by", "Sneha Verma"),
        ("Story, script, shot list, prompts, edit", "Claude by Anthropic"),
        ("Canvas template, image and video generation", "LetzAI"),
        ("Characters, locations, storyboard stills", "Nano Banana Pro (Google DeepMind), via LetzAI"),
        ("Video clips and their sound", "Kling V4 (Kuaishou), via LetzAI"),
        ("Music", "Original music-box waltz, composed in code by Claude"),
        ("Cut and mix", "ffmpeg"),
        ("Made at", "FILMHACK.AI, 48-hour challenge, Berlin, 13–15 Nov 2026"),
        ("Organised by", "FILMAKERS.AI"),
        ("Thank you", "Moritz Erdt · the LetzAI team · my WETLANDS team · my friends"),
        ]
y = 180
for k, v in rows:
    d.text((800 - d.textlength(k, font=f(SANS, 30)), y), k, font=f(SANS, 30), fill=GREY)
    d.text((840, y), v, font=f(SANS, 30), fill="white"); y += 68
centre(d, y + 40, "Powered by LetzAI  ·  All characters are fictional", f(SANS, 28), GREY)
c.save(f"{OUT}/05_credits.png")
print("cards done")

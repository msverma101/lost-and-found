#!/usr/bin/env python3
"""Build the step-by-step slides (1920x1080) of how LOST & FOUND was made on the LetzAI canvas template,
from the section renders in images/canvas_sections, then write process_carousel.pdf."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(ROOT, "images/canvas_sections"); MT = os.path.join(ROOT, "../movie_test")
OUT = os.path.join(ROOT, "images/process"); os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f = lambda s, b=False: ImageFont.truetype(FB if b else F, s)
BG = (11, 11, 13); W, H = 1920, 1080; HEAD = 150
COL = {"01": "#e08a1e", "02": "#14b8a6", "03": "#22c55e", "04": "#3b82f6", "05": "#ef4444", "": "#a1a1aa"}
STEP = {"01": "Brief & script", "02": "Look dev", "03": "Locked bible", "04": "Shot boards", "05": "Animate & deliver"}
sec = lambda n: Image.open(os.path.join(SEC, n)).convert("RGB")


def bg_rows(img):
    a = np.asarray(img).astype(int)
    return (np.abs(a - np.array(BG)).sum(2) > 40).sum(1) <= img.width * 0.012


def split(img, n):
    """Cut a tall image into n parts at background rows and lay them side by side."""
    free = np.where(bg_rows(img))[0]; cuts = [0]
    for k in range(1, n):
        t = img.height * k // n; cuts.append(int(free[np.abs(free - t).argmin()]))
    cuts.append(img.height)
    parts = [img.crop((0, a, img.width, b)) for a, b in zip(cuts, cuts[1:])]
    out = Image.new("RGB", (sum(p.width for p in parts) + 40 * (n - 1), max(p.height for p in parts)), BG); x = 0
    for p in parts:
        out.paste(p, (x, 0)); x += p.width + 40
    return out


def side(*imgs, gap=40):
    out = Image.new("RGB", (sum(i.width for i in imgs) + gap * (len(imgs) - 1), max(i.height for i in imgs)), BG); x = 0
    for i in imgs:
        out.paste(i, (x, (out.height - i.height) // 2)); x += i.width + gap
    return out


n = 0


def slide(step, title, caption, img=None):
    global n
    n += 1
    s = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(s); c = COL[step]
    d.rectangle([0, 0, W, 8], fill=c)
    if step:
        pill = f"STEP {step} · {STEP[step]}".upper(); pw = int(f(24, True).getlength(pill)) + 40
        d.rounded_rectangle([60, 36, 60 + pw, 84], 24, fill=c)
        d.text((80, 44), pill, font=f(24, True), fill="#0b0b0d")
        d.text((60 + pw + 30, 38), title, font=f(40, True), fill="#f4f4f5")
    else:
        d.text((60, 38), title, font=f(40, True), fill="#f4f4f5")
    d.text((60, 100), caption, font=f(24), fill="#a1a1aa")
    if img is not None:
        sc = min((W - 80) / img.width, (H - HEAD - 30) / img.height)
        im = img.resize((int(img.width * sc), int(img.height * sc)), Image.LANCZOS)
        s.paste(im, ((W - im.width) // 2, HEAD + (H - HEAD - 30 - im.height) // 2))
    s.save(os.path.join(OUT, f"{n:02d}.png")); return s


slides = []
# cover
cov = Image.open(os.path.join(MT, "stills/s01_sh06_c0b54850.jpg")).convert("RGB").resize((W, H))
cov = Image.blend(cov, Image.new("RGB", (W, H), BG), 0.55); d = ImageDraw.Draw(cov)
d.text((100, 640), "LOST & FOUND", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 110), fill="#f5e6c8")
d.text((104, 790), "How a 3-minute film was made, step by step, on the LetzAI canvas template", font=f(36), fill="#f4f4f5")
d.text((104, 850), "Story, prompts and edit by Claude · images and video through LetzAI · FILMHACK.AI 2026, Berlin", font=f(26), fill="#d4d4d8")
n += 1; cov.save(os.path.join(OUT, f"{n:02d}.png")); slides.append(cov)

slides.append(slide("01", "The brief", "Constraints first: runtime, formats and the hard no-gos (no real faces, brands or borrowed music). Plus a naming rule and status colours.",
                    split(sec("01_brief_and_script__01_brief.png"), 2)))
slides.append(slide("01", "Logline, beat sheet, script", "Claude wrote the story from scratch: a 7-beat structure with timings, then four short scenes with only two spoken lines.",
                    sec("01_brief_and_script__02_script.png")))
sl = sec("01_brief_and_script__03_shot_list_and_schedule.png")
k = sl.width / 1712
import glob as _g, json as _j
_pg = _j.load(open(_g.glob(os.path.join(ROOT, "canvas_raw/page_6aa4d413.json"))[0]))
_t = next(x["data"]["text"] for x in _pg["nodes"] if x["kind"] == "text" and "S01_SH01" in (x["data"].get("text") or ""))
rows = [l.rstrip() for l in _t.split("\n") if l.startswith("S0")]
rows = [l if l.endswith((".", "!", "?", '"')) else l + "…" for l in rows]
sh = Image.new("RGB", (3000, 1300), "#ffffff"); dd = ImageDraw.Draw(sh); ff = f(30)
for i, l in enumerate(rows):
    x = 30 if i < 14 else 1530; y = 30 + (i % 14) * 88
    sid, scn, dur, desc = l.split(None, 3)
    dd.text((x, y), f"{sid}   {scn} · {dur}", font=f(30, True), fill="#111")
    dd.text((x, y + 38), desc.lstrip("— ").strip(), font=f(26), fill="#333")
slides.append(slide("01", "Shot list (27 shots)", "Every shot gets an ID, scene, length and action; the same text becomes the video prompt.", sh))
style = Image.new("RGB", (1700, 420), BG); d = ImageDraw.Draw(style)
d.text((0, 0), "STYLE BLOCK (pasted into every image prompt)", font=f(30, True), fill="#14b8a6")
d.multiline_text((0, 70), "Photoreal live-action film still, shot on 35mm film, fine grain,\nnatural skin texture, muted palette of moss green, rust orange,\nteal and warm amber.", font=f(40), fill="#f4f4f5", spacing=18)
d.text((0, 300), "Memories (1984): golden haze, heavier grain.   Model for all stills: Nano Banana Pro", font=f(28), fill="#a1a1aa")
slides.append(slide("02", "Look dev, the shortcut", "No time for lighting and lens studies, so the look was fixed in one style block and the bible sheets did the rest.",
                    side(style, sec("02_look_dev__03_palette_and_texture.png").crop((0, 540, 1400, 1341)), gap=80)))

slides.append(slide("03", "Locked characters", "Turnarounds, expressions and wardrobe for Otto (68), young Otto, Ines and Vera. Each sheet records its model and LetzAI ID.",
                    sec("03_locked_bible__01_locked_characters.png")))
rej = Image.open(os.path.join(MT, "bible/a2_young_otto_REJECTED_too_old.jpg")).convert("RGB")
ok = Image.open(os.path.join(MT, "bible/a2_young_otto_sheet_572e3c81.jpg")).convert("RGB")
def label(im, t, c):
    im = im.resize((1376, int(im.height * 1376 / im.width))); out = Image.new("RGB", (im.width, im.height + 80), BG)
    out.paste(im, (0, 80)); ImageDraw.Draw(out).text((0, 10), t, font=f(48, True), fill=c); return out
slides.append(slide("03", "Rejected vs locked", "Young Otto, first try: he looked about 45, so it was rejected. Second try: 25, locked. Nothing gets built on an unlocked sheet.",
                    side(label(rej, "✗ REJECTED: looks 45", "#ef4444"), label(ok, "✓ LOCKED: young Otto, 25", "#22c55e"), gap=60)))
slides.append(slide("03", "Locked locations", "The lost-and-found office and the 1984 dance hall. Every shot in a location starts from this frame.",
                    sec("03_locked_bible__02_locked_locations.png")))
slides.append(slide("03", "Props, vehicle and wardrobe", "The walnut music box (tag 0419), the yellow-and-grey train and a wardrobe note per character, plus the lock rule.",
                    sec("03_locked_bible__03_props_vehicles_and_wardrobe.png")))

sb = sec("04_shot_boards__01_storyboard_with_locked_characters_and_locations.png"); k = sb.width / 2000
cols = [(15, 430), (535, 945), (1050, 1465), (1570, 1985)]
caps = ["Night office: Otto alone with the music box. 6 shots.", "Memory, 1984: the dance, the train, too late. 7 shots.",
        "The counter: Ines brings ticket 0419; 'It isn't here.' 10 shots.", "Resolve: 'She'd want you to have it.' 4 shots."]
grid_h = [560, 700, 830, 440]
for i, (a, b) in enumerate(cols):
    grid = sb.crop((int(a * k), int(150 * k), int(b * k), int(grid_h[i] * k)))
    cov_ = sb.crop((int(a * k), int(870 * k), int(b * k), int(1100 * k)))
    if i in (1, 2):
        grid = split(grid, 2)
    slides.append(slide("04", f"Shot board, scene {i + 1}", caps[i] + " Each still is built from the locked sheets it names.",
                        side(grid, cov_, gap=60)))

dv = sec("05_animate_and_deliver__02_delivery_formats.png")
slides.append(slide("05", "Delivery formats", "16:9 master plus a 9:16 vertical crop. The status notes say honestly what is finished and what is not.",
                    dv.crop((0, 0, int(1100 * dv.width / 2000), dv.height))))
slides.append(slide("05", "Sound and handoff", "A checklist before sending, and the sound plan: original music-box waltz, Kling clip audio, two subtitled lines.",
                    (lambda im: side(im.crop((0, 0, 1320, 1110)), im.crop((0, 1130, 1320, im.height))))(sec("05_animate_and_deliver__03_sound_and_handoff.png"))))
slides.append(slide("05", "The result: every shot", "SH01–SH14 are Kling clips. The last 1.5 minutes (SH15–SH27) are still frames because the hackathon's LetzAI credits ran out.",
                    Image.open(os.path.join(MT, "review/final_sheet.jpg")).convert("RGB")))
for extra in ("06_workflow.png", "07_sound.png"):
    n += 1; im = Image.open(os.path.join(ROOT, "images", extra)).convert("RGB"); im.save(os.path.join(OUT, f"{n:02d}.png")); slides.append(im)

slides[0].save(os.path.join(ROOT, "process_carousel.pdf"), save_all=True, append_images=slides[1:], resolution=150)
print(len(slides), "slides")

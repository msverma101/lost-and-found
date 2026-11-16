#!/usr/bin/env python3
"""Legible renders of the LetzAI canvas "movie test": one image per page and one per column section.
Usage: python3 render_sections.py <canvas_raw dir> <out dir> [scale]"""
import glob, hashlib, json, os, sys, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAW, OUT = sys.argv[1], sys.argv[2]
S = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
CACHE = os.path.join(RAW, "media"); os.makedirs(CACHE, exist_ok=True); os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = (11, 11, 13)
canvas = json.load(open(os.path.join(RAW, "canvas.json")))
order = {p["id"][:8]: (i, p["name"]) for i, p in enumerate(canvas["pages"])}
font = lambda size, bold=False: ImageFont.truetype(FB if bold else F, max(8, int(size)))


def fill_of(d):
    fs = d.get("fills")
    return fs[0].get("color") if fs else d.get("fill")


def media(d):
    url = d.get("url") or d.get("thumbUrl")
    p = os.path.join(CACHE, "full_" + hashlib.md5(url.encode()).hexdigest() + ".jpg")
    if not os.path.exists(p):
        urllib.request.urlretrieve(url, p)
    return Image.open(p).convert("RGB")


def wrap(text, fnt, width):
    out = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            t = (line + " " + word) if line else word
            if fnt.getlength(t) <= width or not line:
                line = t
            else:
                out.append(line); line = word
        out.append(line)
    return "\n".join(out)


def collapse(img, keep=50):
    a = np.asarray(img).astype(int)
    busy = (np.abs(a - np.array(BG)).sum(2) > 40).sum(1) > img.width * 0.012
    rows, run = [], 0
    for y, b in enumerate(busy):
        run = 0 if b else run + 1
        if run <= keep:
            rows.append(y)
    return Image.fromarray(np.asarray(img)[rows])


for f in sorted(glob.glob(os.path.join(RAW, "page_*.json")), key=lambda f: order[os.path.basename(f)[5:13]][0]):
    idx, name = order[os.path.basename(f)[5:13]]
    nodes = sorted(json.load(open(f))["nodes"], key=lambda n: n.get("z", 0))
    box = lambda n: (n["position"]["x"], n["position"]["y"], n["position"]["x"] + (n.get("size") or {}).get("w", 0),
                     n["position"]["y"] + (n.get("size") or {}).get("h", 0))
    bs = [box(n) for n in nodes]
    x0, y0 = min(b[0] for b in bs) - 60, min(b[1] for b in bs) - 60
    x1, y1 = max(b[2] for b in bs) + 60, max(b[3] for b in bs) + 60
    T = lambda x, y: (int((x - x0) * S), int((y - y0) * S))
    img = Image.new("RGB", T(x1, y1), BG); dr = ImageDraw.Draw(img)
    for n in nodes:
        d, k = n["data"], n["kind"]
        a, b = T(*box(n)[:2]), T(*box(n)[2:])
        r = int((d.get("cornerRadius") or 0) * S)
        if k == "shape":
            dr.rounded_rectangle([a, b], r, fill=fill_of(d))
        elif k == "section":
            dr.rounded_rectangle([a, b], r, fill=fill_of(d) or "#141417", outline="#3a3a40", width=2)
            if d.get("title"):
                dr.text((a[0] + 4, a[1] - int(26 * S)), d["title"], fill="#a1a1aa", font=font(18 * S))
        elif k == "line":
            dr.line([T(d["from"]["x"], d["from"]["y"]), T(d["to"]["x"], d["to"]["y"])],
                    fill=d.get("stroke") or "#333", width=max(2, int((d.get("strokeWidth") or 2) * S)))
        elif k == "media":
            im = media(d); w, h = b[0] - a[0], b[1] - a[1]
            img.paste(im.resize((w, h), Image.LANCZOS), a)
        elif k == "text":
            fnt = font((d.get("fontSize") or 16) * S, d.get("bold"))
            txt = wrap(d.get("text") or "", fnt, max(40, b[0] - a[0]))
            dr.multiline_text(a, txt, fill=d.get("textColor") or "#e4e4e7", font=fnt,
                              spacing=int(fnt.size * ((d.get("lineHeight") or 1.3) - 1)))
    slug = name.split("—")[-1].strip().lower().replace(" & ", "_and_").replace(" ", "_")
    tag = f"{idx + 1:02d}_{slug}"
    page = collapse(img)
    page.save(os.path.join(OUT, f"{tag}__00_full_page.png")); print(tag, "page", page.size)
    # columns = coloured heading bands along the top
    top = min(b[1] for b in bs)
    bands = sorted([box(n) for n in nodes if n["kind"] == "shape" and box(n)[1] <= top + 5 and box(n)[2] - box(n)[0] > 300])
    for i, bd in enumerate(bands):
        label = next((n["data"].get("text", "") for n in nodes if n["kind"] == "text"
                      and bd[0] <= n["position"]["x"] <= bd[2] and bd[1] <= n["position"]["y"] <= bd[3]), f"section{i+1}")
        ca, cb = T(bd[0] - 30, y0), T(bd[2] + 30, y1)
        col = collapse(img.crop((max(0, ca[0]), 0, min(img.width, cb[0]), img.height)))
        fn = os.path.join(OUT, f"{tag}__{i + 1:02d}_{label.lower().replace(' & ', '_and_').replace(', ', '_').replace(' — ', '_').replace(' ', '_')}.png")
        col.save(fn); print("  ", os.path.basename(fn), col.size)

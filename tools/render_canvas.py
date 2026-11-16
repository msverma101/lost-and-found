#!/usr/bin/env python3
"""Render each page of the LetzAI canvas "movie test" (LOST & FOUND) to a PNG from its saved JSON.
Usage: python3 render_canvas.py <canvas_raw dir> <out dir>"""
import glob, hashlib, json, os, sys, textwrap, urllib.request
from PIL import Image, ImageDraw, ImageFont

RAW, OUT = sys.argv[1], sys.argv[2]
CACHE = os.path.join(RAW, "media"); os.makedirs(CACHE, exist_ok=True); os.makedirs(OUT, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
canvas = json.load(open(os.path.join(RAW, "canvas.json")))
order = {p["id"][:8]: (i, p["name"]) for i, p in enumerate(canvas["pages"])}


def fill_of(d):
    f = (d.get("fills") or [{}])[0] if d.get("fills") else None
    return f.get("color") if f else d.get("fill")


def media(url):
    p = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest() + ".jpg")
    if not os.path.exists(p):
        urllib.request.urlretrieve(url, p)
    return Image.open(p).convert("RGB")


for f in glob.glob(os.path.join(RAW, "page_*.json")):
    pid = os.path.basename(f)[5:13]
    idx, name = order[pid]
    nodes = sorted(json.load(open(f))["nodes"], key=lambda n: n.get("z", 0))
    xs = [n["position"]["x"] for n in nodes] + [n["position"]["x"] + n["size"]["w"] for n in nodes if n.get("size")]
    ys = [n["position"]["y"] for n in nodes] + [n["position"]["y"] + n["size"]["h"] for n in nodes if n.get("size")]
    pad = 80
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad - 60, max(xs) + pad, max(ys) + pad
    s = min(1.0, 3200 / (x1 - x0))
    W, H = int((x1 - x0) * s), int((y1 - y0) * s)
    img = Image.new("RGB", (W, H), "#0b0b0d"); dr = ImageDraw.Draw(img)
    step = max(12, int(40 * s))
    for gx in range(0, W, step):
        for gy in range(0, H, step):
            dr.point((gx, gy), fill="#26262b")
    T = lambda x, y: (int((x - x0) * s), int((y - y0) * s))
    for n in nodes:
        d, k = n["data"], n["kind"]
        x, y = n["position"]["x"], n["position"]["y"]
        w, h = (n.get("size") or {}).get("w", 0), (n.get("size") or {}).get("h", 0)
        a, b = T(x, y), T(x + w, y + h)
        r = int((d.get("cornerRadius") or 0) * s)
        if k == "shape":
            dr.rounded_rectangle([a, b], r, fill=fill_of(d) or None, outline=(d.get("stroke") or {}).get("color") if isinstance(d.get("stroke"), dict) else None)
        elif k == "section":
            dr.rounded_rectangle([a, b], r, fill=fill_of(d) or "#16161a", outline="#3a3a40", width=max(1, int(2 * s)))
            if d.get("title"):
                dr.text((a[0] + 4, a[1] - int(30 * s) - 4), d["title"], fill="#a1a1aa", font=ImageFont.truetype(FONT, max(11, int(24 * s))))
        elif k == "line":
            dr.line([T(d["from"]["x"], d["from"]["y"]), T(d["to"]["x"], d["to"]["y"])], fill=d.get("stroke", "#555"), width=max(1, int(d.get("strokeWidth", 2) * s)))
        elif k == "media":
            try:
                im = media(d.get("thumbUrl") or d["url"])
                im = im.resize((max(1, b[0] - a[0]), max(1, b[1] - a[1])))
                img.paste(im, a)
            except Exception as e:
                dr.rectangle([a, b], outline="#666"); print("media failed", e)
        elif k == "text":
            fs = max(9, int((d.get("fontSize") or 20) * s))
            font = ImageFont.truetype(FONTB if d.get("bold") else FONT, fs)
            cw = max(8, int((b[0] - a[0]) / (fs * 0.55)))
            txt = "\n".join(textwrap.fill(line, cw) if line else "" for line in (d.get("text") or "").split("\n"))
            dr.multiline_text(a, txt, fill=d.get("textColor") or "#e4e4e7", font=font, spacing=int(fs * 0.4))
    dr.text((16, 12), f"LetzAI canvas · movie test · {name}", fill="#f4f4f5", font=ImageFont.truetype(FONTB, 30))
    out = os.path.join(OUT, f"canvas_{idx + 1:02d}_{name.split('—')[-1].strip().lower().replace(' ', '_').replace('&', 'and')}.png")
    img.save(out); print(out, img.size)

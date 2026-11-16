#!/usr/bin/env python3
"""letz: generate images and videos with the LetzAI API (https://letz.ai/docs/api).

Examples:
  letz.py image "wet Berlin courtyard at dawn, low angle, 35mm" --ar 16:9
  letz.py video "she turns towards the window" --image still.jpg --duration 5
  letz.py video "a tram passes, camera pans left" --model video-seedance25 --res 720p
  letz.py edit "make it night, add a lit window" --image still.jpg
  letz.py upload selfie.jpg          # gives a URL usable as --image
  letz.py models                     # models and credit prices
  letz.py status video <id>          # check or re-download a job

The key is read from ~/.config/letzai/api_key (or $LETZAI_API_KEY).
Credits come from the organization in ~/.config/letzai/org_id
(or $LETZAI_ORG_ID); pass --personal to use your own account instead.
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.letz.ai"
CATALOG = "https://letz.ai/docs/models.json"
CONF = Path.home() / ".config" / "letzai"
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
# Resolution name -> the "mode" value each image model family expects.
GEMINI_MODES = {"1k": "default", "2k": "2k", "hd": "2k", "4k": "4k"}


def conf(name, env):
    if os.environ.get(env):
        return os.environ[env].strip()
    f = CONF / name
    return f.read_text().strip() if f.exists() else None


def call(method, path, body=None, auth=True, url=None):
    headers = {"Accept": "application/json", "User-Agent": "letz-cli"}
    if auth:
        key = conf("api_key", "LETZAI_API_KEY")
        if not key:
            sys.exit("No API key: put it in ~/.config/letzai/api_key")
        headers["Authorization"] = "Bearer " + key
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url or API + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"LetzAI refused the request ({e.code}): {e.read().decode(errors='replace')[:800]}")
    return json.loads(raw) if raw else {}


def org(args):
    return None if args.personal else conf("org_id", "LETZAI_ORG_ID")


def with_org(body, args):
    o = org(args)
    if o:
        body["organizationId"] = o
    return body


def upload(path):
    """Upload a local file and return its public URL."""
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    rec = call("POST", "/user-assets", {
        "extension": p.suffix.lstrip(".").lower(),
        "originalFilename": p.name,
        "mimeType": mime,
        "fileSize": p.stat().st_size,
    })
    req = urllib.request.Request(rec["uploadUrl"], data=p.read_bytes(),
                                 headers={"Content-Type": mime}, method="PUT")
    try:
        urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Upload failed ({e.code}): {e.read().decode(errors='replace')[:400]}")
    url = rec.get("imageUrl") or rec.get("url")
    if not url:
        sys.exit("Upload gave no URL: " + json.dumps(rec)[:400])
    return url


def source(value):
    """Turn --image input into ('id', uuid) or ('url', url); local files are uploaded."""
    if UUID.match(value):
        return "id", value
    if value.startswith(("http://", "https://")):
        return "url", value
    if not Path(value).exists():
        sys.exit(f"Not a file, URL or LetzAI image id: {value}")
    print(f"Uploading {value} ...", file=sys.stderr)
    return "url", upload(value)


def size_for(ar, long_side=1600):
    w, h = (float(x) for x in ar.split(":"))
    if w >= h:
        W, H = long_side, long_side * h / w
    else:
        W, H = long_side * w / h, long_side
    return max(480, int(round(W / 16) * 16)), max(480, int(round(H / 16) * 16))


def find_url(obj, key):
    """Result URL: <key>.original, wherever the job object keeps it."""
    v = obj.get(key) or {}
    if isinstance(v, dict) and v.get("original"):
        return v["original"]
    for nested in ("generatedImageCompletion",):
        if isinstance(obj.get(nested), dict):
            u = find_url(obj[nested], key)
            if u:
                return u
    # Image edits keep their results in a list of choices.
    for choice in obj.get("imageCompletionChoices") or []:
        if isinstance(choice, dict):
            u = find_url(choice, key)
            if u:
                return u
    return None


def wait(kind, job_id, timeout):
    path = {"image": "/images/", "video": "/videos/", "edit": "/image-edits/",
            "upscale": "/upscale/"}[kind] + job_id
    key = "videoVersions" if kind == "video" else "imageVersions"
    start, last = time.time(), None
    while True:
        j = call("GET", path)
        st = j.get("status")
        line = f"{st} {j.get('progress', '')}%"
        if line != last:
            print(f"  {line}", file=sys.stderr)
            last = line
        if st in ("ready", "saved") and find_url(j, key):
            return j, find_url(j, key)
        if st in ("failed", "interrupted", "not_allowed"):
            sys.exit(f"Job {job_id} ended as '{st}': {j.get('progressMessage') or ''}")
        if time.time() - start > timeout:
            sys.exit(f"Still '{st}' after {timeout}s. Check later with: letz.py status {kind} {job_id}")
        time.sleep(3 if kind != "video" else 8)


def save(url, out_dir, name, job_id):
    ext = Path(url.split("?")[0]).suffix or ".bin"
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40] or "letz"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{slug}_{job_id[:8]}{ext}"
    req = urllib.request.Request(url, headers={"User-Agent": "letz-cli"})
    with urllib.request.urlopen(req, timeout=600) as r:
        dest.write_bytes(r.read())
    return dest


def finish(kind, job, args, label):
    job_id = job["id"]
    print(f"Started {kind} {job_id}", file=sys.stderr)
    if args.no_wait:
        print(job_id)
        return
    _, url = wait(kind, job_id, args.timeout)
    dest = save(url, args.out, args.name or label, job_id)
    print(f"{dest}\n  id:  {job_id}\n  url: {url}")


def cmd_image(args):
    w, h = size_for(args.ar)
    body = {"prompt": args.prompt, "width": w, "height": h, "quality": args.quality,
            "creativity": args.creativity, "hasWatermark": args.watermark}
    if args.model:
        body["baseModel"] = args.model
    if args.res:
        gem = args.model and ("gemini" in args.model or "nano" in args.model or "nbf" in args.model)
        body["mode"] = GEMINI_MODES.get(args.res, args.res) if gem else args.res
    with_org(body, args)
    for _ in range(args.n):
        finish("image", call("POST", "/images", body), args, args.prompt)


def cmd_video(args):
    settings = {"mode": args.model, "duration": args.duration}
    if args.res:
        settings["resolution"] = args.res
    if args.sound:
        settings["withSound"] = True
    body = {"prompt": args.prompt, "settings": settings}
    frames = [source(v) for v in (args.image, args.last) if v]
    if len(frames) == 1 and frames[0][0] == "id":
        body["originalImageCompletionId"] = frames[0][1]
    elif len(frames) == 1:
        body["imageUrl"] = frames[0][1]
    elif frames:
        if any(k == "id" for k, _ in frames):
            sys.exit("With --last, give both frames as files or URLs, not LetzAI ids.")
        body["imageUrls"] = [v for _, v in frames]
    # Always state the shape: without it some models return portrait video
    # even from a landscape first frame.
    short = {"4k": 2160, "2k": 1440}.get(args.res.lower()) or int(re.sub(r"\D", "", args.res) or 720)
    w, h = (float(x) for x in args.ar.split(":"))
    even = lambda v: int(round(v / 2) * 2)
    body["width"], body["height"] = (even(short * w / h), short) if w >= h else (short, even(short * h / w))
    with_org(body, args)
    finish("video", call("POST", "/videos", body), args, args.prompt)


def cmd_edit(args):
    settings = {"aspect_ratio": args.ar, "resolution": args.res}
    if args.model:
        settings["model"] = args.model
    body = {"mode": "context", "prompt": args.prompt, "imageCompletionsCount": 1,
            "settings": settings}
    if args.model:
        body["baseModel"] = args.model
    srcs = [source(v) for v in args.image]
    if len(srcs) == 1 and srcs[0][0] == "id":
        body["originalImageCompletionId"] = srcs[0][1]
    elif any(k == "id" for k, _ in srcs):
        sys.exit("With several --image inputs, give files or URLs, not LetzAI ids.")
    else:
        body["inputImageUrls"] = [v for _, v in srcs]
    with_org(body, args)
    finish("edit", call("POST", "/image-edits", body), args, args.prompt)


def cmd_upload(args):
    for f in args.files:
        print(upload(f))


def cmd_status(args):
    key = "videoVersions" if args.kind == "video" else "imageVersions"
    path = {"image": "/images/", "video": "/videos/", "edit": "/image-edits/",
            "upscale": "/upscale/"}[args.kind] + args.id
    j = call("GET", path)
    url = find_url(j, key)
    print(f"{j.get('status')} {j.get('progress', '')}%  {j.get('progressMessage') or ''}")
    if url:
        print(f"{save(url, args.out, args.name or j.get('prompt') or args.kind, args.id)}\n  url: {url}")


def cmd_models(args):
    cat = call("GET", None, auth=False, url=CATALOG)["models"]
    rows = {"image": [], "video": []}
    for key, m in cat.items():
        if not m.get("active"):
            continue
        caps = m.get("capabilities", {})
        if "generation" in caps:
            api_name = m.get("frontend", {}).get("baseModel", key)
            price = ", ".join(f"{k} {v}" for k, v in caps["generation"]["pricing"].items()
                              if k in ("1k", "1.5k", "2k", "4k", "_flat"))
            rows["image"].append((api_name, m["displayName"], price + " credits"))
        if "video" in caps:
            v = caps["video"]
            price = ", ".join(f"{k[10:]} {p}" for k, p in v["pricing"].items()
                              if k.startswith("_perSecond") and len(k) > 10)
            d = v.get("duration", {})
            rows["video"].append((key, m["displayName"],
                                  f"{d.get('min')}-{d.get('max')} s; credits per second: {price}"))
    for kind, flag in (("image", "--model for image"), ("video", "--model for video")):
        print(f"\n{flag}:")
        for name, label, info in rows[kind]:
            print(f"  {name:<34} {label:<28} {info}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-o", "--out", default="letz_out", help="folder for downloads (default: ./letz_out)")
    common.add_argument("--name", help="file name stem (default: from the prompt)")
    common.add_argument("--no-wait", action="store_true", help="start the job and print its id only")
    common.add_argument("--timeout", type=int, default=1500, help="seconds to wait (default 1500)")
    common.add_argument("--personal", action="store_true", help="spend your own credits, not the organization's")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("image", parents=[common], help="text to image")
    s.add_argument("prompt")
    s.add_argument("--model", help="base model, e.g. gemini-3-pro-image, seedream-5-5 (default: account default)")
    s.add_argument("--ar", default="16:9", help="aspect ratio (default 16:9)")
    s.add_argument("--res", help="resolution tier: 1k, 2k, 4k (default: the model's own)")
    s.add_argument("--quality", type=int, default=2, help="1-6 (default 2)")
    s.add_argument("--creativity", type=int, default=2, help="1-6 (default 2)")
    s.add_argument("--watermark", action="store_true", help="add the LetzAI watermark")
    s.add_argument("-n", type=int, default=1, help="number of images")
    s.set_defaults(fn=cmd_image)

    s = sub.add_parser("video", parents=[common], help="text or image to video")
    s.add_argument("prompt")
    s.add_argument("--image", help="first frame: file, URL or LetzAI image id")
    s.add_argument("--last", help="last frame: file or URL")
    s.add_argument("--model", default="video-kling4", help="video mode (default video-kling4)")
    s.add_argument("--duration", type=int, default=5, help="seconds (default 5)")
    s.add_argument("--res", default="720p", help="720p, 1080p ... (default 720p)")
    s.add_argument("--ar", default="16:9", help="aspect ratio (default 16:9; use 9:16 for portrait)")
    s.add_argument("--sound", action="store_true", help="ask for sound on models where it is optional")
    s.set_defaults(fn=cmd_video)

    s = sub.add_parser("edit", parents=[common], help="edit one or more images with a prompt")
    s.add_argument("prompt")
    s.add_argument("--image", action="append", required=True, help="file, URL or id; repeat for up to 9 references")
    s.add_argument("--model", help="e.g. gemini-3-pro-image-preview (default: platform default)")
    s.add_argument("--ar", default="16:9")
    s.add_argument("--res", default="2k", help="2k (90 credits) or 4k (180)")
    s.set_defaults(fn=cmd_edit)

    s = sub.add_parser("upload", help="upload local files, print their URLs")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_upload)

    s = sub.add_parser("status", parents=[common], help="check a job and download it if ready")
    s.add_argument("kind", choices=["image", "video", "edit", "upscale"])
    s.add_argument("id")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("models", help="list models and credit prices")
    s.set_defaults(fn=cmd_models)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

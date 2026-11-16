#!/usr/bin/env python3
"""Build the prompt and reference list for one shot from the project cards.

  python3 shot.py            list the shots
  python3 shot.py 2A         keyframe (still) command for shot 2A
  python3 shot.py 2A --video video command, animating the shot's keyframe

Reads 06_shots.csv, 01_look/look.md, 02_characters/<name>/character.md and
03_locations/<name>/location.md. Each card's "## Prompt block" paragraph is
pasted in word for word, and its "## References" list supplies the images.
Prints a letz.py command; nothing is generated until you run it.
"""
import csv
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LETZ = HERE.parent / "letz.py"


def section(path, title):
    text = path.read_text()
    m = re.search(rf"^## {title}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def card(kind, name):
    path = HERE / kind / name / ("character.md" if kind == "02_characters" else "location.md")
    if not path.exists():
        sys.exit(f"No card: {path.relative_to(HERE)}")
    return path


def block(path):
    lines = [l.lstrip("> ").strip() for l in section(path, "Prompt block").splitlines()
             if l.startswith(">")]
    return " ".join(lines).rstrip(".")


def refs(path):
    out = []
    for line in section(path, "References").splitlines():
        m = re.match(r"\s*-\s+(\S+)", line)
        if not m:
            continue
        ref = m.group(1)
        local = path.parent / ref
        if local.exists():
            out.append(str(local))
        elif ref.startswith(("http://", "https://")) or re.fullmatch(r"[0-9a-f-]{36}", ref):
            out.append(ref)
        else:
            print(f"Warning: missing reference {local.relative_to(HERE)}, skipped", file=sys.stderr)
    return out


def names(cell):
    return [n.strip() for n in cell.replace(";", ",").split(",") if n.strip()]


def main():
    rows = list(csv.DictReader(open(HERE / "06_shots.csv")))
    if len(sys.argv) < 2:
        for r in rows:
            print(f"{r['id']:<5} {r['status']:<8} {r['camera'][:40]:<40}  {r['action'][:60]}")
        return
    shot = next((r for r in rows if r["id"] == sys.argv[1]), None)
    if not shot:
        sys.exit(f"No shot {sys.argv[1]} in 06_shots.csv")
    video = "--video" in sys.argv

    look = HERE / "01_look" / "look.md"
    chars = [card("02_characters", n) for n in names(shot["characters"])]
    loc = card("03_locations", shot["location"]) if shot["location"] else None

    parts = [shot["camera"]]
    for c in chars:
        parts.append(f"{c.parent.name.capitalize()}: {block(c)}")
    parts.append(shot["action"])
    if loc:
        parts.append(f"Location: {block(loc)}")
    parts.append(block(look))
    if video:
        sound = shot["sound"]
        if shot["dialogue"]:
            sound = f"{sound}. Dialogue: {shot['dialogue']}"
        if sound:
            parts.append(f"Sound: {sound}")
    prompt = ". ".join(p.strip().rstrip(".") for p in parts if p.strip()) + "."

    print(f"Shot {shot['id']} ({'video' if video else 'keyframe'})\n\n{prompt}\n")
    if video:
        kf = shot["keyframe"]
        if not kf:
            sys.exit("No keyframe yet: make and approve the still first, then put its "
                     "file, URL or LetzAI id in the keyframe column.")
        cmd = ["python3", str(LETZ), "video", prompt, "--image", kf,
               "--model", shot["model"] or "video-kling4",
               "--duration", shot["duration"] or "5", "--sound",
               "-o", str(HERE / "clips"), "--name", shot["id"]]
    else:
        stack = [r for c in chars for r in refs(c)[:1]]
        if loc:
            stack += refs(loc)[:1]
        stack += refs(look)[:1]
        stack = stack[:9]
        print("References:\n" + "\n".join(f"  {r}" for r in stack) + "\n")
        cmd = ["python3", str(LETZ), "edit", prompt]
        for r in stack:
            cmd += ["--image", r]
        cmd += ["--model", "gemini-3-pro-image", "--res", "1k",
                "-o", str(HERE / "keyframes"), "--name", shot["id"]]
    print(" ".join(shlex.quote(c) for c in cmd))


if __name__ == "__main__":
    main()

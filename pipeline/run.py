#!/usr/bin/env python3
"""python3 run.py stills [ids]  |  python3 run.py clips [ids]   (ids default: all missing)
Stills: Nano Banana Pro edit from the locked bible refs -> stills/<id>.jpg
Clips:  Kling V4 720p from the still                   -> clips/<id>.mp4
Every job is appended to log.md."""
import concurrent.futures as cf, glob, os, re, subprocess, sys
import time
from shots import BIBLE_URL as BIBLE, SHOTS, RULE

os.chdir(os.path.dirname(os.path.abspath(__file__)))
LETZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "letz.py")


def run(cmd, logname):
    for attempt in range(8):
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = p.stdout + p.stderr
        if "(429)" not in out:
            break
        time.sleep(20 + 15 * attempt)
    open(logname, "w").write(out)
    m = re.search(r"id:\s+(\S+)", out)
    return p.returncode, (m.group(1) if m else "-"), out


def newest(folder, stem):
    files = sorted(glob.glob(f"{folder}/{stem.lower()}*"), key=os.path.getmtime)
    return files[-1] if files else None


def still(s):
    sid, _, _, refs, prompt, _ = s
    cmd = [LETZ, "edit", prompt + " " + RULE, "--model", "gemini-3-pro-image", "--ar", "16:9",
           "-o", "stills", "--name", sid]
    for r in refs:
        cmd += ["--image", BIBLE[r]]
    rc, jid, out = run(cmd, f"stills/{sid}.log")
    f = newest("stills", sid + "_")
    return sid, "still", jid, f if rc == 0 else "FAILED: " + out[-200:].replace("\n", " ")


def clip(s):
    sid, _, sec, _, _, motion = s
    img = newest("stills", sid + "_")
    if not img:
        return sid, "clip", "-", "no still"
    speech = '"' in motion
    prompt = motion + (" Natural ambient room sound only, no music." if not speech else " No music.")
    cmd = [LETZ, "video", prompt, "--image", img, "--model", "video-kling4", "--duration", str(sec),
           "--res", "720p", "-o", "clips", "--name", sid, "--sound"]
    rc, jid, out = run(cmd, f"clips/{sid}.log")
    f = newest("clips", sid + "_")
    return sid, "clip", jid, f if rc == 0 else "FAILED: " + out[-200:].replace("\n", " ")


def main():
    kind, ids = sys.argv[1], sys.argv[2:]
    folder = "stills" if kind == "stills" else "clips"
    todo = [s for s in SHOTS if (s[0] in ids) or (not ids and not newest(folder, s[0] + "_"))]
    fn = still if kind == "stills" else clip
    with cf.ThreadPoolExecutor(3) as ex, open("log.md", "a") as log:
        for sid, k, jid, res in ex.map(fn, todo):
            line = f"| {sid} | {k} | {'Nano Banana Pro' if k == 'still' else 'Kling V4 720p'} | {jid} | {res} |"
            print(line, flush=True)
            log.write(line + "\n")


if __name__ == "__main__":
    main()

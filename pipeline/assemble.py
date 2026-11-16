#!/usr/bin/env python3
"""Cut LOST & FOUND: clips/ + audio/ -> out/lost_and_found_16x9.mp4 and out/lost_and_found_9x16.mp4.
Missing clips are replaced by their still (slow zoom) so the cut always runs."""
import glob, os, subprocess, sys
MIX_ONLY = '--mix-only' in sys.argv
from shots import SHOTS

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("out/parts", exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
V = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,setsar=1"
ENC = ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

# clip-audio level per shot: memories quiet, dialogue/hum/bell full
LEVEL = {sid: 0.45 for sid, *_ in SHOTS}
for sid in ("S02_SH07", "S02_SH08", "S02_SH09", "S02_SH10", "S02_SH11", "S02_SH12"):
    LEVEL[sid] = 0.12
for sid in ("S03_SH14", "S03_SH18", "S03_SH19", "S04_SH24"):
    LEVEL[sid] = 1.0
# dip to black in/out around the memory
FADE_OUT = {"S01_SH06": 0.8, "S02_SH12": 0.8}
FADE_IN = {"S01_SH01": 1.5, "S02_SH07": 0.8, "S02_SH13": 0.8}


def sh(cmd):
    subprocess.run(cmd, check=True)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).strip())


def has_audio(f):
    return bool(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a",
                                         "-show_entries", "stream=index", "-of", "csv=p=0", f]).strip())


parts, times, t = [], {}, 0.0
for sid, sc, sec, *_ in SHOTS:
    clips = sorted(glob.glob(f"clips/{sid.lower()}_*.mp4"), key=os.path.getmtime)
    out = f"out/parts/{sid}.mp4"
    if clips:
        src = clips[-1]
        d = min(dur(src), sec)
    else:
        src = sorted(glob.glob(f"stills/{sid.lower()}_*.jpg"))[-1]
        d = float(sec)
        print("NO CLIP, using still:", sid)
    if MIX_ONLY and os.path.exists(out):
        d = dur(out)
        times[sid] = (t, d); t += d; parts.append(out)
        continue
    vf = V
    if sid in FADE_IN:
        vf += f",fade=t=in:d={FADE_IN[sid]}"
    if sid in FADE_OUT:
        vf += f",fade=t=out:st={d - FADE_OUT[sid]:.2f}:d={FADE_OUT[sid]}"
    if clips and has_audio(src):
        a = ["-af", f"volume={LEVEL[sid]},afade=t=in:d=0.05,afade=t=out:st={d - 0.08:.2f}:d=0.08"]
        sh(["ffmpeg", "-v", "error", "-y", "-t", f"{d:.3f}", "-i", src, "-vf", vf, *a, "-t", f"{d:.3f}", *ENC, out])
    elif clips:
        sh(["ffmpeg", "-v", "error", "-y", "-t", f"{d:.3f}", "-i", src, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf, "-map", "0:v", "-map", "1:a", "-t", f"{d:.3f}", *ENC, out])
    else:
        motion = next(s[5] for s in SHOTS if s[0] == sid)
        sub = ""
        if '"' in motion:  # no clip means no spoken line: show it as a subtitle
            line = motion.split('"')[1].replace("'", "’").replace(":", r"\:")
            sub = (f",drawtext=fontfile={FONT}:text='{line}':fontsize=46:fontcolor=white:borderw=3:"
                   f"bordercolor=black@0.8:x=(w-tw)/2:y=h-140:enable='between(t,1.5,{d - 1})'")
        sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", src, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", f"scale=2112:-2,zoompan=z='1+0.0006*on':d=1:s=1920x1080:fps=24{sub},format=yuv420p,setsar=1",
            "-map", "0:v", "-map", "1:a", "-t", f"{d:.3f}", *ENC, out])
    times[sid] = (t, d)
    t += d
    parts.append(out)

# end title + credits
title_len, cred_len = 7.0, 8.0
txt = lambda s: s.replace(":", r"\:").replace("'", "’")
sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=24:d={title_len}",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
    "-vf", f"drawtext=fontfile={FONTB}:text='LOST & FOUND':fontsize=110:fontcolor=0xE8D9B0:x=(w-tw)/2:y=(h-th)/2,"
           f"fade=t=in:d=1.2,fade=t=out:st={title_len - 1}:d=1,format=yuv420p",
    "-map", "0:v", "-map", "1:a", "-t", str(title_len), *ENC, "out/parts/zz_title.mp4"])
credits = ["Written, directed and edited with Claude", "Images: Nano Banana Pro  ·  Video: Kling V4",
           "Powered by LetzAI", "Made at the AI FILMHACK 2026", "Original music-box score composed in code",
           "All characters are fictional."]
dt = ",".join(f"drawtext=fontfile={FONT}:text='{txt(c)}':fontsize=40:fontcolor=0xD8D8D8:x=(w-tw)/2:y={300 + i * 80}"
              for i, c in enumerate(credits))
sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=24:d={cred_len}",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
    "-vf", f"{dt},fade=t=in:d=0.8,fade=t=out:st={cred_len - 1}:d=1,format=yuv420p",
    "-map", "0:v", "-map", "1:a", "-t", str(cred_len), *ENC, "out/parts/zz_credits.mp4"])
parts += ["out/parts/zz_title.mp4", "out/parts/zz_credits.mp4"]
times["TITLE"] = (t, title_len)
total = t + title_len + cred_len

with open("out/parts/list.txt", "w") as f:
    f.writelines(f"file '{os.path.basename(p)}'\n" for p in parts)
sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "out/parts/list.txt", "-c", "copy",
    "out/picture_cut.mp4"])

# score: theme from the first wind (SH06) fading out over SH13; theme_end from the box opening (SH22) to the end,
# ducked under Ines' line (SH24)
a_start, _ = times["S01_SH06"]
a_end = times["S02_SH13"][0] + times["S02_SH13"][1]
b_start = times["S03_SH22"][0]
d24s, d24 = times["S04_SH24"]
b_len = total - b_start
# rain + room tone from the office clips, looped under every shot that had to use a still
amb = [c for c in sorted(glob.glob("clips/s01_sh0[234]_*.mp4"))]
sh(["ffmpeg", "-v", "error", "-y", *sum((["-i", c] for c in amb), []), "-filter_complex",
    "".join(f"[{i}:a]" for i in range(len(amb))) + f"concat=n={len(amb)}:v=0:a=1,aresample=48000[a]",
    "-map", "[a]", "audio/ambience.wav"])
nostill = [sid for sid, *_ in SHOTS if not glob.glob(f"clips/{sid.lower()}_*.mp4")]
amb_start = times[nostill[0]][0] if nostill else t
amb_len = t - amb_start
mix = (
    f"[3:a]atrim=0:{amb_len:.2f},afade=t=in:d=0.5,afade=t=out:st={max(amb_len - 2, 0):.2f}:d=2,volume=0.4,"
    f"adelay={int(amb_start * 1000)}|{int(amb_start * 1000)}[m3];"

    f"[1:a]atrim=0:{a_end - a_start:.2f},afade=t=in:d=2,afade=t=out:st={a_end - a_start - 4:.2f}:d=4,"
    f"volume=0.55,adelay={int(a_start * 1000)}|{int(a_start * 1000)}[m1];"
    f"[2:a]atrim=0:{b_len:.2f},afade=t=in:d=1.5,afade=t=out:st={b_len - 3:.2f}:d=3,"
    f"volume='if(between(t,{d24s - b_start:.2f},{d24s - b_start + d24:.2f}),0.18,0.55)':eval=frame,"
    f"adelay={int(b_start * 1000)}|{int(b_start * 1000)}[m2];"
    f"[0:a][m1][m2][m3]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.9[a]"
)
sh(["ffmpeg", "-v", "error", "-y", "-i", "out/picture_cut.mp4", "-i", "audio/theme.wav", "-i", "audio/theme_end.wav", "-stream_loop", "-1", "-i", "audio/ambience.wav",
    "-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "out/lost_and_found_16x9.mp4"])
# 9:16 cutdown: centre crop
sh(["ffmpeg", "-v", "error", "-y", "-i", "out/lost_and_found_16x9.mp4", "-vf",
    "crop=608:1080:(iw-608)/2:0,scale=1080:1920,setsar=1", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
    "-c:a", "copy", "out/lost_and_found_9x16.mp4"])
print(f"done: {total:.1f}s")
for k, (s, d) in times.items():
    print(f"  {k}  {s:6.1f}s  +{d:.1f}")

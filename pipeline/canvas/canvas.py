# Canvas, page and node IDs are replaced with placeholders. Put your own canvas IDs here.
#!/usr/bin/env python3
"""Fill the LetzAI canvas "movie test" with LOST & FOUND. python3 canvas/canvas.py [p1|p3|p4|p5text]"""
import json, os, sys, urllib.request

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.getcwd())
KEY = open(os.path.expanduser("~/.config/letzai/api_key")).read().strip()
C = "<id-5>"
P1, P2, P3, P4, P5 = ("<id-6>", "<id-16>",
                      "<id-10>", "<id-11>",
                      "<id-13>")


def api(method, path, body=None):
    req = urllib.request.Request(f"https://api.letz.ai/canvas/{C}/{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"{}")


def body(text, fs=22, color="#e4e4e7"):
    return {"text": text, "variant": "body", "fontSize": fs, "textColor": color, "bold": False,
            "italic": False, "underline": False, "runs": None, "lineHeight": 1.45}


def patch(page, node, text, fs=22):
    api("PATCH", f"pages/{page}/nodes/{node}", {"data": body(text, fs)})


def create(page, nodes):
    for i in range(0, len(nodes), 25):
        api("POST", f"pages/{page}/nodes/batch", {"nodes": nodes[i:i + 25]})
    print(page[:8], "created", len(nodes))


def p1():
    from shots import SHOTS
    patch(P1, "<id-15>",
          "Deliverable: short film LOST & FOUND, 16:9 master + 9:16 cutdown\nRuntime: ~3:00\n"
          "Aspect ratio: 16:9, 1920x1080, 24 fps\nDelivery date: 15 Nov 2026 (AI Filmhack)\n\n"
          "Hard no-gos: no real people's faces or voices, no brands/logos (train line is fictional "
          "'Linie Nord'), no film/artist names in prompts, no copyrighted music (score is original).", 20)
    patch(P1, "<id-3>",
          "LOGLINE\nA lonely night clerk at a city lost-and-found office has kept one unclaimed music box for "
          "40 years; when a young woman finally comes to claim it, he must give back the last piece of the "
          "woman he loved.\n\nTREATMENT\nRain, the last train. In a tiled office full of forgotten things, OTTO "
          "(68) tags umbrellas and gloves, then unlocks a drawer and winds a walnut music box. Its melody takes "
          "him to 1984: dancing with VERA; Vera on a night train leaving the box on the seat; young Otto too late "
          "on the platform. The bell rings. INES (32) holds a 40-year-old claim ticket: 0419. Otto lies: it isn't "
          "here. Leaving, she hums the melody. He gives her the box. Inside is a note: 'For O.' Vera meant it for "
          "him. Ines gives him the note and leaves the box. Otto winds it as a train passes.\n\n"
          "TONE\nTender, quiet, bittersweet. Warm amber lamp against cold fluorescent; memories in golden haze.", 19)
    patch(P1, "<id-9>",
          "1. Open — last train leaves, the office window glows (0:00)\n\n2. Establish — Otto tags lost things, "
          "unlocks the music box (0:08)\n\n3. Turn — 1984: the dance, the train, too late (0:39)\n\n4. Escalate — "
          "the bell; Ines and ticket 0419; 'It isn't here.' (1:22)\n\n5. Peak — she hums the melody; he gives "
          "the box; the note 'For O.' (1:51)\n\n6. Resolve — 'She'd want you to have it.' (2:20)\n\n7. End card — "
          "Otto winds the box as a train passes; title (2:39)", 20)
    patch(P1, "<id-12>",
          "SCENE 1 — INT. LOST-AND-FOUND OFFICE — NIGHT\nRain. OTTO tags an umbrella, shelves a teddy, unlocks a "
          "drawer, winds a walnut music box. Amber light on his wet eyes.\n\nSCENE 2 — INT. DANCE HALL / TRAIN / "
          "EXT. PLATFORM — NIGHT (1984)\nYoung OTTO and VERA dance. Vera leaves the box on a train seat. Young "
          "Otto arrives as the doors close.\n\nSCENE 3 — INT. OFFICE — NIGHT\nThe bell. INES holds out ticket 0419.\n"
          "OTTO\nIt isn't here.\nShe leaves, humming the melody. He slides the box across. Inside: 'For O.'\n\n"
          "SCENE 4 — INT./EXT. OFFICE — NIGHT\nINES\nShe'd want you to have it.\nShe leaves. Otto winds the box; "
          "a train passes.", 17)
    rows = "\n".join(f"{s[0]}  S{s[1]}  {s[2]}s  — {s[5][:90]}" for s in SHOTS)
    create(P1, [{"kind": "text", "position": {"x": 5440, "y": 184}, "size": {"w": 1500, "h": 1900},
                 "data": body("SHOT LIST (all 27; lens/move in each prompt; status: LOCKED stills, Kling V4 720p clips)\n\n"
                              + rows, 16)},
                {"kind": "text", "position": {"x": 3600, "y": 2200}, "size": {"w": 1600, "h": 200},
                 "data": body("SCHEDULE — 15 Nov 2026, one unit (Claude + LetzAI, AI Filmhack credits)\n"
                              "Bible 13:35 · Stills 13:45 · Kling clips 14:00 · Score + mix + cut after clips · "
                              "Location: LetzAI only, no shoot.", 18)}])


def p2():
    patch(P2, "<id-8>",
          "Look dev was skipped for time: the look was set directly in the bible prompts and one style block "
          "(photoreal 35mm, fine grain, muted moss green / rust orange / teal / amber; memories golden haze). "
          "Model for all stills: Nano Banana Pro (gemini-3-pro-image). See 03 for the locked frames.", 20)


def p3():
    create(P3, json.load(open("canvas/p3.json")))


def p4():
    create(P4, json.load(open("canvas/p4.json")))
    cov = {"<id-2>": "Lens: 24mm wide, 50mm medium, macro inserts\nMovement: slow push-ins, static\nSound: rain, fluorescent hum, train; music box enters SH06\nContinuity risk: Otto's glasses on/off, tag 0419",
           "<id-14>": "Lens: 35mm, shallow focus\nMovement: circling dance, wide platform\nSound: music box theme only, muffled rain\nContinuity risk: young Otto's face vs. old Otto; Vera's dress",
           "<id-1>": "Lens: 50mm and 85mm close-ups\nMovement: mostly static, handheld on Ines\nSound: bell, Otto's line, Ines humming\nContinuity risk: box in drawer vs. on counter; Ines' wet hair",
           "<id-4>": "Lens: OTS 50mm, wide 24mm\nMovement: slow pull back at end\nSound: Ines' line, theme end + train\nContinuity risk: note in whose hand; box stays on counter"}
    for n, t in cov.items():
        patch(P4, n, t, 18)


def p5text():
    patch(P5, "<id-7>",
          "VO script: none. Lines: Otto 'It isn't here.' / Ines 'She'd want you to have it.' (Kling sound)\n"
          "Music direction: original music-box waltz in A minor (audio/musicbox.py)\nSFX needs: rain, train, bell, hum (Kling clip audio)\n"
          "Mix notes: clip audio low under theme; theme dips under dialogue", 16)


if __name__ == "__main__":
    for step in sys.argv[1:] or ["p1", "p2", "p3", "p4", "p5text"]:
        globals()[step]()
        print("done", step)

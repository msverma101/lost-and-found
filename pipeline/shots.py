"""LOST & FOUND shot list. Each shot: id, scene, seconds, refs (bible keys), still prompt, motion prompt.

Run:  python3 run.py stills [ids...]   then   python3 run.py clips [ids...]
"""

BIBLE = {
    "otto": "bible/a_otto_sheet_ff2c5faa.jpg",
    "young": "bible/a2_young_otto_sheet_572e3c81.jpg",
    "ines": "bible/b_ines_sheet_265aed9d.jpg",
    "vera": "bible/c_vera_sheet_b74f8d23.jpg",
    "office": "bible/la_office_ec73097c.jpg",
    "hall": "bible/lb_dancehall_7b01bcda.jpg",
    "box": "bible/p_musicbox_418f6c6a.jpg",
    "train": "bible/v_train_fcceae0d.jpg",
}

# Uploaded URLs of the same files (avoid re-uploading on every job)
BIBLE_URL = {
    "otto": "<URL of your locked reference image>",
    "young": "<URL of your locked reference image>",
    "ines": "<URL of your locked reference image>",
    "vera": "<URL of your locked reference image>",
    "office": "<URL of your locked reference image>",
    "hall": "<URL of your locked reference image>",
    "box": "<URL of your locked reference image>",
    "train": "<URL of your locked reference image>",
}

NOW = ("Present day, night. Lost-and-found office lit by a cold fluorescent tube and a warm green banker's lamp; "
       "rain outside. Photoreal 35mm film still, fine grain, muted moss green, rust orange, teal and amber.")
PAST = ("1984, memory. Warm golden hazy light, soft halation, heavier warm film grain, faded 1980s colour. "
        "Photoreal film still.")
RULE = ("Single cinematic 16:9 frame, NOT a reference sheet, no split panels, no text, no logos, no watermark. "
        "Match faces, hair and wardrobe exactly to the reference images.")

SHOTS = [
    # ---- Scene 1: the office at night
    ("S01_SH01", 1, 8, ["train", "office"], NOW + " Extreme wide from the far end of a rainy elevated platform: the yellow and grey train pulls out of frame right; across the tracks one lit window of the small lost-and-found office glows warm in the dark station wall.",
     "The train slides out of frame to the right, revealing the lit office window. Rain falls, puddles ripple, slow push in toward the window."),
    ("S01_SH02", 1, 6, ["otto", "office"], NOW + " Medium shot over the counter: OTTO (the old man in the green cardigan from the reference) sits at the wooden counter writing in a big ledger under the green lamp, reading glasses on; rain streaks the window behind him.",
     "Otto writes slowly in the ledger, pauses, adjusts his glasses. Rain runs down the window behind him. Static camera."),
    ("S01_SH03", 1, 5, ["otto", "office"], NOW + " Close-up insert of Otto's old hands tying a small paper claim tag onto a folded red umbrella on the counter, a single wet glove beside it.",
     "His hands loop the string and tie the tag with a small careful knot. Slight handheld drift."),
    ("S01_SH04", 1, 6, ["otto", "office"], NOW + " Medium shot from the side: Otto places a worn teddy bear on a crowded wooden shelf of tagged lost objects; he is half turned, glancing toward a small locked drawer under the counter.",
     "Otto sets the teddy bear on the shelf, straightens it, then his gaze drifts to the drawer. Slow dolly in."),
    ("S01_SH05", 1, 6, ["otto", "box", "office"], NOW + " Close-up: Otto's hands turn a small brass key in the drawer under the counter; inside lies the walnut music box with the swallow inlay and the paper tag 0419.",
     "The key turns, the drawer slides open, his hands lift the walnut music box out gently. Camera follows the box up."),
    ("S01_SH06", 1, 8, ["otto", "box"], NOW + " Tight close-up on Otto's face, lit from below by warm amber light from the open music box he holds; his pale blue eyes glisten.",
     "He turns the brass crank, the lid is open, warm light flickers on his face, his eyes fill with tears and he almost smiles. Very slow push in."),
    # ---- Scene 2: memory 1984
    ("S02_SH07", 2, 6, ["box", "hall"], PAST + " Extreme close-up of the spinning brass cylinder and comb of the music box, catching golden light, sparkles like a mirror ball.",
     "The brass cylinder turns, light sparkles, the image drifts and dissolves toward flickering dots of light like a mirror ball."),
    ("S02_SH08", 2, 8, ["young", "vera", "hall"], PAST + " Wide shot of the dance hall with paper lanterns and a mirror ball: young OTTO (25, dark wavy hair, brown corduroy jacket, from the reference) and VERA (auburn curls, teal polka-dot dress, white cardigan) dance slowly in the middle of the floor among blurred couples.",
     "They slow-dance, turning gently, mirror ball light sweeps over them. Slow circular camera move."),
    ("S02_SH09", 2, 6, ["young", "vera", "hall"], PAST + " Close two-shot: Vera laughs and rests her head on young Otto's shoulder while they dance; his eyes are closed, happy; lantern bokeh behind.",
     "Vera laughs softly and leans her head on his shoulder, they sway. Shallow focus, light flares drift."),
    ("S02_SH10", 2, 7, ["vera", "box", "train"], PAST + " Inside the yellow and grey commuter train at night, 1984: Vera sits by the rain-streaked window, the walnut music box on her lap, a small folded note tucked under its lid; she looks out, uncertain.",
     "Vera looks out of the window, then sets the music box down on the empty seat beside her, touching it once. Train lights flicker past."),
    ("S02_SH11", 2, 6, ["young", "train"], PAST + " Night station platform in the rain, 1984: young Otto runs onto the platform, out of breath, as the yellow and grey train doors close and it starts to leave.",
     "Young Otto runs toward the train, the train pulls away, he slows and stops, breathing hard, watching it go. Camera stays wide."),
    ("S02_SH12", 2, 5, ["box", "train"], PAST + " The empty train seat, the walnut music box left alone on it, passing station lights streaking across the window.",
     "The train rocks gently, lights slide across the music box on the empty seat. Slow push in."),
    ("S02_SH13", 2, 5, ["otto", "box", "office"], NOW + " Close-up of old Otto in the present, the open music box in his hands, the golden memory light fading back to cold fluorescent.",
     "The warm light fades, the crank slows to a stop, Otto exhales and lowers his eyes."),
    # ---- Scene 3: the counter
    ("S03_SH14", 3, 4, ["ines", "office"], NOW + " Extreme close-up of the brass service bell on the counter; a woman's hand in a wet rust-orange raincoat sleeve reaches in to strike it.",
     "The hand strikes the bell once, sharply. Raindrops on the sleeve."),
    ("S03_SH15", 3, 6, ["otto", "box", "office"], NOW + " Medium shot: Otto, startled, quickly closes the music box and slides it into the drawer, turning toward the counter.",
     "Otto snaps the lid shut, pushes the box into the drawer and closes it, then turns to face the counter."),
    ("S03_SH16", 3, 7, ["ines", "office"], NOW + " Medium shot across the counter from Otto's side: INES (short dark curls, freckles, silver hoops, wet rust-orange raincoat, from the reference) stands at the counter holding out a small yellowed paper claim ticket, hopeful.",
     "Ines pushes wet curls from her face and holds out the old ticket, smiling nervously. Slight handheld."),
    ("S03_SH17", 3, 5, ["box", "office"], NOW + " Extreme close-up insert of an old yellowed paper claim ticket on the wooden counter, stamped number 0419, faded blue handwriting.",
     "A finger slides the ticket forward across the counter. Static macro shot."),
    ("S03_SH18", 3, 7, ["otto", "office"], NOW + " Tight close-up, head and shoulders only, of Otto behind the counter, face filling the frame, reading glasses on, looking down at the ticket, guilty; shelves soft and out of focus behind him, 85mm lens.",
     "Otto looks at the ticket for a long moment, swallows, shakes his head slightly and quietly says: \"It isn't here.\" His voice is low and old."),
    ("S03_SH19", 3, 6, ["ines", "office"], NOW + " Medium shot of Ines at the counter, disappointed, folding the ticket into her coat pocket.",
     "Ines nods, tucks the ticket away and turns to the door, softly humming a simple tune to herself. Camera holds."),
    ("S03_SH20", 3, 6, ["otto", "office"], NOW + " Close-up of Otto behind the counter hearing a melody, his face changing from guilt to recognition.",
     "Otto freezes, his eyes widen at the humming, then he reaches down toward the drawer. Slow push in."),
    ("S03_SH21", 3, 7, ["otto", "ines", "box", "office"], NOW + " Two-shot across the counter: Otto places the walnut music box on the counter and slides it toward Ines, who has turned back, surprised.",
     "Otto slides the music box across the counter toward Ines; she steps back to the counter, hand to her mouth. Static wide two-shot."),
    ("S03_SH22", 3, 8, ["ines", "box", "office"], NOW + " Close-up of Ines opening the walnut music box; under the lid lies a small folded old note; warm light on her freckled face.",
     "Ines opens the lid, the cylinder starts turning, she finds the folded note and unfolds it, her eyes fill with tears."),
    ("S03_SH23", 3, 4, ["box", "ines", "office"], NOW + " In the same tiled office with the green lamp, macro close-up over the open walnut music box on the wooden counter: an old folded note in faded ink handwriting that reads only \"For O.\" held in a woman's fingers.",
     "The note trembles slightly in her fingers. Static macro, shallow focus."),
    # ---- Scene 4: resolve and end
    ("S04_SH24", 4, 7, ["ines", "otto", "office"], NOW + " Over-the-shoulder from behind Otto: Ines across the counter holds the small note out to him, tender smile.",
     "Ines gives Otto the note and says gently: \"She'd want you to have it.\" Her voice is warm and soft."),
    ("S04_SH25", 4, 6, ["otto", "office"], NOW + " Close-up of Otto reading the small note, reading glasses on, eyes wet.",
     "Otto reads the note, his lips tremble, then a slow smile spreads across his face. Very slow push in."),
    ("S04_SH26", 4, 6, ["ines", "box", "office"], NOW + " Wide shot of the office: Ines walks out through the glass door onto the rainy platform; the walnut music box stays on the counter in the lamp light.",
     "Ines opens the door and steps out into the rain, the door swings shut, the music box sits on the counter. Static wide."),
    ("S04_SH27", 4, 8, ["otto", "box", "office", "train"], NOW + " Wide shot from the rainy platform looking at the lit office window: inside, Otto sits winding the music box, a small warm figure in the glowing window.",
     "Otto winds the music box in the window, a yellow and grey train glides past in the foreground and its lights flicker over the scene. Slow pull back."),
]

# Film project template

Copy this folder for each new film: `cp -r _template my-film`.

Every AI shot is built from the same parts, in the same order, so characters,
places and the look stay consistent from shot to shot.

## The folders, in production order

| # | File / folder | Real-film equivalent | What goes in it |
|---|---|---|---|
| 0 | `00_brief.md` | Treatment, hackathon rules | Logline, length, format, rules, modifiers, deadline |
| 1 | `01_look/` | Moodboard + DP's look book | `look.md` (palette, film stock, lenses, light, what to avoid) and `moodboard.jpg` |
| 2 | `02_characters/<name>/` | Casting + costume | `character.md` (fixed description, wardrobe) and `sheet.jpg` (turnaround + expressions) |
| 3 | `03_locations/<name>/` | Production design, location scout | `location.md` (era, materials, props, light) and `sheet.jpg` (wide, reverse, details) |
| 4 | `04_props.md` | Props list | Hero props that appear in more than one shot |
| 5 | `05_script.md` | Script | Scenes, action, dialogue |
| 6 | `06_shots.csv` | Shot list / storyboard | One row per shot: framing, lens, movement, action, who, where, sound, model |
| 7 | `07_sound.md` | Sound design + music | Voices, room tone, effects, music, licences |
| 8 | `08_delivery.md` | Delivery + legal | Export specs, credits, releases, AI disclosure |
| – | `log.md` | Camera report | Every generation: id, model, refs, verdict |
| – | `keyframes/`, `clips/`, `edit/` | Rushes and edit | Generated stills, generated clips, cuts |

## The process

1. **Brief.** Fill `00_brief.md` first. Nothing gets generated before the length, format and rules are known.
2. **Look.** Write `look.md`, then generate one moodboard. Approve it before anything else: every later prompt reuses its block.
3. **Characters.** For each character write `character.md`, then generate `sheet.jpg` (front, three-quarter, profile, back, three expressions, grey background). If a real actor is involved, upload their photo first (`letz.py upload photo.jpg`) and put the URL under References.
4. **Locations.** Same for each location: `location.md`, then `sheet.jpg` (wide, reverse angle, two details, no people).
5. **Shot list.** Break the script into shots in `06_shots.csv`.
6. **Keyframes.** For each shot, `python3 shot.py <shot-id>` prints the full prompt and the letz.py command. The keyframe is made as an *edit* with the character, location and moodboard sheets as references.
7. **Clips.** Animate each approved keyframe (`shot.py <shot-id> --video`).
8. **Log everything** in `log.md`, then cut in `edit/`.

## The reference stack (always in this order)

For a keyframe still, pass up to these references:

1. Character sheet(s) of everyone in the shot
2. Location sheet
3. Moodboard
4. The previous approved keyframe, if the shot continues an action

For a video clip, the approved keyframe is the first frame. Add a last frame only when the end pose matters.

## The prompt formula

```
[Camera]   framing, angle, lens, movement
[Who]      each character's prompt block
[Action]   what happens, in order
[Where]    location prompt block
[Look]     look prompt block
[Sound]    (video only) effects, voices, "no music"
```

`shot.py` builds this from the cards, so a character or the look is described in exactly the same words in every shot. Change a card once and every later prompt follows.

## Model notes (checked 13 Nov 2026)

- Stills: Nano Banana Pro (`gemini-3-pro-image`) keeps faces and wardrobe consistent across references.
- Video: Seedance 2.5 refuses input images showing realistic faces, even AI-made ones. Use Kling V4 for shots with visible faces; Seedance is fine for hands, backs and objects.
- Keep tests at 1k stills and 720p clips. Raise the resolution only for final shots.

# LOST & FOUND

A solo concept film written by AI and made with Claude + LetzAI at FILMHACK.AI (48-hour challenge, Berlin, 13–15 Nov 2026),
together with the full step-by-step process on the LetzAI canvas template.

**Live page:** https://msverma101.github.io/lost-and-found

## What's in this repo

| Folder | What it is |
|---|---|
| `index.html`, `media/` | The website: the film (WebM + MP4), process slides, music, photos, credits |
| `pipeline/` | The scripts that made the film |
| `tools/` | The scripts that made the process slides, the cards and the LinkedIn video cut |

### `pipeline/`: how the film was made
- `plan.md`: brief, logline, beats, the locked bible and the sound plan
- `style.txt`: the style block pasted into every image prompt
- `shots.py`: all 27 shots (scene, length, references, prompt, camera movement). The reference-image URLs are replaced with placeholders; use your own locked sheets.
- `letz.py`: a small LetzAI API client (images, videos, edits). Reads your key from `~/.config/letzai/api_key` or `$LETZAI_API_KEY`.
- `run.py`: generates the stills and video clips for every shot through `letz.py`, logging every job ID
- `assemble.py`: cuts clips (or slow-zoom stills where a clip is missing), title and credits, mixes the sound, and writes 16:9 and 9:16 versions with ffmpeg
- `audio/musicbox.py`: the original music-box waltz, synthesised in Python with no samples
- `canvas/canvas.py`: fills the LetzAI canvas pages through the API (canvas IDs replaced with placeholders)

Typical run: `python3 run.py stills`, then `python3 run.py clips`, then `python3 assemble.py`.

### `tools/`: how the slides and video were made
`render_canvas.py` and `render_sections.py` redraw canvas pages from the canvas JSON. `build_process_slides.py` builds the 18 process slides.
`make_cards.py` and `build_video.sh` build the LinkedIn cut. They were written for this project's local folder layout, so treat them as examples rather than ready-to-run tools.

## Credits
Directed by Sneha Verma · story, script, prompts and edit by Claude (Anthropic) · images and video via LetzAI (Nano Banana Pro by Google DeepMind, Kling V4 by Kuaishou) · cut with ffmpeg · made at FILMHACK.AI, organised by FILMAKERS.AI. All characters are fictional.

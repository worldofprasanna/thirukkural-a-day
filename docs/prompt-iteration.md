# Iterating on prompts

The two prompts that change the look of everything are `pipeline/prompts/story_generation.md` (story voice) and `pipeline/prompts/style_guide.md` (visual style). `panel_generation.md` is mostly a fixed template that assembles the other two — you'll touch it less often.

## Story prompt

Goal: catch preachy or flat stories before you commit.

1. Edit `prompts/story_generation.md`.
2. Pick two contrasting kurals from `selected_kurals.json` — one metaphor-heavy (e.g. 211, rain) and one concrete-action (e.g. 81, hospitality). A good prompt works on both shapes.
3. Regenerate story JSON only:
   ```bash
   python generate.py --kural-id 211 --skip-images
   python generate.py --kural-id 81  --skip-images
   ```
4. `git diff content/kurals/` and read each story aloud. Ask:
   - Does a character *say* the moral? (bad — rewrite the prompt.)
   - Are there generic Western names or settings? (bad — tighten the cultural-setting rule.)
   - Does line 6 feel like a summary tacked on? (bad — push for transformation through action, not narration.)
5. When both stories feel right, commit the prompt change.
6. Only then regenerate panels.

## Style guide

Goal: keep the folk-art style from drifting toward generic Indian art or away from kid-softness.

1. Edit `prompts/style_guide.md`.
2. Pick **one** kural and one panel to A/B. Don't regenerate 12 panels to evaluate a style change — image budget is real.
3. Force regeneration of that panel:
   ```bash
   python generate.py --kural-id 211 --force
   ```
   This re-runs all 4 panels for kural 211 (the pipeline regenerates the whole set when --force is passed). If you only want panel 1, delete `pipeline/.cache/` entries for panels 2–4 manually — or just live with regenerating the set.
4. Eyeball against the palette and the "what to avoid" list in `style_guide.md`:
   - Earthy palette, no neons or gradients.
   - Flat figures with thin black outlines.
   - Kid-soft faces, no fear.
   - No text anywhere in the image.
5. When the style is right on one kural, batch-regenerate affected kurals.

## When character consistency drifts

If panels 2–4 drift from panel 1 (different clothing, different skin tone, etc.), the fix order is:

1. Tighten the character `description` field in the story JSON — more concrete visual anchors (specific garment colour, hair style, one distinguishing feature).
2. Regenerate with `--force`. Panels 2–4 use panel 1 as an image reference, so a better panel 1 usually helps the rest.
3. If drift persists after two tries, accept it for MVP. Ship it. Revisit post-launch.

## What not to do

- Don't hand-edit generated story JSON to "fix" a preachy line. The prompt is the fix. Hand edits get overwritten.
- Don't loop `--force` regenerations to chase a perfect panel. Budget is real, drift is part of image gen.
- Don't change the JSON schema in `story.py` without also updating `web/app/types.ts` in the same commit.

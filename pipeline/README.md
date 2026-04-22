# Pipeline

Offline generation: kural → 6-line story + 4-panel folk-art comic + 2×2 composite.

## Setup

```bash
cd pipeline
uv venv
source .venv/bin/activate
uv pip install -e .
```

Create a `.env` at the repo root (copy `.env.example`) with:

```
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

## Run

```bash
# One kural (writes /content/kurals/{id}.json + /web/public/images/{id}/*.png)
python generate.py --kural-id 211

# Every kural in selected_kurals.json
python generate.py --all

# Story-only (for prompt iteration — skips the expensive image step)
python generate.py --kural-id 211 --skip-images

# Ignore image cache and regenerate panels from scratch
python generate.py --kural-id 211 --force
```

Image generations are cached by SHA256 of `(prompt + reference_image_bytes)` in `pipeline/.cache/`. The cache is gitignored. Regenerating the same kural without `--force` will reuse cached panels.

## Layout

```
pipeline/
  generate.py              CLI
  story.py                 Claude (tool use) -> structured story JSON
  image.py                 Gemini image gen + cache + image-to-image chaining
  composite.py             PIL 2x2 grid + title + moral
  selected_kurals.json     Seed list (3 Arathupaal kurals)
  prompts/
    story_generation.md    Story system + user prompt
    panel_generation.md    Per-panel image prompt template
    style_guide.md         Folk-art hard constraints
  .cache/                  Image-gen cache (gitignored)
```

## Adding a new kural

1. Append an entry to `selected_kurals.json` (`id`, `chapter`, `tamil`, `translation`, `moral`, `theme`).
2. `python generate.py --kural-id {id}`.
3. Review. If the story preaches, iterate on `prompts/story_generation.md` and re-run with `--skip-images`. If panels drift, re-run without `--skip-images` and `--force` that specific kural.
4. Commit JSON + images together: `content: add kural {id} - {title}`.

## Iterating on prompts

- Story prompt: run `--skip-images` against 2–3 representative kurals and diff the resulting JSONs in git.
- Panel / style prompt: regenerate a single kural with `--force` rather than all of them. Image generation has a daily budget; don't loop.

## Idempotency

Re-running the same kural overwrites `/content/kurals/{id}.json` and the panel PNGs cleanly. No append, no error, no manual cleanup needed.

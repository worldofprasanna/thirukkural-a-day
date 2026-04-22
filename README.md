# Thirukkural for Kids

I want to narrate new bed time stories for my kids and thought of getting the story inspiration from Thirukkural (2000 year old tamil couplets). My kids are 4 years & 1 year old, so it has to be very simple at least for my first kid to understand and that is the objective of this repo.

Take a printed copy of the Kural with explanation and file it to make it as a book.

Each kural is transformed into a **6-line story** and a **4-panel comic** in Indian folk art style, so kids can absorb the moral through narrative and visuals rather than translation alone.

## Status

Early MVP. Starting with 20 curated kurals from the Arathupaal (Virtue) section before expanding further.

## How it works

```
kural (classical Tamil)
    ↓
Claude generates a 6-line story + 4 story beats + character descriptions
    ↓
Image model generates 4 panels in Indian folk art style
    ↓
Panels composed into a shareable 2×2 grid
    ↓
Static Next.js site serves everything
```

Content is pre-generated offline and served as static assets. No runtime LLM or image generation costs.

## Project structure

```
/pipeline/                  Python generation pipeline (run offline)
    generate.py             Main entry point
    prompts/                Story and image prompt templates
    selected_kurals.json    The 20 MVP kurals

/content/kurals/            Generated story JSON per kural
    211.json
    ...

/web/                       Next.js static site
    app/
        page.tsx            Grid of all kurals
        kural/[id]/page.tsx Detail view with story + comic
    public/images/          Generated comic images per kural

/docs/                      Design notes, style guide, prompt iterations
```

## Design choices

- **English-only** for MVP. Tamil and bilingual versions come later.
- **Indian folk art style** (Madhubani-inspired, softened for kids) — culturally rooted, visually distinctive, differentiates from generic kids' content.
- **Pre-generated content**, not on-demand. Kural content is fixed, so generate once and serve forever.
- **Static site, no backend.** The hard work lives in the offline pipeline.

## Running the pipeline

```bash
cd pipeline
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

export ANTHROPIC_API_KEY=...
export GEMINI_API_KEY=...

python generate.py --kural-id 211           # single kural
python generate.py --all                    # all kurals in selected_kurals.json
```

## Running the site locally

```bash
cd web
pnpm install
pnpm dev
```

## Deploying

The site deploys as a static export to Vercel. Push to `main` and Vercel picks it up.

## License

Content (stories, images) licensed under CC BY-SA 4.0 so teachers and parents can freely share and adapt.
Code licensed under MIT.

The original Thirukkural is in the public domain.

# CLAUDE.md

Context for Claude Code sessions working on this repository.

## Project in one line

Turn each Thirukkural into a 6-line kids' story and a 4-panel folk-art comic, served as a static Next.js site.

## Who this is for

Tamil-speaking parents, teachers, and kids worldwide. Public product, English-only in MVP. The audience reads in English but the cultural context is Tamil/Indian — names, settings, clothing, food, and visual style should reflect that.

## Architecture — what lives where and why

Two distinct halves. Do not conflate them.

**Pipeline (`/pipeline`)** — offline Python. Reads kurals, calls Claude for stories, calls an image model for panels, composes them into grids, writes JSON and PNG files to `/content` and `/web/public/images`. Runs rarely (once per kural, or when we iterate on prompts).

**Web (`/web`)** — Next.js static site. Reads pre-generated content at build time. Zero runtime LLM or image calls. Deploys as a static export to Vercel.

**Why this split**: kural content is fixed. Generating on every page load is wasteful and expensive. Generating once and serving static is fast, cheap, and reliable. Do not add runtime LLM calls to the web app without explicit discussion.

## Content pipeline — the contract

Each kural flows through these stages. Every stage has a fixed output shape that the next stage depends on.

1. **Input**: an entry in `pipeline/selected_kurals.json` with `id`, `tamil`, `translation`, `moral`, `theme`.
2. **Story generation**: Claude returns a JSON object with `title`, `story` (6 lines), `moral_line`, `characters` (array with `name` + detailed visual description), `panels` (4 items, each with `beat` and `scene`).
3. **Image generation**: one image per panel. The character descriptions are injected verbatim into every panel prompt so the same character looks the same across all four.
4. **Composition**: a 2×2 grid PNG stitched with PIL, with folk-art-styled borders, title at top, moral at bottom. This is the shareable hero asset.
5. **Output**:
   - `/content/kurals/{id}.json` — full story metadata
   - `/web/public/images/{id}/panel-{1..4}.png`
   - `/web/public/images/{id}/composite.png`

The JSON schema for `/content/kurals/{id}.json` is the source of truth for the web app. If you change it, update the TypeScript types in `web/app/types.ts` in the same commit.

## The three hardest problems — don't pretend they're solved

1. **Character consistency across 4 panels** — the main technical risk. We pass character descriptions verbatim into every panel prompt and use image-to-image chaining (panel 1 as reference for panels 2–4). Expect some drift; accept it in MVP. If a kural's panels look inconsistent, re-run that kural, don't ship drift.
2. **Story quality over moralizing tone** — easy to generate preachy garbage. Stories must show, not tell. The moral should land through action, not a summary sentence at the end. If a draft story has a character literally saying the moral, iterate.
3. **Visual style consistency** — the folk art style can drift toward generic "Indian art" or lose the kid-friendly softness. Style guide lives in `pipeline/prompts/style_guide.md` — treat it as a hard constraint, not a suggestion.

## Coding conventions

**Python (pipeline)**
- Python 3.11+, managed with `uv`.
- Use the `anthropic` SDK for Claude calls, not raw HTTP.
- All prompts live as `.md` files in `pipeline/prompts/`, not inline in Python. Load and format them at runtime. This lets us iterate on prompts without touching code.
- Structured output: use Claude's JSON mode / tool use for story generation. Never parse free-form text.
- Idempotent generation — rerunning `generate.py --kural-id 211` should overwrite cleanly, not append or error.
- Cache image generations by prompt hash in `pipeline/.cache/`. Image generation is the expensive step.

**TypeScript (web)**
- Next.js 15, App Router, static export (`output: 'export'`).
- Tailwind for styling. No CSS-in-JS.
- All content loaded via `fs` in `generateStaticParams` and server components — no client-side fetching for kural data.
- Types for kural JSON live in `web/app/types.ts`. If you read a kural, type it.
- Use `next/image` with `unoptimized: true` (required for static export).

**General**
- Commit messages: conventional commits (`feat:`, `fix:`, `content:`, `chore:`). Use `content:` when adding or regenerating kurals.
- No secrets in the repo. API keys via `.env.local` (gitignored).
- When generating new kurals, commit the JSON and images in the same commit as the kural ID change.

## Common tasks

**Adding a new kural to the MVP**
1. Add entry to `pipeline/selected_kurals.json`.
2. Run `python generate.py --kural-id {id}`.
3. Review the generated story and panels manually. Regenerate if story is preachy or panels are inconsistent.
4. Commit the JSON + images in one commit: `content: add kural {id} - {title}`.

**Iterating on the story prompt**
1. Edit `pipeline/prompts/story_generation.md`.
2. Re-run against 2–3 representative kurals (pick a metaphor-heavy one and a concrete-action one).
3. Diff the outputs against the previous versions in git.

**Iterating on visual style**
1. Edit `pipeline/prompts/style_guide.md`.
2. Regenerate a single panel for one kural to A/B quickly. Don't regenerate all 80 panels while iterating.
3. Once the style lands, regenerate affected kurals in a batch.

**Adding a new page to the web app**
Keep the site minimal. Grid + detail pages are the MVP. New pages require a concrete user story, not just "it would be nice to have."

## What not to do

- Do not add a database. Content is files. This is intentional.
- Do not add runtime LLM calls to the web app. Generation is offline.
- Do not use image URLs from third-party CDNs in production content. Everything ships in `/web/public/images`.
- Do not hand-edit generated story JSON to "fix" output. If a story is bad, iterate on the prompt and regenerate. Hand edits get overwritten and hide prompt quality issues.
- Do not generate all 20 kurals before validating 3 end-to-end. Cheap iteration first, batch later.
- Do not introduce Tamil script into the web app yet. Language expansion is a post-MVP milestone with its own design work.
- Do not use emoji in UI. Icons, if any, should fit the folk-art aesthetic.

## MVP scope — what "done" looks like

- 20 kurals generated, reviewed, and committed.
- Grid landing page showing all 20 with thumbnails.
- Detail page per kural: Tamil text, English translation, 6-line story, 4-panel comic, moral line.
- OG tags for WhatsApp link previews (critical — this is how the Tamil community shares).
- Deployed to a production Vercel URL on a custom domain.
- No analytics yet, no accounts, no comments, no search.

## Style references

- Thirukkural source text and translations: Project Madurai (public domain).
- Folk art visual reference: simplified Madhubani — flat figures, large expressive eyes, earthy palette (turmeric yellow, indigo, terracotta, forest green, cream), thin black outlines, decorative motifs but not ornate.
- Story tone reference: the best of Indian kids' storytelling — Amar Chitra Katha, Tulika Books, Pratham Books. Warm, grounded, never condescending.

## Known constraints

- Image generation has a per-day budget. Don't loop regenerations without a reason.
- Character consistency is best-effort, not guaranteed. Manual review is part of the workflow.
- Vercel free tier is fine for MVP but watch bandwidth if the site takes off — images are the big cost.

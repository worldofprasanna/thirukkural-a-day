# Web (Next.js static site)

Reads pre-generated content from `/content/kurals/*.json` and images from `/web/public/images/{id}/*.png` at build time. No runtime LLM or image calls.

## Setup

```bash
cd web
pnpm install
```

## Run

```bash
pnpm dev          # local dev server at http://localhost:3000
pnpm build        # static export to web/out/
pnpm typecheck
```

The site builds cleanly whether or not any kurals have been generated yet. With an empty `/content/kurals/`, the grid shows an empty state.

## Pages

- `/` — grid of all kurals with their composite thumbnails.
- `/kural/{id}/` — detail page: Tamil, English translation, 6-line story, 4 individual panels, moral. Per-page OG tags (image = composite) for WhatsApp previews.

## Deploy

Static export (`output: 'export'`). Push to `main`; Vercel serves `web/out/`.

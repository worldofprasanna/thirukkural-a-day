"""CLI entry for the kural generation pipeline.

Examples:
    python generate.py --kural-id 211
    python generate.py --all
    python generate.py --kural-id 211 --skip-images   # iterate on story prompt only
    python generate.py --kural-id 211 --force         # bypass image cache
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from composite import composite_panels
from image import generate_panels
from story import generate_story, write_story_json

PIPELINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_DIR.parent
PROMPTS_DIR = PIPELINE_DIR / "prompts"
CACHE_DIR = PIPELINE_DIR / ".cache"
SELECTED_KURALS = PIPELINE_DIR / "selected_kurals.json"
CONTENT_DIR = REPO_ROOT / "content" / "kurals"
IMAGES_ROOT = REPO_ROOT / "web" / "public" / "images"


def load_selected() -> list[dict[str, Any]]:
    return json.loads(SELECTED_KURALS.read_text(encoding="utf-8"))


def find_kural(all_kurals: list[dict[str, Any]], kural_id: int) -> dict[str, Any]:
    for k in all_kurals:
        if int(k["id"]) == kural_id:
            return k
    raise SystemExit(f"Kural {kural_id} not found in {SELECTED_KURALS.name}")


def run_one(kural: dict[str, Any], skip_images: bool, force: bool) -> None:
    kid = kural["id"]
    print(f"[{kid}] story...", flush=True)
    story = generate_story(kural, PROMPTS_DIR)
    json_path = write_story_json(kural, story, CONTENT_DIR)
    print(f"[{kid}] wrote {json_path.relative_to(REPO_ROOT)}", flush=True)

    if skip_images:
        print(f"[{kid}] --skip-images set, done.", flush=True)
        return

    story_json = json.loads(json_path.read_text(encoding="utf-8"))
    images_dir = IMAGES_ROOT / str(kid)
    print(f"[{kid}] panels...", flush=True)
    panel_paths = generate_panels(
        story_json=story_json,
        prompts_dir=PROMPTS_DIR,
        images_dir=images_dir,
        cache_dir=CACHE_DIR,
        force=force,
    )
    for p in panel_paths:
        print(f"[{kid}]   {p.relative_to(REPO_ROOT)}", flush=True)

    composite_path = images_dir / "composite.png"
    composite_panels(panel_paths, story.title, story.moral_line, composite_path)
    print(f"[{kid}] composite -> {composite_path.relative_to(REPO_ROOT)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a kural story + 4-panel comic.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--kural-id", type=int, help="Generate a single kural by ID.")
    group.add_argument("--all", action="store_true", help="Generate every kural in selected_kurals.json.")
    parser.add_argument("--skip-images", action="store_true", help="Generate story JSON only.")
    parser.add_argument("--force", action="store_true", help="Bypass image cache; regenerate panels.")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")

    kurals = load_selected()
    targets = kurals if args.all else [find_kural(kurals, args.kural_id)]

    for kural in targets:
        run_one(kural, skip_images=args.skip_images, force=args.force)

    return 0


if __name__ == "__main__":
    sys.exit(main())

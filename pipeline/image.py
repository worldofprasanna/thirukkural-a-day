"""Panel image generation via Gemini, with prompt-hash caching and panel-1 reference chaining."""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

IMAGE_MODEL = "gemini-2.5-flash-image"


def _load_templates(prompts_dir: Path) -> tuple[str, str]:
    style = (prompts_dir / "style_guide.md").read_text(encoding="utf-8")
    panel = (prompts_dir / "panel_generation.md").read_text(encoding="utf-8")
    return style, panel


def _characters_block(characters: list[dict[str, str]]) -> str:
    lines = []
    for c in characters:
        lines.append(f"- **{c['name']}** — {c['description']}")
    return "\n".join(lines)


def _build_panel_prompt(
    panel_template: str,
    style_guide: str,
    characters_block: str,
    panel_index: int,
    beat: str,
    scene: str,
) -> str:
    return (
        panel_template
        .replace("{{style_guide}}", style_guide)
        .replace("{{characters_block}}", characters_block)
        .replace("{{panel_index}}", str(panel_index))
        .replace("{{beat}}", beat)
        .replace("{{scene}}", scene)
    )


def _cache_key(prompt: str, reference_png_bytes: bytes | None) -> str:
    h = hashlib.sha256()
    h.update(prompt.encode("utf-8"))
    if reference_png_bytes is not None:
        h.update(b"\x00")
        h.update(hashlib.sha256(reference_png_bytes).digest())
    return h.hexdigest()


def _extract_image(response: Any) -> Image.Image:
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) is not None:
            return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
    raise RuntimeError("Gemini response contained no image part")


def _generate_one(
    client: genai.Client,
    prompt: str,
    reference: Image.Image | None,
) -> Image.Image:
    contents: Any = prompt if reference is None else [prompt, reference]
    config = types.GenerateContentConfig(response_modalities=["IMAGE"])
    if reference is None:
        config.image_config = types.ImageConfig(aspect_ratio="1:1")
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=contents,
        config=config,
    )
    return _extract_image(response)


def generate_panels(
    story_json: dict[str, Any],
    prompts_dir: Path,
    images_dir: Path,
    cache_dir: Path,
    force: bool = False,
) -> list[Path]:
    """Generate the four panel PNGs for a kural. Panel 1 is text-only; 2-4 use panel 1 as reference."""
    style_guide, panel_template = _load_templates(prompts_dir)
    characters_block = _characters_block(story_json["characters"])
    images_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    client = genai.Client()
    written: list[Path] = []
    panel_one_bytes: bytes | None = None
    panel_one_image: Image.Image | None = None

    for idx, panel in enumerate(story_json["panels"], start=1):
        prompt = _build_panel_prompt(
            panel_template, style_guide, characters_block, idx, panel["beat"], panel["scene"]
        )
        reference = panel_one_image if idx > 1 else None
        reference_bytes = panel_one_bytes if idx > 1 else None
        key = _cache_key(prompt, reference_bytes)
        cache_path = cache_dir / f"{key}.png"
        out_path = images_dir / f"panel-{idx}.png"

        if cache_path.exists() and not force:
            image = Image.open(cache_path).convert("RGB")
        else:
            image = _generate_one(client, prompt, reference)
            image.save(cache_path, format="PNG")

        image.save(out_path, format="PNG")
        written.append(out_path)

        if idx == 1:
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            panel_one_bytes = buf.getvalue()
            panel_one_image = image

    return written

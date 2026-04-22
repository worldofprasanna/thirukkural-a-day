"""Story generation: kural -> structured JSON via Claude tool use."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from pydantic import BaseModel, Field, ValidationError, field_validator

STORY_MODEL = "claude-sonnet-4-6"

STORY_TOOL: dict[str, Any] = {
    "name": "submit_story",
    "description": "Submit the six-line kids' story and four comic beats for this kural.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Kid-friendly title, 3-6 words. No generic 'The Story of X' phrasing.",
            },
            "story": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 6,
                "maxItems": 6,
                "description": "Exactly six short sentences. One line per list item. No numbering.",
            },
            "moral_line": {
                "type": "string",
                "description": "One gentle line for under the comic. Must NOT be spoken by any character in the story.",
            },
            "characters": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {
                            "type": "string",
                            "description": (
                                "Detailed visual description so an illustrator can redraw the same character "
                                "four times: hair (length, colour, style), skin tone, clothing (specific garment, "
                                "colour, pattern), one distinguishing feature. Concrete and visual only."
                            ),
                        },
                    },
                    "required": ["name", "description"],
                },
            },
            "panels": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": {
                        "beat": {
                            "type": "string",
                            "description": "Short label for this panel's story moment.",
                        },
                        "scene": {
                            "type": "string",
                            "description": (
                                "Visual description: who is in frame, what they are doing, setting, mood. "
                                "Do not reference previous panels by number."
                            ),
                        },
                    },
                    "required": ["beat", "scene"],
                },
            },
        },
        "required": ["title", "story", "moral_line", "characters", "panels"],
    },
}


class Character(BaseModel):
    name: str
    description: str


class Panel(BaseModel):
    beat: str
    scene: str


class Story(BaseModel):
    title: str
    story: list[str] = Field(min_length=6, max_length=6)
    moral_line: str
    characters: list[Character] = Field(min_length=1)
    panels: list[Panel] = Field(min_length=4, max_length=4)

    @field_validator("story", mode="before")
    @classmethod
    def _coerce_story_lines(cls, v: Any) -> Any:
        # Claude occasionally returns `story` as a JSON-encoded string instead of an array
        # despite the tool schema. Coerce back to a list rather than failing the run.
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
            except json.JSONDecodeError:
                # Fall back to newline-split so a plain-text response still works.
                parsed = [line.strip() for line in v.splitlines() if line.strip()]
            return parsed
        return v


def _load_prompt(prompts_dir: Path) -> tuple[str, str]:
    """Return (system, user_template) split from story_generation.md."""
    raw = (prompts_dir / "story_generation.md").read_text(encoding="utf-8")
    # Expect '## System' and '## User' headers.
    system_marker = "## System"
    user_marker = "## User"
    if system_marker not in raw or user_marker not in raw:
        raise ValueError("story_generation.md must contain '## System' and '## User' sections")
    _, after_system = raw.split(system_marker, 1)
    system, user = after_system.split(user_marker, 1)
    return system.strip(), user.strip()


def _format_user(template: str, kural: dict[str, Any]) -> str:
    out = template
    for key in ("id", "theme", "tamil", "translation", "moral"):
        out = out.replace(f"{{{{{key}}}}}", str(kural.get(key, "")))
    return out


def generate_story(kural: dict[str, Any], prompts_dir: Path) -> Story:
    """Call Claude with tool use, validate, return Story."""
    client = Anthropic()
    system, user_template = _load_prompt(prompts_dir)
    user = _format_user(user_template, kural)

    response = client.messages.create(
        model=STORY_MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[STORY_TOOL],  # type: ignore[arg-type]
        tool_choice={"type": "tool", "name": "submit_story"},
        messages=[{"role": "user", "content": user}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_story":
            try:
                return Story.model_validate(block.input)
            except ValidationError as e:
                raise RuntimeError(
                    f"Claude returned a malformed story payload for kural {kural.get('id')}:\n{e}"
                ) from e

    raise RuntimeError(
        f"Claude did not invoke submit_story for kural {kural.get('id')}. "
        f"Stop reason: {response.stop_reason}"
    )


def write_story_json(kural: dict[str, Any], story: Story, content_dir: Path) -> Path:
    """Write /content/kurals/{id}.json, merging kural source fields + generated story."""
    out_path = content_dir / f"{kural['id']}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": kural["id"],
        "chapter": kural.get("chapter", ""),
        "theme": kural.get("theme", ""),
        "tamil": kural["tamil"],
        "translation": kural["translation"],
        "moral": kural["moral"],
        **story.model_dump(),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
